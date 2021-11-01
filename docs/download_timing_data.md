Use the Download_Master.py file in the [src](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/src) folder to download historical F1 timing data from the [Ergast API](http://ergast.com/mrd/), and upload it to your BigQuery project.

## Instructions
1. Follow and complete all the 'Getting Started' instructions in the main project README file.
2. Follow the instructions in the data_lookups.md documentation file in the [doc](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/docs) folder, updating the lookups relevant to the race of interest and uploading them to your BigQuery project.
3. Open the file *download__master.py* in the [src](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/src) folder. Edit the input parameters to choose a year and a range of round numbers to download. Running the code will download all the requested data from the Ergast API, save the results as csv files in the *bigquery_upload* folder, and then upload the datasets into BigQuery.

## BigQuery tables created by *Download__Master.py*
In all of the entries in the table below, {YYYYRR} represents the 4-digit year and 2-digit round number of the race, whilst {YYYY} represents the 4-digit year of the round.
| Dataset Name | Table Name | Description | Created when... |
| ------------ | ----------- | ----------- | ----------- |
| F1_Modelling_Raw  | Constructors_{YYYYRR} | Constructors participating in the race | *download_raw_yesno* = 'yes' |
| F1_Modelling_Raw  | Drivers_{YYYYRR} | Drivers participating in the race | *download_raw_yesno* = 'yes' |
| F1_Modelling_Raw  | Qualifying_Laptimes_{YYYYRR} | Times in Q1, Q2 and Q3 for each driver | *download_raw_yesno* = 'yes' |
| F1_Modelling_Raw  | Race_Laptimes_{YYYYRR} | Lap by lap timing of each driver in the race | *download_raw_yesno* = 'yes' |
| F1_Modelling_Raw  | Race_Pitstops_{YYYYRR} | Lap numbers of pitstops, and how long they took | *download_raw_yesno* = 'yes' |
| F1_Modelling_Raw  | Rounds_{YYYY} | Details of all the races (i.e. *rounds*) in the year | *download_raw_yesno* = 'yes' |
| F1_Modelling_Combined  | Combined_{YYYYRR} | Combines all of the above datasets with the manual lookups, that must be uploaded from the *data/manual_lookups* folder into BigQuery before running this. Adds in extra data fields on tyre stints, tyre compounds, and circuit characteristics. This dataset becomes really useful when it comes to the fitting of tyre deg curves on historical data. | *upload_combined_yesno* = 'yes' |
