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
Generated at: `2026-10-29T05:41:52+00:00`
As of date: `2026-10-29`
Packages assessed: `40200`
Resources assessed: `204994`

### Split JSON Outputs
| File | Group | Jurisdiction values | Packages | Resources |
| --- | --- | --- | --- | --- |
| freshness_tree_federal.json | Federal | federal | 30069 | 139122 |
| freshness_tree_provincial.json | Provincial | provincial | 9895 | 64423 |
| freshness_tree_municipal_user.json | Municipal and user | municipal, user | 236 | 1449 |

### Package Jurisdictions
```mermaid
pie showData title Package jurisdiction
    "federal": 30069
    "provincial": 9895
    "municipal": 236
```

### Package Freshness Status
```mermaid
pie showData title Package freshness status
    "unknown": 31805
    "late": 4248
    "current": 4052
    "due_soon": 95
```

### Resource Freshness Status
```mermaid
pie showData title Resource freshness status
    "unknown": 145264
    "late": 32869
    "current": 26354
    "due_soon": 507
```

### Package Update Timing
```mermaid
pie showData title Package timing against expected update date
    "Late > 1 year": 2806
    "Late 91-365 days": 1017
    "Late 31-90 days": 192
    "Late 8-30 days": 126
    "Late 1-7 days": 107
    "Due in 0-7 days": 95
    "Due in 8-30 days": 494
    "Current > 30 days": 3558
    "Unknown": 31805
```

### Departments Keeping Data Current
```mermaid
xychart-beta
    title "Departments with highest current package share"
    x-axis ["chrc-ccdp", "csps-efpc", "fintrac-canafe", "apa", "pei-ipe", "pwgsc-tpsgc", "ns-ne", "ic", "on", "ccohs-cchst", "bc-cb", "cmc-mcc", "cmhc-schl", "osfi-bsif", "isc-sac"]
    y-axis "Current packages (%)" 0 --> 100
    bar [73, 71, 62, 60, 55, 50, 44, 41, 41, 37, 35, 33, 29, 28, 27]
```

### Skipped Jurisdictions
None.
<!-- FRESHCHECK_REPORT_END -->
