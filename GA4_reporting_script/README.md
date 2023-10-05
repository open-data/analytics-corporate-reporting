# analytics-corporate-reporting
Analytics reporting for the Open Government Portal
Google Analytic GA4 reporting:
install prerequisite from requirements.txt file
creat credential ( https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py#create_credentials)
Add service account to GA (https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py#add_service_account_to_the_google_analytics_account)
download the catalogue compressed json file generated on the last day of the previous month.
Create two directories in the root GA_TMP_DIR and GA_STATIC_DIR and save the catalogue in GA_STATIC_DIR
run the scripts one time per months. Once the update takes effect it abrobts on additional attempt due to file names if you run again.
The script will first download historic records from open government analytic page then retreives last month statistics from GA4. It updates the csv files and then pushes to the registery. 
