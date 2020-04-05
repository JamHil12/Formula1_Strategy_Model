###### Upload_Constructor.py
# Uploads constructor data into BigQuery, downloading from the Ergast API

import requests as rq
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os

def upload_constructor(year,round_start,round_end):
    round_num = round_start

    ## OBTAIN SCHEMA FOR UPLOAD
    key_path = "..." #Insert your BigQuery credentials json file path here
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("constructorId", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("nationality", "STRING")
    ]

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
        if os.path.exists('bigquery_upload/constructors_{0}{1}.csv'.format(year,round_num_csv_suffix)):
            os.remove('bigquery_upload/constructors_{0}{1}.csv'.format(year,round_num_csv_suffix))
            print('Deleted old file bigquery_upload/constructors_{0}{1}.csv'.format(year,round_num_csv_suffix))

        ## TRY TO QUERY THE ERGAST API, AND OBTAIN THE JSON RESULTS
        print('Round {0}: Attempting to request Constructors json from Ergast API'.format(round_num))
        try:
            response = rq.get('http://ergast.com/api/f1/{0}/{1}/constructors.json'.format(year,round_num))
        except:
            print('Round {0}: Error getting response from Ergast API - Constructors'.format(round_num))
            sys.exit()
        print('Round {0}: Successfully obtained responses from Ergast API'.format(round_num))
        constructors_dict = response.json()
        print('Round {0}: Successfully converted response into constructors_dict'.format(round_num))

        ### CONSTRUCT CLEAN DATAFRAME
        constructors_df = pd.DataFrame(data = constructors_dict['MRData']['ConstructorTable']['Constructors'])
        constructors_df['year'] = year
        constructors_df['round'] = round_num
        constructors_df = constructors_df[['year','round','constructorId','url','name','nationality']]

        ### SAVE TO CSV FILE
        print('Round {0}: Attempting to save constructors_df into a csv file'.format(round_num))
        try:
           with open('bigquery_upload/constructors_{0}{1}.csv'.format(year,round_num_csv_suffix), 'w',newline='') as csv_file:
               constructors_df.to_csv(csv_file,index=False)
        except:
           print('Round {0}: Error saving to a csv file'.format(round_num))
           sys.exit()
        print('Round {0}: Successfully saved into a csv file'.format(round_num))

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload round {0} to BigQuery'.format(round_num))
        table = dataset.table('Constructors_{0}{1}'.format(year,round_num_csv_suffix))
        with open('bigquery_upload/constructors_{0}{1}.csv'.format(year,round_num_csv_suffix), 'rb') as source_file:
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