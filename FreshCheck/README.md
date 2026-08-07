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
Generated at: `2026-08-07T13:36:55+00:00`
As of date: `2026-08-07`
Packages assessed: `47711`
Resources assessed: `243321`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35774 | 163916 |
| freshness_tree_provincial.json | Provincial | provincial | 11652 | 77755 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 285 | 1650 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35774
    "provincial": 11652
    "municipal": 285
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37731
    "current": 4932
    "late": 4903
    "due_soon": 145
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 173624
    "late": 39064
    "current": 29887
    "due_soon": 746
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3367
    "Late 91-365 days": 857
    "Late 31-90 days": 421
    "Late 8-30 days": 167
    "Late 1-7 days": 91
    "Due in 0-7 days": 145
    "Due in 8-30 days": 452
    "Current > 30 days": 4480
    "Unknown": 37731
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "ns-ne", "on", "tf", "ccohs-cchst", "cmc-mcc", "bc-cb", "cer-rec", "ab", "qc"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 57, 54, 44, 43, 43, 40, 40, 35, 29, 28, 27]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
