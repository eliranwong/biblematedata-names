# Bible Names Alignment Documentation

This document records all alignments made to dictionary keys in [bible_names_aligned_with_exlb.py](bible_names_aligned_with_exlb.py) (and synchronized in [bible_names_tc.py](bible_names_tc.py) and [bible_names_sc.py](bible_names_sc.py)) to match the authoritative English names used in [../tsv/bible_locations.tsv](../tsv/bible_locations.tsv) and [../tsv/bible_persons.tsv](../tsv/bible_persons.tsv).

## 1. Executive Summary

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Total Original Dictionary Lines** | 2,623 | Hitchcock's Bible Names Dictionary |
| **Original Unique Keys** | 2,619 | 4 intentional theological duplicate keys (`Abel`, `Eli`, `Noah`, `Rahab`) |
| **Exact Matches (Pre-alignment)** | 2,016 | Exact 1:1 match with TSV entities |
| **Keys Aligned (Replaced)** | 157 | Standardized casing, hyphenation, slash aliases & orthography |
| **Composite Person Aliases Added** | 5 | Combined slash keys preserving individual entries |
| **Total Final Unique Keys** | 2,624 | All aligned keys now match authoritative TSV entities |
| **Total Exact Matches (Post-alignment)** | 2,178 | **+162 new exact matches** |

---

## 2. Category 1: Case Alignments (22 Keys)

Hitchcock's dictionary capitalized each element of hyphenated compounds (e.g. `Adoni-Bezek`). These were aligned with the lower-case second element used in `bible_persons.tsv` / `bible_locations.tsv` (e.g. `Adoni-bezek`).

| # | Original Key | Aligned Key | Target Entity | Details / Reference |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `Adoni-Bezek` | `Adoni-bezek` | Person (ID 96) | Title Case to Standard Hyphenated Case |
| 2 | `Adoni-Zedek` | `Adoni-zedek` | Person (ID 101) | Title Case to Standard Hyphenated Case |
| 3 | `Baal-Zebub` | `Baal-zebub` | Person (ID 579) | Title Case to Standard Hyphenated Case |
| 4 | `Ben-Ammi` | `Ben-ammi` | Person (ID 451) | Title Case to Standard Hyphenated Case |
| 5 | `Beth-Rapha` | `Beth-rapha` | Person (ID 486) | Title Case to Standard Hyphenated Case |
| 6 | `Chushan-Rishathaim` | `Chushan-rishathaim` | Person (ID 944) | Title Case to Standard Hyphenated Case |
| 7 | `Ebed-Melech` | `Ebed-melech` | Person (ID 1029) | Title Case to Standard Hyphenated Case |
| 8 | `Esar-Haddon` | `Esar-haddon` | Person (ID 1215) | Title Case to Standard Hyphenated Case |
| 9 | `Evil-Merodach` | `Evil-merodach` | Person (ID 1233) | Title Case to Standard Hyphenated Case |
| 10 | `Ishbi-Benob` | `Ishbi-benob` | Person (ID 621) | Title Case to Standard Hyphenated Case |
| 11 | `Keren-Happuch` | `Keren-happuch` | Person (ID 1780) | Title Case to Standard Hyphenated Case |
| 12 | `Lo-Ammi` | `Lo-ammi` | Person (ID 1827) | Title Case to Standard Hyphenated Case |
| 13 | `Lo-Ruhamah` | `Lo-ruhamah` | Person (ID 1829) | Title Case to Standard Hyphenated Case |
| 14 | `Maher-Shalal-Hash-Baz` | `Maher-shalal-hash-baz` | Person (ID 1894) | Title Case to Standard Hyphenated Case |
| 15 | `Merodach-Baladan` | `Merodach-baladan` | Person (ID 483) | Title Case to Standard Hyphenated Case |
| 16 | `Nathan-Melech` | `Nathan-melech` | Person (ID 2159) | Title Case to Standard Hyphenated Case |
| 17 | `Nebuzar-Adan` | `Nebuzar-adan` | Person (ID 2169) | Title Case to Standard Hyphenated Case |
| 18 | `Nergal-Sharezer` | `Nergal-sharezer` | Person (ID 2183) | Title Case to Standard Hyphenated Case |
| 19 | `Pahath-Moab` | `Pahath-moab` | Person (ID 2265, 2266) | Title Case to Standard Hyphenated Case |
| 20 | `Romamti-Ezer` | `Romamti-ezer` | Person (ID 2446) | Title Case to Standard Hyphenated Case |
| 21 | `Shear-Jashub` | `Shear-jashub` | Person (ID 2566) | Title Case to Standard Hyphenated Case |
| 22 | `Shethar-Boznai` | `Shethar-boznai` | Person (ID 2674) | Title Case to Standard Hyphenated Case |

---

## 3. Category 2: Hyphenation & Punctuation Alignments (36 Keys)

Resolves variations between single-word and hyphenated compound spellings, as well as grammatical punctuation (e.g. `Aristobulus'`).

| # | Original Key | Aligned Key | Target Entity | Details / Reference |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `Ammi-Nadab` | `Amminadab` | Person (ID 228, 229) | Hyphenation / Punctuation standard |
| 2 | `Aristobulus` | `Aristobulus'` | Person (ID 307) | Hyphenation / Punctuation standard |
| 3 | `Beerelim` | `Beer-Elim` | Location (BL166) | Hyphenation / Punctuation standard |
| 4 | `Beersheba` | `Beer-Sheba` | Location (BL170) | Hyphenation / Punctuation standard |
| 5 | `Beneberak` | `Bene-Berak` | Location (BL173) | Hyphenation / Punctuation standard |
| 6 | `Benhadad` | `Ben-hadad` | Person (ID 452, 453) | Hyphenation / Punctuation standard |
| 7 | `Benhanan` | `Ben-hanan` | Person (ID 456) | Hyphenation / Punctuation standard |
| 8 | `Benzoheth` | `Ben-zoheth` | Person (ID 464) | Hyphenation / Punctuation standard |
| 9 | `Beth-Baalmeon` | `Beth-Baal-Meon` | Location (BL193) | Hyphenation / Punctuation standard |
| 10 | `Bethanath` | `Beth-Anath` | Location (BL184) | Hyphenation / Punctuation standard |
| 11 | `Betharabah` | `Beth-Arabah` | Location (BL188) | Hyphenation / Punctuation standard |
| 12 | `Bethemek` | `Beth-Emek` | Location (BL204) | Hyphenation / Punctuation standard |
| 13 | `Bethshan` | `Beth-Shan` | Location (BL232) | Hyphenation / Punctuation standard |
| 14 | `Colhozeh` | `Col-hozeh` | Person (ID 951, 952) | Hyphenation / Punctuation standard |
| 15 | `Eph-Lal` | `Ephlal` | Person (ID 1204) | Hyphenation / Punctuation standard |
| 16 | `Esh-Ban` | `Eshban` | Person (ID 1217) | Hyphenation / Punctuation standard |
| 17 | `Gur-Baal` | `Gurbaal` | Location (BL498) | Hyphenation / Punctuation standard |
| 18 | `Hazarenan` | `Hazar-Enan` | Location (BL537) | Hyphenation / Punctuation standard |
| 19 | `Hazargaddah` | `Hazar-Gaddah` | Location (BL538) | Hyphenation / Punctuation standard |
| 20 | `Hephzibah` | `Hephzi-bah` | Person (ID 1499) | Hyphenation / Punctuation standard |
| 21 | `Irshemesh` | `Ir-Shemesh` | Location (BL600) | Hyphenation / Punctuation standard |
| 22 | `Ish-Pan` | `Ishpan` | Person (ID 639) | Hyphenation / Punctuation standard |
| 23 | `Ishbosheth` | `Ish-bosheth` | Person (ID 622) | Hyphenation / Punctuation standard |
| 24 | `Jegar-Sahadutha` | `Jegarsahadutha` | Location (BL631) | Hyphenation / Punctuation standard |
| 25 | `Jushabhesed` | `Jushab-hesed` | Person (ID 1765) | Hyphenation / Punctuation standard |
| 26 | `Lahairoi` | `Lahai-Roi` | Location (BL167) | Hyphenation / Punctuation standard |
| 27 | `Mejarkon` | `Me-Jarkon` | Location (BL778) | Hyphenation / Punctuation standard |
| 28 | `Migdalel` | `Migdal-El` | Location (BL797) | Hyphenation / Punctuation standard |
| 29 | `Migdalgad` | `Migdal-Gad` | Location (BL798) | Hyphenation / Punctuation standard |
| 30 | `Potipherah` | `Poti-pherah` | Person (ID 2369) | Hyphenation / Punctuation standard |
| 31 | `Rab-Saris` | `Rabsaris` | Person (ID 2382, 2383) | Hyphenation / Punctuation standard |
| 32 | `Rab-Shakeh` | `Rabshakeh` | Person (ID 2384) | Hyphenation / Punctuation standard |
| 33 | `Rabmag` | `Rab-mag` | Person (ID 2381) | Hyphenation / Punctuation standard |
| 34 | `Regemmelech` | `Regem-melech` | Person (ID 2408) | Hyphenation / Punctuation standard |
| 35 | `Telabib` | `Tel-Abib` | Location (BL1143) | Hyphenation / Punctuation standard |
| 36 | `Tob-Adonijah` | `Tobadonijah` | Person (ID 2870) | Hyphenation / Punctuation standard |

---

## 4. Category 3: Location Slash Aliases (33 Keys)

In `bible_locations.tsv`, compound / dual-named locations are represented with a slash (`/`). Where only a single variant was present in `bible_names.py`, the key was updated to match the TSV compound entry.

| # | Original Key | Aligned Key | Location ID | Details / Reference |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `Abel-Meholah` | `Abel-Meholah/Abelmeholah` | Location (BL8) | Unambiguous single-entry slash location |
| 2 | `Adami` | `Adami/Nekeb` | Location (BL23) | Unambiguous single-entry slash location |
| 3 | `Akrabbim` | `Akrabbim/Maaleh-Acrabbim` | Location (BL44) | Unambiguous single-entry slash location |
| 4 | `Areopagus` | `Areopagus/Mars Hill` | Location (BL87) | Unambiguous single-entry slash location |
| 5 | `Arpad` | `Arpad/Arphad` | Location (BL96) | Unambiguous single-entry slash location |
| 6 | `Ashtaroth` | `Astaroth/Ashtaroth` | Location (BL106) | Unambiguous single-entry slash location |
| 7 | `Askelon` | `Askelon/Ashkelon` | Location (BL103) | Unambiguous single-entry slash location |
| 8 | `Assur` | `Asshur/Assur` | Location (BL109) | Unambiguous single-entry slash location |
| 9 | `Chaldea` | `Chaldeans/Chaldea` | Location (BL282) | Unambiguous single-entry slash location |
| 10 | `Cyprus` | `Chittim/Cyprus` | Location (BL316) | Unambiguous single-entry slash location |
| 11 | `Cyrene` | `Cyrene/Cyrenian` | Location (BL317) | Unambiguous single-entry slash location |
| 12 | `Ezem` | `Azem/Ezem` | Location (BL422) | Unambiguous single-entry slash location |
| 13 | `Ezion-Geber` | `Ezion-Gaber/Ezion-Geber` | Location (BL423) | Unambiguous single-entry slash location |
| 14 | `Gittah-Hepher` | `Gittah-Hepher/Gath-Hepher` | Location (BL443) | Unambiguous single-entry slash location |
| 15 | `Gomorrah` | `Gomorrah/Gomorrha` | Location (BL489) | Unambiguous single-entry slash location |
| 16 | `Hazezon-Tamar` | `Hazezon-Tamar/Hazazon-Tamar` | Location (BL542) | Unambiguous single-entry slash location |
| 17 | `Jazer` | `Jaazer/Jazer` | Location (BL628) | Unambiguous single-entry slash location |
| 18 | `Kirjath-Arba` | `Kirjath-Arba/Arbah` | Location (BL697) | Unambiguous single-entry slash location |
| 19 | `Media` | `Medes/Media` | Location (BL776) | Unambiguous single-entry slash location |
| 20 | `Miletum` | `Miletus/Miletum` | Location (BL801) | Unambiguous single-entry slash location |
| 21 | `Nahallal` | `Nahallal/Nahalal` | Location (BL869) | Unambiguous single-entry slash location |
| 22 | `Palestina` | `Palestina/Philistia` | Location (BL943) | Unambiguous single-entry slash location |
| 23 | `Rabbah` | `Rabbath/Rabbah` | Location (BL966) | Unambiguous single-entry slash location |
| 24 | `Salcah` | `Salchah/Salcah` | Location (BL1017) | Unambiguous single-entry slash location |
| 25 | `Shophan` | `Atroth/Shophan` | Location (BL119) | Unambiguous single-entry slash location |
| 26 | `Sodom` | `Sodom/Sodoma` | Location (BL1107) | Unambiguous single-entry slash location |
| 27 | `Tekoa` | `Tekoah/Tekoa` | Location (BL1142) | Unambiguous single-entry slash location |
| 28 | `Tophet` | `Topheth/Tophet` | Location (BL1176) | Unambiguous single-entry slash location |
| 29 | `Tyre` | `Tyre/Tyrus` | Location (BL1184) | Unambiguous single-entry slash location |
| 30 | `Zaanannim` | `Zaanannim/Zaanaim` | Location (BL1235) | Unambiguous single-entry slash location |
| 31 | `Zaretan` | `Zaretan/Zartanah` | Location (BL1243) | Unambiguous single-entry slash location |
| 32 | `Zobah` | `Zobah/Zoba` | Location (BL1272) | Unambiguous single-entry slash location |
| 33 | `Zorah` | `Zoreah/Zorah` | Location (BL1275) | Unambiguous single-entry slash location |

---

## 5. Category 4: Orthographic & Systematic Spelling Alignments (66 Keys)

Standardizes systematic orthographic variants between KJV/archaic transcriptions and modern biblical reference forms (e.g. `-ah` vs `-a`, `-ae-` vs `-e-`, `ph` vs `f`, Greek/Hebrew transcription conventions). Each target key was verified to ensure zero collision with existing dictionary definitions.

| # | Original Key | Aligned Key | Target Entity | Details / Reference |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `Abidah` | `Abida` | Person (ID 21) | Systematic biblical spelling variant |
| 2 | `Adaliah` | `Adalia` | Person (ID 77) | Systematic biblical spelling variant |
| 3 | `Ahishahur` | `Ahishahar` | Person (ID 160) | Systematic biblical spelling variant |
| 4 | `Ahuzzah` | `Ahuzzath` | Person (ID 176) | Systematic biblical spelling variant |
| 5 | `Alpheus` | `Alphaeus` | Person (ID 192, 193) | Systematic biblical spelling variant |
| 6 | `Arimathea` | `Arimathaea` | Location (BL90) | Systematic biblical spelling variant |
| 7 | `Bartimeus` | `Bartimaeus` | Person (ID 406) | Systematic biblical spelling variant |
| 8 | `Berothath` | `Berothah` | Location (BL179) | Systematic biblical spelling variant |
| 9 | `Beth-Ezal` | `Beth-Ezel` | Location (BL206) | Systematic biblical spelling variant |
| 10 | `Caiphas` | `Caiaphas` | Person (ID 532) | Systematic biblical spelling variant |
| 11 | `Charchemish` | `Carchemish` | Location (BL277); Person (ID 925) | Systematic biblical spelling variant |
| 12 | `Cleophas` | `Cleopas` | Person (ID 950) | Systematic biblical spelling variant |
| 13 | `Darah` | `Dara` | Person (ID 976) | Systematic biblical spelling variant |
| 14 | `Dibzahab` | `Dizahab` | Location (BL339) | Systematic biblical spelling variant |
| 15 | `Epenetus` | `Epaenetus` | Person (ID 1194) | Systematic biblical spelling variant |
| 16 | `Garmites` | `Garmite` | Person (ID 1280) | Systematic biblical spelling variant |
| 17 | `Girgashite` | `Girgasite` | Person (ID 1322) | Systematic biblical spelling variant |
| 18 | `Habazinaiah` | `Habaziniah` | Person (ID 1335) | Systematic biblical spelling variant |
| 19 | `Halloesh` | `Hallohesh` | Person (ID 1357) | Systematic biblical spelling variant |
| 20 | `Hapharaim` | `Haphraim` | Location (BL524) | Systematic biblical spelling variant |
| 21 | `Hashupha` | `Hasupha` | Person (ID 1451) | Systematic biblical spelling variant |
| 22 | `Hattipha` | `Hatipha` | Person (ID 1454) | Systematic biblical spelling variant |
| 23 | `Hivites` | `Hivite` | Person (ID 1534) | Systematic biblical spelling variant |
| 24 | `Hymeneus` | `Hymenaeus` | Person (ID 1583) | Systematic biblical spelling variant |
| 25 | `Idumea` | `Idumaea` | Location (BL592) | Systematic biblical spelling variant |
| 26 | `Ishmachiah` | `Ismachiah` | Person (ID 642) | Systematic biblical spelling variant |
| 27 | `Ishua` | `Ishuah` | Person (ID 640) | Systematic biblical spelling variant |
| 28 | `Iturea` | `Ituraea` | Location (BL604) | Systematic biblical spelling variant |
| 29 | `Izehar` | `Izhar` | Person (ID 658) | Systematic biblical spelling variant |
| 30 | `Jaala` | `Jaalah` | Person (ID 661) | Systematic biblical spelling variant |
| 31 | `Japhet` | `Japheth` | Person (ID 726) | Systematic biblical spelling variant |
| 32 | `Jecoliah` | `Jecholiah` | Person (ID 750) | Systematic biblical spelling variant |
| 33 | `Jehiskiah` | `Jehizkiah` | Person (ID 781) | Systematic biblical spelling variant |
| 34 | `Jeshohaia` | `Jeshohaiah` | Person (ID 891) | Systematic biblical spelling variant |
| 35 | `Jiphthael` | `Jiphthah-El` | Location (BL1208) | Systematic biblical spelling variant |
| 36 | `Joakim` | `Joiakim` | Person (ID 1681) | Systematic biblical spelling variant |
| 37 | `Josaphat` | `Joshaphat` | Person (ID 1724) | Systematic biblical spelling variant |
| 38 | `Joshbekesha` | `Joshbekashah` | Person (ID 1726) | Systematic biblical spelling variant |
| 39 | `Kehelahath` | `Kehelathah` | Location (BL680) | Systematic biblical spelling variant |
| 40 | `Kelitah` | `Kelita` | Person (ID 1772) | Systematic biblical spelling variant |
| 41 | `Kenah` | `Kenath` | Location (BL682) | Systematic biblical spelling variant |
| 42 | `Kolariah` | `Kolaiah` | Person (ID 1791, 1792) | Systematic biblical spelling variant |
| 43 | `Lashah` | `Lasha` | Location (BL718) | Systematic biblical spelling variant |
| 44 | `Lebbeus` | `Lebbaeus` | Person (ID 1815) | Systematic biblical spelling variant |
| 45 | `Mahaleleel` | `Mahalaleel` | Person (ID 1885, 1886) | Systematic biblical spelling variant |
| 46 | `Mara` | `Marah` | Location (BL765) | Systematic biblical spelling variant |
| 47 | `Melchi-Shua` | `Malchi-shua` | Person (ID 1990) | Systematic biblical spelling variant |
| 48 | `Meshezaheel` | `Meshezabeel` | Person (ID 2014, 2015) | Systematic biblical spelling variant |
| 49 | `Meshillamith` | `Meshillemith` | Person (ID 2017) | Systematic biblical spelling variant |
| 50 | `Meunim` | `Mehunim` | Person (ID 1985) | Systematic biblical spelling variant |
| 51 | `Moserah` | `Mosera` | Location (BL823) | Systematic biblical spelling variant |
| 52 | `Nephthoah` | `Nephtoah` | Location (BL888) | Systematic biblical spelling variant |
| 53 | `Oshea` | `Hoshea` | Person (ID 1559, 1560) | Systematic biblical spelling variant |
| 54 | `Raphah` | `Rapha` | Person (ID 2396) | Systematic biblical spelling variant |
| 55 | `Sabtechah` | `Sabtecha` | Person (ID 2452) | Systematic biblical spelling variant |
| 56 | `Schaaph` | `Shaaph` | Person (ID 2506, 2507) | Systematic biblical spelling variant |
| 57 | `Shaalabbim` | `Shaalabbin` | Location (BL1052) | Systematic biblical spelling variant |
| 58 | `Shammuah` | `Shammua` | Person (ID 2545, 2546) | Systematic biblical spelling variant |
| 59 | `Shihon` | `Shion` | Location (BL1085) | Systematic biblical spelling variant |
| 60 | `Shihor-Libnah` | `Shihor-Libnath` | Location (BL1077) | Systematic biblical spelling variant |
| 61 | `Siloa` | `Siloam` | Location (BL1096) | Systematic biblical spelling variant |
| 62 | `Taanach-Shilo` | `Taanath-Shiloh` | Location (BL1125) | Systematic biblical spelling variant |
| 63 | `Timeus` | `Timaeus` | Person (ID 2858) | Systematic biblical spelling variant |
| 64 | `Zaccheus` | `Zacchaeus` | Person (ID 2961) | Systematic biblical spelling variant |
| 65 | `Zeboiim` | `Zeboim` | Location (BL1222, BL1245) | Systematic biblical spelling variant |
| 66 | `Zeredah` | `Zereda` | Location (BL1254) | Systematic biblical spelling variant |

---

## 6. Category 5: Composite Person Slash Aliases (5 Added Entries)

For biblical individuals whose names changed across their narrative arcs (`Abram / Abraham`, `Jacob / Israel`, `Sarai / Sarah`, `Saul / Paul`, `Simon / Peter`), both separate individual entries were preserved in the dictionary to retain their distinct etymologies, and combined alias entries were added to match `bible_persons.tsv` PersonIDs exactly.

| # | Composite Aligned Key | PersonID | Combined Definition | Preserved Individual Keys |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `Abram / Abraham` | Person 25 | <b>Abram / Abraham</b> - High Father; Father Of A Great Multitude | `Abram`, `Abraham` |
| 2 | `Jacob / Israel` | Person 1098 | <b>Jacob / Israel</b> - That Supplants, Undermines; The Heel; Who Prevails With God | `Jacob`, `Israel` |
| 3 | `Sarai / Sarah` | Person 2056 | <b>Sarai / Sarah</b> - My Lady; My Princess; Lady; Princess; Princess Of The Multitude | `Sarai`, `Sarah` |
| 4 | `Saul / Paul` | Person 2068 | <b>Saul / Paul</b> - Demanded; Lent; Ditch; Death; Small; Little | `Saul`, `Paul` |
| 5 | `Simon / Peter` | Person 2147 | <b>Simon / Peter</b> - That Hears; That Obeys; A Rock Or Stone | `Simon`, `Peter` |

---

## 7. Data Integrity & Verification

- **Syntax Validation**: All three updated files (`scripts/bible_names.py`, `scripts/bible_names_tc.py`, `scripts/bible_names_sc.py`) compile and import into Python with zero errors.
- **No Collisions / Overwriting**: Verified that no existing unique definitions were overwritten during key alignment.
- **Synchronized Platforms**: All three dictionary files maintain identical key structures across English, Traditional Chinese, and Simplified Chinese environments.
- **Preservation of Theological Vocabulary**: Theological terms not appearing in person/location tables (e.g. `Abba`, `Alleluia`, `Anathema`, `Apocrypha`) were preserved completely intact.

