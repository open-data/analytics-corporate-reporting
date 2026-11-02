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
Generated at: `2026-11-02T05:57:27+00:00`
As of date: `2026-11-02`
Packages assessed: `48203`
Resources assessed: `243750`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 36168 | 166161 |
| freshness_tree_provincial.json | Provincial | provincial | 11749 | 75934 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 286 | 1655 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 36168
    "provincial": 11749
    "municipal": 286
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 38184
    "late": 5075
    "current": 4732
    "due_soon": 212
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 173152
    "late": 38589
    "current": 30291
    "due_soon": 1718
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3364
    "Late 91-365 days": 1230
    "Late 31-90 days": 233
    "Late 8-30 days": 136
    "Late 1-7 days": 112
    "Due in 0-7 days": 212
    "Due in 8-30 days": 491
    "Current > 30 days": 4241
    "Unknown": 38184
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "apa", "csps-efpc", "fintrac-canafe", "pei-ipe", "ns-ne", "pwgsc-tpsgc", "on", "ccohs-cchst", "ic", "bc-cb", "cmc-mcc", "tf", "ab", "cmhc-schl"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 67, 64, 58, 44, 43, 41, 40, 37, 35, 30, 29, 27, 27]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
