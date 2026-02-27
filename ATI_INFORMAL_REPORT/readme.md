# ATI Informal Requests Report
[![Generate ATI INFORMAL Reports](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_ati_informals.yml/badge.svg)](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_ati_informals.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/open-data/analytics-corporate-reporting?path=ATI_INFORMAL_REPORT%2Freadme.md)

[Open Government Analytics - ATI informal requests per summary](https://open.canada.ca/data/en/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/e664cf3d-6cb7-4aaa-adfa-e459c2552e3e) is updated monthly providing stats on the volumne ATI Informal Requests submitted via `https://open.canada.ca/en/search/ati` 

This report offers a variety of aggregrations of the dataset 

| File | Flat Viewer |
|--|--|
|**idtot_df.csv**  *Top 100 ATI Packages by Number of Informal Requests for All Time.*  | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=ATI_INFORMAL_REPORT%2Fidtot_df.csv&sort=Number%20of%20Informal%20Requests%2Cdesc)|
|**org_df.csv** Number of Informal Requests by organization by month.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=ATI_INFORMAL_REPORT%2Forg_df.csv)|
|**orgtot.csv contains** Total Innformal Requests by organization.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=ATI_INFORMAL_REPORT%2Forgtot_df.csv)|
|**top_10_df.csv**  Top 10 packages by informal requsts by month.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=ATI_INFORMAL_REPORT%2top_10_df.csv)|

## Requests and Unique Package Requests last 12 months

```mermaid

xychart-beta
    title "Monthly 🟩Num. Informal Requests and 🟦Num. Unique Packages Requested - Last 12 Months"
    x-axis [2025-2, 2025-3, 2025-4, 2025-5, 2025-6, 2025-7, 2025-8, 2025-9, 2025-10, 2025-11, 2025-12, 2026-1]
    y-axis "Unique Packages" 0 --> 9046
    y-axis "Number of Informal Requests" 0 --> 10508

    line [1521, 1745, 1338, 696, 862, 912, 894, 786, 1076, 969, 807, 1161]
    line [2846, 2102, 1677, 795, 968, 1084, 1035, 987, 1340, 1219, 1032, 1408]
```
## Number of Requests and Unique Package Requests last 24 Months

|   Year |   Month |   Number of Informal Requests |   Unique Packages |
|-------:|--------:|------------------------------:|------------------:|
|   2026 |       1 |                          1408 |              1161 |
|   2025 |      12 |                          1032 |               807 |
|   2025 |      11 |                          1219 |               969 |
|   2025 |      10 |                          1340 |              1076 |
|   2025 |       9 |                           987 |               786 |
|   2025 |       8 |                          1035 |               894 |
|   2025 |       7 |                          1084 |               912 |
|   2025 |       6 |                           968 |               862 |
|   2025 |       5 |                           795 |               696 |
|   2025 |       4 |                          1677 |              1338 |
|   2025 |       3 |                          2102 |              1745 |
|   2025 |       2 |                          2846 |              1521 |
|   2025 |       1 |                          2111 |              1845 |
|   2024 |      12 |                          2202 |              1865 |
|   2024 |      11 |                          2575 |              2254 |
|   2024 |      10 |                          2126 |              1792 |
|   2024 |       9 |                          2088 |              1740 |
|   2024 |       8 |                          2152 |              1750 |
|   2024 |       7 |                         10498 |              8155 |
|   2024 |       6 |                          7541 |              7040 |
|   2024 |       5 |                          9398 |              9036 |
|   2024 |       4 |                          7329 |              7109 |
|   2024 |       3 |                           929 |               813 |
|   2024 |       2 |                          1585 |              1329 |

## Total Informal Requests Top 25 Organizations 

| Organization Name - EN                                 | Organization Name - FR                                    | owner_org                                            |   Number of Informal Requests |   Unique Packages |
|:-------------------------------------------------------|:----------------------------------------------------------|:-----------------------------------------------------|------------------------------:|------------------:|
| Immigration, Refugees and Citizenship Canada           | Immigration, Réfugiés et Citoyenneté Canada               | https://open.canada.ca/data/organization/cic         |                         13629 |              3595 |
| National Defence                                       | Défense nationale                                         | https://open.canada.ca/data/organization/dnd-mdn     |                          6514 |              3104 |
| Global Affairs Canada                                  | Affaires mondiales Canada                                 | https://open.canada.ca/data/organization/dfatd-maecd |                          5944 |              2897 |
| Health Canada                                          | Santé Canada                                              | https://open.canada.ca/data/organization/hc-sc       |                          5426 |              3728 |
| Canada Border Services Agency                          | Agence des services frontaliers du Canada                 | https://open.canada.ca/data/organization/cbsa-asfc   |                          4284 |              1126 |
| Innovation, Science and Economic Development Canada    | Innovation, Sciences et Développement économique Canada   | https://open.canada.ca/data/organization/ic          |                          4137 |              2319 |
| Library and Archives Canada                            | Bibliothèque et Archives Canada                           | https://open.canada.ca/data/organization/lac-bac     |                          3985 |              1940 |
| Canadian Security Intelligence Service                 | Service canadien du renseignement de sécurité             | https://open.canada.ca/data/organization/csis-scrs   |                          3791 |               657 |
| Employment and Social Development Canada               | Emploi et Développement social Canada                     | https://open.canada.ca/data/organization/esdc-edsc   |                          3496 |              1508 |
| Canada Revenue Agency                                  | Agence du revenu du Canada                                | https://open.canada.ca/data/organization/cra-arc     |                          3487 |              1370 |
| Natural Resources Canada                               | Ressources naturelles Canada                              | https://open.canada.ca/data/organization/nrcan-rncan |                          3371 |              2073 |
| Fisheries and Oceans Canada                            | Pêches et Océans Canada                                   | https://open.canada.ca/data/organization/dfo-mpo     |                          3309 |              1538 |
| Public Safety Canada                                   | Sécurité publique Canada                                  | https://open.canada.ca/data/organization/ps-sp       |                          3093 |              1241 |
| Department of Finance Canada                           | Ministère des Finances Canada                             | https://open.canada.ca/data/organization/fin         |                          2892 |              1598 |
| Public Services and Procurement Canada                 | Services publics et Approvisionnement Canada              | https://open.canada.ca/data/organization/pwgsc-tpsgc |                          2843 |              1383 |
| Canadian Heritage                                      | Patrimoine canadien                                       | https://open.canada.ca/data/organization/pch         |                          2829 |              1179 |
| Transport Canada                                       | Transports Canada                                         | https://open.canada.ca/data/organization/tc          |                          2408 |              1460 |
| Correctional Service of Canada                         | Service correctionnel du Canada                           | https://open.canada.ca/data/organization/csc-scc     |                          2352 |              1157 |
| Treasury Board of Canada Secretariat                   | Secrétariat du Conseil du Trésor du Canada                | https://open.canada.ca/data/organization/tbs-sct     |                          2057 |               868 |
| Royal Canadian Mounted Police                          | Gendarmerie royale du Canada                              | https://open.canada.ca/data/organization/rcmp-grc    |                          1961 |               688 |
| Department of Justice Canada                           | Ministère de la Justice Canada                            | https://open.canada.ca/data/organization/jus         |                          1737 |               730 |
| Indigenous Services Canada                             | Services aux Autochtones Canada                           | https://open.canada.ca/data/organization/isc-sac     |                          1719 |               722 |
| Environment and Climate Change Canada                  | Environnement et Changement climatique Canada             | https://open.canada.ca/data/organization/ec          |                          1555 |               604 |
| Crown-Indigenous Relations and Northern Affairs Canada | Relations Couronne-Autochtones et Affaires du Nord Canada | https://open.canada.ca/data/organization/aandc-aadnc |                          1297 |               436 |
| Canadian Food Inspection Agency                        | Agence canadienne d'inspection des aliments               | https://open.canada.ca/data/organization/cfia-acia   |                          1212 |               618 |

## Top 25 Most Requested

| Unique Identifier                                                                                                   | Request Number   | owner_org                                                           | Organization Name - EN                       | Organization Name - FR                        |   Number of Informal Requests |
|:--------------------------------------------------------------------------------------------------------------------|:-----------------|:--------------------------------------------------------------------|:---------------------------------------------|:----------------------------------------------|------------------------------:|
| [3c1be26542a25dbff394488d5d1d5368](https://open.canada.ca/en/search/ati/reference/3c1be26542a25dbff394488d5d1d5368) | A-2024-014       | [aecl-eacl](https://open.canada.ca/data/organization/aecl-eacl)     | Atomic Energy of Canada Limited              | Énergie atomique du Canada, Limitée           |                          1000 |
| [9ceef5a77d1fadd06365de7665ee296c](https://open.canada.ca/en/search/ati/reference/9ceef5a77d1fadd06365de7665ee296c) | A-2023-00117     | [tbs-sct](https://open.canada.ca/data/organization/tbs-sct)         | Treasury Board of Canada Secretariat         | Secrétariat du Conseil du Trésor du Canada    |                            86 |
| [16dbde4ba59e9c1d03865e6016854a53](https://open.canada.ca/en/search/ati/reference/16dbde4ba59e9c1d03865e6016854a53) | ATI2024-033      | [bdc](https://open.canada.ca/data/organization/bdc)                 | Business Development Bank of Canada          | Banque de développement du Canada             |                            85 |
| [17d7ead4362f1ec0363d8e406c632653](https://open.canada.ca/en/search/ati/reference/17d7ead4362f1ec0363d8e406c632653) | 2025-03          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            75 |
| [0840a2cb3bd6f7e62556b8584d4f1659](https://open.canada.ca/en/search/ati/reference/0840a2cb3bd6f7e62556b8584d4f1659) | 2025-01          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            74 |
| [c82f2d40c7b2a3a2de0be5b8c8ad8996](https://open.canada.ca/en/search/ati/reference/c82f2d40c7b2a3a2de0be5b8c8ad8996) | 2024-06-12       | [prpa-appr](https://open.canada.ca/data/organization/prpa-appr)     | Prince Rupert Port Authority                 | L’Administration portuaire de Prince Rupert   |                            74 |
| [c02441374acc93c0d335f9e1717cad3c](https://open.canada.ca/en/search/ati/reference/c02441374acc93c0d335f9e1717cad3c) | A-2019-83837     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            44 |
| [43b79c2ade0139300fcd0b7fab0b55b0](https://open.canada.ca/en/search/ati/reference/43b79c2ade0139300fcd0b7fab0b55b0) | A-2024-00020     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            43 |
| [489c43108a10bf94af2650dcaacd6b52](https://open.canada.ca/en/search/ati/reference/489c43108a10bf94af2650dcaacd6b52) | A-2023-00129     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            42 |
| [6669303c723d67af9c252f2b47d086aa](https://open.canada.ca/en/search/ati/reference/6669303c723d67af9c252f2b47d086aa) | A-2020-00482     | [pwgsc-tpsgc](https://open.canada.ca/data/organization/pwgsc-tpsgc) | Public Services and Procurement Canada       | Services publics et Approvisionnement Canada  |                            40 |
| [f4571fd28501329a6055a7ea2a9ccc90](https://open.canada.ca/en/search/ati/reference/f4571fd28501329a6055a7ea2a9ccc90) | A-2023-00777     | [tbs-sct](https://open.canada.ca/data/organization/tbs-sct)         | Treasury Board of Canada Secretariat         | Secrétariat du Conseil du Trésor du Canada    |                            40 |
| [fa4fa7f1c1c19d134f48403036626623](https://open.canada.ca/en/search/ati/reference/fa4fa7f1c1c19d134f48403036626623) | 2A-2021-12699    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            39 |
| [02cf7be366f8c0b149a53cb936c4d8a5](https://open.canada.ca/en/search/ati/reference/02cf7be366f8c0b149a53cb936c4d8a5) | 1A-2022-08633    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            37 |
| [f94cf02dc4f1abc369c341e778482ed5](https://open.canada.ca/en/search/ati/reference/f94cf02dc4f1abc369c341e778482ed5) | 1A-2022-06919    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [cca1c6a4dcf37611d33962b8a1e1fc43](https://open.canada.ca/en/search/ati/reference/cca1c6a4dcf37611d33962b8a1e1fc43) | A-2019-83845     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [91cbf6a82443ac952cb5a57857a340b7](https://open.canada.ca/en/search/ati/reference/91cbf6a82443ac952cb5a57857a340b7) | A-2022-01147     | [ec](https://open.canada.ca/data/organization/ec)                   | Environment and Climate Change Canada        | Environnement et Changement climatique Canada |                            35 |
| [b1d7780013585d893fbed095dac6ac11](https://open.canada.ca/en/search/ati/reference/b1d7780013585d893fbed095dac6ac11) | A-2020-144       | [csis-scrs](https://open.canada.ca/data/organization/csis-scrs)     | Canadian Security Intelligence Service       | Service canadien du renseignement de sécurité |                            35 |
| [efc8e31eceb9b168153d6aad073740e2](https://open.canada.ca/en/search/ati/reference/efc8e31eceb9b168153d6aad073740e2) | 2A-2021-61194    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            33 |
| [02e9a86f0248eebe0912ed77febffa72](https://open.canada.ca/en/search/ati/reference/02e9a86f0248eebe0912ed77febffa72) | A-2022-00373     | [tc](https://open.canada.ca/data/organization/tc)                   | Transport Canada                             | Transports Canada                             |                            33 |
| [034678e46266d05c918e794d7f39d5be](https://open.canada.ca/en/search/ati/reference/034678e46266d05c918e794d7f39d5be) | 2A-2020-93526    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            31 |
| [4357dacc2517090b30db7e5272291a5b](https://open.canada.ca/en/search/ati/reference/4357dacc2517090b30db7e5272291a5b) | A-2019-09085     | [lac-bac](https://open.canada.ca/data/organization/lac-bac)         | Library and Archives Canada                  | Bibliothèque et Archives Canada               |                            31 |
| [88c5c9d37af76de85fbb3383135d7c51](https://open.canada.ca/en/search/ati/reference/88c5c9d37af76de85fbb3383135d7c51) | A-2021-02254     | [esdc-edsc](https://open.canada.ca/data/organization/esdc-edsc)     | Employment and Social Development Canada     | Emploi et Développement social Canada         |                            30 |
| [d793308d8e71096775e185f1f738515f](https://open.canada.ca/en/search/ati/reference/d793308d8e71096775e185f1f738515f) | A-2021-669       | [csis-scrs](https://open.canada.ca/data/organization/csis-scrs)     | Canadian Security Intelligence Service       | Service canadien du renseignement de sécurité |                            30 |
| [489b57895397d43833ecdb0f8b88b2cf](https://open.canada.ca/en/search/ati/reference/489b57895397d43833ecdb0f8b88b2cf) | A-2020-373       | [csis-scrs](https://open.canada.ca/data/organization/csis-scrs)     | Canadian Security Intelligence Service       | Service canadien du renseignement de sécurité |                            29 |
| [b1b3199daa5891d9f508a68ccd7e85d4](https://open.canada.ca/en/search/ati/reference/b1b3199daa5891d9f508a68ccd7e85d4) | A-2019-96612     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            29 |

