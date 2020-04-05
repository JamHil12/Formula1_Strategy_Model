###### Upload_Round.py
# Uploads round data into BigQuery, downloading from the Ergast API

import requests as rq
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os
import datetime

def upload_round(year):
    ## OBTAIN SCHEMA FOR UPLOAD
    key_path = "..." #Insert your BigQuery credentials json file path here
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("raceName", "STRING"),
        bigquery.SchemaField("circuitId", "STRING"),
        bigquery.SchemaField("circuitName", "STRING"),
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("time", "TIME")
    ]

    ## CLEAR THE CSV UPLOADS FOLDER
    mypath = "bigquery_upload"
    for root, dirs, files in os.walk(mypath):
        for file in files:
            os.remove(os.path.join(root, file))

    print('***Attempting year {0}'.format(year))
    ## REMOVE CSV FILE IF IT ALREADY EXISTS
    if os.path.exists('bigquery_upload/rounds_{0}.csv'.format(year)):
        os.remove('bigquery_upload/rounds_{0}.csv'.format(year))
        print('Deleted old file bigquery_upload/rounds_{0}.csv'.format(year))

    ## TRY TO QUERY THE ERGAST API, AND OBTAIN THE JSON RESULTS
    print('Attempting to request Rounds json from Ergast API')
    try:
        response = rq.get('http://ergast.com/api/f1/{0}.json'.format(year))
    except:
        print('Error getting response from Ergast API - Rounds')
        sys.exit()
    print('Successfully obtained responses from Ergast API')
    rounds_dict = response.json()
    print('Successfully converted response into rounds_dict')

    ### CONSTRUCT CLEAN DATAFRAME
    rounds_list = rounds_dict['MRData']['RaceTable']['Races']
    for i in range(len(rounds_list)):
        rounds_list[i]['circuitId'] = rounds_list[i]['Circuit']['circuitId']
        rounds_list[i]['circuitName'] = rounds_list[i]['Circuit']['circuitName']
        del rounds_list[i]['Circuit']
    rounds_df = pd.DataFrame(data = rounds_list)
    rounds_df['year'] = year
    rounds_df['time'] = rounds_df['time'].apply(lambda x: datetime.datetime.strptime(str(x).replace('Z',''), '%H:%M:%S').time())
    rounds_df = rounds_df[['year','round','url','raceName','circuitId','circuitName','date','time']]

    ### SAVE TO CSV FILE
    print('Attempting to save rounds_df into a csv file')
    try:
       with open('bigquery_upload/rounds_{0}.csv'.format(year), 'w',newline='') as csv_file:
           rounds_df.to_csv(csv_file,index=False)
    except:
       print('Error saving to a csv file')
       sys.exit()
    print('Successfully saved into a csv file')

    ### UPLOAD INTO BIGQUERY
    print('Attempting to upload to BigQuery')
    table = dataset.table('Rounds_{0}'.format(year))
    with open('bigquery_upload/rounds_{0}.csv'.format(year), 'rb') as source_file:
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = 'CSV'
        job_config.write_disposition = 'WRITE_TRUNCATE'
        job_config.schema = schema_for_upload
        job_config.skip_leading_rows = 1
        try:
            job = bigquery_client.load_table_from_file(
                source_file, table, job_config=job_config)
        except:
            print('Error uploading to BigQuery:',sys.exc_info()[0])
            sys.exit()

    print('***Successfully completed upload of year {0}'.format(year))