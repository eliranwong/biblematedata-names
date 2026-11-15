#!/usr/bin/env python3
"""
Translate scripts/bible_names_tc.py into Traditional Chinese:
- Dictionary keys: Traditional Chinese names from tsv/bible_locations.tsv, tsv/bible_persons.tsv,
  names_english_chinese.tsv, and extra_names_tc.py.
- Values: Translated into Traditional Chinese ("<b>{TC_Key}</b> - {TC_Meaning}").
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import re
import sqlite3
from collections import Counter, OrderedDict

from scripts.name_meanings_tc import name_meanings_tc
from scripts.extra_meanings_ad import extra_meanings_ad
from scripts.extra_meanings_eh import extra_meanings_eh
from scripts.extra_meanings_ip import extra_meanings_ip
from scripts.extra_meanings_qz import extra_meanings_qz
from scripts.extra_names_tc import extra_names_tc

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tsv_loc_path = os.path.join(root_dir, 'tsv', 'bible_locations.tsv')
    tsv_per_path = os.path.join(root_dir, 'tsv', 'bible_persons.tsv')
    tsv_nec_path = os.path.join(root_dir, 'tsv', 'names_english_chinese.tsv')
    exlb3_path = os.path.join(root_dir, 'exlb3.data')
    src_en_path = os.path.join(root_dir, 'scripts', 'bible_names.py')
    out_tc_path = os.path.join(root_dir, 'scripts', 'bible_names_tc.py')

    # 1. Load Locations
    loc_map = {}
    with open(tsv_loc_path, 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            loc_map[r['English']] = r['Traditional Chinese'].strip()

    # 2. Load Persons
    per_map = {}
    with open(tsv_per_path, 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            en = r['English']
            tc = r['Traditional Chinese']
            parts = [p.strip() for p in tc.split('|')]
            noise = {'祭司', '妻子', '兒子', '女兒', '孫子', '來到', '聲音', '上來', '殿', '王', '生', '族', '引誘', '嫩', '赫', '轉身', '十八萬', '二百五十', '耶路撒冷', '罵陣', '父親', '威但'}
            valid_parts = [p for p in parts if p not in noise and not any(p.endswith(n) for n in ['人', '書'])]
            if en == 'Abram / Abraham': clean_tc = '亞伯蘭 / 亞伯拉罕'
            elif en == 'Jacob / Israel': clean_tc = '雅各 / 以色列'
            elif en == 'Sarai / Sarah': clean_tc = '撒萊 / 撒拉'
            elif en == 'Saul / Paul': clean_tc = '掃羅 / 保羅'
            elif en == 'Simon / Peter': clean_tc = '西門 / 彼得'
            elif valid_parts: clean_tc = valid_parts[0]
            else: clean_tc = parts[0]
            per_map.setdefault(en, []).append(clean_tc)
    per_tc = {en: Counter(tcs).most_common(1)[0][0] for en, tcs in per_map.items()}

    # 3. Load names_english_chinese
    nec_map = {}
    with open(tsv_nec_path, 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            t = r['cu2010t'].strip()
            if t:
                nec_map.setdefault(r['name'].lower(), []).append(t)
                for col in ['esvuk16', 'bsb', 'engulb']:
                    v = r[col].strip()
                    if v: nec_map.setdefault(v.lower(), []).append(t)
    nec_tc = {k: Counter(v).most_common(1)[0][0] for k, v in nec_map.items()}

    # 4. Master Translation Lookup for Meanings
    trans_lookup = {}
    for d in [extra_meanings_ad, extra_meanings_eh, extra_meanings_ip, extra_meanings_qz, name_meanings_tc]:
        for k, v in d.items():
            trans_lookup[k.strip().lower()] = v.strip().replace('"', '')

    # Specific disambiguated meanings
    specific_meanings = {
        "that quavers or totters (zelophehad's daughter)": "顫抖或動搖（西羅非哈的女兒）",
        "large; extended (name of a woman)": "寬大；擴展（女子之名）",
        "proud; quarrelsome (applied to egypt)": "驕傲；好爭吵（指埃及）",
        "vanity; breath; vapor": "虛空；氣息；水汽",
        "a city; mourning": "城邑；哀哭",
        "the offering or lifting up": "奉獻或舉起",
        "eli, my god, my god": "以利，我的神，我的神",
        "same as noah": "同挪亞",
        "same as rahab": "同喇合"
    }
    trans_lookup.update(specific_meanings)

    # Load from exlb3.data
    conn = sqlite3.connect(exlb3_path)
    cursor = conn.cursor()
    cursor.execute('SELECT exlbp.content, exlbp_TC.content FROM exlbp JOIN exlbp_TC ON exlbp.path = exlbp_TC.path')
    hitchcock_by_name = {}
    for en_row, tc_row in cursor.fetchall():
        m_en_h2 = re.search(r'<h2[^>]*>([^<]+)</h2>', en_row)
        m_tc_h2 = re.search(r'<h2[^>]*>([^<]+)</h2>', tc_row)
        m_en_m = re.search(r'([^<>\n\r]+)\s*-\s*<font color=\"brown\"><i>Hitchcock\'s Bible Names</i></font>', en_row)
        m_tc_m = re.search(r'([^<>\n\r]+)\s*-\s*<font color=\"brown\"><i>《希區柯克聖經人名》</i></font>', tc_row)
        if m_en_h2 and m_tc_h2 and m_en_m and m_tc_m:
            en_n = m_en_h2.group(1).strip().lower()
            if en_n not in ['noah', 'rahab', 'abel', 'eli']:
                hitchcock_by_name[en_n] = m_tc_m.group(1).strip().replace('"', '')
            trans_lookup[m_en_m.group(1).strip().lower()] = m_tc_m.group(1).strip().replace('"', '')

        en_matches = re.findall(r'([^<>\n\r]+?)\s*-\s*<font color=\"brown\"><i>([^<]+)</i></font>', en_row)
        tc_matches = re.findall(r'([^<>\n\r]+?)\s*-\s*<font color=\"brown\"><i>([^<]+)</i></font>', tc_row)
        if len(en_matches) == len(tc_matches):
            for (e_text, _), (t_text, _) in zip(en_matches, tc_matches):
                e_clean = e_text.strip().lstrip('·').strip().lower()
                t_clean = t_text.strip().lstrip('·').strip().replace('"', '')
                if e_clean and t_clean and e_clean not in trans_lookup:
                    trans_lookup[e_clean] = t_clean
                e_parts = [p.strip() for p in e_clean.split(';')]
                t_parts = [p.strip().replace('"', '') for p in t_clean.split('；')]
                if len(e_parts) == len(t_parts) and len(e_parts) > 1:
                    for ep, tp in zip(e_parts, t_parts):
                        if ep and tp and ep not in trans_lookup:
                            trans_lookup[ep] = tp
    conn.close()

    def get_tc_key(en_name, en_val):
        # Disambiguate duplicate keys
        if en_name == 'Abel':
            if 'City' in en_val: return loc_map.get('Abel', '亞比拉')
            return per_tc.get('Abel', '亞伯')
        if en_name == 'Noah':
            if 'Zelophehad' in en_val: return '挪阿'
            return '挪亞'
        if en_name == 'Rahab':
            if 'Egypt' in en_val: return '拉哈伯'
            return '喇合'
        if en_name == 'Eli':
            return '以利'

        # Priority 1: Person or Location TSV
        if en_name in per_tc and en_name not in loc_map:
            return per_tc[en_name]
        if en_name in loc_map and en_name not in per_tc:
            return loc_map[en_name]
        if en_name in per_tc and en_name in loc_map:
            if any(w in en_val.lower() for w in ['city', 'mountain', 'valley', 'river', 'place', 'well', 'fountain', 'waters', 'stone']):
                return loc_map[en_name]
            return per_tc[en_name]

        # Priority 2: names_english_chinese
        if en_name.lower() in nec_tc:
            return nec_tc[en_name.lower()]

        # Priority 3: extra names
        if en_name in extra_names_tc:
            return extra_names_tc[en_name]

        return en_name

    def clean_text(text):
        t = text.replace('"', '').replace("'", "")
        # Remove parenthetical english words e.g. / elisheba, elizabeth
        t = re.sub(r'[/／]\s*[a-zA-Z,\s]+(?=[)）])', '', t)
        t = re.sub(r'[（(][a-zA-Z,\s]+[)）]', '', t)
        t = re.sub(r'\s+([)）])', r'', t)
        return t.strip()

    def translate_meaning(en_name, en_val):
        nl = en_name.lower()
        vl = en_val.strip().lower()

        # Check whole val lookup first
        if vl in trans_lookup:
            return clean_text(trans_lookup[vl])

        # Semicolon parts
        parts = [p.strip() for p in en_val.split(';')]
        tc_parts = []
        all_parts_found = True
        for p in parts:
            if not p: continue
            pl = p.lower()
            if pl in trans_lookup:
                tc_parts.append(clean_text(trans_lookup[pl]))
            else:
                all_parts_found = False
                break
        if all_parts_found and tc_parts:
            return "；".join(tc_parts)

        # Hitchcock by name (for names not in special list)
        if nl in hitchcock_by_name and nl not in ['noah', 'rahab', 'abel', 'eli']:
            return clean_text(hitchcock_by_name[nl])

        return clean_text(en_val)

    # 5. Read entries from bible_names.py
    entries = []
    with open(src_en_path, 'r', encoding='utf-8') as f:
        for l in f:
            m = re.match(r'^\s*\"([^\"]+)\":\s*\"<b>[^<]+</b>\s*-\s*(.*)\",?\s*$', l)
            if m:
                entries.append((m.group(1), m.group(2)))

    # 6. Group meanings by tc_key
    tc_entries = OrderedDict()
    for en_name, en_val in entries:
        tc_key = get_tc_key(en_name, en_val)
        tc_meaning = translate_meaning(en_name, en_val)
        
        # Split tc_meaning into individual clauses and sanitize
        clauses = [clean_text(c) for c in tc_meaning.split('；') if clean_text(c)]
        
        if tc_key not in tc_entries:
            tc_entries[tc_key] = []
        for c in clauses:
            if c == f'同{tc_key}':
                continue
            if c not in tc_entries[tc_key]:
                tc_entries[tc_key].append(c)

    # 7. Write out scripts/bible_names_tc.py
    lines = ["bible_names_tc = {\n"]
    for tc_key, clauses in tc_entries.items():
        combined_meaning = "；".join(clauses)
        combined_meaning = combined_meaning.replace('"', '\\"')
        val = f"<b>{tc_key}</b> - {combined_meaning}"
        lines.append(f'    "{tc_key}": "{val}",\n')
    lines.append("}\n")

    with open(out_tc_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"Successfully generated {out_tc_path} with {len(tc_entries)} unique Traditional Chinese entries.")

if __name__ == '__main__':
    main()
