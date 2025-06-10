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

Ce référentiel regroupe des scripts Python conçus pour générer des statistiques sur le parcours des visiteurs du Portail ouvert du Canada. Il inclut également des analyses statistiques relatives aux divulgations proactives ainsi qu’aux ensembles de données ouvertes publiés par les institutions.

## **Script de création des rapports depuis GA4**

Google Analytics 4 (GA4) est utilisé pour suivre le parcours des utilisateurs sur le Portail ouvert du Canada. Les scripts dans le répertoire intitulé GA4 Reporting Script permettent d’extraire des rapports à l’aide de l’API GA4.

**Prérequis:** Créer un nouvel identifiant pour GA4, puis l’enregistrer localement sous le nom credentials.json. Ensuite, ouvrez ce fichier avec un éditeur de texte et copiez l’adresse courriel qui y figure. Ajoutez cette adresse dans la section Gestion des accès de la propriété GA4 afin de lui accorder les autorisations nécessaires. Voici le lien pour créer l’identifiant : https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py?hl=fr#create_credentials

**Étape 1:** Cloner le référentiel ou télécharger le contenu du répertoire GA4_reporting_script. Ensuite, ajoutez le fichier d’identifiants téléchargé précédemment (credentials.json) et créez deux nouveaux répertoires nommés GA_TMP_DIR et GA_STATIC_DIR dans le même répertoire.
Vous trouverez ci-dessous un aperçu du contenu du répertoire GA4_reporting_script.
 
![
  ](https://github.com/open-data/analytics-corporate-reporting/blob/main/GA4_reporting_script.png)

**Étape 2:** Installez les dépendances nécessaires à partir du fichier requirements.txt. La création d’un environnement virtuel, comme illustré dans la figure ci-dessous, reste à votre discrétion.
 
 
 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/ga_venv_requirement.png)

**Étape 3:** À la fin de chaque mois, téléchargez le catalogue au format JSON Lines, généré quotidiennement, à partir du lien suivant : https://open.canada.ca/static/od-do-canada.jsonl.gz. Renommez ensuite le fichier selon le format suivant : od-do-canada.YYYYMMDD.jl.gz (exemple : od-do-canada.20231031.jl.gz). Il est également possible de télécharger ce fichier directement depuis ce référentiel à la fin de chaque mois.

**Étape 4:**Exécutez le script og_ga4_analytics.py en veillant à ce que la fonction resource_patch.resources_update() reste désactivée, afin d’éviter tout téléversement inattendu de statistiques vers le registre. Par défaut, les statistiques du mois précédent seront générées et enregistrées dans le répertoire GA_TMP_DIR. Les archives mises à jour seront quant à elles sauvegardées dans le répertoire GA_STATIC_DIR. Ajoutez dans le fichier country_region.yml tout nouveau pays apparaissant dans le terminal, ainsi que sa traduction en français.

 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/new_country.PNG)

Procédez à une vérification aléatoire des fichiers générés. Une fois la validation effectuée, relancez l’exécution du script og_ga4_analytics.py avec la fonction resource_patch.resources_update() activée. Toutes les statistiques seront alors régénérées et automatiquement téléversées sur le registre. Ces mises à jour seront visibles sur le portail public dans un délai d’environ quinze minutes.

## **Carte ouverte**

Nous utilisons également Google Analytics 4 (GA4) pour suivre la consultation des cartes interactives intégrant nos données géospatiales.

**Étape 1:**  Cloner le référentiel ou télécharger le contenu du répertoire Open_map. Ensuite, installez les dépendances requises à partir du fichier requirements.txt.

**Étape 2:** Exécutez le script og_ga4_openMap.py au début de chaque mois, en veillant à ce que la fonction open_map_patch.resources_update() soit désactivée. Vérifiez ensuite que le fichier généré contient bien l’historique ainsi que les statistiques du mois précédent. Si le contenu est conforme, relancez l’exécution du script avec open_map_patch.resources_update() activée, afin de téléverser le nouveau rapport dans le registre.

## **Divulgation proactive**

Des tâches s’exécutent quotidiennement afin de refléter les mises à jour des divulgations proactives dans les fichiers suivants :
-	**structure_pd.csv**  contient les mises à jour quotidiennes sur les divulgations proactives normalisées. 
-	**nonstruc_pd.csv** contient les mises à jour quotidiennes sur les divulgations proactives non normalisées.
-	**all_pd.csv**  contient des enregistrements agrégés par type de divulgation proactive.
-	**unpivoted_pd.csv**  contient toutes les divulgations proactives en format non croisés. 
-	**pd_per_dept.csv** Contient les mises à jour des divulgations proactives par ministères.

**Nouveaux ATI, contrats, subventions, voyages et hospitalité au cours des 7 derniers jours**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/PD_plot.svg)


## **Données ouvertes**
Ce référentiel contient également les ensembles de données ouvertes créés au cours de l’année fiscale en cours, ainsi que le taux de la cote d’ouverture.

**Données ouvertes créées au cours de l’exercice financier en cours**
![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/opendata.svg)
