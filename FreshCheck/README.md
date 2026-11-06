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
Generated at: `2026-11-06T06:38:22+00:00`
As of date: `2026-11-06`
Packages assessed: `40482`
Resources assessed: `206532`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 30289 | 140204 |
| freshness_tree_provincial.json | Provincial | provincial | 9955 | 64868 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 238 | 1460 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 30289
    "provincial": 9955
    "municipal": 238
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 32033
    "late": 4240
    "current": 4054
    "due_soon": 155
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 146315
    "late": 32766
    "current": 26173
    "due_soon": 1278
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 2831
    "Late 91-365 days": 1020
    "Late 31-90 days": 195
    "Late 8-30 days": 132
    "Late 1-7 days": 62
    "Due in 0-7 days": 155
    "Due in 8-30 days": 449
    "Current > 30 days": 3605
    "Unknown": 32033
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "apa", "fintrac-canafe", "pei-ipe", "ns-ne", "pwgsc-tpsgc", "on", "ic", "ccohs-cchst", "bc-cb", "cmc-mcc", "cer-rec", "osfi-bsif", "cmhc-schl"]
    y-axis "Current packages (%)" 0 --> 100
    bar [73, 71, 64, 62, 55, 44, 42, 40, 38, 37, 35, 33, 30, 30, 29]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
