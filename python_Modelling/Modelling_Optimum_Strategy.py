###### Modelling_Optimum_Strategy.py
# Finds the optimum strategy, based on input parameters of tyre wear, age of current tyres, laps completed etc

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import itertools as itt

def find_optimum_strategy(laps_complete,total_race_laps,pitstop_time,current_tyre_description,current_tyre_age,
                          soft_tyre_deg_quadratic,soft_tyre_deg_linear,medium_tyre_pace_deficit,medium_tyre_deg_quadratic,
                          medium_tyre_deg_linear,hard_tyre_pace_deficit,hard_tyre_deg_quadratic,hard_tyre_deg_linear,
                          need_to_use_different_tyre,output_type):
    '''
    Outputs a dataframe with the optimal strategy, based on input race parameters.
    Method: Grid search of all possible combinations for the remaining race distance
    Assumptions:
    * The optimum strategy has at most 2 pitstops
    * The effect of tyre degradation on laptime is quadratic in the age of the tyre
    :param laps_complete: integer, number of laps in the race already completed
    :param total_race_laps: integer, total number of laps in the race
    :param pitstop_time: float, the total loss in race time (in seconds) due to making a pitstop
    :param current_tyre_description: string, the description of the current tyre (Soft, Medium or Hard)
    :param current_tyre_age: integer, the number of laps the current tyre has already completed
    :param soft_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a soft tyre in laps
    :param soft_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a soft tyre in laps
    :param medium_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a medium tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param medium_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a medium tyre in laps
    :param medium_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a medium tyre in laps
    :param hard_tyre_pace_deficit: float, the positive raw amount of time (in seconds) a hard tyre is slower than the soft tyre due to lower grip (fuel & degradation corrected)
    :param hard_tyre_deg_quadratic: float, the coefficient 'a' of t^2 in "laptime tyre effect = at^2 + bt", where t is the age of a hard tyre in laps
    :param hard_tyre_deg_linear: float, the coefficient 'b' of t in "laptime tyre effect = at^2 + bt", where t is the age of a hard tyre in laps
    :param need_to_use_different_tyre: string, either 'yes' or 'no' depending on whether only one tyre compound has been used in the race so far
    :param output_type: string, either 'dataframe', 'words' or 'chart' depending on how you want the output to look
    :return:
    '''

    tyres = ['Soft', 'Medium', 'Hard']
    # 1st round of pitstops
    if laps_complete + 1 > total_race_laps - 1:
        print('Optimal strategy is to not pit (less than 2 laps to the finish)')
        sys.exit()
    pit_lap_1 = list(range(laps_complete + 1,total_race_laps - 1))
    pit_lap_1.append(-1) #-1 meaning no pit stop
    pit_lap_2 = list(range(laps_complete + 1,total_race_laps - 1))
    pit_lap_2.append(-1) #-1 meaning no 2nd pit stop
    index = pd.MultiIndex.from_product([pit_lap_1,tyres,pit_lap_2,tyres], names=["pitstop_1_lap", "pitstop_1_tyre", "pitstop_2_lap", "pitstop_2_tyre"])
    pitstop_df = pd.DataFrame(index=index).reset_index()
    pitstop_df["pitstop_0_lap"] = laps_complete
    pitstop_df["pitstop_0_tyre"] = current_tyre_description
    pitstop_df["pitstop_0_tyre_age"] = current_tyre_age
    include = []
    # Remove any combiations of pit laps which don't make sense (i.e. pit stop 2 must happen after pit stop 1)
    # Remove any combinations where only 1 tyre of tyre is used in the race
    for index, row in pitstop_df.iterrows():
        if need_to_use_different_tyre == 'yes':
            x = ((row["pitstop_2_lap"] > row["pitstop_1_lap"] and not (row["pitstop_2_tyre"] == row["pitstop_1_tyre"] and row["pitstop_1_tyre"] == row["pitstop_0_tyre"])) or (row["pitstop_2_lap"] == -1 and not (row["pitstop_1_tyre"] == row["pitstop_0_tyre"])))
            include.append(x)
        else:
            x = (row["pitstop_2_lap"] == -1 or row["pitstop_1_lap"] == -1 or (row["pitstop_2_lap"] > row["pitstop_1_lap"]))
            include.append(x)
    pitstop_df = pitstop_df[include].reset_index()
    pitstop_df = pitstop_df[["pitstop_0_lap","pitstop_0_tyre","pitstop_0_tyre_age","pitstop_1_lap","pitstop_1_tyre","pitstop_2_lap","pitstop_2_tyre"]]
    pitstop_df["pitstop_1_tyre"].loc[pitstop_df['pitstop_1_lap'] == -1] = "No pitstop"
    pitstop_df["pitstop_2_tyre"].loc[pitstop_df['pitstop_2_lap'] == -1] = "No pitstop"
    pitstop_df.drop_duplicates(inplace=True)
    pitstop_df.reset_index()
    #pitstop_df[["pitstop_1_lap", "pitstop_1_tyre", "pitstop_2_lap", "pitstop_2_tyre"]].to_csv('optimal_strategy_pitstop_df.csv')
    race_time_adj_list = []
    for index, row in pitstop_df.iterrows():
        #Model tyre degradation as at^2 + bt + c, where t is tyre age in laps, and a, b and c depend on the tyre compound chosen
        a = []
        if row["pitstop_0_tyre"] == 'Soft':
            a.append(soft_tyre_deg_quadratic)
        elif row["pitstop_0_tyre"] == 'Medium':
            a.append(medium_tyre_deg_quadratic)
        elif row["pitstop_0_tyre"] == 'Hard':
            a.append(hard_tyre_deg_quadratic)
        if row["pitstop_1_tyre"] == 'Soft':
            a.append(soft_tyre_deg_quadratic)
        elif row["pitstop_1_tyre"] == 'Medium':
            a.append(medium_tyre_deg_quadratic)
        elif row["pitstop_1_tyre"] == 'Hard':
            a.append(hard_tyre_deg_quadratic)
        elif row["pitstop_1_tyre"] == 'No pitstop':
            a.append(None)
        if row["pitstop_2_tyre"] == 'Soft':
            a.append(soft_tyre_deg_quadratic)
        elif row["pitstop_2_tyre"] == 'Medium':
            a.append(medium_tyre_deg_quadratic)
        elif row["pitstop_2_tyre"] == 'Hard':
            a.append(hard_tyre_deg_quadratic)
        elif row["pitstop_2_tyre"] == 'No pitstop':
            a.append(None)
        b = []
        if row["pitstop_0_tyre"] == 'Soft':
            b.append(soft_tyre_deg_linear)
        elif row["pitstop_0_tyre"] == 'Medium':
            b.append(medium_tyre_deg_linear)
        elif row["pitstop_0_tyre"] == 'Hard':
            b.append(hard_tyre_deg_linear)
        if row["pitstop_1_tyre"] == 'Soft':
            b.append(soft_tyre_deg_linear)
        elif row["pitstop_1_tyre"] == 'Medium':
            b.append(medium_tyre_deg_linear)
        elif row["pitstop_1_tyre"] == 'Hard':
            b.append(hard_tyre_deg_linear)
        elif row["pitstop_1_tyre"] == 'No pitstop':
            b.append(None)
        if row["pitstop_2_tyre"] == 'Soft':
            b.append(soft_tyre_deg_linear)
        elif row["pitstop_2_tyre"] == 'Medium':
            b.append(medium_tyre_deg_linear)
        elif row["pitstop_2_tyre"] == 'Hard':
            b.append(hard_tyre_deg_linear)
        elif row["pitstop_2_tyre"] == 'No pitstop':
            b.append(None)
        c = []
        if row["pitstop_0_tyre"] == 'Soft':
            c.append(0)
        elif row["pitstop_0_tyre"] == 'Medium':
            c.append(medium_tyre_pace_deficit)
        elif row["pitstop_0_tyre"] == 'Hard':
            c.append(hard_tyre_pace_deficit)
        if row["pitstop_1_tyre"] == 'Soft':
            c.append(0)
        elif row["pitstop_1_tyre"] == 'Medium':
            c.append(medium_tyre_pace_deficit)
        elif row["pitstop_1_tyre"] == 'Hard':
            c.append(hard_tyre_pace_deficit)
        elif row["pitstop_1_tyre"] == 'No pitstop':
            c.append(None)
        if row["pitstop_2_tyre"] == 'Soft':
            c.append(0)
        elif row["pitstop_2_tyre"] == 'Medium':
            c.append(medium_tyre_pace_deficit)
        elif row["pitstop_2_tyre"] == 'Hard':
            c.append(hard_tyre_pace_deficit)
        elif row["pitstop_2_tyre"] == 'No pitstop':
            c.append(None)

        if row["pitstop_1_lap"] == -1: # Must have no pitstops
            stint_0 = list(range(row["pitstop_0_lap"] + 1,total_race_laps + 1))
            stint_laps_0 = list(range(current_tyre_age + 1, total_race_laps + current_tyre_age - row["pitstop_0_lap"] + 1))
            stint_time_0 = stint_time_0 = list(map(lambda x: a[0]*(x**2) + b[0]*x + c[0],stint_laps_0))
            lap_times_adj = pd.DataFrame(stint_0, columns=["lap_number"])
            lap_times_adj["lap_time_adj"] = stint_time_0
            race_time_adj = [sum(stint_time_0), lap_times_adj]
            race_time_adj_list.append(race_time_adj)
        elif row["pitstop_2_lap"] == -1: # Must have exactly 1 pitstop
            stint_0 = list(range(row["pitstop_0_lap"] + 1, row["pitstop_1_lap"] + 1))
            stint_laps_0 = list(range(current_tyre_age + 1, current_tyre_age + row["pitstop_1_lap"] - row["pitstop_0_lap"] + 1))
            stint_1 = list(range(row["pitstop_1_lap"] + 1, total_race_laps + 1))
            stint_laps_1 = list(range(0, total_race_laps - row["pitstop_1_lap"]))
            stint_time_0 = list(map(lambda x: a[0] * (x ** 2) + b[0] * x + c[0] + (pitstop_time if x == current_tyre_age + row["pitstop_1_lap"] - row["pitstop_0_lap"] else 0),stint_laps_0))
            stint_time_1 = list(map(lambda x: a[1] * (x ** 2) + b[1] * x + c[1], stint_laps_1))
            stint_total = stint_0
            stint_total.extend(stint_1)
            stint_time_total = stint_time_0
            stint_time_total.extend(stint_time_1)
            lap_times_adj = pd.DataFrame(stint_total, columns=["lap_number"])
            lap_times_adj["lap_time_adj"] = stint_time_total
            race_time_adj = [sum(stint_time_0) + sum(stint_time_1), lap_times_adj]
            race_time_adj_list.append(race_time_adj)
        else: # Must have exactly 2 pitstops
            stint_0 = list(range(row["pitstop_0_lap"] + 1, row["pitstop_1_lap"] + 1))
            stint_laps_0 = list(range(current_tyre_age + 1, current_tyre_age + row["pitstop_1_lap"] - row["pitstop_0_lap"] + 1))
            stint_1 = list(range(row["pitstop_1_lap"] + 1, row["pitstop_2_lap"] + 1))
            stint_laps_1 = list(range(0, row["pitstop_2_lap"] - row["pitstop_1_lap"]))
            stint_2 = list(range(row["pitstop_2_lap"] + 1, total_race_laps + 1))
            stint_laps_2 = list(range(0, total_race_laps - row["pitstop_2_lap"]))
            stint_time_0 = list(map(lambda x: a[0] * (x ** 2) + b[0] * x + c[0] + (pitstop_time if x == current_tyre_age + row["pitstop_1_lap"] - row["pitstop_0_lap"] else 0),stint_laps_0))
            stint_time_1 = list(map(lambda x: a[1] * (x ** 2) + b[1] * x + c[1] + (pitstop_time if x == row["pitstop_2_lap"] - row["pitstop_1_lap"] - 1 else 0), stint_laps_1))
            stint_time_2 = list(map(lambda x: a[2] * (x ** 2) + b[2] * x + c[2], stint_laps_2))
            stint_total = stint_0
            stint_total.extend(stint_1)
            stint_total.extend(stint_2)
            stint_time_total = stint_time_0
            stint_time_total.extend(stint_time_1)
            stint_time_total.extend(stint_time_2)
            lap_times_adj = pd.DataFrame(stint_total, columns=["lap_number"])
            lap_times_adj["lap_time_adj"] = stint_time_total
            race_time_adj = [sum(stint_time_0) + sum(stint_time_1) + sum(stint_time_2), lap_times_adj]
            race_time_adj_list.append(race_time_adj)

    race_time_adj_forecast = []
    lap_times_adj_forecast = []
    for i in race_time_adj_list:
        race_time_adj_forecast.append(i[0])
        lap_times_adj_forecast.append(i[1])

    pitstop_df["race_time_adjusted"] = race_time_adj_forecast
    pitstop_df["lap_times_adjusted"] = lap_times_adj_forecast
    optimal_strategy_row = pitstop_df[pitstop_df["race_time_adjusted"] == pitstop_df["race_time_adjusted"].min()].reset_index()

    ## Now create an output according to the output_type parameter
    if output_type == 'dataframe':
        return optimal_strategy_row
    elif output_type == 'words':
        print("Optimum strategy (current lap {0}, current tyre {1}):".format(laps_complete,current_tyre_description))
        if optimal_strategy_row["pitstop_1_lap"][0] == -1:
            print("Stay on the current {0} tyres to the finish on lap {1}".format(optimal_strategy_row["pitstop_0_tyre"][0],total_race_laps))
            sys.exit()
        else:
            print("Stay on the current {0} tyres until end of lap {1}".format(optimal_strategy_row["pitstop_0_tyre"][0],
                                                                              optimal_strategy_row["pitstop_1_lap"][0]))
            print("Pit at the end of lap {0} for {1} tyres".format(optimal_strategy_row["pitstop_1_lap"][0],
                                                                   optimal_strategy_row["pitstop_1_tyre"][0]))
        if optimal_strategy_row["pitstop_2_lap"][0] == -1:
            print("Stay on the {0} tyres to the finish on lap {1}".format(optimal_strategy_row["pitstop_1_tyre"][0], total_race_laps))
            sys.exit()
        else:
            print("Stay on the {0} tyres until end of lap {1}".format(optimal_strategy_row["pitstop_1_tyre"][0],
                                                                      optimal_strategy_row["pitstop_2_lap"][0]))
            print("Pit at the end of lap {0} for {1} tyres".format(optimal_strategy_row["pitstop_2_lap"][0],
                                                                   optimal_strategy_row["pitstop_2_tyre"][0]))
            print("Stay on the {0} tyres to the finish on lap {1}".format(optimal_strategy_row["pitstop_2_tyre"][0],
                                                                          total_race_laps))

    elif output_type == 'chart':
        optimal_lap_times_adj = optimal_strategy_row["lap_times_adjusted"][0]
        ## Plot the laptimes
        fig, ax = plt.subplots()
        ## Define the data to be plotted
        axis_raw = optimal_lap_times_adj.sort_values(by=['lap_number'])
        ## Define the colour scheme & line style
        tyres = []
        tyre_stint = []
        for t in optimal_lap_times_adj["lap_number"]:
            if (t <= optimal_strategy_row["pitstop_1_lap"][0] or optimal_strategy_row["pitstop_1_lap"][0] == -1):
                tyres.append(optimal_strategy_row["pitstop_0_tyre"][0])
                tyre_stint.append('1')
            elif ((t > optimal_strategy_row["pitstop_1_lap"][0] and t <= optimal_strategy_row["pitstop_2_lap"][0]) or optimal_strategy_row["pitstop_2_lap"][0] == -1):
                tyres.append(optimal_strategy_row["pitstop_1_tyre"][0])
                tyre_stint.append('2')
            elif t > optimal_strategy_row["pitstop_2_lap"][0]:
                tyres.append(optimal_strategy_row["pitstop_2_tyre"][0])
                tyre_stint.append('3')
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
        axis_raw['colour_scheme'] = colours
        axis_raw['tyre_description'] = tyres
        axis_raw['tyre_stint_number'] = tyre_stint
        axis_raw_grouped = axis_raw.groupby(
            ['tyre_stint_number','tyre_description', 'colour_scheme']).size().reset_index()
        for index, row in axis_raw_grouped.iterrows():
            stint = row['tyre_stint_number']
            colour_plot = row['colour_scheme']
            tyre_description = row['tyre_description']
            label_str = 'Stint #' + stint + ' : ' + tyre_description
            ## Plot
            axis_raw_filtered = axis_raw[axis_raw['tyre_stint_number'] == stint].sort_values(
                by=['lap_number'])
            x_axis = axis_raw_filtered['lap_number']
            y_axis = axis_raw_filtered['lap_time_adj']
            ax.plot(x_axis, y_axis, label=label_str,
                    color=colour_plot)
        plt.title("Forecasted adjusted race lap times")
        plt.xlabel("Lap Number")
        plt.ylabel("Adjusted Lap Time (seconds)")
        plt.legend()
        plt.minorticks_on()
        plt.grid(which='major', linestyle=':', linewidth='0.5', color='0.7')
        plt.grid(which='minor', linestyle=':', linewidth='0.5', color='0.85')
        plt.show()
    else:
        print('Invalid output type. Please choose either dataframe, words or chart.')

#Testing the function out
#k = 0.3
#d = 0.6
#find_optimum_strategy(3,52,24,'Soft',3,0.012,-0.01,d,0.012*k,-0.01*k,2*d,0.012*(k**2),-0.01*(k**2),'yes','chart')