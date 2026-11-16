#!/usr/bin/env python3
"""
Generate scripts/bible_locations_tc.py and scripts/bible_locations_sc.py
by replacing English location names in scripts/bible_locations.py with
Traditional Chinese and Simplified Chinese names from the canonical BL mapping.
"""

import os
import re
import sys

# Ensure repository root is in python path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.duplicate_exlbl_indexes2 import build_bl_mapping
from data.python.bible_locations import BIBLE_LOCATIONS

def main():
    print("Building canonical location mappings...")
    bl_map, verse_names, pair_overrides, rows, ref_regex, iconn = build_bl_mapping()
    iconn.close()

    bible_locations_path = os.path.join(repo_root, "scripts", "bible_locations.py")
    tc_path = os.path.join(repo_root, "scripts", "bible_locations_tc.py")
    sc_path = os.path.join(repo_root, "scripts", "bible_locations_sc.py")

    with open(bible_locations_path, "r", encoding="utf-8") as f:
        orig_lines = f.readlines()

    tc_lines = []
    sc_lines = []
    line_re = re.compile(r'^(\s*\"(BL\d+)\":\s*\()\"[^\"]*\"(,\s*.*)$')

    converted_count = 0
    for line in orig_lines:
        if line.startswith("BIBLE_LOCATIONS = {"):
            tc_lines.append("BIBLE_LOCATIONS_TC = {\n")
            sc_lines.append("BIBLE_LOCATIONS_SC = {\n")
            continue
        m = line_re.match(line)
        if m:
            prefix = m.group(1)
            bl_id = m.group(2)
            suffix = m.group(3)
            if bl_id not in bl_map:
                raise KeyError(f"Missing translation for {bl_id}")
            tc_name, sc_name = bl_map[bl_id]
            tc_lines.append(f'{prefix}"{tc_name}"{suffix}\n')
            sc_lines.append(f'{prefix}"{sc_name}"{suffix}\n')
            converted_count += 1
        else:
            tc_lines.append(line)
            sc_lines.append(line)

    print(f"Writing {tc_path}...")
    with open(tc_path, "w", encoding="utf-8") as f:
        f.writelines(tc_lines)

    print(f"Writing {sc_path}...")
    with open(sc_path, "w", encoding="utf-8") as f:
        f.writelines(sc_lines)

    # Generate tsv/bible_locations.tsv
    tsv_path = os.path.join(repo_root, "tsv", "bible_locations.tsv")
    print(f"Writing {tsv_path}...")
    coord_re = re.compile(r'^\s*\"(BL\d+)\":\s*\(\"[^\"]*\",\s*([^,\s]+),\s*([^,\s\)]+)\),?\s*$')
    coord_str_map = {}
    for line in orig_lines:
        m = coord_re.match(line)
        if m:
            bl_id, lat_str, lon_str = m.groups()
            coord_str_map[bl_id] = (lat_str, lon_str)

    tsv_header = ["LocationID", "English", "Traditional Chinese", "Simplified Chinese", "Latitude", "Longitude"]
    tsv_lines = ["\t".join(tsv_header) + "\n"]
    for k in BIBLE_LOCATIONS:
        eng_name = BIBLE_LOCATIONS[k][0]
        tc_name, sc_name = bl_map[k]
        lat_str, lon_str = coord_str_map[k]
        tsv_lines.append(f"{k}\t{eng_name}\t{tc_name}\t{sc_name}\t{lat_str}\t{lon_str}\n")

    with open(tsv_path, "w", encoding="utf-8") as f:
        f.writelines(tsv_lines)

    print(f"Successfully converted {converted_count} locations.")

    # Validation
    from scripts.bible_locations_tc import BIBLE_LOCATIONS_TC
    from scripts.bible_locations_sc import BIBLE_LOCATIONS_SC

    assert len(BIBLE_LOCATIONS_TC) == 1147, f"Expected 1147 entries in TC, got {len(BIBLE_LOCATIONS_TC)}"
    assert len(BIBLE_LOCATIONS_SC) == 1147, f"Expected 1147 entries in SC, got {len(BIBLE_LOCATIONS_SC)}"
    assert set(BIBLE_LOCATIONS_TC.keys()) == set(BIBLE_LOCATIONS.keys()), "TC keys do not match original keys"
    assert set(BIBLE_LOCATIONS_SC.keys()) == set(BIBLE_LOCATIONS.keys()), "SC keys do not match original keys"

    for k in BIBLE_LOCATIONS:
        orig_name, lat, lon = BIBLE_LOCATIONS[k]
        tc_name, tc_lat, tc_lon = BIBLE_LOCATIONS_TC[k]
        sc_name, sc_lat, sc_lon = BIBLE_LOCATIONS_SC[k]

        assert tc_lat == lat and tc_lon == lon, f"Coordinates mismatch in TC for {k}"
        assert sc_lat == lat and sc_lon == lon, f"Coordinates mismatch in SC for {k}"

        if re.search(r"[A-Za-z]", tc_name):
            raise ValueError(f"English characters detected in TC: {k} -> {tc_name}")
        if re.search(r"[A-Za-z]", sc_name):
            raise ValueError(f"English characters detected in SC: {k} -> {sc_name}")

    print("All validations passed successfully!")

if __name__ == "__main__":
    main()

