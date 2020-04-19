import Download_Utilities as dt

## Define the year and range of rounds to download from the Ergast API and upload to BigQuery
year = '2019'
round_start = 9
round_end = 9
download_raw_yesno = 'yes' #Either 'yes' or 'no'.
upload_combined_yesno = 'yes' #Either 'yes' or 'no'. To combine, you need to upload tyre stint data manually beforehand.
#The next line defines where to find the BigQuery json file for authentication to upload to your BigQuery project
key_path = "credentials/f1modeller_bq_credentials.json"

if download_raw_yesno == 'yes':
    dt.download_round(year, key_path)
    dt.download_constructor(year, round_start, round_end, key_path)
    dt.download_driver(year, round_start, round_end, key_path)
    dt.download_qualifying_laptime(year, round_start, round_end, key_path)
    dt.download_race_laptime(year, round_start, round_end, key_path)
    dt.download_race_pitstop(year, round_start, round_end, key_path)
if upload_combined_yesno == 'yes':
    dt.upload_combined(year, round_start, round_end, key_path)
