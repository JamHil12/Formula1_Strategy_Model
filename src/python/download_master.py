import download_utilities as dt

# Start of user inputs
year = '2019'
round_start = 2
round_end = 2
download_raw_yesno = True
upload_combined_yesno = False
key_path = 'credentials/f1modeller_bq_credentials.json'
# End of user inputs

if download_raw_yesno:
    dt.download_round(year, key_path)
    dt.download_constructor(year, round_start, round_end, key_path)
    dt.download_driver(year, round_start, round_end, key_path)
    dt.download_qualifying_laptime(year, round_start, round_end, key_path)
    dt.download_race_laptime(year, round_start, round_end, key_path)
    dt.download_race_pitstop(year, round_start, round_end, key_path)
if upload_combined_yesno:
    dt.upload_combined(year, round_start, round_end, key_path)
