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
Generated at: `2026-10-25T04:35:34+00:00`
As of date: `2026-10-25`
Packages assessed: `48151`
Resources assessed: `243439`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 36119 | 165918 |
| freshness_tree_provincial.json | Provincial | provincial | 11746 | 75866 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 286 | 1655 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 36119
    "provincial": 11746
    "municipal": 286
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 38141
    "late": 5067
    "current": 4820
    "due_soon": 123
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 172945
    "late": 38761
    "current": 31067
    "due_soon": 666
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3362
    "Late 91-365 days": 1226
    "Late 31-90 days": 224
    "Late 8-30 days": 149
    "Late 1-7 days": 106
    "Due in 0-7 days": 123
    "Due in 8-30 days": 462
    "Current > 30 days": 4358
    "Unknown": 38141
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "ns-ne", "on", "ccohs-cchst", "ic", "bc-cb", "cmc-mcc", "tf", "cmhc-schl", "ab"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 58, 53, 44, 41, 40, 40, 35, 30, 29, 27, 27]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
