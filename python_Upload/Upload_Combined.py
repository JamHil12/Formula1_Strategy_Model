###### Upload_Combined.py
# Combines all the other datasets together, ready for visualisation and modelling

from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os

def upload_combined(year,round_start,round_end):
    round_num = round_start

    ## OBTAIN SCHEMA FOR UPLOAD
    key_path = "..." #Insert your BigQuery credentials json file path here
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
        bigquery.SchemaField("pitstop_number", "FLOAT"),
        bigquery.SchemaField("pitstop_duration", "FLOAT"),
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
        key_path = "..." #Insert your BigQuery credentials json file path here
        credentials = service_account.Credentials.from_service_account_file(key_path)
        bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)

        query_job = bigquery_client.query("""
            WITH qual_time_raw_1 as (
 SELECT
 year,
 round,
 driverId,
 CASE
 WHEN q1 < q2 and q1 < q3 THEN q1
 WHEN q2 < q3 THEN q2
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
            rp.stop as pitstop_number,
            rp.duration as pitstop_duration,
            cr.tyre_stress as circuit_tyre_stress_rating,
            cr.asphalt_abrasion as circuit_asphalt_abrasion_rating,
            cr.asphalt_grip as circuit_asphalt_grip_rating,
            cr.downforce as circuit_downforce_rating,
            cr.lateral as circuit_lateral_rating,
            t.stint as tyre_stint_number,
            t.tyre,
            t.tyre_description,
            t.tyre_status,
            1 + (l.lap - t.from_lap) as tyre_age_laps,
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
        print('Year {0}, round {1}: Attempting to save results_df into a csv file'.format(year,round_num))
        try:
            with open('bigquery_upload/combined_{0}{1}.csv'.format(year, round_num_csv_suffix), 'w',
                      newline='') as csv_file:
                results_df.to_csv(csv_file, index=False)
        except:
            print('Year {0}, round {1}: Error saving to a csv file'.format(year,round_num))
            sys.exit()
        print('Year {0}, round {1}: Successfully saved into a csv file'.format(year,round_num))

        ### UPLOAD INTO BIGQUERY
        print('Attempting to upload year {0}, round {1} to BigQuery'.format(year,round_num))
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
                print('Error uploading year {0}, round {1}:'.format(year,round_num), sys.exc_info()[0])
                sys.exit()

        ### MOVE ONTO THE NEXT ROUND
        print('***Successfully completed upload of year {0}, round {1}'.format(year, round_num))
        round_num += 1