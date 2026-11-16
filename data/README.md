# Useful Datasets (`data/`)

This directory contains the curated, ready-to-use biblical name, person, location, and etymology datasets produced by the **biblematedata-names** project. All datasets are UTF-8 encoded, cross-checked against the Chinese Union Version (和合本, CUV), and aligned across English, Traditional Chinese (`TC`), and Simplified Chinese (`SC`).

## Directory Structure

- **[`data/tsv/`](tsv/README.md)** — Tab-separated value (`.tsv`) datasets for spreadsheets, SQLite/SQL imports, NLP pipelines, and custom scripts.
- **[`data/python/`](python/README.md)** — Ready-to-import Python dictionary modules (`.py`) and alignment documentation.

## Dataset Overview

| Dataset | TSV (`data/tsv/`) | Python (`data/python/`) | Entries | Description |
| :--- | :--- | :--- | ---: | :--- |
| **Biblical Persons** | `bible_persons.tsv` | — | 3,086 | Authoritative `PersonID` mapping across English, Traditional Chinese, and Simplified Chinese. |
| **Biblical Locations & Coordinates** | `bible_locations.tsv` | `bible_locations.py`, `bible_locations_tc.py`, `bible_locations_sc.py` | 1,147 | `LocationID` (`BL1`–`BL1274`) with English/TC/SC names and `(Latitude, Longitude)` coordinates. |
| **Verse-Level Name Mappings** | `names_english_chinese_names_fixed.tsv` | `names_english_chinese.py` | 36,898 | Verse-by-verse mapping (`book`, `chapter`, `verse`) between CUV (`cu2010s`, `cu2010t`) and English (`esvuk16`, `bsb`, `engulb`) with 90 upstream Chinese alignment fixes applied. |
| **Upstream Source Names (Unfixed)** | `names_original_source_with_wrong_Chinese_names.tsv` | — | 36,898 | Original 20-column dataset from `BibleNLP/biblical-names-data` preserved for reference and diffing. |
| **Hitchcock's Bible Names Dictionary** | — | `bible_names_original.py`, `bible_names_aligned_with_exlbp.py`, `bible_names_tc.py`, `bible_names_sc.py` | 2,396–2,624 | Biblical name meanings/etymologies in English (original and `exlbp`-aligned), Traditional Chinese, and Simplified Chinese, plus `bible_names_alignment_changes.md`. |

## Notes on Consistency

- **CUV Terminology:** All Traditional Chinese names are verified against the Chinese Union Version (`CUV.bible`) and cross-referenced against `biblePeople.data`, `exlb3.data`, and `indexes2.sqlite`.
- **TC ↔ SC Parity:** Simplified Chinese datasets are deterministically converted from Traditional Chinese using OpenCC (`t2s.json`) to maintain 1:1 structural parity.
- **Pipe-Separated Variants:** Where a biblical figure or title has multiple canonical names or CUV transliterations (e.g., `Abram / Abraham` → `亞伯蘭|亞伯拉罕`), variants are joined with `|` in `bible_persons.tsv`.

