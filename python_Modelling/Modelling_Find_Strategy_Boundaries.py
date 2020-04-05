###### Modelling_Find_Optimal_Strategy_Boundaries.py
# Uses the find_optimum_strategy function defined in Modelling_Optimum_Strategy.py
# Finds the optimal strategy for a range of tyre deg parameters

import pandas as pd
import Modelling_Optimum_Strategy as mos

#Input parameters here (see Modelling_Optimum_Strategy.py for their definitions)
laps_complete = 3
total_race_laps = 52
pitstop_time = 24
current_tyre_description = 'Soft'
current_tyre_age = 3
need_to_use_different_tyre = 'yes'

# Parameter 1 will be called 'k' later, and is the multiplicative factor by which each harder step of tyre compound has less degradation.
param1_range = []
i = 0.15
while i < 0.3:
    param1_range.append(i)
    i += 0.03

# Parameter 2 will be called 'd' later, and is the difference in seconds per lap between each step of tyre compound, without any degradation factor.
param2_range = []
i = 0.6
while i < 1.4:
    param2_range.append(i)
    i += 0.2

# Cross join to get all the possible combinations of parameters
index = pd.MultiIndex.from_product([param1_range,param2_range], names=["k", "d"])
parameter_df = pd.DataFrame(index=index).reset_index()

optimal_strategies = []
# Get the optimal strategy for these different parameter ranges
for index, row in parameter_df.iterrows():
    k = row["k"]
    d = row["d"]
    results_df = mos.find_optimum_strategy(laps_complete,total_race_laps,pitstop_time,current_tyre_description,
                                           current_tyre_age,0.012,-0.01,d,0.012*k,-0.01*k,2*d,0.012*(k**2),-0.01*(k**2),
                                           need_to_use_different_tyre,'dataframe')
    if results_df["pitstop_1_lap"][0] == -1:
        optimal_strategies.append("No pitstops; " + str(results_df["pitstop_0_tyre"][0]))
    elif results_df["pitstop_2_lap"][0] == -1:
        optimal_strategies.append("1 pitstop; " + str(results_df["pitstop_0_tyre"][0]) + " " + str(results_df["pitstop_1_tyre"][0]))
    else:
        optimal_strategies.append("2 pitstops; " + str(results_df["pitstop_0_tyre"][0]) + " " + str(results_df["pitstop_1_tyre"][0]) + " " + str(results_df["pitstop_2_tyre"][0]))

    print("Finished optimising for k = {0} and d = {1}".format(k,d))

parameter_df["optimal_strategies"] = optimal_strategies
parameter_df.to_csv('strategy_boundaries.csv')
