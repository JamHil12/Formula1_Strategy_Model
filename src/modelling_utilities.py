###### Modelling_Utilities.py

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import itertools as itt

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tyre_deg_curve_quadratic(tyre_age, tyre_description, soft_tyre_deg_quadratic, soft_tyre_deg_linear, medium_tyre_pace_deficit,
                             medium_tyre_deg_quadratic, medium_tyre_deg_linear, hard_tyre_pace_deficit, hard_tyre_deg_quadratic,
                             hard_tyre_deg_linear):
    '''
    Outputs a numpy array, converting the input tyre ages and descriptions into tyre degradation-adjusted laptime deltas.
    Model: at^2 + bt + c, where t is tyre age in laps, and a, b and c depend on the tyre compound chosen
    :param tyre_age: numpy array, the range of tyre ages to be evaluated
    :param tyre_description: numpy array, with the same length as tyre_age, with elements of either "Soft", "Medium", "Hard"
    :param soft_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a soft tyre in laps
    :param soft_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a soft tyre in laps
    :param medium_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a medium tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param medium_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a medium tyre in laps
    :param medium_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a medium tyre in laps
    :param hard_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a hard tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param hard_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a hard tyre in laps
    :param hard_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a hard tyre in laps
    :return:
    '''

    def tyre_deg_generator_a(l):
        # Here, l should be a numpy array of strings
        return (soft_tyre_deg_quadratic * (l == 'Soft')) + (medium_tyre_deg_quadratic * (l == 'Medium')) + (
                    hard_tyre_deg_quadratic * (l == 'Hard'))

    def tyre_deg_generator_b(l):
        # Here, l should be a numpy array of strings
        return (soft_tyre_deg_linear * (l == 'Soft')) + (medium_tyre_deg_linear * (l == 'Medium')) + (
                    hard_tyre_deg_linear * (l == 'Hard'))

    def tyre_deg_generator_c(l):
        # Here, l should be a numpy array of strings
        return (medium_tyre_pace_deficit * (l == 'Medium')) + (hard_tyre_pace_deficit * (l == 'Hard'))

    a = tyre_deg_generator_a(tyre_description)
    b = tyre_deg_generator_b(tyre_description)
    c = tyre_deg_generator_c(tyre_description)

    return a * (tyre_age ** 2) + b * tyre_age + c

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def tyre_deg_curve_power(tyre_age, tyre_description, omega, soft_tyre_deg_coeff, medium_tyre_pace_deficit,
                         medium_tyre_deg_coeff, hard_tyre_pace_deficit, hard_tyre_deg_coeff):
    '''
    Outputs a numpy array, converting the input tyre ages and descriptions into tyre degradation-adjusted laptime deltas.
    Model: a*(t^omega) + c, where t is tyre age in laps, and a and c depend on the tyre compound chosen
    :param tyre_age: numpy array, the range of tyre ages to be evaluated
    :param tyre_description: numpy array, with the same length as tyre_age, with elements of either "Soft", "Medium", "Hard"
    :param omega: positive float at least 1, defining the power curve
    :param soft_tyre_deg_coeff: float, the coefficient 'a' of t^omega in "laptime tyre effect = at^omega + c", where t is the age of a soft tyre in laps
    :param medium_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a medium tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param medium_tyre_deg_coeff: float, the coefficient 'a' of t^omega in "laptime tyre effect = at^omega + c", where t is the age of a medium tyre in laps
    :param hard_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a hard tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param hard_tyre_deg_coeff: float, the coefficient 'a' of t^omega in "laptime tyre effect = at^omega + c", where t is the age of a hard tyre in laps
    :return:
    '''

    def tyre_deg_generator_a(l):
        # Here, l should be a numpy array of strings
        return (soft_tyre_deg_coeff * (l == 'Soft')) + (medium_tyre_deg_coeff * (l == 'Medium')) + (
                    hard_tyre_deg_coeff * (l == 'Hard'))

    def tyre_deg_generator_c(l):
        # Here, l should be a numpy array of strings
        return (medium_tyre_pace_deficit * (l == 'Medium')) + (hard_tyre_pace_deficit * (l == 'Hard'))

    a = tyre_deg_generator_a(tyre_description)
    c = tyre_deg_generator_c(tyre_description)

    return a * (tyre_age ** omega) + c

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def find_optimum_strategy(laps_complete, total_race_laps, pitstop_time, current_tyre_description, current_tyre_age,
                          need_to_use_different_tyre, tyre_deg_curve, base_laptime = 0, fuel_laptime_correction = 0,
                          max_pitstops = 3, batch_size = 50000, detailed_logs = False, **kwargs):
    '''
    Outputs a dataframe with the optimal strategy, based on input race parameters.
    Method: Grid search of all possible pitstop lap and tyre choice combinations for the remaining race distance
    Assumptions:
    * The optimum strategy has at most 3 pitstops
    * The effect of tyre degradation on laptime vs the age of the tyre is governed by the 'tyre_deg_curve' input function
    :param laps_complete: integer, number of laps in the race already completed
    :param total_race_laps: integer, total number of laps in the race
    :param pitstop_time: float, the total loss in race time (in seconds) due to making a pitstop
    :param current_tyre_description: string, the description of the current tyre (Soft, Medium or Hard)
    :param current_tyre_age: integer, the number of laps the current tyre has already completed
    :param need_to_use_different_tyre: boolean, depending on whether only one tyre compound has been used in the race so far
    :param tyre_deg_curve: a function, that takes as input numpy arrays of tyre ages and descriptions, and outputs a numpy array of forecasted laptimes.
    :param base_laptime: a float, the race laptime (measured in seconds) from a brand new Soft tyre with 1 lap of fuel remaining
    :param fuel_laptime_correction: a non-negative float. The improvement in laptime, measured in seconds per lap (assumed to be linear), from decreasing fuel load. This is assuming all other variables (including tyre deg) are constant.
    :param max_pitstops: integer, a manual override for the maximum number of pitstops to allow in the output. By default, this is equal to 3.
    :param batch_size: integer, the number of strategies to compare and optimise over per batch. More computing memory means this can be increased. By default, this is equal to 50000.
    :param detailed_logs: boolean, whether or not to return extra detail on where the function is up to in the batching process
    :return:
    '''

    if max_pitstops > 3:
        print('**WARNING**: This function can only optimise to a maximum of 3 pitstops. Therefore, resetting max_pitstops to be 3.')
        max_pitstops = 3
    elif (max_pitstops < 1 & need_to_use_different_tyre == True):
        print('**WARNING**: Incompatible inputs; user has specified that a different tyre needs to be used before the end of the race, but max_pitstops does not allow for this. Therefore, resetting max_pitstops to be 1.')
        max_pitstops = 1

    #Define the shape of the tyre drop-off function
    def generate_laptime(t, td, p, l):
        '''
        :param t: a numpy array of tyre ages
        :param td: a numpy array of tyre descriptions
        :param p: a numpy array of 1s and 0s, where 1s are on the laps where a pitstop is to be made
        :param l: a numpy array of lap numbers
        :return:
        '''

        pitstop_extra = pitstop_time * p
        fuel_correction = fuel_laptime_correction * (total_race_laps - l)
        return tyre_deg_curve(t, td, **kwargs) + pitstop_extra + base_laptime + fuel_correction

    tyres = ['Soft', 'Medium', 'Hard']
    pitlaps_staging = list(range(laps_complete + 1,total_race_laps + 1))
    pitlaps_staging.append(-1) #-1 represents no pitstop
    if max_pitstops == 0:
        pit_lap_1 = [-1]
        pit_lap_2 = [-1]
        pit_lap_3 = [-1]
    elif max_pitstops == 1:
        pit_lap_1 = pitlaps_staging
        pit_lap_2 = [-1]
        pit_lap_3 = [-1]
    elif max_pitstops == 2:
        pit_lap_1 = pitlaps_staging
        pit_lap_2 = pitlaps_staging
        pit_lap_3 = [-1]
    else:
        pit_lap_1 = pitlaps_staging
        pit_lap_2 = pitlaps_staging
        pit_lap_3 = pitlaps_staging

    index = pd.MultiIndex.from_product([pit_lap_1,tyres,pit_lap_2,tyres,pit_lap_3,tyres], names=["pitstop_1_lap", "pitstop_1_tyre", "pitstop_2_lap", "pitstop_2_tyre", "pitstop_3_lap", "pitstop_3_tyre"])
    pitstop_df = pd.DataFrame(index=index).reset_index()
    pitstop_df["pitstop_0_lap"] = laps_complete
    pitstop_df["pitstop_0_tyre"] = current_tyre_description
    pitstop_df["pitstop_0_tyre_age"] = current_tyre_age

    # Remove any combiations of pit laps which don't make sense (i.e. pit stop 2 must happen after pit stop 1)
    # Remove any combinations where only 1 tyre of tyre is used in the race
    p1 = pitstop_df["pitstop_1_lap"].to_numpy()
    p2 = pitstop_df["pitstop_2_lap"].to_numpy()
    p3 = pitstop_df["pitstop_3_lap"].to_numpy()
    t0 = pitstop_df["pitstop_0_tyre"].to_numpy()
    t1 = pitstop_df["pitstop_1_tyre"].to_numpy()
    t2 = pitstop_df["pitstop_2_tyre"].to_numpy()
    t3 = pitstop_df["pitstop_3_tyre"].to_numpy()
    if need_to_use_different_tyre == True:
        x = (p1 > -1) & ((((p3 > p2) & (p2 > p1)) & ~((t3 == t2) & (t2 == t1) & (t1 == t0))) | (((p3 == -1) & (p2 > p1)) & ~((t2 == t1) & (t1 == t0))) | (((p2 == -1) & (p3 == -1)) & ~(t1 == t0)))
    else:
        x = ( ((p1 > -1) & (p3 > p2) & (p2 > p1)) | ((p3 == -1) & (p1 > -1) & (p2 > p1)) | ((p3 == -1) & (p2 == -1)) )
    pitstop_df = pitstop_df[x].reset_index()

    pitstop_df = pitstop_df[["pitstop_0_lap","pitstop_0_tyre","pitstop_0_tyre_age","pitstop_1_lap","pitstop_1_tyre","pitstop_2_lap","pitstop_2_tyre","pitstop_3_lap","pitstop_3_tyre"]]
    pitstop_df["pitstop_1_tyre"].loc[pitstop_df['pitstop_1_lap'] == -1] = "No pitstop"
    pitstop_df["pitstop_2_tyre"].loc[pitstop_df['pitstop_2_lap'] == -1] = "No pitstop"
    pitstop_df["pitstop_3_tyre"].loc[pitstop_df['pitstop_3_lap'] == -1] = "No pitstop"
    pitstop_df.drop_duplicates(inplace=True)
    pitstop_df.reset_index()

    laps = np.arange(laps_complete + 1, total_race_laps + 1)

    for batch_number, group_df in pitstop_df.groupby(np.arange(len(pitstop_df)) // batch_size):
        laps_list = []
        batch_df = group_df.reset_index()
        if detailed_logs == True:
            print('Attempting optimisation with batch number = {0}, df size {1}'.format(batch_number, batch_df.shape[0]))

        for i in range(0, len(batch_df['pitstop_0_lap'].to_numpy())):
            laps_list.append(laps)

        pl1 = batch_df["pitstop_1_lap"].to_numpy()
        pl2 = batch_df["pitstop_2_lap"].to_numpy()
        pl3 = batch_df["pitstop_3_lap"].to_numpy()
        pt0 = batch_df["pitstop_0_tyre"].to_numpy()
        pt1 = batch_df["pitstop_1_tyre"].to_numpy()
        pt2 = batch_df["pitstop_2_tyre"].to_numpy()
        pt3 = batch_df["pitstop_3_tyre"].to_numpy()
        pta0 = batch_df["pitstop_0_tyre_age"].to_numpy()
        l = np.transpose(np.array(laps_list))

        # ~~~~~Lap Number~~~~~
        batch_df['lap_number_list'] = laps_list
        # ~~~~~Stint Number~~~~~
        stint = 1*((l <= pl1)|(pl1 == -1)) + 2*((pl1 > -1) & (l > pl1) & ((l <= pl2)|(pl2 == -1))) + 3*((pl2 > -1) & (l > pl2) & ((l <= pl3)|(pl3 == -1))) + 4*((pl3 > -1) & (l > pl3))
        batch_df['tyre_stint_number_list'] = list(np.transpose(stint))
        # ~~~~~Tyre Ages~~~~~
        ta = l - ((stint == 1)*(l[0] - pta0)) - ((stint == 2)*(1 + pl1)) - ((stint == 3)*(1 + pl2)) - ((stint == 4)*(1 + pl3))
        batch_df['tyre_age_list'] = list(np.transpose(ta))
        # ~~~~~Tyre Descriptions~~~~~
        td = (pt0*(stint == 1)) + (pt1*(stint == 2)) + (pt2*(stint == 3)) + (pt3*(stint == 4))
        batch_df['tyre_description_list'] = list(np.transpose(td))
        # ~~~~~Tyre Statuses~~~~~
        tstat = 1 * ((stint == 1) & (pta0 > 0)) + 2 * (~((stint == 1) & (pta0 > 0)))
        tstat = np.where(tstat == 1, 'Used', 'New')
        batch_df['tyre_status_list'] = list(np.transpose(tstat))
        # ~~~~~Pitstop Laps~~~~~
        pitstop_laps = 1*((l == pl1) | (l == pl2) | (l == pl3))

        stint_time_total = generate_laptime(ta, td, pitstop_laps, l)
        batch_df["race_time_adjusted"] = list(np.transpose(sum(stint_time_total)))
        batch_df["lap_times_adjusted"] = list(np.transpose(stint_time_total))
        optimal_strategy_batch = batch_df[batch_df["race_time_adjusted"] == batch_df["race_time_adjusted"].min()].reset_index()
        optimal_strategy_batch = optimal_strategy_batch[["pitstop_0_lap", "pitstop_0_tyre", "pitstop_0_tyre_age", "pitstop_1_lap",
                                                     "pitstop_1_tyre", "pitstop_2_lap", "pitstop_2_tyre", "pitstop_3_lap",
                                                     "pitstop_3_tyre", "lap_number_list", "tyre_stint_number_list",
                                                     "tyre_age_list", "tyre_description_list", "tyre_status_list",
                                                     "race_time_adjusted", "lap_times_adjusted"]].reset_index()

        if batch_number == 0:
            optimal_strategy = optimal_strategy_batch
        else:
            optimal_strategy = optimal_strategy.append(optimal_strategy_batch)

        if detailed_logs == True:
            print('Completed optimisation with batch number = {0}'.format(batch_number))

    optimal_strategy.reset_index()
    final_optimum_strategy = optimal_strategy[optimal_strategy["race_time_adjusted"] == optimal_strategy["race_time_adjusted"].min()].reset_index()
    return final_optimum_strategy



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def download_laptimes(year, round_num, driver = 'all drivers', key_path = "credentials/f1modeller_bq_credentials.json"):
    '''
    Returns a dataframe with race data for the specified year, round number and driver.
    :param year: an integer, the year of the race you want to download data for
    :param round_num: an integer, the round number of the race you want to download data for
    :param driver: a string, the name of the driver you want to download data for. By default, downloads all drivers.
    :param key_path: a string, optional. Defines the path of the BigQuery json authenticaion key, to allow access for downloading.
    :return:
    '''

    if driver == 'all drivers':
        driver_query_string = ''
    else:
        driver_query_string = """AND LOWER(driver_name) = LOWER('{0}')""".format(driver)
    credentials = service_account.Credentials.from_service_account_file(key_path)
    bigquery_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query_job = bigquery_client.query("""
                    SELECT * FROM `F1_Modelling_Combined.Combined_*`
                    WHERE
                    year = {0}
                    AND round = {1}
                    {2}
                    """.format(year, round_num, driver_query_string))
    return query_job.to_dataframe()



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_laptimes(results_df, title = "Lap Times Chart"):
    '''
    Returns a plot of the race data provided in the input results_df.
    :param results_df: a Pandas dataframe, containing the data you want to plot. It must have the following columns: lap_number (e.g. 5), tyre_stint_number (e.g. 1), tyre_description (e.g. "Hard"), tyre_status (e.g. "New"), lap_time (e.g. 83.642).
    :param title: a string, optional. This allows you to set the title of the chart.
    :return:
    '''
    fig, ax = plt.subplots()
    ## Define the data to be plotted
    axis_raw = results_df.sort_values(by=['lap_number'])
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
    axis_raw_grouped = axis_raw.groupby(['tyre_stint_number','tyre_description','tyre_status','colour_scheme',
                                         'line_style']).size().reset_index()
    for index, row in axis_raw_grouped.iterrows():
        stint = row['tyre_stint_number']
        colour_plot = row['colour_scheme']
        line_plot = row['line_style']
        tyre_description = row['tyre_description']
        tyre_status = row['tyre_status']
        label_str = tyre_status + ' ' + tyre_description
        ## Plot
        axis_raw_filtered = axis_raw[axis_raw['tyre_stint_number'] == stint].sort_values(by=['lap_number'])
        x_axis = axis_raw_filtered['lap_number']
        y_axis = axis_raw_filtered['lap_time']
        ax.plot(x_axis, y_axis, label = label_str,
                linestyle = line_plot,
                color = colour_plot)
    plt.title(title)
    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time (seconds)")
    plt.legend()
    plt.minorticks_on()
    plt.grid(which = 'major', linestyle = ':', linewidth = '0.5', color = '0.7')
    plt.grid(which = 'minor', linestyle = ':', linewidth = '0.5', color = '0.85')
    plt.show()
