# Python Data Modules (`data/python/`)

This directory contains ready-to-import Python dictionary modules for biblical locations, biblical name meanings (*Hitchcock's Bible Names Dictionary*), and verse-level English–Chinese name mappings.

## Files

### Biblical Locations & Coordinates

Each module maps `LocationID` (`"BL1"`–`"BL1274"`) to a `(Name, Latitude, Longitude)` tuple (**1,147** entries each):

| File | Variable | Language |
| :--- | :--- | :--- |
| `bible_locations.py` | `BIBLE_LOCATIONS` | English |
| `bible_locations_tc.py` | `BIBLE_LOCATIONS_TC` | Traditional Chinese (CUV) |
| `bible_locations_sc.py` | `BIBLE_LOCATIONS_SC` | Simplified Chinese (CUV) |

### Hitchcock's Bible Names Dictionary (Etymologies)

| File | Variable | Unique Keys | Description |
| :--- | :--- | ---: | :--- |
| `bible_names_original.py` | `bible_names` | 2,619 | Original unaligned English dictionary (2,623 lines). |
| `bible_names_aligned_with_exlbp.py` | `bible_names` | 2,624 | English dictionary with **162** keys aligned to `bible_persons.tsv`, `bible_locations.tsv`, and `exlbp`, plus **5** composite person slash aliases (`Abram / Abraham`, `Jacob / Israel`, `Sarai / Sarah`, `Saul / Paul`, `Simon / Peter`). |
| `bible_names_tc.py` | `bible_names_tc` | 2,396 | Full Traditional Chinese translation formatted as `"<b>{ChineseKey}</b> - {ChineseMeaning}"`, with homographs disambiguated and shared Chinese names merged cleanly. |
| `bible_names_sc.py` | `bible_names_sc` | 2,396 | Simplified Chinese version generated from `bible_names_tc.py` via OpenCC (`t2s.json`) with 1:1 parity. |
| `bible_names_alignment_changes.md` | — | — | Itemized log of every key alignment and rationale between the original and aligned dictionaries. |

### Verse-Level Name Mappings

- **`names_english_chinese.py`** (`verse_to_names`, **36,898** entries):
  - Format per line: `"book.chapter.verse": [cu2010s, cu2010t, (esvuk16, bsb, engulb)]`
  - **Important:** Because a single verse can contain multiple biblical names, `"book.chapter.verse"` keys repeat across lines. Parse this file line-by-line (or read [`data/tsv/names_english_chinese_names_fixed.tsv`](../tsv/names_english_chinese_names_fixed.tsv)) rather than evaluating it as a single Python `dict`, which would overwrite earlier entries in the same verse.

## Quick Usage

```python
from data.python.bible_locations_tc import BIBLE_LOCATIONS_TC
from data.python.bible_names_tc import bible_names_tc

print(BIBLE_LOCATIONS_TC["BL1"])   # ('亞罷拿', 33.545097, 36.224661)
print(bible_names_tc["亞倫"])      # <b>亞倫</b> - 教師；崇高；力量之山
```

