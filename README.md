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

## Chinese Translation and Localization of Verse Index in `indexes2.sqlite`

`indexes2.sqlite` stores biblical verse-level index data linking verses to characters (`exlbp`), locations (`exlbl`), and topics (`exlbt`). The `exlbp` table was duplicated and localized into `exlbp_tc` and `exlbp_sc` (**21,022** rows each, covering all **53,693** person occurrences across 3,073 unique `PersonID`s):

1. **Table Creation:**
   - Created `exlbp_tc` and `exlbp_sc` with matching schema `(Book INT, Chapter INT, Verse INT, Information TEXT)`.
2. **Traditional Chinese Mapping (`exlbp_tc`):**
   - Replaced all English character names inside `<ref onclick="exlbp('BP{PersonID}')">{Name}</ref>` with their exact Traditional Chinese `Name` from `PEOPLERELATIONSHIP_TC` mapped by `PersonID`, complemented by standard CUV designations for indexing IDs (7000, 7100, 7200, 7300, 7500, etc.) identical to `exlb3.data`.
   - **0** unmapped `PersonID`s and **0** remaining English name occurrences.
3. **Simplified Chinese Mapping (`exlbp_sc`):**
   - Replaced all character names inside `<ref onclick="exlbp('BP{PersonID}')">{Name}</ref>` with their exact Simplified Chinese `Name` from `PEOPLERELATIONSHIP_SC` mapped by `PersonID` (with CUV Simplified indexing titles for 7000–7500).
   - **0** unmapped `PersonID`s and **0** remaining English name occurrences.
4. **English Canonical Entry Name Alignment (`exlbp`):**
   - Standardized all **53,693** person references across all **21,022** rows in the English `exlbp` table so each PersonID consistently displays its exact dictionary heading name from `exlb3.data` (e.g. `BP7000` → `God/Lord/Father`, `BP7100` → `Reference To God`, `BP7200` → `Jesus/Christ/Emmanuel/Son`, `BP7300` → `Reference To Jesus Christ`, `BP7400` → `Reference To the Holy Spirit`, `BP7500` → `Reference To A Bodily Appearence of God`).
   - Replaced surface-form pronouns, fragments, and unclosed italic tags (e.g. `<i>he`, `him`) with exact canonical names across **41,753** references (**18,507** modified rows), achieving **100%** consistency (**0** mismatches).

## Chinese Translation and Localization of Location Verse Index in `indexes2.sqlite`

The location index table `exlbl` was duplicated and localized into `exlbl_tc` and `exlbl_sc` (**4,430** rows each, covering all **6,941** location occurrences across 1,133 unique `BL` location IDs):

1. **Table Creation:**
   - Created `exlbl_tc` and `exlbl_sc` with matching schema `(Book INT, Chapter INT, Verse INT, Information TEXT)`.
2. **Multi-Stage Mapping Pipeline:**
   - **Same-Verse & English Match:** Matched `(Book, Chapter, Verse)` and surface location name against `names_english_chinese.py`, resolving **5,254** occurrences (**75.7%**) directly.
   - **Canonical & CUV-Verified Aliases:** Cross-referenced canonical location names from `exlbli` (`exlb3.data`) and global name frequencies against CUV verse text (`CUV.bible`) to map an additional **1,141** occurrences.
   - **Exhaustive CUV Verification:** Resolved the remaining 248 location IDs by extracting exact biblical place names directly from CUV verse text (e.g. `BL202` → `伯特利`/`伯特利`, `BL986` → `紅海`/`红海`, `BL1021` → `鹽海`/`盐海`, `BL234` → `伯‧示麥`/`伯‧示麦`, `BL701` → `基列‧耶琳`/`基列‧耶琳`, `BL861` → `橄欖山`/`橄榄山`), with demonyms (`Egyptians` → `埃及人`, `Midianites` → `米甸人`) and generic terms (`river` → `大河`, `city` → `城`, `quicksands` → `賽耳底沙灘`) handled with contextual accuracy.
3. **Traditional & Simplified Alignment:**
   - Converted all Traditional Chinese names to Simplified Chinese using the project's comprehensive 725-character biblical Chinese orthographic mapping.
   - Fixed historical closing tag typos (`</exlbp></ref>`) to well-formed `<ref onclick="exlbl('BL...')">...</ref>`.
   - **Final state:** All **4,430** rows and **6,941** references in `exlbl_tc` and `exlbl_sc` mapped to Chinese with **0** remaining English letters or unmapped references.
4. **English Canonical Entry Name Alignment (`exlbl`):**
   - Standardized all **6,941** location references across all **4,430** rows in the English `exlbl` table so each LocationID consistently displays its exact dictionary heading name from `exlb3.data` (e.g. `BL312` → `Ethiopia/Cush`, `BL421` → `Euphrates River`, `BL902` → `Nod`, `BL1093` → `Sidon/Zidon`, `BL202` → `Beth-El`, `BL362` → `Egypt/Egyptians/Egyptian`).
   - Replaced generic surface nouns (e.g. `city`, `river`), inflected forms, and historical tag typos (`</exlbp></ref>`) with exact canonical names across **2,934** references (**2,314** modified rows), achieving **100%** consistency (**0** mismatches).

## Chinese Location Coordinates & Dictionary Localization (`bible_locations_*.py`, `tsv/bible_locations.tsv`, and `exlb3.data` `exlbl_tc` / `exlbl_sc`)

1. **Location Coordinates Mapping (`bible_locations_tc.py`, `bible_locations_sc.py`, and `tsv/bible_locations.tsv`):**
   - Replaced all **1,147** location entries in `scripts/bible_locations_tc.py` (`BIBLE_LOCATIONS_TC`) and `scripts/bible_locations_sc.py` (`BIBLE_LOCATIONS_SC`) with their exact Traditional and Simplified Chinese names mapped by `LocationID` (`BL1`–`BL1274`), preserving exact coordinates `(Name, Latitude, Longitude)`.
   - Exported `tsv/bible_locations.tsv` with six columns (`LocationID`, `English`, `Traditional Chinese`, `Simplified Chinese`, `Latitude`, `Longitude`).
2. **Data Fixes in `exlbl` (`exlb3.data`):**
   - Fixed **68** rows where `<td bgcolor="#FFFFFF"><p><b>` contained an extra `<p>` tag before `<b>` (which previously caused `locations_query.py`'s `<td bgcolor="#FFFFFF"><b>(.*?)</b>` parser to miss the dictionary section).
   - Fixed heading typos (`BL1021` `Salt Ssea` → `Salt Sea`, `BL529` `Har'nepher.` → `Ha'rod.`) and replaced **34** mismatched, truncated, or person-only dictionary articles (`BL45`, `BL53`, `BL109`, `BL111`, `BL117` *Atharim* [was *Spain*], `BL151`, `BL152`, `BL180` *Berothai* [was *Beeroth*], `BL189` *Beth-Arbel* [was *Beth-haram*], `BL262`, `BL286` *Brook Cherith* [was *Cheran*], `BL301` *City of Destruction*, `BL302` *City of Salt*, `BL414` *Rock Etam*, `BL427` *Appii Forum* [was *Apace*], `BL679`, `BL695` *Kirjathaim* [was *Kirjath-jearim*], `BL735`, `BL757`, `BL834` *Mount Ephron*, `BL858` *Mount Zalmon*, `BL944` *Phoenicia*, `BL1029` *Sea of Chinnereth*, `BL1032` *Sea of Galilee*, `BL1034` *Sea of Tiberias*, `BL1066` *Shaveh Kiriathaim*, `BL1088` *Land of Shual*, `BL1097` *Wilderness of Sin*, `BL1118` *Shushan*, `BL1130` *Plain of Tabor*, `BL1200` *Valley of Berachah*, `BL1202` *Valley of Eshcol*, `BL1245` *Zeboim*, and `BL1268` *Ziphron* [was *Sibraim*]) with their authentic *Smith's Bible Dictionary* and *ISBE* geographical entries.
3. **Traditional & Simplified Chinese Location Dictionary (`exlbl_tc` and `exlbl_sc` in `exlb3.data`):**
   - Duplicated `exlbl` into `exlbl_tc` and `exlbl_sc` (**1,161** rows each).
   - Translated all **1,101** unique geographical dictionary descriptions into Traditional Chinese using CUV terminology while preserving all inline `<ref onclick="cr(...)">` Scripture references (with CUV book names) and `<hu>`/`<gu>` Hebrew/Greek text tags.
   - Converted `exlbl_tc` to Simplified Chinese (`exlbl_sc`) via `opencc` (`t2s.json`).
   - Enforced exact mapped Traditional and Simplified Chinese location names in both `<h1 class="window"><ref onclick='searchEntry("EXLBL", "...")'>...</ref></h1>` and `<td bgcolor="#FFFFFF"><b>(.*?)</b>` across all **1,161** rows (**0** mismatches).

## Biblical Persons Dataset (`tsv/bible_persons.tsv`)

Extracted and generated `tsv/bible_persons.tsv` from `biblePeople.data` with four tab-separated columns (`PersonID`, `English`, `Traditional Chinese`, `Simplified Chinese`):
- Contains all **3,085** biblical character entries from `PEOPLERELATIONSHIP` (where `Relationship = "[Reference]"`), joined with `PEOPLERELATIONSHIP_TC` and `PEOPLERELATIONSHIP_SC`.
- Includes `PersonID 7500` (*The Angel* / `使者`) from `PEOPLE`, `PEOPLE_TC`, and `PEOPLE_SC` to ensure complete character coverage.
- Serves as the authoritative character name translation table across the entire workspace (**3,086** total entries).

## Alignment of Bible Names Dictionary (`bible_names.py`)

Standardized the dictionary keys in `scripts/bible_names.py` (*Hitchcock's Bible Names Dictionary*) to align with the authoritative English names used in `tsv/bible_locations.tsv` and `tsv/bible_persons.tsv`:
- **Alignment Metrics:**
  - Total original entries: **2,623** lines (**2,619** unique keys).
  - Exact matches before alignment: **2,016** keys.
  - Aligned / updated keys: **162** entries (**+162 new exact matches**, raising total exact matches to **2,178**).
- **Categories of Alignment:**
  1. **Case Standardizations (22 keys):** Converted all-caps compound words to standard hyphenated casing (e.g. `Adoni-Bezek` → `Adoni-bezek`, `Ebed-Melech` → `Ebed-melech`, `Evil-Merodach` → `Evil-merodach`, `Merodach-Baladan` → `Merodach-baladan`).
  2. **Hyphenation & Punctuation Alignments (36 keys):** Standardized single-word vs. hyphenated spellings and punctuation (e.g. `Beersheba` → `Beer-Sheba`, `Benhadad` → `Ben-hadad`, `Ammi-Nadab` → `Amminadab`, `Aristobulus` → `Aristobulus'`).
  3. **Location Slash Aliases (33 keys):** Mapped dual-named / compound location references where only one form existed in the dictionary (e.g. `Abel-Meholah` → `Abel-Meholah/Abelmeholah`, `Areopagus` → `Areopagus/Mars Hill`, `Arpad` → `Arpad/Arphad`, `Tyre` → `Tyre/Tyrus`).
  4. **Orthographic & Systematic Spelling Alignments (66 keys):** Unified archaic KJV spellings with modern biblical transcriptions without key collisions (e.g. `Abidah` → `Abida`, `Alpheus` → `Alphaeus`, `Arimathea` → `Arimathaea`, `Bartimeus` → `Bartimaeus`, `Zaccheus` → `Zacchaeus`).
  5. **Composite Person Slash Aliases (5 added entries):** Preserved distinct individual entries while adding combined slash keys for characters whose names changed across scripture (`Abram / Abraham`, `Jacob / Israel`, `Sarai / Sarah`, `Saul / Paul`, `Simon / Peter`).
- All changes are itemized with justification and reference IDs in `scripts/bible_names_alignment_changes.md`.

## Traditional Chinese Localization of Bible Names (`bible_names_tc.py`)

Translated and localized `scripts/bible_names_tc.py` into Traditional Chinese:
- **Key Translation:**
  - Mapped English dictionary keys to their official Traditional Chinese names from `tsv/bible_persons.tsv` and `tsv/bible_locations.tsv`.
  - Mapped complementary terms via `tsv/names_english_chinese.tsv` and verified standard CUV translations for theological and doctrinal terms (e.g. `阿爸`, `哈利路亞`, `敵基督`, `次經`).
  - Disambiguated homographic English names into separate Traditional Chinese entries (e.g. Person Abel → `亞伯` vs. City Abel → `亞比拉`; Noah of the Ark → `挪亞` vs. Zelophehad's daughter Noah → `挪阿`; Egypt Rahab → `拉哈伯` vs. Jericho Rahab → `喇合`).
  - Merged multiple English etymologies sharing the same Chinese name (e.g. `巴拉` across *Baalah*, *Baalath*, and *Barak*) with semicolons (`；`) so all biblical meanings are preserved without loss.
- **Value & Etymology Translation:**
  - Fully translated all **2,628** entry meanings into Traditional Chinese matching CUV theological terminology, drawing from `exlbp_TC` in `exlb3.data`, `scripts/name_meanings_tc.py`, and biblical lexicon references.
  - Sanitized quotes, parenthetical references, and redundant aliases.
  - Formatted strictly as `"<b>{ChineseKey}</b> - {ChineseMeaning}"`.
- **Result:** **2,397** unique Traditional Chinese entries with **0** Latin characters and **0** remaining English words.

## Simplified Chinese Conversion of Bible Names (`bible_names_sc.py`)

Generated `scripts/bible_names_sc.py` by converting `scripts/bible_names_tc.py` to Simplified Chinese using `opencc` (`t2s.json`):
- Both dictionary keys and etymological values were converted cleanly into Simplified Chinese.
- Set the dictionary variable to `bible_names_sc`.
- Maintained exact 1:1 parity with `bible_names_tc.py` (**2,397** unique entries, **0** duplicate keys, **0** Latin characters).
- Enforces consistency with Simplified Chinese names in `tsv/bible_persons.tsv` and `tsv/bible_locations.tsv`.

## Comprehensive Audit & Correction of Chinese Person and Location Names

Performed a full cross-check of all **3,086** biblical person entries and **1,147** biblical location entries against `CUV.bible`, `KJV.bible`, `biblePeople.data` (`PEOPLE`), `exlb3.data`, `indexes2.sqlite`, and `tsv/names_english_chinese.tsv`, fixing shifted word-alignment errors, common-word noise, Simplified-character leaks, and `BP*`-to-`PersonID` index offsets across all TSVs, SQLite databases, and Python scripts:

1. **Biblical Persons (`tsv/bible_persons.tsv`):**
   - Corrected **101** Traditional Chinese entries and regenerated all **Simplified Chinese** entries from Traditional Chinese via `opencc` (`t2s.json`, **97** updated):
     - **Pipe-separated (`|`) entries (42 corrected, 30 verified & kept):** Removed spurious common nouns, titles, verbs, numbers, place names, relatives' names, and duplicate Simplified Chinese variants (e.g. `20 Abiathar` `亞比亞他|祭司` → `亞比亞他`, `23 Abiel` `孫子|亞別` → `亞別`, `26 Abigail` `亞比該|妻子` → `亞比該`, `59 Absalom` `生|押沙龍|押沙龙` → `押沙龍`, `682 Jacob / Israel` `雅各|以色列|耶和華` → `雅各|以色列`, `903 Jesse` `耶西|兒子` → `耶西`, `994 David` `大衛|兒子|罵陣|父親|王|大卫` → `大衛`, `1324 God` `上帝|耶和華|萬軍|推羅|耶和华` → `上帝|耶和華`, `1727 Joshua` `約書亞|引誘|嫩` → `約書亞`, `2745 Simon / Peter` `西門|彼得|西门 彼得|西門 彼得` → `西門|彼得`, `2762 Solomon` `所羅門|殿|二百五十|兒子|所罗门` → `所羅門`), while preserving verified multi-name/multi-transliteration entries (e.g. `58 Abram / Abraham` `亞伯蘭|亞伯拉罕`, `102 Adoram` `亞多蘭|哈多蘭`, `121 Ahaziah` `亞哈謝|約哈斯`, `791 Jehoiachin` `約雅斤|耶哥尼雅|哥尼雅`, `2479 Saul / Paul` `掃羅|保羅`).
     - **Shifted single-name mismatches (23 corrected):** Fixed entries such as `31 Abihail` (`大衛` → `亞比孩`), `417 Bavai` (`賓內` → `巴瓦伊`), `425 Bechorath` (`玄孫` → `比歌拉`), `464 Ben-zoheth` (`梭黑` → `便‧梭黑`), `515 Bishlam` (`上書` → `比施蘭`), `569 Azur` (`先知` → `押朔`), `624 Ishi` (`梭黑` → `以示`), `711 Jairus` (`葉魯` → `睚魯`), `1539 Hodaiah` (`第萊雅` → `何大雅`), `1596 Iddo` (`弟兄` → `易多`), `1740 Jozabad` (`族長` → `約撒拔`), `1760 Judas Iscariot` (`加略` → `加略人猶大`), `1929 Manasseh` (`兒子` → `瑪拿西`), `1943 Mary Magdalene` (`抹大拉` → `抹大拉的馬利亞`), `2098 Mithredath` (`比施蘭` → `米特利達`), `2194 Nethaneel` (`兄弟` → `拿坦業`), `2310 Pelet` (`兒子` → `毗力`), `2483 Segub` (`安` → `西割`), `2574 Shebaniah` (`約瑟` → `示巴尼`), `2607 Shelomith` (`兒子` → `示羅密`), `2689 Shimei` (`兒子` → `示每`), `2721 Shobek` (`毗利哈` → `朔百`), `2809 Tabeel` (`米特利達` → `他別`), `2870 Tobadonijah` (`亞多尼雅` → `駝‧巴多尼雅`), and `3052 Zeror` (`曾孫` → `洗羅`).
     - **CUV spelling, spacing, and Simplified-character fixes (36 corrected):** Standardized entries such as `963 Cush` (`古实` → `古實`), `579 Baal-zebub` (`巴力 西卜` → `巴力‧西卜`), `1766 Justus` (`提多 犹士都` → `提多‧猶士都`), `968 Cyrus` (`居魯士` → `塞魯士`), `90 Adlai` (`亞第萊` → `亞第賚`), `340 Ashriel` (`亞斯烈` → `亞斯列`), `1055 Elasah` (`以利亞薩` → `以利亞撒`), `1104–1106, 1110 Eliel` (`以利業` → `以列`), `1773–1775 Kemuel` (`基摩利` → `基母利`), `2147 Naomi` (`拿娥米` → `拿俄米`), and verse-specific CUV variants (`耶利末`/`耶利摩`, `撒迦利雅`/`撒迦利亞`, etc.).

2. **Biblical Locations (`tsv/bible_locations.tsv`):**
   - Corrected **10** Traditional Chinese entries (`BL106` `亞斯她錄` → `亞斯他錄`, `BL114` `亞大錄` → `亞他綠`, `BL224` `伯米羅` → `米羅`, `BL279` `地方` → `迦西斐雅`, `BL730` `古伯` → `利比亞`, `BL925` `巴特羅` → `巴忒羅`, `BL1119` `敘加` → `觜加`, `BL1121` `敘拉古` → `觜拉古`, `BL1165` `亭拿` → `亭納`, `BL1248` `謝撒` → `泄撒`) and regenerated Simplified Chinese via `opencc` (`t2s.json`, **16** SC entries updated).

3. **SQLite Databases (`biblePeople.data`, `exlb3.data`, `indexes2.sqlite`):**
   - **`biblePeople.data`:** Updated `Name` across `PEOPLE_TC`, `PEOPLE_SC`, `PEOPLERELATIONSHIP_TC`, and `PEOPLERELATIONSHIP_SC` for all 3,086 `PersonID`s.
   - **`exlb3.data`:** Resolved the `BP*`-to-`PersonID` offset across all **3,088** `exlbp` entries (where `exlbp` and `biblePeople.data` diverged for 1,337 IDs, e.g., `BP2107` *Moses* vs. `PersonID 2107` *Mordecai*) by matching `(English name, First Occurrence)` against `PEOPLE`. Updated `<h2 exlbp="...">` headings and `<ref onclick="exlbp('BP...')">` links in `exlbp_TC` (**2,430** rows) and `exlbp_SC` (**2,429** rows), plus location headings and `exlbli_*` labels in `exlbl_tc`, `exlbl_sc`, `exlbli_tc`, and `exlbli_sc` (**10** rows each).
   - **`indexes2.sqlite`:** Updated `<ref onclick="exlbp('BP...')">` links in `exlbp_tc` (**19,233** rows) and `exlbp_sc` (**19,223** rows) using the aligned `BP*` mapping, and updated `<ref onclick="exlbl('BL...')">` links in `exlbl_tc` and `exlbl_sc` (**21** rows each). All three databases passed `PRAGMA integrity_check`.

4. **Python Scripts & Alignment TSV (`scripts/` and `tsv/names_english_chinese_less.tsv`):**
   - **`scripts/names_english_chinese.py`** (**84** lines updated) and **`tsv/names_english_chinese_less.tsv`** (**90** rows updated): Fixed shifted-alignment common words (`兒子`, `妻子`, `生`, `女兒`, `王`, `上書`, `玄孫`, `曾孫`, `族長`, `地方`, etc.), mismatched names, Simplified characters, and spaces in both `cu2010t` and `cu2010s`.
   - **`scripts/bible_names_tc.py`** & **`scripts/bible_names_sc.py`:** Fixed **16** erroneous/spaced/Simplified-character keys and headings in `bible_names_tc.py` (**2,396** entries after deduplication) and regenerated `bible_names_sc.py` via `scripts/build_bible_names_sc.py`.
   - **`scripts/bible_locations_tc.py`** & **`scripts/bible_locations_sc.py`:** Updated **9** location entries in each file.





