> # **La version française suit**

# **analytics-corporate-reporting**

Analytics and Corporate Reporting for the Open Government Portal

## **About**

This repository contains python scripts developed to generate statics on the user journey on open data and proactive disclosure resources. These statics includes page views and downloads with regional and international dimensions.

## **GA4 Reporting Script**

Google Analytic 4 (GA4) is used to track open Canada portal usage. This script should run once a month to retrieve reports from GA4 using its API. 

**Prerequisite:** Create a new GA4 credential and save the JSON file as credentials.json locally. Then open the file  with an editor and copy the email contained to your GA4 property access management. Here is the link to create :  https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py#create_credentials

**Step 1:** clone this repository or download GA4_reporting_script’s content only. Then add the credential file downloaded previously and two new folders named GA_TMP_DIR and GA_STATIC_DIR in the same folder. 

![
  ](https://github.com/open-data/analytics-corporate-reporting/blob/main/GA4_reporting_script.png)

**Step 2:** Install required packages from requirements.txt file. You could step up a new environment prior for your convenience. 

 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/ga_venv_requirement.png)

**Step 3:** Download daily generated JSON Lines catalogue at the end of  the month from https://open.canada.ca/static/od-do-canada.jsonl.gz  and rename is as follow od-do-canada.YYYYMMDD.jl.gz (i.e: od-do-canada.20231031.jl.gz). Or download the file from this repository at the end of the month.

**Step 4:** Run og_ga4_analytics.py with resource_patch.resources_update() being disabled to avoid uploading unexpected results to registry. It defaults to last month’s records and saves the csv files generated in GA_TMP_DIR and updated archive in GA_STATIC_DIR. Add to country_region.yml file any country that appears on your terminal as highlighted in the picture below with their respective translation. 

 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/new_country.PNG)

Then spot check csv files and rerun with resource_patch.resources_update() once validated. It will upload last month statistics into the registry and should be available on the portal with 15 min at Open Government Analytics - Open Government Portal (canada.ca)

## **Open Map**
We also use GA4 to track the usage of our geospatial data using open map view. 

**Step 1:** clone the main repository or download the content of Open_map folder. Then install prerequisite package in the requirement.txt. 

**Step 2:** run og_ga4_openMap.py with open_map_patch.resources_update() disabled once at the beginning of every month to retrieve last month’s statistic. Then spot check the csv file generated, it should append last month’s usage to historical record available on open government analytics page. Once the result aligns with expected outcome rerun with open_map_patch.resources_update() enabled to replace current statistic with updated csv file. 

## **Proactive disclosure**
Daily jobs run to reflect updates on Proactive disclosure (PD) in the following csv files:

| File | Flat Viewer |
|--|--|
|**structure_pd.csv**  contains daily updates on standardized proactive publication.  | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=Corporate_reporting%2Fpd_count%2Fstructure_pd.csv)|
|**nonstruc_pd.csv** contains daily updates on non-standardized proactive publication.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=Corporate_reporting%2Fpd_count%2Fnonstruc_pd.csv)|
|**all_pd.csv contains** aggregated records by proactive disclosure categories (standardized and non-standardized).|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=Corporate_reporting%2Fpd_count%2Fall_pd.csv)|
|**unpivoted_pd.csv**  contains all PDs update in unpivoted format for analytics purposes.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=Corporate_reporting%2Fpd_count%2Funpivoted_pd.csv)|
|**pd_per_dept.csv** contains PD updates per department.|[![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=Corporate_reporting%2Fpd_count%2Fpd_per_dept.csv)|

**New ATI, contracts, grants, travel and hospitality in last 7 days**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/PD_plot.svg)

## **Open Data**
We also provide in this repository open data and non-geospatial open data created within the current fiscal year and the ratio of openness rating.

**Open data created within the current fiscal year**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/opendata.svg)

# **version française**

## **À propos**

Ce référentiel contient des scripts en python qui ont pour but de produire les statistiques du parcours des visiteurs dans le portail ouvert de Canada. Il contient également les statistiques des divulgations proactives et des données ouvertes produites par les départements.

## **Script de création des rapports depuis GA4**

Google analytiques 4 (GA4) est utilisé pour assurer le suivi du parcours des usagers dans le portail ouvert de Canada. Les scripts dans le répertoire nommé GA4 Reporting Script permettent de récupérer les rapports en utilisant l’API de GA4.

**Prérequis:** Créer un nouveau identifiant de GA4 et l’enregistrer localement en tant que credentials.json. Ensuite ouvrir le fichier avec un éditeur et copier le courriel dans la gestion des accès à la propriété du compte GA4. Voici le lien pour créer l’identifiant : https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py?hl=fr#create_credentials

**Étape 1:** Cloner le référentiel ou télécharger le contenu du répertoire GA4_reporting_script. Puis ajouter l’identifiant télécharger précédemment et deux nouveaux répertoires nommés GA_TMP_DIR and GA_STATIC_DIR dans le même répertoire.  Vous trouvez ci-dessous un aperçu du contenu du répertoire GA4_reporting_script. 
 
![
  ](https://github.com/open-data/analytics-corporate-reporting/blob/main/GA4_reporting_script.png)

**Étape 2:** Installer les progiciels requis depuis le fichier requirements.txt. En revanche, La création d’un nouvel environnement tel qu’illustré dans la figure ci-dessous est à votre discrétion.
 
 
 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/ga_venv_requirement.png)

**Étape 3:** Télécharger à la fin de chaque mois à partir du lien https://open.canada.ca/static/od-do-canada.jsonl.gz  le catalogue en format JSON Lines généré quotidiennement. Ensuite renommé le fichier ainsi  od-do-canada.YYYYMMDD.jl.gz (ex: od-do-canada.20231031.jl.gz). Vous pouvez également télécharger depuis ce référentiel à fin du mois.

**Étape 4:** Exécuter og_ga4_analytics.py en gardant le resource_patch.resources_update() désactivé pour éviter le téléversement des statistiques inattendus au registre. Par défaut, les statistiques du mois dernier seront produits et enregistrés dans le répertoire GA_TMP_DIR. Les archives mis à jour seront quant à eux sauvegardés dans le répertoire GA_STATIC_DIR.  Ajouter dans le fichier country_region.yml tout nouveau pays qui apparait sur le terminal et sa traduction en français. 

 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/new_country.PNG)

Vérifier aléatoirement les fichiers générés et puis relancer l’exécution du og_ga4_analytics.py avec le resource_patch.resources_update() activé une fois validé. Tous les statistiques générés seront reproduits et téléversés automatiquement sur le registre. Ces mis à jour seront disponibles sur le portail public dans une quinzaine de minutes.

## **Carte ouverte**

Nous utilisons également GA4 pour suivre la visualisation de carte ouverte avec nos données géospatiales.

**Étape 1:**  Cloner le référentiel ou télécharger le contenu du répertoire Open_map. Ensuite installer les progiciels requis depuis le fichier requirements.txt.

**Étape 2:** Exécuter og_ga4_openMap.py au début de chaque mois en gardant open_map_patch.resources_update() désactivé. Ensuite vérifier que le contenu du fichier généré inclut l’historique et les statistiques du mois dernier. Si c’est le cas, relancer l’exécution avec open_map_patch.resources_update() activé afin de téléverser le nouveau rapport dans le registre. 

## **Divulgation proactive**

Des tâches s’exécutent quotidiennement pour refléter les mis à jour des divulgations proactives dans les fichiers suivants :
-	**structure_pd.csv**  contient les mis à jour quotidien sur les divulgations proactives normalisées. 
-	**nonstruc_pd.csv** contient les mis à jour quotidien sur les divulgations proactives non normalisées.
-	**all_pd.csv**  contient des enregistrements agrégés par type de divulgation proactive.
-	**unpivoted_pd.csv**  contient toutes les divulgations proactives en format non croisés. 
-	**pd_per_dept.csv** Contient les mis à jour des divulgations proactives par ministères.

**Nouveaux ATI, contrats, subventions, voyages et hospitalité au cours des 7 derniers jours**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/PD_plot.svg)


## **Données ouvertes**
Vous trouvez également dans ce référentiel les données ouvertes créées courant l’année fiscale en cours et le taux de la côte d’ouverture.

**Données ouvertes créées au cours de l’exercice en cours**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/opendata.svg)
