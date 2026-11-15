#!/usr/bin/env python3
"""
Generate tsv/bible_persons.tsv from biblePeople.data
with columns: PersonID, English, Traditional Chinese, Simplified Chinese.
"""

import os
import sqlite3

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(repo_root, "biblePeople.data")
    tsv_path = os.path.join(repo_root, "tsv", "bible_persons.tsv")

    bconn = sqlite3.connect(db_path)

    query = """
    SELECT r.PersonID, r.Name, r_tc.Name, r_sc.Name
    FROM PEOPLERELATIONSHIP r
    JOIN PEOPLERELATIONSHIP_TC r_tc ON r.PersonID = r_tc.PersonID 
        AND r.Relationship = r_tc.Relationship 
        AND r.RelationshipOrder = r_tc.RelationshipOrder
    JOIN PEOPLERELATIONSHIP_SC r_sc ON r.PersonID = r_sc.PersonID 
        AND r.Relationship = r_sc.Relationship 
        AND r.RelationshipOrder = r_sc.RelationshipOrder
    WHERE r.Relationship = "[Reference]"
    ORDER BY r.PersonID
    """
    rows = bconn.execute(query).fetchall()

    # Include PersonID 7500 (The Angel) from PEOPLE tables if not in PEOPLERELATIONSHIP
    pids = {r[0] for r in rows}
    if 7500 not in pids:
        row_7500 = bconn.execute("""
            SELECT p.PersonID, p.Name, p_tc.Name, p_sc.Name
            FROM PEOPLE p
            JOIN PEOPLE_TC p_tc ON p.Number = p_tc.Number
            JOIN PEOPLE_SC p_sc ON p.Number = p_sc.Number
            WHERE p.PersonID = 7500
            LIMIT 1
        """).fetchone()
        if row_7500:
            rows.append(row_7500)
            rows.sort(key=lambda x: x[0])

    bconn.close()

    header = ["PersonID", "English", "Traditional Chinese", "Simplified Chinese"]
    lines = ["\t".join(header) + "\n"]

    for pid, en, tc, sc in rows:
        lines.append(f"{pid}\t{en}\t{tc}\t{sc}\n")

    with open(tsv_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Successfully generated {tsv_path} with {len(rows)} entries (+1 header row).")

if __name__ == "__main__":
    main()

