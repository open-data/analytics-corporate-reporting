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
    x-axis [2024-8, 2024-9, 2024-10, 2024-11, 2024-12, 2025-1, 2025-2, 2025-3, 2025-4, 2025-5, 2025-6, 2025-7]
    y-axis "Unique Packages" 0 --> 10094
    y-axis "Number of Informal Requests" 0 --> 12777

    line [2315, 2553, 2271, 2867, 2479, 2553, 2263, 2291, 1711, 1202, 1240, 1283]
    line [2892, 3279, 2713, 3527, 3151, 3110, 3920, 3091, 2153, 1667, 1499, 1635]
```
## Number of Requests and Unique Package Requests last 24 Months

|   Year |   Month |   Number of Informal Requests |   Unique Packages |
|-------:|--------:|------------------------------:|------------------:|
|   2025 |       7 |                          1635 |              1283 |
|   2025 |       6 |                          1499 |              1240 |
|   2025 |       5 |                          1667 |              1202 |
|   2025 |       4 |                          2153 |              1711 |
|   2025 |       3 |                          3091 |              2291 |
|   2025 |       2 |                          3920 |              2263 |
|   2025 |       1 |                          3110 |              2553 |
|   2024 |      12 |                          3151 |              2479 |
|   2024 |      11 |                          3527 |              2867 |
|   2024 |      10 |                          2713 |              2271 |
|   2024 |       9 |                          3279 |              2553 |
|   2024 |       8 |                          2892 |              2315 |
|   2024 |       7 |                         12767 |              9660 |
|   2024 |       6 |                          9006 |              8301 |
|   2024 |       5 |                         10694 |             10084 |
|   2024 |       4 |                          9032 |              8622 |
|   2024 |       3 |                          1539 |              1241 |
|   2024 |       2 |                          2189 |              1792 |
|   2024 |       1 |                          2235 |              1715 |
|   2023 |      12 |                          1538 |              1123 |
|   2023 |      11 |                          1766 |              1416 |
|   2023 |      10 |                          1890 |              1578 |
|   2023 |       9 |                          1414 |              1159 |
|   2023 |       8 |                          1616 |              1286 |

## Total Informal Requests Top 25 Organizations 

| Organization Name - EN                              | Organization Name - FR                                  | owner_org                                            |   Number of Informal Requests |   Unique Packages |
|:----------------------------------------------------|:--------------------------------------------------------|:-----------------------------------------------------|------------------------------:|------------------:|
| Immigration, Refugees and Citizenship Canada        | Immigration, Réfugiés et Citoyenneté Canada             | https://open.canada.ca/data/organization/cic         |                         26528 |              6414 |
| National Defence                                    | Défense nationale                                       | https://open.canada.ca/data/organization/dnd-mdn     |                          6003 |              2899 |
| Royal Canadian Mounted Police                       | Gendarmerie royale du Canada                            | https://open.canada.ca/data/organization/rcmp-grc    |                          5954 |              2157 |
| Global Affairs Canada                               | Affaires mondiales Canada                               | https://open.canada.ca/data/organization/dfatd-maecd |                          5503 |              2734 |
| Health Canada                                       | Santé Canada                                            | https://open.canada.ca/data/organization/hc-sc       |                          5201 |              3644 |
| Canada Border Services Agency                       | Agence des services frontaliers du Canada               | https://open.canada.ca/data/organization/cbsa-asfc   |                          3970 |              1026 |
| Library and Archives Canada                         | Bibliothèque et Archives Canada                         | https://open.canada.ca/data/organization/lac-bac     |                          3936 |              1910 |
| Privy Council Office                                | Bureau du Conseil privé                                 | https://open.canada.ca/data/organization/pco-bcp     |                          3927 |              1775 |
| Innovation, Science and Economic Development Canada | Innovation, Sciences et Développement économique Canada | https://open.canada.ca/data/organization/ic          |                          3860 |              2185 |
| Canadian Security Intelligence Service              | Service canadien du renseignement de sécurité           | https://open.canada.ca/data/organization/csis-scrs   |                          3596 |               609 |
| Canada Revenue Agency                               | Agence du revenu du Canada                              | https://open.canada.ca/data/organization/cra-arc     |                          3391 |              1343 |
| Natural Resources Canada                            | Ressources naturelles Canada                            | https://open.canada.ca/data/organization/nrcan-rncan |                          3239 |              2018 |
| Employment and Social Development Canada            | Emploi et Développement social Canada                   | https://open.canada.ca/data/organization/esdc-edsc   |                          3207 |              1418 |
| Fisheries and Oceans Canada                         | Pêches et Océans Canada                                 | https://open.canada.ca/data/organization/dfo-mpo     |                          3139 |              1480 |
| Public Safety Canada                                | Sécurité publique Canada                                | https://open.canada.ca/data/organization/ps-sp       |                          2897 |              1176 |
| Public Services and Procurement Canada              | Services publics et Approvisionnement Canada            | https://open.canada.ca/data/organization/pwgsc-tpsgc |                          2714 |              1337 |
| Department of Finance Canada                        | Ministère des Finances Canada                           | https://open.canada.ca/data/organization/fin         |                          2711 |              1511 |
| Canadian Heritage                                   | Patrimoine canadien                                     | https://open.canada.ca/data/organization/pch         |                          2655 |              1134 |
| Transport Canada                                    | Transports Canada                                       | https://open.canada.ca/data/organization/tc          |                          2319 |              1430 |
| Correctional Service of Canada                      | Service correctionnel du Canada                         | https://open.canada.ca/data/organization/csc-scc     |                          2227 |              1121 |
| Treasury Board of Canada Secretariat                | Secrétariat du Conseil du Trésor du Canada              | https://open.canada.ca/data/organization/tbs-sct     |                          1951 |               822 |
| Public Health Agency of Canada                      | Agence de la santé publique du Canada                   | https://open.canada.ca/data/organization/phac-aspc   |                          1752 |               818 |
| Department of Justice Canada                        | Ministère de la Justice Canada                          | https://open.canada.ca/data/organization/jus         |                          1590 |               669 |
| Indigenous Services Canada                          | Services aux Autochtones Canada                         | https://open.canada.ca/data/organization/isc-sac     |                          1546 |               668 |
| Environment and Climate Change Canada               | Environnement et Changement climatique Canada           | https://open.canada.ca/data/organization/ec          |                          1476 |               571 |

## Top 25 Most Requested

| Unique Identifier                                                                                                   | Request Number   | owner_org                                                           | Organization Name - EN                       | Organization Name - FR                        |   Number of Informal Requests |
|:--------------------------------------------------------------------------------------------------------------------|:-----------------|:--------------------------------------------------------------------|:---------------------------------------------|:----------------------------------------------|------------------------------:|
| [3c1be26542a25dbff394488d5d1d5368](https://open.canada.ca/en/search/ati/reference/3c1be26542a25dbff394488d5d1d5368) | A-2024-014       | [aecl-eacl](https://open.canada.ca/data/organization/aecl-eacl)     | Atomic Energy of Canada Limited              | Énergie atomique du Canada, Limitée           |                          1000 |
| [9ceef5a77d1fadd06365de7665ee296c](https://open.canada.ca/en/search/ati/reference/9ceef5a77d1fadd06365de7665ee296c) | A-2023-00117     | [tbs-sct](https://open.canada.ca/data/organization/tbs-sct)         | Treasury Board of Canada Secretariat         | Secrétariat du Conseil du Trésor du Canada    |                            85 |
| [16dbde4ba59e9c1d03865e6016854a53](https://open.canada.ca/en/search/ati/reference/16dbde4ba59e9c1d03865e6016854a53) | ATI2024-033      | [bdc](https://open.canada.ca/data/organization/bdc)                 | Business Development Bank of Canada          | Banque de développement du Canada             |                            85 |
| [17d7ead4362f1ec0363d8e406c632653](https://open.canada.ca/en/search/ati/reference/17d7ead4362f1ec0363d8e406c632653) | 2025-03          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            75 |
| [c82f2d40c7b2a3a2de0be5b8c8ad8996](https://open.canada.ca/en/search/ati/reference/c82f2d40c7b2a3a2de0be5b8c8ad8996) | 2024-06-12       | [prpa-appr](https://open.canada.ca/data/organization/prpa-appr)     | Prince Rupert Port Authority                 | L’Administration portuaire de Prince Rupert   |                            74 |
| [0840a2cb3bd6f7e62556b8584d4f1659](https://open.canada.ca/en/search/ati/reference/0840a2cb3bd6f7e62556b8584d4f1659) | 2025-01          | [mpa-apm](https://open.canada.ca/data/organization/mpa-apm)         | Montreal Port Authority                      | Administration portuaire de Montréal          |                            74 |
| [6be4ebb38887612c291d632ff4fa22f3](https://open.canada.ca/en/search/ati/reference/6be4ebb38887612c291d632ff4fa22f3) | 1A-2023-34690    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            63 |
| [6758d5bf059fbc8e16d92d0f1ff61e7c](https://open.canada.ca/en/search/ati/reference/6758d5bf059fbc8e16d92d0f1ff61e7c) | A-2022-52421     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            43 |
| [c02441374acc93c0d335f9e1717cad3c](https://open.canada.ca/en/search/ati/reference/c02441374acc93c0d335f9e1717cad3c) | A-2019-83837     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            43 |
| [43b79c2ade0139300fcd0b7fab0b55b0](https://open.canada.ca/en/search/ati/reference/43b79c2ade0139300fcd0b7fab0b55b0) | A-2024-00020     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            43 |
| [489c43108a10bf94af2650dcaacd6b52](https://open.canada.ca/en/search/ati/reference/489c43108a10bf94af2650dcaacd6b52) | A-2023-00129     | [aafc-aac](https://open.canada.ca/data/organization/aafc-aac)       | Agriculture and Agri-Food Canada             | Agriculture et Agroalimentaire Canada         |                            42 |
| [6669303c723d67af9c252f2b47d086aa](https://open.canada.ca/en/search/ati/reference/6669303c723d67af9c252f2b47d086aa) | A-2020-00482     | [pwgsc-tpsgc](https://open.canada.ca/data/organization/pwgsc-tpsgc) | Public Services and Procurement Canada       | Services publics et Approvisionnement Canada  |                            40 |
| [f4571fd28501329a6055a7ea2a9ccc90](https://open.canada.ca/en/search/ati/reference/f4571fd28501329a6055a7ea2a9ccc90) | A-2023-00777     | [tbs-sct](https://open.canada.ca/data/organization/tbs-sct)         | Treasury Board of Canada Secretariat         | Secrétariat du Conseil du Trésor du Canada    |                            39 |
| [fa4fa7f1c1c19d134f48403036626623](https://open.canada.ca/en/search/ati/reference/fa4fa7f1c1c19d134f48403036626623) | 2A-2021-12699    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            38 |
| [02cf7be366f8c0b149a53cb936c4d8a5](https://open.canada.ca/en/search/ati/reference/02cf7be366f8c0b149a53cb936c4d8a5) | 1A-2022-08633    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            37 |
| [0f876de901a2ebf76c56471a67d05642](https://open.canada.ca/en/search/ati/reference/0f876de901a2ebf76c56471a67d05642) | A-2022-03600     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [f94cf02dc4f1abc369c341e778482ed5](https://open.canada.ca/en/search/ati/reference/f94cf02dc4f1abc369c341e778482ed5) | 1A-2022-06919    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [9674ed871ac388717efa733046a47ed1](https://open.canada.ca/en/search/ati/reference/9674ed871ac388717efa733046a47ed1) | 2A-2023-02896    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            36 |
| [cca1c6a4dcf37611d33962b8a1e1fc43](https://open.canada.ca/en/search/ati/reference/cca1c6a4dcf37611d33962b8a1e1fc43) | A-2019-83845     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            35 |
| [b1d7780013585d893fbed095dac6ac11](https://open.canada.ca/en/search/ati/reference/b1d7780013585d893fbed095dac6ac11) | A-2020-144       | [csis-scrs](https://open.canada.ca/data/organization/csis-scrs)     | Canadian Security Intelligence Service       | Service canadien du renseignement de sécurité |                            34 |
| [9ddddbe17f2825427ec77a010db22511](https://open.canada.ca/en/search/ati/reference/9ddddbe17f2825427ec77a010db22511) | A-2022-44116     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            34 |
| [89090aeab44453c5d382e1af74fac873](https://open.canada.ca/en/search/ati/reference/89090aeab44453c5d382e1af74fac873) | A-2022-01590     | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            34 |
| [91cbf6a82443ac952cb5a57857a340b7](https://open.canada.ca/en/search/ati/reference/91cbf6a82443ac952cb5a57857a340b7) | A-2022-01147     | [ec](https://open.canada.ca/data/organization/ec)                   | Environment and Climate Change Canada        | Environnement et Changement climatique Canada |                            33 |
| [efc8e31eceb9b168153d6aad073740e2](https://open.canada.ca/en/search/ati/reference/efc8e31eceb9b168153d6aad073740e2) | 2A-2021-61194    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            33 |
| [3d7f1c22acde8320b5b8dea9ebe8fdff](https://open.canada.ca/en/search/ati/reference/3d7f1c22acde8320b5b8dea9ebe8fdff) | 1A-2023-07235    | [cic](https://open.canada.ca/data/organization/cic)                 | Immigration, Refugees and Citizenship Canada | Immigration, Réfugiés et Citoyenneté Canada   |                            32 |

