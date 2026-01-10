# Datastore Tracker Report
[![Update CKAN Datastore Stats](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_datastore_tracker.yml/badge.svg)](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_datastore_tracker.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/open-data/analytics-corporate-reporting?path=datastore_tracker%2Freadme.md)
#### The Datastore Tracker Report captures stats on the Open.Canada.ca CKAN Datastore. 

|DS_num_tracker.csv |  [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/DS_num_tracker.csv) | 
|----|----|
|org_stats.csv | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=datastore_tracker/org_stats.csv) | 
|ds-resources.csv | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=ddatastore_tracker/ds-resources.csv) |

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
| open.canada.ca | csc-scc | 15 |
| open.canada.ca | csec-cstc | 14 |
| open.canada.ca | csps-efpc | 1 |
| open.canada.ca | dfatd-maecd | 43 |
| open.canada.ca | dfo-mpo | 2 |
| open.canada.ca | dnd-mdn | 22 |
| open.canada.ca | ec | 2 |
| open.canada.ca | elections | 23 |
| open.canada.ca | esdc-edsc | 541 |
| open.canada.ca | fin | 14 |
| open.canada.ca | hc-sc | 119 |
| open.canada.ca | iaac-aeic | 2 |
| open.canada.ca | ic | 23 |
| open.canada.ca | infc | 2 |
| open.canada.ca | irb-cisr | 16 |
| open.canada.ca | isc-sac | 10 |
| open.canada.ca | lac-bac | 8 |
| open.canada.ca | nrc-cnrc | 1 |
| open.canada.ca | nrcan-rncan | 50 |
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
| open.canada.ca | tbs-sct | 189 |
| open.canada.ca | tc | 39 |
| open.canada.ca | vac-acc | 12 |
| open.canada.ca | wd-deo | 10 |
| www.canada.ca | cra-arc | 58 |
| www.canada.ca | tbs-sct | 14 |
<!-- RESOURCE_COUNTS_END -->

#### Dictionary edit radar (by type)
<!-- DICT_RADAR_START -->
```mermaid
radar-beta
  axis T["Type"], L["Label"], N["Notes"]
  curve u["Upload"]{0, 0, 0}
  curve r["Remote"]{0, 0, 0}

  showLegend true

  min 0
  graticule circle
  ticks 5
```
<!-- DICT_RADAR_END -->
