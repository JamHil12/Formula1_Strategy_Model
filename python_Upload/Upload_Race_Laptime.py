###### Upload_Race_Laptime.py
# Uploads race laptime data into BigQuery, downloading from the Ergast API

import requests as rq
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os

def upload_race_laptime(year,round_start,round_end):
    round_num = round_start

    ## OBTAIN SCHEMA FOR UPLOAD
    key_path = "..." #Insert your BigQuery credentials json file path here
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("lap", "INTEGER"),
        bigquery.SchemaField("driverId", "STRING"),
        bigquery.SchemaField("position", "INTEGER"),
        bigquery.SchemaField("time", "FLOAT")
    ]

    ## DEFINE A USEFUL FUNCTION TO CONVERT THE LAP TIMES TO SECONDS
    def get_sec(time_str):
        """Get Seconds from time."""
        m, s = time_str.split(':')
        return int(m) * 60 + float(s)

    ## CLEAR THE CSV UPLOADS FOLDER
    mypath = "bigquery_upload"
    for root, dirs, files in os.walk(mypath):
        for file in files:
            os.remove(os.path.join(root, file))

    while round_num <= round_end:
        print('***Attempting year {0}, round number {1}'.format(year, round_num))
        ## REMOVE CSV FILE IF IT ALREADY EXISTS
        if len(str(round_num)) == 1:
            round_num_csv_suffix = '0' + str(round_num)
        else:
            round_num_csv_suffix = str(round_num)
        if os.path.exists('bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix)):
            os.remove('bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix))
            print('Deleted old file bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix))
        ## TRY TO QUERY THE ERGAST API, AND OBTAIN THE JSON RESULTS
        lap = 1
        ## NEED TO FIND THE NUMBER OF LAPS IN THE RACE AND ASSIGN TO lap_max
        print('Attempting to request Results json from Ergast API')
        try:
            response_results = rq.get('http://ergast.com/api/f1/{0}/{1}/results.json'.format(year,round_num))
        except:
            print('Error getting response from Ergast API - Results')
            sys.exit()
        print('Successfully obtained Results from Ergast API')
        lap_max = int(response_results.json()['MRData']['RaceTable']['Races'][0]['Results'][0]['laps'])

        ## GET THE LAPTIMES
        while lap <= lap_max:
            print('Round {0}, lap number {1}: Attempting to request Laps json from Ergast API'.format(round_num,lap))
            try:
                response = rq.get('http://ergast.com/api/f1/{0}/{1}/laps/{2}.json'.format(year,round_num,lap))
            except:
                print('Round {0}, lap number {1}: Error getting response from Ergast API - Laps'.format(round_num,lap))
                sys.exit()
            print('Round {0}, lap number {1}: Successfully obtained responses from Ergast API'.format(round_num,lap))
            laptimes_dict = response.json()
            print('Round {0}, lap number {1}: Successfully converted response into laptimes_dict'.format(round_num,lap))

            ### CONSTRUCT CLEAN DATAFRAME
            laptimes_df = pd.DataFrame(data = laptimes_dict['MRData']['RaceTable']['Races'][0]['Laps'][0]['Timings'])
            laptimes_df['year'] = year
            laptimes_df['round'] = round_num
            laptimes_df['lap'] = lap
            laptimes_df = laptimes_df[['year','round','lap','driverId','position','time']]
            laptimes_df['time'] = laptimes_df['time'].apply(lambda x: get_sec(x))

            ### SAVE TO CSV FILE
            print('Round {0}, lap number {1}: Attempting to save laptimes_df into a csv file'.format(round_num,lap))
            if lap == 1:
                try:
                   with open('bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix), 'w',newline='') as csv_file:
                       laptimes_df.to_csv(csv_file,index=False)
                except:
                   print('Round {0}, lap number {1}: Error saving to a csv file'.format(round_num,lap))
                   sys.exit()
            else:
                try:
                   with open('bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix), 'a+',newline='') as csv_file:
                       laptimes_df.to_csv(csv_file,index=False,header=False)
                except:
                   print('Round {0}, lap number {1}: Error saving to a csv file'.format(round_num,lap))
                   sys.exit()
            print('Round {0}, lap number {1}: Successfully saved into a csv file'.format(round_num,lap))

            lap += 1

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload round {0} to BigQuery'.format(round_num))
        table = dataset.table('Race_Laptimes_{0}{1}'.format(year,round_num_csv_suffix))
        with open('bigquery_upload/laptimes_{0}{1}.csv'.format(year,round_num_csv_suffix), 'rb') as source_file:
            job_config = bigquery.LoadJobConfig()
            job_config.source_format = 'CSV'
            job_config.write_disposition = 'WRITE_TRUNCATE'
            job_config.schema = schema_for_upload
            job_config.skip_leading_rows = 1
            try:
                job = bigquery_client.load_table_from_file(
                    source_file, table, job_config=job_config)
            except:
                print('Error uploading round {0}:'.format(round_num),sys.exc_info()[0])
                sys.exit()

        ### MOVE ONTO THE NEXT ROUND
        print('***Successfully completed upload of year {0}, round {1}'.format(year,round_num))
        round_num += 1