# Datastore Tracker Report
[![Update CKAN Datastore Stats](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_datastore_tracker.yml/badge.svg)](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_datastore_tracker.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/open-data/analytics-corporate-reporting?path=datastore_tracker%2FREADME.md)
#### The Datastore Tracker Report captures stats on the Open.Canada.ca CKAN Datastore. 



| CSV | Description | Flatdata viewer |
|---|---|---|
| DS_num_tracker.csv | Daily datastore summary metrics (counts, sizes, uploaded/remote source). | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/DS_num_tracker.csv) |
| org_stats.csv | Organization-level usage (size, counts). | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/org_stats.csv) |
| ds-resources.csv | Resource list with datastore stats. | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/ds-resources.csv) |
| ds-dictionary-use.csv | Tracks if CKAN DS dictionary has been used. Count number of fields with data type, labels, and notes completed in each table  | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/ds-dictionary-use.csv) |
| res_views.csv | Captures list of resource views available | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/res_views.csv) |
| res_relations.csv | Resource relationship metadata. | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/res_relations.csv) |
| res_validation_status.csv | Status of ckanext-validation checks on resources. | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/res_validation_status.csv) |

#### Resource Validation Status
#### Resource Validation Status
<!-- VALIDATION_STATUS_CHART_START -->

```mermaid
---
config:
  theme: dark
---
pie showData title Resource Validation Status
    "success": 3340
    "failure": 3198
```

<!-- VALIDATION_STATUS_CHART_END -->

#### Resource View Types
#### Resource View Types
<!-- RESOURCE_VIEW_TYPES_CHART_START -->

```mermaid
---
config:
  theme: dark
---
pie showData title Resource View Types
    "datatables_view": 3010
    "text_view": 205
    "openapi_view": 4
    "image_view": 4
    "power_bi_view": 1
```

<!-- RESOURCE_VIEW_TYPES_CHART_END -->

#### Resource counts by URL host and org
#### Resource counts by URL host and org
<!-- RESOURCE_COUNTS_START -->
| url_host | owner | resource_count |
|---|---|---|
| od-do.agr.gc.ca | aafc-aac | 24 |
| open.canada.ca | aafc-aac | 3 |
| open.canada.ca | atssc-scdata | 4 |
| open.canada.ca | cbsa-asfc | 6 |
| open.canada.ca | cer-rec | 1 |
| open.canada.ca | cfia-acia | 85 |
| open.canada.ca | cic | 2 |
| open.canada.ca | cnsc-ccsn | 31 |
| open.canada.ca | cra-arc | 356 |
| open.canada.ca | csa-asc | 3 |
| open.canada.ca | csc-scc | 14 |
| open.canada.ca | csec-cstc | 14 |
| open.canada.ca | csps-efpc | 1 |
| open.canada.ca | dfatd-maecd | 43 |
| open.canada.ca | dfo-mpo | 2 |
| open.canada.ca | dnd-mdn | 22 |
| open.canada.ca | ec | 2 |
| open.canada.ca | elections | 23 |
| open.canada.ca | esdc-edsc | 544 |
| open.canada.ca | fin | 14 |
| open.canada.ca | hc-sc | 119 |
| open.canada.ca | iaac-aeic | 2 |
| open.canada.ca | ic | 23 |
| open.canada.ca | infc | 2 |
| open.canada.ca | irb-cisr | 16 |
| open.canada.ca | isc-sac | 10 |
| open.canada.ca | lac-bac | 8 |
| open.canada.ca | nrc-cnrc | 1 |
| open.canada.ca | nrcan-rncan | 53 |
| open.canada.ca | opc-cpvp | 9 |
| open.canada.ca | osfi-bsif | 74 |
| open.canada.ca | pc | 933 |
| open.canada.ca | pch | 7 |
| open.canada.ca | pco-bcp | 3 |
| open.canada.ca | phac-aspc | 39 |
| open.canada.ca | psc-cfp | 122 |
| open.canada.ca | pwgsc-tpsgc | 1 |
| open.canada.ca | rcmp-grc | 1 |
| open.canada.ca | ssc-spc | 39 |
| open.canada.ca | tbs-sct | 191 |
| open.canada.ca | tc | 39 |
| open.canada.ca | vac-acc | 12 |
| open.canada.ca | wd-deo | 10 |
| www.canada.ca | cra-arc | 58 |
| www.canada.ca | tbs-sct | 14 |
<!-- RESOURCE_COUNTS_END -->


#### Dictionary edit radar (by type)
#### Dictionary edit radar (by type)
<!-- DICT_RADAR_START -->
```mermaid
radar-beta
  axis T["Type"], L["Label"], N["Notes"]
  curve u["Upload"]{0.00086, 0.00112, 0.00108}
  curve r["Remote"]{0, 0, 0}

  showLegend true

  min 0
  graticule circle
  ticks 5
```
<!-- DICT_RADAR_END -->


#### Top 20 Orgs by View Count
#### Top 20 Orgs by View Count
<!-- TOP_20_OWNERS_CHART_START -->

```mermaid
---
config:
  theme: dark
---
pie showData title Top 20 Orgs by View Count
    "pc": 944
    "esdc-edsc": 591
    "cra-arc": 409
    "tbs-sct": 273
    "hc-sc": 147
    "psc-cfp": 147
    "cfia-acia": 99
    "osfi-bsif": 74
    "nrcan-rncan": 59
    "phac-aspc": 48
    "dfatd-maecd": 43
    "ssc-spc": 41
    "tc": 38
    "cnsc-ccsn": 35
    "ic": 24
    "dnd-mdn": 23
    "elections": 21
    "cic": 17
    "irb-cisr": 16
    "csc-scc": 15
```

<!-- TOP_20_OWNERS_CHART_END -->



#### Resource Relation Type
#### Resource Relation Type
<!-- RESOURCE_RELATION_TYPE_CHART_START -->

```mermaid
---
config:
  theme: dark
---
pie showData title Resource Relation Type
    "references": 5
    "defined_by": 5
    "referenced_by": 3
    "defines": 2
```

<!-- RESOURCE_RELATION_TYPE_CHART_END -->
