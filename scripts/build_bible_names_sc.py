#!/usr/bin/env python3
"""
Convert Traditional Chinese dictionary in scripts/bible_names_tc.py
into Simplified Chinese dictionary in scripts/bible_names_sc.py using opencc.
"""

import os
import subprocess
import re

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tc_path = os.path.join(root_dir, 'scripts', 'bible_names_tc.py')
    sc_path = os.path.join(root_dir, 'scripts', 'bible_names_sc.py')

    with open(tc_path, 'r', encoding='utf-8') as f:
        tc_lines = f.readlines()

    entries = []
    for l in tc_lines:
        m = re.match(r'^\s*\"([^\"]+)\":\s*\"(.*)\",?\s*$', l)
        if m:
            entries.append((m.group(1), m.group(2)))

    print(f"Loaded {len(entries)} entries from {tc_path}")

    # Prepare input for opencc
    # Format: key \t val
    raw_text = "\n".join([f"{k}\t{v}" for k, v in entries])

    p = subprocess.Popen(['opencc', '-c', 't2s.json'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    converted_text, err = p.communicate(raw_text)

    if p.returncode != 0:
        raise RuntimeError(f"opencc failed with error: {err}")

    sc_entries = []
    for line in converted_text.strip().split("\n"):
        if "\t" in line:
            sc_k, sc_v = line.split("\t", 1)
            sc_entries.append((sc_k, sc_v))

    print(f"Converted {len(sc_entries)} entries to Simplified Chinese.")

    # Write out scripts/bible_names_sc.py
    out_lines = ["bible_names_sc = {\n"]
    for sc_k, sc_v in sc_entries:
        out_lines.append(f'    "{sc_k}": "{sc_v}",\n')
    out_lines.append("}\n")

    with open(sc_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f"Successfully generated {sc_path} with {len(sc_entries)} entries.")

if __name__ == '__main__':
    main()
