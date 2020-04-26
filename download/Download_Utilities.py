###### Download_Utilities.py

import requests as rq
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os
import datetime

def download_round(year, key_path):
    ## OBTAIN SCHEMA FOR UPLOAD
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




def download_race_pitstop(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("driverId", "STRING"),
        bigquery.SchemaField("stop", "INTEGER"),
        bigquery.SchemaField("lap", "INTEGER"),
        bigquery.SchemaField("time", "TIME"),
        bigquery.SchemaField("duration", "FLOAT")
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
        if os.path.exists('bigquery_upload/pitstops_{0}{1}.csv'.format(year,round_num_csv_suffix)):
            os.remove('bigquery_upload/pitstops_{0}{1}.csv'.format(year,round_num_csv_suffix))
            print('Deleted old file bigquery_upload/pitstops_{0}{1}.csv'.format(year,round_num_csv_suffix))

        ## TRY TO QUERY THE ERGAST API, AND OBTAIN THE JSON RESULTS
        print('Round {0}: Attempting to request Pitstops json from Ergast API'.format(round_num))
        try:
            response = rq.get('http://ergast.com/api/f1/{0}/{1}/pitstops.json'.format(year,round_num))
        except:
            print('Round {0}: Error getting response from Ergast API - Pitstops'.format(round_num))
            sys.exit()
        print('Round {0}: Successfully obtained responses from Ergast API'.format(round_num))
        pitstops_dict = response.json()
        print('Round {0}: Successfully converted response into pitstops_dict'.format(round_num))

        ### CONSTRUCT CLEAN DATAFRAME
        pitstops_df = pd.DataFrame(data = pitstops_dict['MRData']['RaceTable']['Races'][0]['PitStops'])
        pitstops_df['year'] = year
        pitstops_df['round'] = round_num
        pitstops_df = pitstops_df[['year','round','driverId','stop','lap','time','duration']]

        ### SAVE TO CSV FILE
        print('Round {0}: Attempting to save pitstops_df into a csv file'.format(round_num))
        try:
           with open('bigquery_upload/pitstops_{0}{1}.csv'.format(year,round_num_csv_suffix), 'w',newline='') as csv_file:
               pitstops_df.to_csv(csv_file,index=False)
        except:
           print('Round {0}: Error saving to a csv file'.format(round_num))
           sys.exit()
        print('Round {0}: Successfully saved into a csv file'.format(round_num))

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload round {0} to BigQuery'.format(round_num))
        table = dataset.table('Race_Pitstops_{0}{1}'.format(year,round_num_csv_suffix))
        with open('bigquery_upload/pitstops_{0}{1}.csv'.format(year,round_num_csv_suffix), 'rb') as source_file:
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




def download_race_laptime(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
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




def download_qualifying_laptime(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("driverId", "STRING"),
        bigquery.SchemaField("position", "INTEGER"),
        bigquery.SchemaField("Q1", "FLOAT"),
        bigquery.SchemaField("Q2", "FLOAT"),
        bigquery.SchemaField("Q3", "FLOAT")
    ]

    ## DEFINE A USEFUL FUNCTION TO CONVERT THE LAP TIMES TO SECONDS
    def get_sec(time_str):
        """Get Seconds from time."""
        try:
            m, s = time_str.split(':')
            return int(m) * 60 + float(s)
        except:
            return None

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
        if os.path.exists('bigquery_upload/qualifying_times_{0}{1}.csv'.format(year,round_num_csv_suffix)):
            os.remove('bigquery_upload/qualifying_times_{0}{1}.csv'.format(year,round_num_csv_suffix))
            print('Deleted old file bigquery_upload/qualifying_times_{0}{1}.csv'.format(year,round_num_csv_suffix))

        ## TRY TO QUERY THE ERGAST API, AND OBTAIN THE JSON RESULTS
        print('Round {0}: Attempting to request Qualifying json from Ergast API'.format(round_num))
        try:
            response = rq.get('http://ergast.com/api/f1/{0}/{1}/qualifying.json'.format(year,round_num))
        except:
            print('Round {0}: Error getting response from Ergast API - Qualifying'.format(round_num))
            sys.exit()
        print('Round {0}: Successfully obtained responses from Ergast API'.format(round_num))
        qualifying_dict = response.json()
        print('Round {0}: Successfully converted response into qualifying_dict'.format(round_num))

        ### CONSTRUCT CLEAN DATAFRAME
        qualifying_list = qualifying_dict['MRData']['RaceTable']['Races'][0]['QualifyingResults']
        for i in range(len(qualifying_list)):
            qualifying_list[i]['driverId'] = qualifying_list[i]['Driver']['driverId']
            del qualifying_list[i]['Driver']
            del qualifying_list[i]['Constructor']
        qualifying_df = pd.DataFrame(data=qualifying_list)
        qualifying_df['year'] = year
        qualifying_df['round'] = round_num
        qualifying_df['Q1'] = qualifying_df['Q1'].where((pd.notnull(qualifying_df['Q1'])), None)
        qualifying_df['Q2'] = qualifying_df['Q2'].where((pd.notnull(qualifying_df['Q2'])), None)
        qualifying_df['Q3'] = qualifying_df['Q3'].where((pd.notnull(qualifying_df['Q3'])), None)
        qualifying_df['Q1'] = qualifying_df['Q1'].apply(lambda x: get_sec(x))
        qualifying_df['Q2'] = qualifying_df['Q2'].apply(lambda x: get_sec(x))
        qualifying_df['Q3'] = qualifying_df['Q3'].apply(lambda x: get_sec(x))
        qualifying_df = qualifying_df[['year','round','driverId','position','Q1','Q2','Q3']]

        ### SAVE TO CSV FILE
        print('Round {0}: Attempting to save qualifying_df into a csv file'.format(round_num))
        try:
           with open('bigquery_upload/qualifying_times_{0}{1}.csv'.format(year,round_num_csv_suffix), 'w',newline='') as csv_file:
               qualifying_df.to_csv(csv_file,index=False)
        except:
           print('Round {0}: Error saving to a csv file'.format(round_num))
           sys.exit()
        print('Round {0}: Successfully saved into a csv file'.format(round_num))

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload round {0} to BigQuery'.format(round_num))
        table = dataset.table('Qualifying_Laptimes_{0}{1}'.format(year,round_num_csv_suffix))
        with open('bigquery_upload/qualifying_times_{0}{1}.csv'.format(year,round_num_csv_suffix), 'rb') as source_file:
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




def download_driver(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Raw')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("driverId", "STRING"),
        bigquery.SchemaField("constructorId", "STRING"),
        bigquery.SchemaField("permanentNumber", "INTEGER"),
        bigquery.SchemaField("code", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("givenName", "STRING"),
        bigquery.SchemaField("familyName", "STRING"),
        bigquery.SchemaField("dateOfBirth", "DATE"),
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
        if os.path.exists('bigquery_upload/drivers_{0}{1}.csv'.format(year,round_num_csv_suffix)):
            os.remove('bigquery_upload/drivers_{0}{1}.csv'.format(year,round_num_csv_suffix))
            print('Deleted old file bigquery_upload/drivers_{0}{1}.csv'.format(year,round_num_csv_suffix))

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

        constructors_df = pd.DataFrame(data=constructors_dict['MRData']['ConstructorTable']['Constructors'])
        ctr_counter = 1

        for ctr in constructors_df['constructorId']:
            print('Round {0}, constructor {1}: Attempting to request Drivers json from Ergast API'.format(round_num,ctr))
            try:
                response = rq.get('http://ergast.com/api/f1/{0}/{1}/constructors/{2}/drivers.json'.format(year,round_num,ctr))
            except:
                print('Round {0}, constructor {1}: Error getting response from Ergast API - Drivers'.format(round_num,ctr))
                sys.exit()
            print('Round {0}, constructor {1}: Successfully obtained responses from Ergast API'.format(round_num,ctr))
            drivers_dict = response.json()
            print('Round {0}, constructor {1}: Successfully converted response into drivers_dict'.format(round_num,ctr))

            ### CONSTRUCT CLEAN DATAFRAME
            drivers_df = pd.DataFrame(data = drivers_dict['MRData']['DriverTable']['Drivers'])
            drivers_df['year'] = year
            drivers_df['round'] = round_num
            drivers_df['constructorId'] = ctr
            drivers_df = drivers_df[['year','round','driverId','constructorId','permanentNumber','code','url','givenName',
                                     'familyName','dateOfBirth','nationality']]

            ### SAVE TO CSV FILE
            print('Round {0}, constructor {1}: Attempting to save drivers_df into a csv file'.format(round_num,ctr))
            if ctr_counter == 1:
                try:
                    with open('bigquery_upload/drivers_{0}{1}.csv'.format(year, round_num_csv_suffix), 'w',
                              newline='') as csv_file:
                        drivers_df.to_csv(csv_file, index=False)
                except:
                    print('Round {0}, constructor {1}: Error saving to a csv file'.format(round_num, ctr))
                    sys.exit()
            else:
                try:
                   with open('bigquery_upload/drivers_{0}{1}.csv'.format(year,round_num_csv_suffix), 'a+',newline='') as csv_file:
                       drivers_df.to_csv(csv_file,index=False,header=False)
                except:
                   print('Round {0}, constructor {1}: Error saving to a csv file'.format(round_num,ctr))
                   sys.exit()
            print('Round {0}, constructor {1}: Successfully saved into a csv file'.format(round_num,ctr))

            ctr_counter += 1

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload round {0} to BigQuery'.format(round_num))
        table = dataset.table('Drivers_{0}{1}'.format(year,round_num_csv_suffix))
        with open('bigquery_upload/drivers_{0}{1}.csv'.format(year,round_num_csv_suffix), 'rb') as source_file:
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




def download_constructor(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
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




def upload_combined(year, round_start, round_end, key_path):
    round_num = round_start
    ## OBTAIN SCHEMA FOR UPLOAD
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    dataset = bigquery_client.dataset('F1_Modelling_Combined')
    schema_for_upload = [
        bigquery.SchemaField("year", "INTEGER"),
        bigquery.SchemaField("round", "INTEGER"),
        bigquery.SchemaField("raceName", "STRING"),
        bigquery.SchemaField("circuitName", "STRING"),
        bigquery.SchemaField("driver_name", "STRING"),
        bigquery.SchemaField("constructor_name", "STRING"),
        bigquery.SchemaField("best_qual_time", "FLOAT"),
        bigquery.SchemaField("best_qual_time_adjusted", "FLOAT"),
        bigquery.SchemaField("best_qual_time_adjusted_flag", "INTEGER"),
        bigquery.SchemaField("lap_number", "INTEGER"),
        bigquery.SchemaField("perc_race_completed", "FLOAT"),
        bigquery.SchemaField("race_position", "INTEGER"),
        bigquery.SchemaField("lap_time", "FLOAT"),
        bigquery.SchemaField("pitstop_number_inlap", "FLOAT"),
        bigquery.SchemaField("pitstop_number_outlap", "FLOAT"),
        bigquery.SchemaField("circuit_tyre_stress_rating", "INTEGER"),
        bigquery.SchemaField("circuit_asphalt_abrasion_rating", "INTEGER"),
        bigquery.SchemaField("circuit_asphalt_grip_rating", "INTEGER"),
        bigquery.SchemaField("circuit_downforce_rating", "INTEGER"),
        bigquery.SchemaField("circuit_lateral_rating", "INTEGER"),
        bigquery.SchemaField("tyre_stint_number", "INTEGER"),
        bigquery.SchemaField("tyre", "STRING"),
        bigquery.SchemaField("tyre_description", "STRING"),
        bigquery.SchemaField("tyre_status", "STRING"),
        bigquery.SchemaField("tyre_age_laps", "INTEGER"),
        bigquery.SchemaField("upload_timestamp", "TIMESTAMP")
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
        if os.path.exists('bigquery_upload/drivers_{0}{1}.csv'.format(year, round_num_csv_suffix)):
            os.remove('bigquery_upload/drivers_{0}{1}.csv'.format(year, round_num_csv_suffix))
            print('Deleted old file bigquery_upload/drivers_{0}{1}.csv'.format(year, round_num_csv_suffix))

        ## RETRIEVE DATASET FROM BIGQUERY
        print('Attempting to retrieve lap time data from BigQuery')
        credentials = service_account.Credentials.from_service_account_file(key_path)
        bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)

        query_job = bigquery_client.query("""
            WITH qual_time_raw_1 as (
 SELECT
 year,
 round,
 driverId,
 CASE
 WHEN ((q2 IS NULL AND q3 IS NULL) OR (q3 IS NULL AND q1 < q2) OR (q1 < q2 AND q1 < q3)) THEN q1
 WHEN (q2 IS NOT NULL AND (q3 IS NULL OR q2 < q3)) THEN q2
 ELSE q3
 END as best_qual_time

 FROM (
  SELECT year, round, driverId, MIN(Q1) as q1, MIN(Q2) as q2, MIN(Q3) as q3

  FROM `F1_Modelling_Raw.Qualifying_Laptimes_*`

  WHERE
  year = {0}

  GROUP BY 1,2,3
 )
),

qual_time_raw_2 as (
 SELECT
 qt1.year,
 qt1.round,
 qt1.driverId,
 qt1.best_qual_time,
 rb.round_best_qual_time,
 qt1.best_qual_time/rb.round_best_qual_time as qual_ratio

 FROM qual_time_raw_1 qt1
 JOIN (
  SELECT year, round, MIN(best_qual_time) as round_best_qual_time
  FROM qual_time_raw_1
  GROUP BY 1,2
 ) rb
   ON qt1.year = rb.year
   AND qt1.round = rb.round
),

qual_time_raw_3 as (
 SELECT DISTINCT
 year,
 driverId,
 PERCENTILE_CONT(qual_ratio, 0.5) OVER(PARTITION BY year, driverId) AS median_qual_ratio

 FROM qual_time_raw_2
),

qual_time as (
 SELECT
 qt2.year,
 qt2.round,
 qt2.driverId,
 qt2.best_qual_time,
 qt3.median_qual_ratio,
 CASE
 WHEN qt2.best_qual_time IS NULL THEN qt2.round_best_qual_time * qt3.median_qual_ratio
 ELSE qt2.best_qual_time
 END as best_qual_time_adjusted,
 CASE WHEN qt2.best_qual_time IS NULL THEN 1 ELSE 0 END as best_qual_time_adjusted_flag

 FROM qual_time_raw_2 qt2
 JOIN qual_time_raw_3 qt3
   ON qt2.year = qt3.year
   AND qt2.driverId = qt3.driverId

 WHERE
 qt2.year = {0}
 AND qt2.round = {1}
),

total_laps as (
 SELECT year, round, MAX(lap) as race_total_laps

 FROM `F1_Modelling_Raw.Race_Laptimes_*`

 WHERE
 year = {0}
 AND round = {1}

 GROUP BY 1,2
)

SELECT
            l.year,
            l.round,
            r.raceName,
            r.circuitName,
            CONCAT(d.givenName,' ',d.familyName) as driver_name,
            c.name as constructor_name,
            qt.best_qual_time,
            qt.best_qual_time_adjusted,
            qt.best_qual_time_adjusted_flag,
            l.lap as lap_number,
            CAST(l.lap as float64) / tl.race_total_laps as perc_race_completed,
            l.position as race_position,
            l.time as lap_time,
            rp.stop as pitstop_number_inlap,
            rp2.stop as pitstop_number_outlap,
            cr.tyre_stress as circuit_tyre_stress_rating,
            cr.asphalt_abrasion as circuit_asphalt_abrasion_rating,
            cr.asphalt_grip as circuit_asphalt_grip_rating,
            cr.downforce as circuit_downforce_rating,
            cr.lateral as circuit_lateral_rating,
            t.stint as tyre_stint_number,
            t.tyre,
            t.tyre_description,
            t.tyre_status,
            (l.lap - t.from_lap) as tyre_age_laps,
            CURRENT_TIMESTAMP() as upload_timestamp

            FROM `F1_Modelling_Raw.Race_Laptimes_*` l
            LEFT JOIN `F1_Modelling_Raw.Rounds_*` r
              ON l.year = r.year
              AND l.round = r.round
            LEFT JOIN `F1_Modelling_Raw.Drivers_*` d
              ON l.year = d.year
              AND l.round = d.round
              AND l.driverId = d.driverId
            LEFT JOIN `F1_Modelling_Raw.Constructors_*` c
              ON d.year = c.year
              AND d.round = c.round
              AND d.constructorId = c.constructorId
            LEFT JOIN `F1_Modelling_Raw.Race_Pitstops_*` rp
              ON l.year = rp.year
              AND l.round = rp.round
              AND l.driverId = rp.driverId
              AND l.lap = rp.lap
            LEFT JOIN `F1_Modelling_Raw.Race_Pitstops_*` rp2
              ON l.year = rp2.year
              AND l.round = rp2.round
              AND l.driverId = rp2.driverId
              AND l.lap - 1 = rp2.lap
            LEFT JOIN qual_time qt
              ON l.year = qt.year
              AND l.round = qt.round
              AND l.driverId = qt.driverId
            LEFT JOIN total_laps tl
              ON l.year = tl.year
              AND l.round = tl.round
            LEFT JOIN `Custom_Lookups.Circuit_Ratings` cr
              ON r.circuitId = cr.circuitId
            LEFT JOIN `Custom_Lookups.Tyre_Stints_*` t
              ON l.year = t.year
              AND l.round = t.round
              AND l.driverId = t.driverId
              AND l.lap >= t.from_lap
              AND l.lap <= t.to_lap

            WHERE
            l.year = {0}
            AND l.round = {1}
            """.format(year, round_num))

        results_df = query_job.to_dataframe()
        print('Successfully retrieved lap time data from BigQuery')

        ### SAVE TO CSV FILE
        print('Year {0}, round {1}: Attempting to save results_df into a csv file'.format(year, round_num))
        try:
            with open('bigquery_upload/combined_{0}{1}.csv'.format(year, round_num_csv_suffix), 'w',
                      newline='') as csv_file:
                results_df.to_csv(csv_file, index=False)
        except:
            print('Year {0}, round {1}: Error saving to a csv file'.format(year, round_num))
            sys.exit()
        print('Year {0}, round {1}: Successfully saved into a csv file'.format(year, round_num))

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload year {0}, round {1} to BigQuery'.format(year, round_num))
        table = dataset.table('Combined_{0}{1}'.format(year, round_num_csv_suffix))
        with open('bigquery_upload/combined_{0}{1}.csv'.format(year, round_num_csv_suffix), 'rb') as source_file:
            job_config = bigquery.LoadJobConfig()
            job_config.source_format = 'CSV'
            job_config.write_disposition = 'WRITE_TRUNCATE'
            job_config.schema = schema_for_upload
            job_config.skip_leading_rows = 1
            try:
                job = bigquery_client.load_table_from_file(
                    source_file, table, job_config=job_config)
            except:
                print('Error uploading year {0}, round {1}:'.format(year, round_num), sys.exc_info()[0])
                sys.exit()

        ### MOVE ONTO THE NEXT ROUND
        print('***Successfully completed upload of year {0}, round {1}'.format(year, round_num))
        round_num += 1
