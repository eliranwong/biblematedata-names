import apsw, csv, importlib, re, os, sys, json
from agentmake.utils.rag import get_embeddings
from prompt_toolkit.shortcuts import ProgressBar
from biblemate import config, BIBLEMATEVECTORSTORE

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def add_vector_data(db_file="dictionary.db", table="Dictionary", h2=False):
    db_file = os.path.join(BIBLEMATEVECTORSTORE, db_file)
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            # Check if 'entry' column already exists
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            if 'entry' not in column_names:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry TEXT;")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry_vector TEXT;")
            # Update 'entry' and 'entry_vector' columns
            cursor.execute(f"SELECT path, content FROM {table};")
            with ProgressBar() as pb:
                for path, content in pb(cursor.fetchall()):
                    search = re.search(f">([^<>]+?)</{'h2' if h2 else 'ref'}>", content)
                    if search:
                        entry = search.group(1)
                        vector = get_embeddings([entry], config.embedding_model)
                        vector_str = json.dumps(vector.tolist())
                        cursor.execute(f"UPDATE {table} SET entry = ?, entry_vector = ? WHERE path = ?;", (entry, vector_str, path))
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN content;")
            #cursor.execute(f"VACUUM;")

def _insert_name_vector(cursor, table, path, entry):
    entry = re.sub("<[^<>]*?>", "", entry).strip()
    vector = get_embeddings([entry], config.embedding_model)
    vector_str = json.dumps(vector.tolist())
    cursor.execute(
        f"INSERT OR IGNORE INTO {table} (path, entry, entry_vector) VALUES (?,?,?)",
        (path, entry, vector_str),
    )


def _populate_vector_table(db_file, table, entries, create_table=True):
    if not os.path.isfile(db_file):
        return
    with apsw.Connection(db_file) as connection:
        cursor = connection.cursor()
        if create_table:
            cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {table} (
    path          TEXT NOT NULL UNIQUE,
    entry         TEXT,
    entry_vector  TEXT
)
""")
        existing_paths = {row[0] for row in cursor.execute(f"SELECT path FROM {table};")}
        items = [(path, entry) for path, entry in entries if path not in existing_paths]
        if not items:
            print(f"{table}: all {len(entries)} entries already present")
            return
        if sys.stdout.isatty():
            with ProgressBar() as pb:
                for path, entry in pb(items):
                    _insert_name_vector(cursor, table, path, entry)
        else:
            total = len(items)
            for idx, (path, entry) in enumerate(items, 1):
                _insert_name_vector(cursor, table, path, entry)
                if idx % 500 == 0 or idx == total:
                    print(f"Processed {idx}/{total} entries into {table}")
        #cursor.execute(f"VACUUM;")


def add_vector_names(create_table=True, table="exlbn_sc", module_name="bible_names_sc", attr_name=None, db_file=None):
    python_data_dir = os.path.join(REPO_DIR, "data", "python")
    if python_data_dir not in sys.path:
        sys.path.insert(0, python_data_dir)
    names_dict = getattr(importlib.import_module(module_name), attr_name or module_name)

    if db_file is None:
        db_file = os.path.join(REPO_DIR, "data", "sqlite", "exlb.db")
    _populate_vector_table(db_file, table, list(names_dict.items()), create_table=create_table)


def _read_tsv_entries(tsv_file, id_col, entry_col, path_prefix=""):
    with open(tsv_file, newline="", encoding="utf-8") as f:
        return [
            (f"{path_prefix}{row[id_col].strip()}", row[entry_col].strip())
            for row in csv.DictReader(f, delimiter="\t")
            if row[id_col].strip() and row[entry_col].strip()
        ]


def add_vector_locations(create_table=True, table="exlbl_tc", column="Traditional Chinese", tsv_file=None, db_file=None):
    if tsv_file is None:
        tsv_file = os.path.join(REPO_DIR, "data", "tsv", "bible_locations.tsv")
    if db_file is None:
        db_file = os.path.join(REPO_DIR, "data", "sqlite", "exlb.db")
    entries = _read_tsv_entries(tsv_file, "LocationID", column)
    _populate_vector_table(db_file, table, entries, create_table=create_table)


def add_vector_persons(create_table=True, table="exlbp_tc", column="Traditional Chinese", tsv_file=None, db_file=None):
    if tsv_file is None:
        tsv_file = os.path.join(REPO_DIR, "data", "tsv", "bible_persons.tsv")
    if db_file is None:
        db_file = os.path.join(REPO_DIR, "data", "sqlite", "exlb.db")
    entries = _read_tsv_entries(tsv_file, "PersonID", column)
    _populate_vector_table(db_file, table, entries, create_table=create_table)

def fix_vector_collections(db_file="collection.db", table="PARALLEL"):
    db_file = os.path.join(BIBLEMATEVECTORSTORE, db_file)
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            # Update 'entry' and 'entry_vector' columns
            cursor.execute(f"SELECT path, entry FROM {table} WHERE entry LIKE ':%';")
            with ProgressBar() as pb:
                for path, entry in pb(cursor.fetchall()):
                    entry = re.sub("^:", "", entry).strip()
                    vector = get_embeddings([entry], config.embedding_model)
                    vector_str = json.dumps(vector.tolist())
                    cursor.execute(f"UPDATE {table} SET entry = ?, entry_vector = ? WHERE path = ?;", (entry, vector_str, path))
            #cursor.execute(f"VACUUM;")

def add_vector_collections(db_file="collection.db", table="PROMISES", h2=False):
    db_file = os.path.join(BIBLEMATEVECTORSTORE, db_file)
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            # Check if 'entry' column already exists
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            if 'entry' not in column_names:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN path TEXT;")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry TEXT;")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry_vector TEXT;")
            # Update 'entry' and 'entry_vector' columns
            cursor.execute(f"SELECT Tool, Number, Topic FROM {table};")
            with ProgressBar() as pb:
                for tool, number, topic in pb(cursor.fetchall()):
                    path = f"{tool}.{number}"
                    entry = re.sub(r"^[\.0-9: ]+?([^\.0-9 ])", r"\1", topic).strip()
                    vector = get_embeddings([entry], config.embedding_model)
                    vector_str = json.dumps(vector.tolist())
                    cursor.execute(f"UPDATE {table} SET path = ?, entry = ?, entry_vector = ? WHERE Tool = ? AND Number = ?;", (path, entry, vector_str, tool, number))
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN Tool;")
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN Number;")
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN Topic;")
            cursor.execute(f"ALTER TABLE {table} DROP COLUMN Passages;")
            #cursor.execute(f"VACUUM;")

def add_vector_encyclopedias():
    db_file = os.path.join(BIBLEMATEVECTORSTORE, "encyclopedia.db")
    if os.path.isfile(db_file):
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            for table in ("DAC", "DCG", "HAS", "ISB", "KIT", "MSC"):
                print(f"Working on table `{table}` ...")
                # Check if 'entry' column already exists
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                if 'entry' not in column_names:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry TEXT;")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN entry_vector TEXT;")
                # Update 'entry' and 'entry_vector' columns
                cursor.execute(f"SELECT path, content FROM {table};")
                with ProgressBar() as pb:
                    for path, content in pb(cursor.fetchall()):
                        search = re.search(">([^<>]+?)</ref>", content)
                        if search:
                            entry = search.group(1)
                            vector = get_embeddings([entry], config.embedding_model)
                            vector_str = json.dumps(vector.tolist())
                            cursor.execute(f"UPDATE {table} SET entry = ?, entry_vector = ? WHERE path = ?;", (entry, vector_str, path))
                cursor.execute(f"ALTER TABLE {table} DROP COLUMN content;")
            #cursor.execute(f"VACUUM;")


if __name__ == "__main__":
    add_vector_names(table="exlbn", module_name="bible_names_aligned_with_exlbp_exlbl", attr_name="bible_names")
    add_vector_names(table="exlbn_tc", module_name="bible_names_tc")
    add_vector_names(table="exlbn_sc", module_name="bible_names_sc")
    add_vector_locations(table="exlbl", column="English")
    add_vector_locations(table="exlbl_tc", column="Traditional Chinese")
    add_vector_locations(table="exlbl_sc", column="Simplified Chinese")
    add_vector_persons(table="exlbp", column="English")
    add_vector_persons(table="exlbp_tc", column="Traditional Chinese")
    add_vector_persons(table="exlbp_sc", column="Simplified Chinese")