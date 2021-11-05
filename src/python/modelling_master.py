import modelling_utilities as mu
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ~~~~~~~~~~~~~ Finding & plotting optimal strategies with known tyre deg variables ~~~~~~~~~~~~~
laps_complete = 3  # Full racing laps already completed
total_race_laps = 52
pitstop_time = 24  # Total extra time in seconds to make a pitstop
current_tyre_description = 'Soft'  # Either 'Soft', 'Medium' or 'Hard'
current_tyre_age = 3  # Total laps the current tyre has already done
need_to_use_different_tyre = True  # Boolean, depending on whether you still need to use a different compound of tyre before the end of the race

# The following parameters will define the shape of the quadratic tyre deg curve
tyre_deg_curve = mu.tyre_deg_curve_quadratic
k = 0.6
d = 0.6
soft_tyre_deg_quadratic = 0.012,
soft_tyre_deg_linear = -0.01,
medium_tyre_pace_deficit = d,
medium_tyre_deg_quadratic = 0.012*k,
medium_tyre_deg_linear = -0.01*k,
hard_tyre_pace_deficit = 2*d,
hard_tyre_deg_quadratic = 0.012*(k**2),
hard_tyre_deg_linear = -0.01*(k**2)

max_pitstops = 3
base_laptime = 76.52  # The race lap time, measured in seconds, from a brand new Soft tyre with 1 lap of fuel remaining.
fuel_laptime_correction = 0.06  # The improvement in lap time, measured in seconds per lap, from decreasing fuel load.
detailed_logs = True  # Boolean, whether or not to return extra detail on where the function is up to in the batching process.
batch_size = 50000  # Controls the number of strategies that are processed in a single batch. If you have issues with memory, then reduce this batch size.

optimal_strategy = mu.find_optimum_strategy(laps_complete, total_race_laps, pitstop_time, current_tyre_description,
                                            current_tyre_age, need_to_use_different_tyre, tyre_deg_curve,
                                            base_laptime, fuel_laptime_correction, max_pitstops, batch_size, detailed_logs,
                                            soft_tyre_deg_quadratic = soft_tyre_deg_quadratic, soft_tyre_deg_linear = soft_tyre_deg_linear,
                                            medium_tyre_pace_deficit = medium_tyre_pace_deficit, medium_tyre_deg_quadratic = medium_tyre_deg_quadratic, medium_tyre_deg_linear = medium_tyre_deg_linear,
                                            hard_tyre_pace_deficit = hard_tyre_pace_deficit, hard_tyre_deg_quadratic = hard_tyre_deg_quadratic, hard_tyre_deg_linear = hard_tyre_deg_linear
                                           )
for i in range(0,len(optimal_strategy.index)):
    results_df = pd.DataFrame({'lap_number': optimal_strategy.iloc[i]['lap_number_list'],
                              'tyre_stint_number': optimal_strategy.iloc[i]['tyre_stint_number_list'],
                              'tyre_description': optimal_strategy.iloc[i]['tyre_description_list'],
                              'tyre_status': optimal_strategy.iloc[i]['tyre_status_list'],
                              'lap_time': optimal_strategy.iloc[i]['lap_times_adjusted']})
    mu.plot_laptimes(results_df, 'Optimal Strategy #{0}'.format(i))




# ~~~~~~~~~~~~~ Finding optimal strategies with a grid search across multiple tyre deg variables ~~~~~~~~~~~~~
laps_complete = 3
total_race_laps = 52
pitstop_time = 24
current_tyre_description = 'Soft'
current_tyre_age = 3
need_to_use_different_tyre = True

max_pitstops = 2
base_laptime = 76.52
fuel_laptime_correction = 0.06
detailed_logs = False
batch_size = 50000

# The following parameters will define the shape of the quadratic tyre deg curve
tyre_deg_curve = mu.tyre_deg_curve_quadratic
param1_range = np.arange(0.1, 0.2, 0.01) # Parameter 1 will be called 'k' later, and is the multiplicative factor by which each harder step of tyre compound has less degradation.
param2_range = np.arange(0.8, 1.3, 0.1) # Parameter 2 will be called 'd' later, and is the difference in seconds per lap between each step of tyre compound, without any degradation factor.

# Cross join to get all the possible combinations of parameters
parameter_grid = np.transpose([np.tile(param1_range, len(param2_range)), np.repeat(param2_range, len(param1_range))])
optimal_number_pitstops = []
optimal_tyre_choice = []

# Get the optimal strategy for these different parameter ranges
for i in range(0,len(parameter_grid)):
    row = parameter_grid[i]
    k = row[0]
    d = row[1]
    results_df = mu.find_optimum_strategy(laps_complete, total_race_laps, pitstop_time, current_tyre_description,
                                          current_tyre_age, need_to_use_different_tyre, tyre_deg_curve,
                                          base_laptime, fuel_laptime_correction, max_pitstops, batch_size, detailed_logs,
                                          soft_tyre_deg_quadratic = 0.012, soft_tyre_deg_linear = -0.01,
                                          medium_tyre_pace_deficit = d, medium_tyre_deg_quadratic = 0.012*k, medium_tyre_deg_linear = -0.01*k,
                                          hard_tyre_pace_deficit = 2*d, hard_tyre_deg_quadratic = 0.012*(k**2), hard_tyre_deg_linear = -0.01*(k**2))
    if results_df["pitstop_1_lap"][0] == -1:
        optimal_number_pitstops.append(0)
        optimal_tyre_choice.append(str(results_df["pitstop_0_tyre"][0]))
    elif results_df["pitstop_2_lap"][0] == -1:
        optimal_number_pitstops.append(1)
        optimal_tyre_choice.append(str(results_df["pitstop_0_tyre"][0]) + " " + str(results_df["pitstop_1_tyre"][0]))
    else:
        optimal_number_pitstops.append(2)
        alphabetical_tyres = [str(results_df["pitstop_1_tyre"][0]),str(results_df["pitstop_2_tyre"][0])]
        alphabetical_tyres.sort()
        optimal_tyre_choice.append(str(results_df["pitstop_0_tyre"][0]) + " " + alphabetical_tyres[0] + " " + alphabetical_tyres[1])
    print("Finished optimising for k = {:.2f} and d = {:.1f}".format(k, d))

parameter_df = pd.DataFrame(parameter_grid, columns=['k', 'd'])
parameter_df = parameter_df.round({'k': 2, 'd': 1})
parameter_df["optimal_number_pitstops"] = optimal_number_pitstops
parameter_df["optimal_tyre_choice"] = optimal_tyre_choice
pivot_tab = parameter_df.pivot_table('optimal_number_pitstops', index='k', columns='d')
annotations = parameter_df.pivot_table('optimal_tyre_choice', index='k', columns='d', aggfunc=lambda x: ' '.join(x))
sns.heatmap(pivot_tab, annot=annotations, annot_kws={"size": 7}, fmt='', cmap='Blues', cbar=False, linewidths=.3)
plt.xlabel("d")
plt.ylabel("k")
plt.title("Optimal strategy for various tyre parameters")
plt.show()
