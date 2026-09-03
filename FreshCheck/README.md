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
Generated at: `2026-09-03T04:21:28+00:00`
As of date: `2026-09-03`
Packages assessed: `47858`
Resources assessed: `241549`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35912 | 164799 |
| freshness_tree_provincial.json | Provincial | provincial | 11661 | 75100 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 285 | 1650 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35912
    "provincial": 11661
    "municipal": 285
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37867
    "late": 4974
    "current": 4931
    "due_soon": 86
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 171655
    "late": 38641
    "current": 30840
    "due_soon": 413
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3370
    "Late 91-365 days": 1019
    "Late 31-90 days": 383
    "Late 8-30 days": 92
    "Late 1-7 days": 110
    "Due in 0-7 days": 86
    "Due in 8-30 days": 576
    "Current > 30 days": 4355
    "Unknown": 37867
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "ns-ne", "tf", "on", "ccohs-cchst", "cwa-aec", "bc-cb", "cmc-mcc", "ab", "cstm-mstc"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 57, 55, 43, 43, 43, 40, 40, 35, 30, 28, 26]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
