## PD Changes Report
[![Generate PD Activity Reports](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_pd_changes.yml/badge.svg)](https://github.com/open-data/analytics-corporate-reporting/actions/workflows/action_pd_changes.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/open-data/analytics-corporate-reporting?path=PD_CHANGES_RPT%2Fpd_changes_data.csv)



This report uses the Git History of `Corporate_reporting/pd_count/pd_per_dept.csv` to show the number of PD Reports submitted by Organizations over the last 30 days and over the last 6 months, for each type.

    .
    ├── ...
    ├── Corporate_reporting                   
    │   ├── pd_count
    │   │   ├── pd_count.py              # Fetches each PD CSV from Open.Canada.ca, appends to frequency tables tracking the numbers over time 
    │   │   ├── links.txt                # List of URLs for the PD CSVs
    │   │   ├── pd_per_dept.csv          # Daily count of number of PDs per dept, per type. Tracked in git
    │   │   └── ...
    │   └── open_data        
    ├── PD_CHANGES_RPT                 
    │   ├── readme.md                   # this file
    │   ├── pd_changes.py               # Use the Git History of `Corporate_reporting/pd_count/pd_per_dept.csv` to generate report on PD growth over time
    │   ├── pd_changes_data.csv         # Shows current number of records, 30 day△, 6 month△ for each type, per department. 
    │   ├── pd_org_data.csv             # Shows information about each dept, including their FAA Schedule as context for the pd_changes_data
    │   ├── PD_Activity.xlsx            # Packages pd_changes_data and pd_org_data into a Excel Workbook for business users
    │   └── ...
    │                 
    └── ...

pd_changes_data.csv - 
 [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=PD_CHANGES_RPT/pd_changes_data.csv ) pd_org_data.csv - 
 [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/open-data/analytics-corporate-reporting?filename=PD_CHANGES_RPT/pd_org_data.csv )
