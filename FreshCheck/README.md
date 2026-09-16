# FreshCheck

FreshCheck measures whether Open Canada packages and their resources appear current
against the package frequency metadata in the JSONL metadata feed.

The generator reads `https://open.canada.ca/static/od-do-canada.jsonl.gz`, builds
hierarchical package trees, and writes three JSON files grouped by package
`jurisdiction`:

| Output file | Jurisdiction values |
|---|---|
| `freshness_tree_federal.json` | `federal` |
| `freshness_tree_provincial.json` | `provincial` |
| `freshness_tree_municipal_user.json` | `municipal`, `user` |

Each package record contains the organization name, package id, metadata dates,
frequency, jurisdiction, and nested resource records. Each package and resource
also receives:

| Field | Meaning |
|---|---|
| `expected_update_date` | `metadata_modified` plus the package `frequency` interval. |
| `days_until_expected_update` | Positive values mean the item is not due yet; negative values mean it is late. |
| `freshness_status` | `current`, `due_soon`, `late`, or `unknown`. |

Frequency values are parsed as ISO 8601 date durations such as `P1D`, `P1W`,
`P1M`, `P3M`, `P6M`, and `P1Y`. Month and year frequencies use calendar-aware
month addition.

Run locally:

```bash
python3 FreshCheck/fresh_check.py
```

Smoke test without committing generated outputs:

```bash
python3 FreshCheck/fresh_check.py \
  --limit 25 \
  --output-dir FreshCheck/smoke_output \
  --readme FreshCheck/smoke_README.md
rm -rf FreshCheck/smoke_output FreshCheck/smoke_README.md
```

<!-- FRESHCHECK_REPORT_START -->
Generated at: `2026-09-16T16:53:03+00:00`
As of date: `2026-09-16`
Packages assessed: `47921`
Resources assessed: `241854`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35976 | 165044 |
| freshness_tree_provincial.json | Provincial | provincial | 11660 | 75160 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 285 | 1650 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35976
    "provincial": 11660
    "municipal": 285
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37936
    "late": 4938
    "current": 4831
    "due_soon": 216
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 172020
    "late": 37964
    "current": 29947
    "due_soon": 1923
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3380
    "Late 91-365 days": 1090
    "Late 31-90 days": 278
    "Late 8-30 days": 131
    "Late 1-7 days": 59
    "Due in 0-7 days": 216
    "Due in 8-30 days": 472
    "Current > 30 days": 4359
    "Unknown": 37936
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "tf", "on", "ns-ne", "ccohs-cchst", "ic", "bc-cb", "cwa-aec", "cmc-mcc", "cer-rec"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 58, 55, 43, 42, 42, 40, 39, 35, 33, 30, 29]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
