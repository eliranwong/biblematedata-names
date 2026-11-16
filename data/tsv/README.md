# TSV Datasets (`data/tsv/`)

This directory provides UTF-8 tab-separated value (`.tsv`) datasets for biblical persons, locations (with coordinates), and verse-level English–Chinese name occurrences.

## Files

### 1. `bible_persons.tsv`
Authoritative biblical person name translation table (**3,086** entries, extracted from `biblePeople.data` `PEOPLERELATIONSHIP` plus `PersonID 7500` *The Angel*).

- **Columns:** `PersonID`, `English`, `Traditional Chinese`, `Simplified Chinese`
- **Notes:**
  - Multi-name or multi-transliteration entries (e.g., `58 Abram / Abraham`) are pipe-separated (`亞伯蘭|亞伯拉罕` / `亚伯兰|亚伯拉罕`).
  - Audited against `CUV.bible`, `KJV.bible`, `exlb3.data`, and `indexes2.sqlite` to eliminate shifted word-alignment errors, common-word noise, and Simplified-character leaks in Traditional Chinese.

### 2. `bible_locations.tsv`
Authoritative biblical location and coordinate dataset (**1,147** entries, covering `BL1`–`BL1274`).

- **Columns:** `LocationID`, `English`, `Traditional Chinese`, `Simplified Chinese`, `Latitude`, `Longitude`
- **Notes:**
  - Every `LocationID` is aligned with the `exlbl` dictionary in `exlb3.data` and the `exlbl` verse index in `indexes2.sqlite`.

### 3. `names_english_chinese_names_fixed.tsv`
Cleaned, verse-level biblical name mapping (**36,898** rows) derived from [BibleNLP/biblical-names-data](https://github.com/BibleNLP/biblical-names-data).

- **Columns:** `book`, `chapter`, `verse`, `cu2010s`, `cu2010t`, `esvuk16`, `bsb`, `engulb`
- **Notes:**
  - `book` uses numbered book IDs (`1`–`66`, Genesis–Revelation).
  - Includes **90** corrected `cu2010t` / `cu2010s` rows fixing shifted-alignment common words (e.g., `兒子`, `妻子`, `王`, `地方`), mismatched names, spaces, and Simplified-character leaks (contributed back upstream in [BibleNLP/biblical-names-data#2](https://github.com/BibleNLP/biblical-names-data/pull/2)).

### 4. `names_original_source_with_wrong_Chinese_names.tsv`
Original 20-column upstream TSV from `BibleNLP/biblical-names-data` (**36,898** rows), retained for provenance and comparison against `names_english_chinese_names_fixed.tsv`.

- **Columns:** `ref`, `text`, `macula_lemma`, `macula_eng`, `macula_lxx_greek`, `hcb`, `cu2010s`, `cu2010t`, `rso94`, `sruv06`, `tbi`, `lsg10`, `rv09`, `tpb08`, `esvuk16`, `arbnav`, `tglulb`, `bsb`, `engulb`, `bbc`

## Quick Usage (Python)

```python
import csv

with open("data/tsv/bible_persons.tsv", encoding="utf-8", newline="") as f:
    persons = list(csv.DictReader(f, delimiter="\t"))

with open("data/tsv/bible_locations.tsv", encoding="utf-8", newline="") as f:
    locations = list(csv.DictReader(f, delimiter="\t"))
```

