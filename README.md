# **analytics-corporate-reporting**

Analytics and Corporate Reporting for the Open Government Portal

## **About**

This repository contains python scripts developed to generate statics on the user journey on open data and proactive disclosure resources. These statics includes page views and downloads with regional and international dimensions.

## **GA4 Reporting Script**

Google Analytic 4 (GA4) is used to track open Canada portal usage. This script should run once a month to retrieve reports from GA4 using its API. 

**Prerequisite:**

Create a new GA4 credential and save the JSON file as credentials.json locally. Then open the file  with an editor and copy the email contained to your GA4 property access management. Here is the link to create :  https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py#create_credentials

**Step 1:** clone this repository or download GA4_reporting_script’s content only. Then add the credential file downloaded previously and two new folders named GA_TMP_DIR and GA_STATIC_DIR in the same folder. 
![
  ](https://github.com/open-data/analytics-corporate-reporting/blob/main/GA4_reporting_script.png)

**Step 2:** Install required packages from requirements.txt file. You could step up a new environment prior for your convenience. 

 ![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/ga_venv_requirement.png)

**Step 3:** Download daily generated JSON Lines catalogue at the end of  the month from https://open.canada.ca/static/od-do-canada.jsonl.gz  and rename is as follow od-do-canada.YYYYMMDD.jl.gz (i.e: od-do-canada.20231031.jl.gz)

**Step 4:** Run og_ga4_analytics.py with resource_patch.resources_update() being disabled to avoid uploading unexpected results to registry. It defaults to last month’s records and saves the csv files generated in GA_TMP_DIR and updated archive in GA_STATIC_DIR. Spot check csv files and rerun with resource_patch.resources_update() once validated. It will upload last month statistics into the registry and should be available on the portal with 15 min at Open Government Analytics - Open Government Portal (canada.ca)

## **Open Map**
We also use GA4 to track the usage of our geospatial data using open map view. 

**Step 1:** clone the main repository or download the content of Open_map folder. Then install prerequisite package in the requirement.txt. 

**Step 2:** run og_ga4_openMap.py once at the beginning of every month to retrieve last month’s statistic. Then spot check the csv file generated, it should append last month’s usage to historical record available on open government analytics page. Once the result aligns with expected outcome run open_map_patch.py to replace statistic with update csv file. 

## **Proactive disclosure visualization**

![
](https://github.com/open-data/analytics-corporate-reporting/blob/main/plot.svg=900x700)
