import Download_Utilities as dt

## Define the year and range of rounds to download from the Ergast API and upload to BigQuery
year = '2019'
round_start = 2
round_end = 2
download_raw_yesno = True
upload_combined_yesno = False
#The next line defines where to find the BigQuery json file for authentication to upload to your BigQuery project
key_path = "credentials/f1modeller_bq_credentials.json"

if download_raw_yesno == True:
    dt.download_round(year, key_path)
    dt.download_constructor(year, round_start, round_end, key_path)
    dt.download_driver(year, round_start, round_end, key_path)
    dt.download_qualifying_laptime(year, round_start, round_end, key_path)
    dt.download_race_laptime(year, round_start, round_end, key_path)
    dt.download_race_pitstop(year, round_start, round_end, key_path)
if upload_combined_yesno == True:
    dt.upload_combined(year, round_start, round_end, key_path)
