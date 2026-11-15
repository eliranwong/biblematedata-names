import re
import sqlite3

def main():
    bconn = sqlite3.connect("biblePeople.data")
    rel_tc = dict(bconn.execute("SELECT DISTINCT PersonID, Name FROM PEOPLERELATIONSHIP_TC").fetchall())
    rel_sc = dict(bconn.execute("SELECT DISTINCT PersonID, Name FROM PEOPLERELATIONSHIP_SC").fetchall())
    bconn.close()

    missing_pid_tc = {
        1565: "戶勒", 2184: "尼利亞", 2187: "拿坦業", 2775: "蘇珊娜", 2776: "蘇西",
        2777: "循都基", 2778: "他巴俄", 2779: "他比勒", 2780: "他別", 2781: "大比大／多加",
        2782: "他伯利們", 2783: "他罕", 2784: "他罕", 2785: "他哈", 2786: "他哈",
        2787: "他哈", 2788: "答比匿", 2789: "達買", 2790: "達買", 2791: "達們",
        2792: "他瑪", 2793: "他瑪", 2794: "他瑪", 2795: "單戶篾", 2796: "他發",
        2797: "他普亞", 2798: "他利亞", 2799: "他施", 2800: "他施",
        7000: "上帝／主／父", 7100: "指上帝", 7200: "耶穌／基督／以馬內利／聖子",
        7300: "指耶穌基督", 7500: "天使",
    }

    missing_pid_sc = {
        1565: "户勒", 2184: "尼利亚", 2187: "拿坦业", 2775: "苏珊娜", 2776: "苏西",
        2777: "循都基", 2778: "他巴俄", 2779: "他比勒", 2780: "他别", 2781: "大比大／多加",
        2782: "他伯利们", 2783: "他罕", 2784: "他罕", 2785: "他哈", 2786: "他哈",
        2787: "他哈", 2788: "答比匿", 2789: "达买", 2790: "达买", 2791: "达们",
        2792: "他玛", 2793: "他玛", 2794: "他玛", 2795: "单户篾", 2796: "他发",
        2797: "他普亚", 2798: "他利亚", 2799: "他施", 2800: "他施",
        7000: "上帝／主／父", 7100: "指上帝", 7200: "耶稣／基督／以马内利／圣子",
        7300: "指耶稣基督", 7500: "天使",
    }

    map_tc = dict(rel_tc)
    map_tc.update(missing_pid_tc)

    map_sc = dict(rel_sc)
    map_sc.update(missing_pid_sc)

    iconn = sqlite3.connect("indexes2.sqlite")
    rows = iconn.execute("SELECT Book, Chapter, Verse, Information FROM exlbp").fetchall()

    regex = re.compile(r"<ref onclick=\"exlbp\(([\x27\x22]?BP)?(\d+)([\x27\x22]?)\)\">([^<]*)</ref>")

    def make_repl(mapping):
        def _repl(m):
            prefix = m.group(1) or ""
            pid = int(m.group(2))
            suffix = m.group(3) or ""
            orig_name = m.group(4)
            ch_name = mapping.get(pid, orig_name)
            return f"<ref onclick=\"exlbp({prefix}{pid}{suffix})\">{ch_name}</ref>"
        return _repl

    repl_tc = make_repl(map_tc)
    repl_sc = make_repl(map_sc)

    tc_data = [(b, c, v, regex.sub(repl_tc, info)) for b, c, v, info in rows]
    sc_data = [(b, c, v, regex.sub(repl_sc, info)) for b, c, v, info in rows]

    cursor = iconn.cursor()
    cursor.execute("BEGIN TRANSACTION;")
    cursor.execute("DROP TABLE IF EXISTS exlbp_tc;")
    cursor.execute("CREATE TABLE exlbp_tc (Book INT, Chapter INT, Verse INT, Information TEXT);")
    cursor.executemany("INSERT INTO exlbp_tc (Book, Chapter, Verse, Information) VALUES (?, ?, ?, ?);", tc_data)

    cursor.execute("DROP TABLE IF EXISTS exlbp_sc;")
    cursor.execute("CREATE TABLE exlbp_sc (Book INT, Chapter INT, Verse INT, Information TEXT);")
    cursor.executemany("INSERT INTO exlbp_sc (Book, Chapter, Verse, Information) VALUES (?, ?, ?, ?);", sc_data)

    iconn.commit()

    count_tc = iconn.execute("SELECT COUNT(*) FROM exlbp_tc;").fetchone()[0]
    count_sc = iconn.execute("SELECT COUNT(*) FROM exlbp_sc;").fetchone()[0]
    count_orig = iconn.execute("SELECT COUNT(*) FROM exlbp;").fetchone()[0]
    iconn.close()

    print(f"Original exlbp rows: {count_orig}")
    print(f"Created exlbp_tc rows: {count_tc}")
    print(f"Created exlbp_sc rows: {count_sc}")

if __name__ == "__main__":
    main()

