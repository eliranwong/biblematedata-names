import html
import re
import sqlite3
import sys

def get_heading_map(exlb3_path="exlb3.data"):
    conn = sqlite3.connect(exlb3_path)
    cursor = conn.cursor()
    cursor.execute("SELECT path, content FROM exlbp")
    rows = cursor.fetchall()
    conn.close()

    heading_map = {}
    for path, content in rows:
        m = re.search(r'<h[12][^>]*>(.*?)</h[12]>', content)
        if m:
            raw = m.group(1).strip()
            clean = re.sub(r'<[^>]+>', '', raw).strip()
            clean = html.unescape(clean)
            heading_map[path] = clean
        else:
            print(f"Warning: No heading found in {path}")
            
    print(f"Loaded {len(heading_map)} exact entry names from {exlb3_path}.")
    return heading_map

def update_exlbp(db_path="indexes2.sqlite", exlb3_path="exlb3.data"):
    heading_map = get_heading_map(exlb3_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, Book, Chapter, Verse, Information FROM exlbp")
    rows = cursor.fetchall()

    ref_pattern = re.compile(r"<ref onclick=[\"']exlbp\('([^']+)'\)[\"']>.*?</ref>")

    total_rows = len(rows)
    changed_rows = 0
    total_refs = 0
    changed_refs = 0
    unmapped_bps = set()

    updates = []

    for rowid, book, ch, vs, info in rows:
        if not info:
            continue

        def replace_ref(m):
            nonlocal total_refs, changed_refs
            total_refs += 1
            bp = m.group(1)
            old_full = m.group(0)
            
            # Extract old inner name
            old_name_m = re.search(r">([\s\S]*?)</ref>", old_full)
            old_name = old_name_m.group(1) if old_name_m else ""

            new_name = heading_map.get(bp)
            if not new_name:
                unmapped_bps.add(bp)
                return old_full

            if new_name != old_name:
                changed_refs += 1

            return f'<ref onclick="exlbp(\'{bp}\')">{new_name}</ref>'

        new_info = ref_pattern.sub(replace_ref, info)
        if new_info != info:
            changed_rows += 1
            updates.append((new_info, rowid))

    print(f"Total rows inspected: {total_rows}")
    print(f"Rows with changes: {changed_rows}")
    print(f"Total references checked: {total_refs}")
    print(f"References updated: {changed_refs}")
    if unmapped_bps:
        print(f"Warning: {len(unmapped_bps)} unmapped BP IDs: {unmapped_bps}")
    else:
        print("All BP references successfully mapped to exact entry names!")

    print(f"Applying {len(updates)} row updates to {db_path}...")
    cursor.executemany("UPDATE exlbp SET Information = ? WHERE rowid = ?", updates)
    conn.commit()

    # Integrity check
    cursor.execute("PRAGMA integrity_check")
    status = cursor.fetchone()[0]
    print(f"Database integrity check: {status}")

    # Inspect row 5
    cursor.execute("SELECT rowid, Book, Chapter, Verse, Information FROM exlbp WHERE rowid = 5")
    r5 = cursor.fetchone()
    print(f"\nVerification of Row 5:")
    print(f"  RowID {r5[0]} ({r5[1]}:{r5[2]}:{r5[3]}): {r5[4]}")

    conn.close()

if __name__ == "__main__":
    update_exlbp()

