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
    x-axis [2025-10, 2025-11, 2025-12, 2026-1, 2026-2, 2026-3, 2026-4, 2026-5, 2026-6, 2026-7, 2026-8, 2026-9]
    y-axis "Unique Packages" 0 --> 8839
    y-axis "Number of Informal Requests" 0 --> 11044

    line [1226, 1165, 954, 1243, 926, 907, 2928, 3875, 4193, 4005, 1634, 1379]
    line [1551, 1451, 1195, 1494, 1163, 1234, 3581, 4480, 4798, 4531, 2026, 1826]
```
## Number of Requests and Unique Package Requests last 24 Months

|   Year |   Month |   Number of Informal Requests |   Unique Packages |
|-------:|--------:|------------------------------:|------------------:|
|   2026 |       9 |                          1826 |              1379 |
|   2026 |       8 |                          2026 |              1634 |
|   2026 |       7 |                          4531 |              4005 |
|   2026 |       6 |                          4798 |              4193 |
|   2026 |       5 |                          4480 |              3875 |
|   2026 |       4 |                          3581 |              2928 |
|   2026 |       3 |                          1234 |               907 |
|   2026 |       2 |                          1163 |               926 |
|   2026 |       1 |                          1494 |              1243 |
|   2025 |      12 |                          1195 |               954 |
|   2025 |      11 |                          1451 |              1165 |
|   2025 |      10 |                          1551 |              1226 |
|   2025 |       9 |                          1319 |               981 |
|   2025 |       8 |                          1645 |              1251 |
|   2025 |       7 |                          1491 |              1169 |
|   2025 |       6 |                          1375 |              1136 |
|   2025 |       5 |                          1580 |              1123 |
|   2025 |       4 |                          1993 |              1569 |
|   2025 |       3 |                          2903 |              2126 |
|   2025 |       2 |                          3669 |              2032 |
|   2025 |       1 |                          2863 |              2328 |
|   2024 |      12 |                          2917 |              2262 |
|   2024 |      11 |                          3334 |              2692 |
|   2024 |      10 |                          2462 |              2043 |

## Total Informal Requests Top 25 Organizations 

| Organization Name - EN                                 | Organization Name - FR                                          | owner_org                                            |   Number of Informal Requests |   Unique Packages |
|:-------------------------------------------------------|:----------------------------------------------------------------|:-----------------------------------------------------|------------------------------:|------------------:|
| Immigration, Refugees and Citizenship Canada           | Immigration, Réfugiés et Citoyenneté Canada                     | https://open.canada.ca/data/organization/cic         |                         33200 |              7430 |
| Health Canada                                          | Santé Canada                                                    | https://open.canada.ca/data/organization/hc-sc       |                          7319 |              5169 |
| Royal Canadian Mounted Police                          | Gendarmerie royale du Canada                                    | https://open.canada.ca/data/organization/rcmp-grc    |                          7153 |              2547 |
| Global Affairs Canada                                  | Affaires mondiales Canada                                       | https://open.canada.ca/data/organization/dfatd-maecd |                          6783 |              3289 |
| Innovation, Science and Economic Development Canada    | Innovation, Sciences et Développement économique Canada         | https://open.canada.ca/data/organization/ic          |                          5637 |              3066 |
| Privy Council Office                                   | Bureau du Conseil privé                                         | https://open.canada.ca/data/organization/pco-bcp     |                          5307 |              2362 |
| Canada Border Services Agency                          | Agence des services frontaliers du Canada                       | https://open.canada.ca/data/organization/cbsa-asfc   |                          5019 |              1362 |
| Library and Archives Canada                            | Bibliothèque et Archives Canada                                 | https://open.canada.ca/data/organization/lac-bac     |                          4767 |              2607 |
| Employment and Social Development Canada               | Emploi et Développement social Canada                           | https://open.canada.ca/data/organization/esdc-edsc   |                          4474 |              1845 |
| Canadian Security Intelligence Service                 | Service canadien du renseignement de sécurité                   | https://open.canada.ca/data/organization/csis-scrs   |                          4255 |               740 |
| Canada Revenue Agency                                  | Agence du revenu du Canada                                      | https://open.canada.ca/data/organization/cra-arc     |                          4130 |              1605 |
| Natural Resources Canada                               | Ressources naturelles Canada                                    | https://open.canada.ca/data/organization/nrcan-rncan |                          3978 |              2506 |
| Fisheries and Oceans Canada                            | Pêches et Océans Canada                                         | https://open.canada.ca/data/organization/dfo-mpo     |                          3632 |              1747 |
| Department of Finance Canada                           | Ministère des Finances Canada                                   | https://open.canada.ca/data/organization/fin         |                          3607 |              1985 |
| Public Services and Procurement Canada                 | Services publics et Approvisionnement Canada                    | https://open.canada.ca/data/organization/pwgsc-tpsgc |                          3350 |              1662 |
| Canadian Heritage                                      | Patrimoine canadien                                             | https://open.canada.ca/data/organization/pch         |                          3237 |              1361 |
| National Defence                                       | Défense nationale                                               | https://open.canada.ca/data/organization/dnd-mdn     |                          2837 |              1619 |
| Correctional Service of Canada                         | Service correctionnel du Canada                                 | https://open.canada.ca/data/organization/csc-scc     |                          2744 |              1351 |
| Department of Justice Canada                           | Ministère de la Justice Canada                                  | https://open.canada.ca/data/organization/jus         |                          2143 |               917 |
| Public Health Agency of Canada                         | Agence de la santé publique du Canada                           | https://open.canada.ca/data/organization/phac-aspc   |                          2131 |              1009 |
| Indigenous Services Canada                             | Services aux Autochtones Canada                                 | https://open.canada.ca/data/organization/isc-sac     |                          2068 |               865 |
| Environment and Climate Change Canada                  | Environnement et Changement climatique Canada                   | https://open.canada.ca/data/organization/ec          |                          1785 |               684 |
| Public Safety Canada                                   | Sécurité publique Canada                                        | https://open.canada.ca/data/organization/ps-sp       |                          1720 |               576 |
| Department of Housing, Infrastructure and Communities  | Ministère du Logement, de l’Infrastructure et des Collectivités | https://open.canada.ca/data/organization/infc        |                          1494 |               622 |
| Crown-Indigenous Relations and Northern Affairs Canada | Relations Couronne-Autochtones et Affaires du Nord Canada       | https://open.canada.ca/data/organization/aandc-aadnc |                          1458 |               496 |

## Top 25 Most Requested

| Unique Identifier                                                                                                   | Request Number   | owner_org                                                           | Organization Name - EN                       | Organization Name - FR                        |   Number of Informal Requests |
|:--------------------------------------------------------------------------------------------------------------------|:-----------------|:--------------------------------------------------------------------|:---------------------------------------------|:----------------------------------------------|------------------------------:|
| [3c1be26542a25dbff394488d5d1d5368](https://open.canada.ca/en/search/ati/reference/3c1be26542a25dbff394488d5d1d5368) | A-2024-014       | [aecl-eacl](https://open.canada.ca/data/organization/aecl-eacl)     | Atomic Energy of Canada Limited              | Énergie atomique du Canada, Limitée           |                          1000 |
| [16dbde4ba59e9c1d03865e6016854a53](https://open.canada.ca/en/search/ati/reference/16dbde4ba59e9c1d03865e6016854a53) | ATI2024-033      | [bdc](https://open.canada.ca/data/organization/bdc)                 | Business Development Bank of Canada          | Banque de développement du Canada             |                            86 |
| [17d7ead4362f1ec0363d8e406c632653](https://open.canada.ca/en/search/ati/reference/17d7ead4362f1ec0363d8e406c632653) | 2025-03          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            77 |
| [0840a2cb3bd6f7e62556b8584d4f1659](https://open.canada.ca/en/search/ati/reference/0840a2cb3bd6f7e62556b8584d4f1659) | 2025-01          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            75 |
| [c82f2d40c7b2a3a2de0be5b8c8ad8996](https://open.canada.ca/en/search/ati/reference/c82f2d40c7b2a3a2de0be5b8c8ad8996) | 2024-06-12       | [prpa-appr](https://open.canada.ca/data/organization/prpa-appr)     | Prince Rupert Port Authority                 | L’Administration portuaire de Prince Rupert   |                            74 |
| [0112d4baa4ef1ad94931e00fdbb0887c](https://open.canada.ca/en/search/ati/reference/0112d4baa4ef1ad94931e00fdbb0887c) | A-2023-02215     | [esdc-edsc](https://open.canada.ca/data/organization/esdc-edsc)     | Employment and Social Development Canada     | Emploi et Développement social Canada         |                            70 |
| [6be4ebb38887612c291d632ff4fa22f3](https://open.canada.ca/en/search/ati/reference/6be4ebb38887612c291d632ff4fa22f3) | 1A-2023-34690    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            64 |
| [817d35b5021c2554ffe56317c32d82a0](https://open.canada.ca/en/search/ati/reference/817d35b5021c2554ffe56317c32d82a0) | A-2024-21239     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            48 |
| [c02441374acc93c0d335f9e1717cad3c](https://open.canada.ca/en/search/ati/reference/c02441374acc93c0d335f9e1717cad3c) | A-2019-83837     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            44 |
| [6758d5bf059fbc8e16d92d0f1ff61e7c](https://open.canada.ca/en/search/ati/reference/6758d5bf059fbc8e16d92d0f1ff61e7c) | A-2022-52421     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            43 |
| [43b79c2ade0139300fcd0b7fab0b55b0](https://open.canada.ca/en/search/ati/reference/43b79c2ade0139300fcd0b7fab0b55b0) | A-2024-00020     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            43 |
| [489c43108a10bf94af2650dcaacd6b52](https://open.canada.ca/en/search/ati/reference/489c43108a10bf94af2650dcaacd6b52) | A-2023-00129     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            42 |
| [fa4fa7f1c1c19d134f48403036626623](https://open.canada.ca/en/search/ati/reference/fa4fa7f1c1c19d134f48403036626623) | 2A-2021-12699    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            42 |
| [02cf7be366f8c0b149a53cb936c4d8a5](https://open.canada.ca/en/search/ati/reference/02cf7be366f8c0b149a53cb936c4d8a5) | 1A-2022-08633    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            41 |
| [6669303c723d67af9c252f2b47d086aa](https://open.canada.ca/en/search/ati/reference/6669303c723d67af9c252f2b47d086aa) | A-2020-00482     | [pwgsc-tpsgc](https://open.canada.ca/data/organization/pwgsc-tpsgc) | Public Services and Procurement Canada       | Services publics et Approvisionnement Canada  |                            40 |
| [91cbf6a82443ac952cb5a57857a340b7](https://open.canada.ca/en/search/ati/reference/91cbf6a82443ac952cb5a57857a340b7) | A-2022-01147     | [ec](https://open.canada.ca/data/organization/ec)                   | Environment and Climate Change Canada        | Environnement et Changement climatique Canada |                            37 |
| [0f876de901a2ebf76c56471a67d05642](https://open.canada.ca/en/search/ati/reference/0f876de901a2ebf76c56471a67d05642) | A-2022-03600     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            37 |
| [f94cf02dc4f1abc369c341e778482ed5](https://open.canada.ca/en/search/ati/reference/f94cf02dc4f1abc369c341e778482ed5) | 1A-2022-06919    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [cb05e4abbcdb28f1b55e049e4a3bb770](https://open.canada.ca/en/search/ati/reference/cb05e4abbcdb28f1b55e049e4a3bb770) | A-2024-71243     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [cca1c6a4dcf37611d33962b8a1e1fc43](https://open.canada.ca/en/search/ati/reference/cca1c6a4dcf37611d33962b8a1e1fc43) | A-2019-83845     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [89090aeab44453c5d382e1af74fac873](https://open.canada.ca/en/search/ati/reference/89090aeab44453c5d382e1af74fac873) | A-2022-01590     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [9ddddbe17f2825427ec77a010db22511](https://open.canada.ca/en/search/ati/reference/9ddddbe17f2825427ec77a010db22511) | A-2022-44116     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [dc2df35abcdb427a9482e9c349287b5c](https://open.canada.ca/en/search/ati/reference/dc2df35abcdb427a9482e9c349287b5c) | 2A-2024-56507    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [9674ed871ac388717efa733046a47ed1](https://open.canada.ca/en/search/ati/reference/9674ed871ac388717efa733046a47ed1) | 2A-2023-02896    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [b1d7780013585d893fbed095dac6ac11](https://open.canada.ca/en/search/ati/reference/b1d7780013585d893fbed095dac6ac11) | A-2020-144       | [csis-scrs](https://open.canada.ca/data/organization/csis-scrs)     | Canadian Security Intelligence Service       | Service canadien du renseignement de sécurité |                            35 |

