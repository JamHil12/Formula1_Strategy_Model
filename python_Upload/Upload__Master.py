import Upload_Constructor as uc
import Upload_Driver as ud
import Upload_Qualifying_Laptime as uql
import Upload_Race_Laptime as url
import Upload_Race_Pitstop as urp
import Upload_Round as ur
import Upload_Combined as ucom
import sys

## DEFINE THE YEAR AND THE RANGE OF ROUND NUMBERS TO UPLOAD
year = '2019'
round_start = 15
round_end = 21
upload_raw_yesno = 'yes' #Either 'yes' or 'no'. This controls whether all the raw data from the Ergast API is collected.
upload_combined_yesno = 'no' #Either 'yes' or 'no'. This controls whether the raw data is combined with manually collected tyre stint data. If selecting 'yes', you need to have already manually uploaded tyre stint data into BigQuery, e.g. by reading off the following Pirelli link, storing in Excel and exporting into BigQuery. https://racingspot.pirelli.com/global/en-ww/gp-hungary

## CHECK THE RANGE IS VALID
if round_start > round_end:
    print('Invalid round range: round_end should be at least as large as round_start')
    sys.exit()
elif round_start < 1:
    print('Invalid round range: round_start should be at least 1')
    sys.exit()

## RUN THE UPLOADS
if upload_raw_yesno == 'yes':
    uc.upload_constructor(year,round_start,round_end)
    ud.upload_driver(year,round_start,round_end)
    uql.upload_qualifying_laptime(year,round_start,round_end)
    url.upload_race_laptime(year,round_start,round_end)
    urp.upload_race_pitstop(year,round_start,round_end)
    ur.upload_round(year)
if upload_combined_yesno == 'yes':
    ucom.upload_combined(year, round_start, round_end)

