# biblematedata-names

[BibleMateData](https://github.com/eliranwong/biblematedata) is a separate project to provide data for [BibleMate AI Projects](https://github.com/eliranwong/biblemate).

This project is to map biblical names in [biblematedata](https://github.com/eliranwong/biblematedata) from English to Traditional and Simplified Chinese, and to numbered book IDs.

## Credits:

* Initial name mapping data is from [BibleNLP/biblical-names-data](https://github.com/BibleNLP/biblical-names-data).  I have modified the data to fit the format of biblematedata.

* Bible retrieval skill for AI agents to work on the missing data: [biblemate-agentic-workspace](https://github.com/eliranwong/biblemate-agentic-workspace)

## Building the Initial `names_english_chinese.py` Mapping

1. Start with the biblical names dataset from [BibleNLP/biblical-names-data](https://github.com/BibleNLP/biblical-names-data) (`names_english_chinese.tsv` / `names_english_chinese_less.tsv`).
2. Map USFM book abbreviations to numbered book IDs (`1`–`66`) using `book_map_numbered.py`.
3. Format each entry as `"book.chapter.verse": [cu2010s, cu2010t, (esvuk16, bsb, engulb)]` in `names_english_chinese.py`, preserving multiple name entries per verse (note: `verse_to_names` contains duplicate `book.chapter.verse` keys and should be parsed line-by-line rather than evaluated as a Python `dict`).

## Refining and Completing `names_english_chinese.py`

1. **Filling missing `cu2010t` / `cu2010s` entries using CUV:** Retrieved the corresponding Chinese Union Version (CUV) verses via `.agents/skills/bible/bible_retriever.py` to populate empty `cu2010t` values (Traditional Chinese) and convert them to `cu2010s` (Simplified Chinese):
   - Filled **41** entries across 13 verses for 27 `PersonID`s that had no Chinese name anywhere in `PEOPLE_TC`.
   - Filled **632** additional empty entries by ranking candidate `(cu2010s, cu2010t)` pairs from `names_english_chinese.py` and verifying that the Chinese name appears in the retrieved CUV verse text (plus explicit CUV place/person mappings such as `Dan` → `但`, `Paddan-aram` → `巴旦‧亞蘭`, `Ramoth-gilead` → `基列的拉末`, `Jabesh-gilead` → `基列‧雅比`).
   - Remaining **206** empty entries correspond to rows where the English tuple is empty (`('', '', '')`) or CUV omits the explicit name in that verse.

## Full Chinese Name Mapping in `biblePeople.data`

`PEOPLE_TC`, `PEOPLE_SC`, `PEOPLERELATIONSHIP_TC`, and `PEOPLERELATIONSHIP_SC` were populated from `PEOPLE` and `PEOPLERELATIONSHIP` through the following multi-stage pipeline:

1. **Exact Verse & English Name Match:**
   - Matched `(Book, Chapter, Verse)` against `"book.chapter.verse"` in `names_english_chinese.py` and checked whether `Name` appeared in `(esvuk16, bsb, engulb)`, replacing with the first non-empty `cu2010t` (`PEOPLE_TC`) or `cu2010s` (`PEOPLE_SC`) — **13,522** rows updated in each table.
2. **Slash-Alias Splitting & High-Confidence Fuzzy Matching:**
   - Split `/` alias names (e.g., `Jacob / Israel`, `Abram / Abraham`) and matched each part against the same verse's tuple — **1,585** rows updated.
   - Applied same-verse fuzzy matching (`difflib.SequenceMatcher` ratio $\ge 0.90$, excluding `God` vs `GOD`) for minor spelling differences (e.g., `Abiah` ↔ `Abijah`, `Enos` ↔ `Enosh`, `Mahalaleel` ↔ `Mahalalel`) — **263** rows updated.
3. **CUV-Verified Global & Lower-Threshold Fuzzy Matching:**
   - Cross-checked global exact matches and same-verse fuzzy matches ($\ge 0.70$) against retrieved CUV verse texts (**503** rows updated), and extracted remaining proper names directly from the CUV verses (**4,496** rows updated, plus **154** additional rows after updating `names_english_chinese.py`).
4. **Descriptive `PersonID`s, Titles, and `PersonID` Propagation:**
   - Translated the **37** descriptive `PersonID`s (e.g., `Daughter of Machir` → `瑪吉的女兒`/`玛吉的女儿`, `Daughter of Lot - Younger` → `羅得的小女兒`/`罗得的小女儿`) using exact CUV proper names verified against `names_english_chinese.py` and CUV, alongside `God` (`1324` → `上帝`) and `The Angel` (`7500` → `天使`) — **11,318** rows updated.
   - Propagated each `PersonID`'s most frequent Chinese name to its remaining English rows in `PEOPLE_TC` / `PEOPLE_SC` — **1,487** rows updated.
5. **Relationship Table Mapping (`PEOPLERELATIONSHIP_TC` / `PEOPLERELATIONSHIP_SC`):**
   - Duplicated `PEOPLERELATIONSHIP` into `PEOPLERELATIONSHIP_TC` and `PEOPLERELATIONSHIP_SC`.
   - Mapped each `PersonID` to all distinct non-English `Name`s in `PEOPLE_TC` / `PEOPLE_SC` (ordered by `Number`, joined with `|`), and applied the descriptive `PersonID` translations for the 14 `PersonID`s absent from `PEOPLE_TC`.
   - **Final state:** All **33,368** rows in `PEOPLE_TC` / `PEOPLE_SC` and all **12,099** rows in `PEOPLERELATIONSHIP_TC` / `PEOPLERELATIONSHIP_SC` are mapped to Chinese with **0** remaining English or `NULL`/empty `Name` values.

## Chinese Translation and Localization of `exlb3.data`

`exlb3.data` contains rich biographical profiles and name etymologies for biblical individuals in the `exlbp` table. To support both Traditional and Simplified Chinese environments, `exlbp` was duplicated and localized into `exlbp_TC` and `exlbp_SC` (**3,088** rows each):

1. **Table Duplication:**
   - Created `exlbp_TC` and `exlbp_SC` with the schema `(path UNIQUE NOT NULL, content TEXT)` and copied all 3,088 profile rows from `exlbp`.

2. **Traditional Chinese Mapping (`exlbp_TC`):**
   - **PersonID-Based Character Name Mapping:**
     - Mapped every profile heading `<h2 exlbp="{PersonID}">` and every `<ref onclick="exlbp('BP{PersonID}')">` link (**43,908** references total) to the exact Traditional Chinese `Name` associated with that `PersonID` in `PEOPLERELATIONSHIP_TC` from `biblePeople.data` (**0** mismatches).
     - The top `Child of:` (`父母：`) field was similarly mapped directly from the first referenced parent's `PersonID`.
     - The 34 `PersonID`s absent from `PEOPLERELATIONSHIP_TC` (such as titles or collective designations like `BP7000`, `BP7100`, `BP7200`, `BP7300`, `BP7500`, and post-biblical/variant records) were mapped to standard CUV Traditional Chinese equivalents.
   - **Name Etymology Translation (`name_meanings_tc.py`):**
     - Extracted **3,163** unique name meaning descriptions across *People's Bible Names* and *Hitchcock's Bible Names*.
     - Translated them into Traditional Chinese matching CUV theological terminology, keeping pronunciation prefixes (`<i>...</i>`) and translating dictionary source labels (`《聖經人名》` and `《希區柯克聖經人名》`).
     - Exported the complete mapping as the `name_meanings_tc` dictionary in `scripts/name_meanings_tc.py`.
   - **Biographical Data Translation:**
     - Extracted **2,956** unique biographical text templates across the 3,087 profile entries containing a `Biographical Data` section (1 entry, `BP2780`, lacks a biographical section; the remaining rows represent homonymous individuals sharing identical dictionary entries).
     - Parameterized inline Scripture links (`<BCV_n/>`) and person links (`<EXLBP_n/>`) to preserve HTML tag integrity, translated the entries into Traditional Chinese, and restored all embedded references.
   - **Scripture References (`bcv`):**
     - Translated all **45,980** `<ref onclick="bcv(...)">` references to use standard CUV Traditional Chinese book names (`創世記`–`啟示錄`).
   - **Vital Data, Locations, and UI Labels:**
     - Standardized and translated all UI labels: `Vital Data` (`基本資料`), `Gender` (`性別` / `男` / `女`), `Birth/Death Year` (`出生/逝世年份`), `Birth/Death Location` (`出生/逝世地點`), `Near Relation` (`近親關係`), `Paternal Ancestory` (`父系祖先`), `Occurences In Authorized Version` (`在和合本／欽定本中出現的經文`), etc.
     - Translated dates and eras (`Unknown` → `未知`, `BC` → `公元前 ... 年`, `AD` → `公元 ... 年`, `Before` → `早於`).
     - Translated biblical geographic locations (`Jerusalem` → `耶路撒冷`, `Egypt` → `埃及`, `Babylon` → `巴比倫`, etc.) and tribal/genealogical notes (`From the Tribe of Judah` → `屬猶大支派`, `In the Genealogy of Jesus` → `在耶穌的家譜中`, etc.).

3. **Simplified Chinese Mapping (`exlbp_SC`):**
   - Converted the complete contents of `exlbp_TC` to Simplified Chinese using `opencc` (`t2s.json`) for speed, determinism, and 1:1 cross-language alignment across all etymological and biographical text.
   - Enforced exact `PEOPLERELATIONSHIP_SC` names by `PersonID` across all `<h2 exlbp="...">` headers, `<ref onclick="exlbp('BP...')">` links, and `父母：` fields (**0** mismatches).
   - Exported the Simplified Chinese name meanings dictionary as `name_meanings_sc` in `scripts/name_meanings_sc.py` (**3,163** entries).

