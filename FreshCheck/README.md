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
Generated at: `2026-11-25T08:23:55+00:00`
As of date: `2026-11-25`
Packages assessed: `48359`
Resources assessed: `244772`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 36312 | 167166 |
| freshness_tree_provincial.json | Provincial | provincial | 11761 | 75949 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 286 | 1657 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 36312
    "provincial": 11761
    "municipal": 286
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 38319
    "late": 5083
    "current": 4716
    "due_soon": 241
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 174108
    "late": 38465
    "current": 30578
    "due_soon": 1621
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3598
    "Late 91-365 days": 1059
    "Late 31-90 days": 269
    "Late 8-30 days": 91
    "Late 1-7 days": 66
    "Due in 0-7 days": 241
    "Due in 8-30 days": 528
    "Current > 30 days": 4188
    "Unknown": 38319
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "fintrac-canafe", "apa", "csps-efpc", "pei-ipe", "pwgsc-tpsgc", "tf", "ns-ne", "ic", "ccohs-cchst", "on", "cmc-mcc", "bc-cb", "ab", "cmhc-schl"]
    y-axis "Current packages (%)" 0 --> 100
    bar [78, 75, 67, 60, 58, 50, 50, 44, 41, 40, 40, 36, 35, 27, 27]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
