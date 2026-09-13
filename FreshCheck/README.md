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
Generated at: `2026-09-13T04:42:49+00:00`
As of date: `2026-09-13`
Packages assessed: `47930`
Resources assessed: `241857`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 35981 | 165095 |
| freshness_tree_provincial.json | Provincial | provincial | 11664 | 75112 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 285 | 1650 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 35981
    "provincial": 11664
    "municipal": 285
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 37932
    "late": 4971
    "current": 4834
    "due_soon": 193
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 171914
    "late": 38320
    "current": 29926
    "due_soon": 1697
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 3380
    "Late 91-365 days": 1010
    "Late 31-90 days": 370
    "Late 8-30 days": 135
    "Late 1-7 days": 76
    "Due in 0-7 days": 193
    "Due in 8-30 days": 475
    "Current > 30 days": 4359
    "Unknown": 37932
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "tf", "ns-ne", "on", "ccohs-cchst", "cwa-aec", "ic", "bc-cb", "cmc-mcc", "cer-rec"]
    y-axis "Current packages (%)" 0 --> 100
    bar [77, 67, 61, 60, 57, 55, 43, 42, 42, 40, 40, 39, 35, 30, 29]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
