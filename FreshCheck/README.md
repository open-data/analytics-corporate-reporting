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
Generated at: `2026-09-23T04:42:10+00:00`
As of date: `2026-09-23`
Packages assessed: `47931`
Resources assessed: `241930`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35986 | 165102 |
| freshness_tree_provincial.json | Provincial | provincial | 11660 | 75178 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 285 | 1650 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35986
    "provincial": 11660
    "municipal": 285
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37948
    "late": 4961
    "current": 4822
    "due_soon": 200
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 172100
    "late": 38258
    "current": 30227
    "due_soon": 1345
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3351
    "Late 91-365 days": 1081
    "Late 31-90 days": 323
    "Late 8-30 days": 97
    "Late 1-7 days": 109
    "Due in 0-7 days": 200
    "Due in 8-30 days": 513
    "Current > 30 days": 4309
    "Unknown": 37948
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "cmhc-schl", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "tf", "on", "ns-ne", "ccohs-cchst", "ic", "bc-cb", "cer-rec", "cwa-aec"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 76, 67, 61, 60, 58, 55, 43, 41, 40, 40, 39, 35, 33, 33]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
