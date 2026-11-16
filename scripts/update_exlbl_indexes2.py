import html
import re
import sqlite3

def get_heading_map(exlb3_path="exlb3.data"):
    conn = sqlite3.connect(exlb3_path)
    cursor = conn.cursor()
    cursor.execute("SELECT path, content FROM exlbl")
    rows = cursor.fetchall()
    conn.close()

    heading_map = {}
    for path, content in rows:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', content)
        if m:
            raw = m.group(1).strip()
            clean = re.sub(r'<[^>]+>', '', raw).strip()
            clean = html.unescape(clean)
            heading_map[path] = clean
        else:
            print(f"Warning: No heading found in {path}")
            
    print(f"Loaded {len(heading_map)} exact entry names from {exlb3_path}.")
    return heading_map

def update_exlbl(db_path="indexes2.sqlite", exlb3_path="exlb3.data"):
    heading_map = get_heading_map(exlb3_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, Book, Chapter, Verse, Information FROM exlbl")
    rows = cursor.fetchall()

    ref_pattern = re.compile(r"<ref onclick=[\"']exlbl\('([^']+)'\)[\"']>.*?</ref>")

    total_rows = len(rows)
    changed_rows = 0
    total_refs = 0
    changed_refs = 0
    unmapped_bls = set()

    updates = []

    for rowid, book, ch, vs, info in rows:
        if not info:
            continue

        def replace_ref(m):
            nonlocal total_refs, changed_refs
            total_refs += 1
            bl = m.group(1)
            old_full = m.group(0)
            
            # Extract old inner name
            old_name_m = re.search(r">([\s\S]*?)</ref>", old_full)
            old_name = old_name_m.group(1) if old_name_m else ""

            new_name = heading_map.get(bl)
            if not new_name:
                unmapped_bls.add(bl)
                return old_full

            if new_name != old_name:
                changed_refs += 1

            return f'<ref onclick="exlbl(\'{bl}\')">{new_name}</ref>'

        new_info = ref_pattern.sub(replace_ref, info)
        if new_info != info:
            changed_rows += 1
            updates.append((new_info, rowid))

    print(f"Total rows inspected: {total_rows}")
    print(f"Rows with changes: {changed_rows}")
    print(f"Total references checked: {total_refs}")
    print(f"References updated: {changed_refs}")
    if unmapped_bls:
        print(f"Warning: {len(unmapped_bls)} unmapped BL IDs: {unmapped_bls}")
    else:
        print("All BL references successfully mapped to exact entry names!")

    print(f"Applying {len(updates)} row updates to {db_path}...")
    cursor.executemany("UPDATE exlbl SET Information = ? WHERE rowid = ?", updates)
    conn.commit()

    # Integrity check
    cursor.execute("PRAGMA integrity_check")
    status = cursor.fetchone()[0]
    print(f"Database integrity check: {status}")

    # Inspect sample rows
    print("\nVerification of Sample Rows:")
    for check_id in [4, 5, 10, 15, 22, 478]:
        cursor.execute("SELECT rowid, Book, Chapter, Verse, Information FROM exlbl WHERE rowid = ?", (check_id,))
        r = cursor.fetchone()
        print(f"  RowID {r[0]} ({r[1]}:{r[2]}:{r[3]}): {r[4]}")

    conn.close()

if __name__ == "__main__":
    update_exlbl()

