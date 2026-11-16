#!/usr/bin/env python3
"""Build exlbt_tc (Traditional Chinese Hitchcock topical analysis) in exlb3.data.

Phases:
  prep    create table, mechanically translate bcv scripture refs, apply the
          name dictionary, extract remaining English text nodes into chunks
  status  chunk translation progress
  apply   splice translated chunks back into the table
  verify  integrity checks
"""
import json
import os
import re
import sqlite3
import sys

DB = "/home/eliran/dev/biblematedata-names/exlb3.data"
WORK = "/tmp/exlbt_tc_work"
REPO = "/home/eliran/dev/biblematedata-names"

# 66 canonical CUV Traditional Chinese book names (1-based)
BOOKS = [
    "創世記", "出埃及記", "利未記", "民數記", "申命記", "約書亞記", "士師記",
    "路得記", "撒母耳記上", "撒母耳記下", "列王紀上", "列王紀下", "歷代志上",
    "歷代志下", "以斯拉記", "尼希米記", "以斯帖記", "約伯記", "詩篇", "箴言",
    "傳道書", "雅歌", "以賽亞書", "耶利米書", "耶利米哀歌", "以西結書",
    "但以理書", "何西阿書", "約珥書", "阿摩司書", "俄巴底亞書", "約拿書",
    "彌迦書", "那鴻書", "哈巴谷書", "西番雅書", "哈該書", "撒迦利亞書",
    "瑪拉基書", "馬太福音", "馬可福音", "路加福音", "約翰福音", "使徒行傳",
    "羅馬書", "哥林多前書", "哥林多後書", "加拉太書", "以弗所書", "腓立比書",
    "歌羅西書", "帖撒羅尼迦前書", "帖撒羅尼迦後書", "提摩太前書", "提摩太後書",
    "提多書", "腓利門書", "希伯來書", "雅各書", "彼得前書", "彼得後書",
    "約翰一書", "約翰二書", "約翰三書", "猶大書", "啟示錄",
]
assert len(BOOKS) == 66, len(BOOKS)

REF_OPENER = re.compile(r"<ref onclick=\"bcv\((\d+),(\d+),(\d+)\)\">")
TAG_RE = re.compile(r"<[^>]*>")
CJK = re.compile(r"[一-鿿㐀-䶿]")

# generic english words that must never act as biblical-name dictionary keys
STOPWORDS = {
    "son", "sons", "daughter", "ben", "of", "the", "see", "also", "called",
    "same", "god", "lord", "he", "she", "it", "man", "woman", "men", "women",
    "city", "land", "sea", "mount", "river", "one", "two", "three", "first",
    "second", "third", "day", "night", "name", "book", "children", "job",
    "no", "so", "on", "in", "is", "as", "at", "an", "am", "do", "we", "me",
    "us", "by", "to", "or", "and", "if", "up", "go", "am",
    # conceptual / common words that polluted the dictionaries
    "judgment", "sin", "put", "destruction", "valley", "brook", "salt",
}

# ------------------------------------------------------------------ helpers


def clean_tag_text(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def build_name_map(conn):
    name_map = {}

    def add(eng, zh):
        eng = (eng or "").strip()
        zh = (zh or "").strip()
        if not eng or not zh:
            return
        if len(eng) <= 2 or (len(eng) > 3 and eng == eng.lower()):
            return
        if any(ch.isdigit() for ch in eng):
            return
        if eng.lower() in STOPWORDS:
            return
        k = eng.lower()
        if k not in name_map:
            # curated h2 values may hold pipe-joined variants: keep the first
            name_map[k] = re.split(r"[|｜]", zh)[0].strip()

    def add_variants(eng, zh):
        """Register pipe-joined name variants (first wins)."""
        zh = (zh or "").strip() or ""
        for p in [q.strip() for q in re.split(r"[|｜]", zh) if q.strip()]:
            add(eng, p)

    for e, c in conn.execute(
        "SELECT e1.content, e2.content FROM exlbp e1 JOIN exlbp_TC e2 ON e1.path=e2.path"
    ):
        me, mc = re.search(r"<h2[^>]*>(.*?)</h2>", e, re.S), re.search(r"<h2[^>]*>(.*?)</h2>", c, re.S)
        if me and mc:
            add(clean_tag_text(me.group(1)), clean_tag_text(mc.group(1)))
    for e, c in conn.execute(
        "SELECT e1.content, e2.content FROM exlbl e1 JOIN exlbl_tc e2 ON e1.path=e2.path"
    ):
        me, mc = re.search(r"<h1[^>]*>(.*?)</h1>", e, re.S), re.search(r"<h1[^>]*>(.*?)</h1>", c, re.S)
        if me and mc:
            add(clean_tag_text(me.group(1)), clean_tag_text(mc.group(1)))
    for le, lc in conn.execute(
        "SELECT e1.location, e2.location FROM exlbli e1 JOIN exlbli_tc e2 ON e1.path=e2.path"
    ):
        if le and lc:
            add(le, lc)
            for v in re.split(r"[;,]", le):
                add(v, lc)
    conn.close()

    # names_english_chinese.py: majority vote per english key (the file has
    # verse-level misalignments; the consistent reading wins)
    path = os.path.join(REPO, "scripts", "names_english_chinese.py")
    if os.path.exists(path):
        rx = re.compile(r'"(\d+)\.(\d+)\.(\d+)":\s*\[\s*"([^"]*)",\s*"([^"]*)",\s*\(([^)]*)\)')
        votes = {}
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                m = rx.search(line)
                if not m:
                    continue
                tc = m.group(5)
                for a, b in re.findall(r'"([^"]*)"|\x27([^\x27]*)\x27', m.group(6)):
                    eng = (a or b).strip()
                    if not eng or not tc:
                        continue
                    if len(eng) <= 2 or (len(eng) > 3 and eng == eng.lower()):
                        continue
                    if any(ch.isdigit() for ch in eng):
                        continue
                    if eng.lower() in STOPWORDS:
                        continue
                    tc_primary = re.split(r"[|｜]", tc)[0].strip()
                    votes.setdefault(eng, {})[tc_primary] = votes.setdefault(eng, {}).get(tc_primary, 0) + 1
        from collections import Counter
        for eng, zhs in votes.items():
            if eng.lower() in name_map:
                continue
            top = Counter(zhs).most_common(1)
            if top:
                add(eng, top[0][0])
        # conflict resolution: where the curated value disagrees with an
        # overwhelming names-file majority, the curated h2 was a verse-level
        # fragment/misalignment - take the dominant reading
        conflict = 0
        for eng, zhs in votes.items():
            k = eng.lower()
            if k not in name_map:
                continue
            total = sum(zhs.values())
            if total < 10:
                continue
            top, cnt = Counter(zhs).most_common(1)[0]
            if cnt / total >= 0.9 and name_map[k] != top:
                name_map[k] = top
                conflict += 1
        print(f"dictionary conflicts resolved by majority: {conflict}")
    return name_map


def build_book_vocab(ref_inners_with_book):
    """Collect the set of leading book-word phrases used in ref display texts.
    ref_inners_with_book: iterable of (book_number, display_text)."""
    counter = {}
    for book, text in ref_inners_with_book:
        tokens = re.findall(r"\S+", text)
        phrase = []
        ok = True
        for i, t in enumerate(tokens[:3]):
            if ":" in t:
                break
            if re.fullmatch(r"[0-9]+", t):
                nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
                if i == 0 and re.search(r"[A-Za-z]", nxt):
                    phrase.append(t)
                    continue
                break
            if re.fullmatch(r"[0-9]?[A-Za-z][A-Za-z\.\-]*", t):
                phrase.append(t)
                continue
            break
        if phrase:
            p = re.sub(r"[^0-9a-z\- ]", "", " ".join(phrase).lower())
            p = re.sub(r"\s+", " ", p).strip()
            if p:
                counter.setdefault(p, {}).setdefault(book, 0)
                counter[p][book] = counter[p].get(book, 0) + 1
    vocab = {}
    for p, books in counter.items():
        if not re.search(r"[a-z]", p):
            continue
        tot = sum(books.values())
        main, cnt = max(books.items(), key=lambda kv: kv[1])
        ratio = cnt / tot
        pure_alpha = not any(ch.isdigit() for ch in p)
        if ratio >= 0.9 or (pure_alpha and ratio >= 0.7 and tot >= 5):
            vocab[p] = main
    return vocab


def translate_refs(content, vocab=None):
    """Replace the leading English book word of each bcv ref display text with
    the traditional Chinese book name taken from the bcv book number."""
    if vocab is None:
        vocab = BOOKWORD_VOCAB
    out = []
    idx = 0
    for m in REF_OPENER.finditer(content):
        out.append(content[idx : m.start()])
        end = content.find("</ref>", m.end())
        if end == -1:
            break
        book = int(m.group(1))
        inner = content[m.end() : end]
        replaced = False
        if 1 <= book <= 66 and re.search(r"[A-Za-z]", inner):
            span_m = None
            toks = list(re.finditer(r"\S+", inner))
            for k in (3, 2, 1):
                if len(toks) < k:
                    continue
                phrase = " ".join(t.group(0) for t in toks[:k])
                p = re.sub(r"[^0-9a-z\- ]", "", phrase.lower())
                p = re.sub(r"\s+", " ", p).strip()
                if p and p in vocab:
                    vocab_book = vocab[p]
                    zh = BOOKS[vocab_book - 1] if 1 <= vocab_book <= 66 else BOOKS[book - 1]
                    span_m = (toks[0].start(), toks[k - 1].end())
                    break
            if span_m:
                span = inner[span_m[0] : span_m[1]]
                # only replace when the span contains no tags
                if "<" not in span:
                    out.append(m.group(0))
                    out.append(inner[: span_m[0]])
                    out.append(zh + " ")
                    out.append(inner[span_m[1] :])
                    replaced = True
        if not replaced:
            out.append(m.group(0) + inner)
        out.append("</ref>")
        idx = end + len("</ref>")
    out.append(content[idx:])
    return "".join(out)


def split_parts(content):
    """[(kind, text)] with kind 'tag' or 'text', order preserved."""
    parts = []
    pos = 0
    for m in TAG_RE.finditer(content):
        if m.start() > pos:
            parts.append(("text", content[pos : m.start()]))
        parts.append(("tag", m.group(0)))
        pos = m.end()
    if pos < len(content):
        parts.append(("text", content[pos:]))
    return parts


RUN_RE = re.compile(r"[0-9]?[A-Za-z][A-Za-z'\-]*(?: [0-9]?[A-Za-z][A-Za-z'\-]*)*")


def apply_name_text(t, name_map):
    """Replace known biblical names inside a text node (case-sensitive:
    Title-Case or ALL-CAPS only), possessive-aware, longest-match first."""
    if not re.search(r"[A-Z]", t):
        return t
    out = []
    pos = 0
    for m in RUN_RE.finditer(t):
        out.append(t[pos : m.start()])
        run = m.group(0)
        words = run.split(" ")
        zh_used = None
        tail_rest = None
        for i in range(len(words), 0, -1):
            first = " ".join(words[:i]).strip()
            bare = first[:-2] if first.lower().endswith("'s") else first
            # candidate must start uppercase (or Title-Case/ALL-CAPS body):
            # avoids matching lowercase fragments of prose
            letters = [c for c in bare if c.isalpha()]
            if not letters or letters[0].islower():
                continue
            if bare.lower() in STOPWORDS:
                continue
            zh = name_map.get(bare.lower())
            if zh:
                zh_used = zh
                tail_rest = run[len(" ".join(words[:i])) :]
                break
        if zh_used is None:
            out.append(run)
        elif tail_rest == "'s":
            out.append(zh_used + "的")
        else:
            out.append(zh_used + tail_rest if tail_rest else zh_used)
        pos = m.end()
    out.append(t[pos:])
    return "".join(out)


def skip_segment(t):
    if not re.search(r"[A-Za-z]{2}", t):
        return True
    stripped = t.strip()
    if not re.search(r"[A-Za-z]{2}", stripped):
        return True
    core = re.sub(r"[\s,.;:()\[\]#&\-–—/+'\"]+", "", stripped)
    if not re.search(r"[A-Za-z]", core):
        return True
    if re.fullmatch(r"[0-9ivxIVXlcLC]+", core):
        return True
    cjk = len(CJK.findall(stripped))
    letters = len(re.findall(r"[A-Za-z]", stripped))
    if cjk >= max(1, 0.5 * (cjk + letters)):
        return True
    return False


# ------------------------------------------------------------------- phases


BOOKWORD_VOCAB = {}


def build_vocab_once():
    conn = sqlite3.connect(DB)
    pairs = []
    for (content,) in conn.execute("SELECT content FROM exlbt"):
        if not content:
            continue
        for m in REF_OPENER.finditer(content):
            end = content.find("</ref>", m.end())
            if end == -1:
                continue
            book = int(m.group(1))
            inner = content[m.end() : end]
            if re.search(r"[A-Za-z]", inner):
                pairs.append((book, re.sub(r"<[^>]*>", "", inner)))
    conn.close()
    return build_book_vocab(pairs)


def preprocess():
    vocab = build_vocab_once()
    globals()["BOOKWORD_VOCAB"] = vocab
    print(f"book vocab: {len(vocab)} phrases")
    name_map = build_name_map(sqlite3.connect(DB))
    rows = sqlite3.connect(DB).execute(
        "SELECT path, content FROM exlbt ORDER BY path"
    ).fetchall()
    print(f"rows: {len(rows)}, name map: {len(name_map)}")
    segs = []
    for path, content in rows:
        if content is None:
            continue
        content = translate_refs(content)
        parts = split_parts(content)
        in_ref = 0
        for kind, t in parts:
            if kind == "tag":
                if re.match(r"<ref\b", t):
                    in_ref += 1
                elif re.match(r"</ref", t):
                    in_ref = max(0, in_ref - 1)
                continue
            if in_ref > 0:
                continue
            if re.search(r"[A-Z]", t):
                t2 = apply_name_text(t, name_map)
            else:
                t2 = t
            if skip_segment(t2):
                continue
            segs.append(t2.strip())
    print(f"segments after mechanical passes: {len(segs)}")
    total = sum(len(s) for s in segs)
    print(f"chars to translate: {total}")
    # chunk them ~40k chars
    nchunks = max(1, round(total / 40000))
    per = (len(segs) + nchunks - 1) // nchunks
    os.makedirs(WORK, exist_ok=True)
    n = 0
    meta = []
    for start in range(0, len(segs), per):
        n += 1
        chunk = segs[start : start + per]
        fn = os.path.join(WORK, f"chunk_{n:03d}.json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False)
        meta.append([n, len(chunk)])
    with open(os.path.join(WORK, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"nchunk": n, "chunk_sizes": meta}, f)
    print(f"chunks: {n}")


def phase_prep():
    os.makedirs(WORK, exist_ok=True)
    # baseline table
    conn = sqlite3.connect(DB)
    conn.execute('CREATE TABLE IF NOT EXISTS "exlbt_tc" ( path unique not null, content text )')
    conn.execute('INSERT OR IGNORE INTO "exlbt_tc" SELECT path, content FROM exlbt')
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM exlbt_tc").fetchone()[0]
    print(f"exlbt_tc baseline rows: {n}")
    conn.close()
    preprocess()


def phase_status():
    done = pending = 0
    meta = json.load(open(os.path.join(WORK, "meta.json")))
    for n in range(1, meta["nchunk"] + 1):
        fn = os.path.join(WORK, f"chunk_{n:03d}.out")
        if os.path.exists(fn):
            done += 1
        else:
            pending += 1
    print(f"chunks done: {done}, pending: {pending}")


def phase_apply():
    global BOOKWORD_VOCAB
    vocab = build_vocab_once()
    meta = json.load(open(os.path.join(WORK, "meta.json")))
    src_all, trans = [], []
    for n in range(1, meta["nchunk"] + 1):
        fn = os.path.join(WORK, f"chunk_{n:03d}.json")
        fo = os.path.join(WORK, f"chunk_{n:03d}.out")
        src = json.load(open(fn, encoding="utf-8"))
        out = json.load(open(fo, encoding="utf-8"))
        assert isinstance(out, list), f"{fo} is not a JSON array"
        if len(out) != len(src):
            raise SystemExit(f"{fo} length mismatch: {len(out)} != {len(src)}")
        src_all.extend(src)
        trans.extend(out)
    print(f"loaded {len(trans)} translations")

    name_map = build_name_map(sqlite3.connect(DB))
    rows = sqlite3.connect(DB).execute(
        "SELECT path, content FROM exlbt ORDER BY path"
    ).fetchall()
    conn = sqlite3.connect(DB)
    updates = []
    i = 0
    for path, content in rows:
        if content is None:
            continue
        base = translate_refs(content, vocab)
        parts = split_parts(base)
        in_ref = 0
        new_content = []
        for kind, t in parts:
            if kind == "tag":
                if re.match(r"<ref\b", t):
                    in_ref += 1
                elif re.match(r"</ref", t):
                    in_ref = max(0, in_ref - 1)
                new_content.append(t)
                continue
            if in_ref > 0:
                new_content.append(t)
                continue
            t2 = apply_name_text(t, name_map) if re.search(r"[A-Z]", t) else t
            if skip_segment(t2):
                new_content.append(t)
                continue
            if i >= len(src_all) or t2.strip() != src_all[i]:
                raise SystemExit(f"alignment break at segment {i} (row {path})")
            new_content.append(trans[i])
            i += 1
        updates.append(("".join(new_content), path))
    if i != len(trans):
        raise SystemExit(f"alignment mismatch: consumed {i}, expected {len(trans)}")
    print(f"updating {len(updates)} rows")
    conn.executemany('UPDATE "exlbt_tc" SET content=? WHERE path=?', updates)
    conn.commit()
    print("rows updated:", conn.total_changes)
    print("integrity:", conn.execute("PRAGMA integrity_check").fetchone()[0])
    counts = conn.execute(
        "SELECT (SELECT COUNT(*) FROM exlbt), (SELECT COUNT(*) FROM exlbt_tc)"
    ).fetchone()
    print(f"rows exlbt={counts[0]} exlbt_tc={counts[1]}")
    conn.close()


def phase_verify():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT e1.path, e1.content, e2.content FROM exlbt e1 JOIN exlbt_tc e2 ON e1.path=e2.path"
    ).fetchall()
    bad_tags = bad_refs = 0
    remaining_eng = 0
    for path, eng, zh in rows:
        te, tz = TAG_RE.findall(eng), TAG_RE.findall(zh)
        if te != tz:
            bad_tags += 1
            if bad_tags < 3:
                print("TAG DIFF in", path, te[:6], tz[:6])
        refs_e = re.findall(r"bcv\(\d+,\d+,\d+\)", eng)
        refs_z = re.findall(r"bcv\(\d+,\d+,\d+\)", zh)
        if refs_e != refs_z:
            bad_refs += 1
    ascii_ratio = 0
    for path, eng, zh in rows:
        text = " ".join(re.split(r"<[^>]*>", zh))
        # count latin letters outside of common abbreviations
        lat = re.findall(r"[A-Za-z]", text)
        cjk = len(CJK.findall(text))
        if lat and lat > 2 * cjk:
            remaining_eng += 1
    print(f"rows compared: {len(rows)}; tag-mismatch rows: {bad_tags}; ref-code mismatches: {bad_refs}")
    print(f"rows still mostly-English: {remaining_eng}")
    print("integrity:", conn.execute("PRAGMA integrity_check").fetchone()[0])
    conn.close()


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "prep"
    if phase == "prep":
        phase_prep()
    elif phase == "status":
        phase_status()
    elif phase == "apply":
        phase_apply()
    elif phase == "verify":
        phase_verify()
    else:
        print(__doc__)
