###### Modelling_Plot_Laptime.py
# Plots the laptimes from a user-defined race, for the user's choice of drivers

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

def plot_laptimes(year,round_num,driver):
    print('*** Plotting lap times from Year {0}, Round {1}: {2}'.format(year,round_num,driver))
    print('Attempting to retrieve combined lap time data from BigQuery')
    key_path = "..." #Insert your BigQuery credentials json file path here
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query_job = bigquery_client.query("""
                SELECT * FROM `F1_Modelling_Combined.Combined_*`
                WHERE
                year = {0}
                AND round = {1}
                """.format(year, round_num))
    results_df = query_job.to_dataframe()
    print('Successfully retrieved combined lap time data from BigQuery')

    results_df_filtered = results_df[results_df['driver_name'] == driver]

    ## Plot the laptimes
    fig, ax = plt.subplots()
    ## Define the data to be plotted
    axis_raw = results_df_filtered.sort_values(by=['driver_name', 'lap_number'])
    ## Define the colour scheme & line style
    tyres = axis_raw['tyre_description']
    colours = []
    for t in tyres:
        if t == 'Soft':
            colour = 'r'
        elif t == 'Medium':
            colour = 'y'
        elif t == 'Hard':
            colour = '0.5'
        elif t == 'Inter':
            colour = 'g'
        elif t == 'Wet':
            colour = 'b'
        else:
            colour = 'k'
        colours.append(colour)
    tyre_status = axis_raw['tyre_status']
    line_style = []
    for t in tyre_status:
        if t == 'New':
            line = '-'
        elif t == 'Used':
            line = '--'
        else:
            line = ':'
        line_style.append(line)
    axis_raw['colour_scheme'] = colours
    axis_raw['line_style'] = line_style
    axis_raw_grouped = axis_raw.groupby(['tyre_stint_number','tyre','tyre_description','tyre_status','colour_scheme',
                                         'line_style']).size().reset_index()
    #print(axis_raw_grouped)
    for index, row in axis_raw_grouped.iterrows():
        stint = row['tyre_stint_number']
        colour_plot = row['colour_scheme']
        line_plot = row['line_style']
        tyre = row['tyre']
        tyre_description = row['tyre_description']
        tyre_status = row['tyre_status']
        label_str = tyre_status + ' ' + tyre_description + ' tyre (' + tyre + ')'
        ## Plot
        axis_raw_filtered = axis_raw[axis_raw['tyre_stint_number'] == stint].sort_values(by=['driver_name', 'lap_number'])
        x_axis = axis_raw_filtered['lap_number']
        y_axis = axis_raw_filtered['lap_time']
        ax.plot(x_axis,y_axis, label = label_str,
                linestyle = line_plot,
                color = colour_plot)
    plt.title("Race Lap Times from Year {0}, Round {1}: {2}".format(year,round_num,driver))
    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time (seconds)")
    plt.legend()
    plt.minorticks_on()
    plt.grid(which = 'major', linestyle = ':', linewidth = '0.5', color = '0.7')
    plt.grid(which = 'minor', linestyle = ':', linewidth = '0.5', color = '0.85')
    plt.show()