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
Generated at: `2026-07-11T03:39:39+00:00`
As of date: `2026-07-11`
Packages assessed: `47537`
Resources assessed: `244450`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35609 | 165182 |
| freshness_tree_provincial.json | Provincial | provincial | 11642 | 77604 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 286 | 1664 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35609
    "provincial": 11642
    "municipal": 285
    "user": 1
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37542
    "current": 4888
    "late": 4854
    "due_soon": 253
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 172893
    "late": 40417
    "current": 29514
    "due_soon": 1626
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3376
    "Late 91-365 days": 838
    "Late 31-90 days": 278
    "Late 8-30 days": 289
    "Late 1-7 days": 73
    "Due in 0-7 days": 253
    "Due in 8-30 days": 361
    "Current > 30 days": 4527
    "Unknown": 37542
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "ns-ne", "tf", "on", "ccohs-cchst", "bc-cb", "cmc-mcc", "cer-rec", "ab", "cstm-mstc"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 57, 56, 44, 43, 42, 40, 35, 33, 30, 27, 26]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
