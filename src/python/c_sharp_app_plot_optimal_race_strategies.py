import modelling_utilities as mu
import sys
import pandas as pd

# ~~~~~~~~~~~~~ Input parameters ~~~~~~~~~~~~~ #
raw_args_list = sys.argv[1].split(',')  # argv[1] is a comma separated list arg1,arg2,...,arg17; the split command generates the corresponding Python list
# The following parameters define the current racing scenario
laps_complete = int(raw_args_list[0])  # Full racing laps already completed
total_race_laps = int(raw_args_list[1])
pitstop_time = float(raw_args_list[2])  # Total extra time in seconds to make a pitstop
current_tyre_description = str(raw_args_list[3])  # Either 'Soft', 'Medium' or 'Hard'
current_tyre_age = int(raw_args_list[4])  # Total laps the current tyre has already done
need_to_use_different_tyre = bool(raw_args_list[5])  # Boolean, depending on whether you still need to use a different compound of tyre before the end of the race
max_pitstops = int(raw_args_list[6]) # Here you can choose a maximum number of pitstops. The find_optimium_strategy function has a absolute maximum of 3 that it can handle, and by default this parameter is set to be 3.
base_laptime = float(raw_args_list[7]) # The race laptime (measured in seconds) from a brand new Soft tyre with 1 lap of fuel remaining. By default, this is 0. (N.B. this parameter only affects the size of the laptimes - the choice of optimal strategy remains the same regardless of this parameter.)
fuel_laptime_correction = float(raw_args_list[8]) # The improvement in laptime, measured in seconds per lap (assumed to be linear), from decreasing fuel load. This is assuming all other variables (including tyre deg) are constant. By default, this is 0. (N.B. this parameter only affects the size of the laptimes - the choice of optimal strategy remains the same regardless of this parameter.)

# The following parameters define the shape of the assumed quadratic tyre deg curve
tyre_deg_curve = mu.tyre_deg_curve_quadratic
soft_tyre_deg_quadratic = float(raw_args_list[9])
soft_tyre_deg_linear = float(raw_args_list[10])
medium_tyre_pace_deficit = float(raw_args_list[11])
medium_tyre_deg_quadratic = float(raw_args_list[12])
medium_tyre_deg_linear = float(raw_args_list[13])
hard_tyre_pace_deficit = float(raw_args_list[14])
hard_tyre_deg_quadratic = float(raw_args_list[15])
hard_tyre_deg_linear = float(raw_args_list[16])


# ~~~~~~~~~~~~~ Finding & plotting optimal strategies with known tyre deg variables ~~~~~~~~~~~~~ #
detailed_logs = False # Boolean, whether or not to return extra detail on where the function is up to in the batching process. Mainly used for diagnostics and/or understanding any processes taking a long time.
batch_size = 50000 # Controls the number of potential strategies that are computed over in a single batch. If you have issues with memory, then reduce this batch size.

optimal_strategy = mu.find_optimum_strategy(laps_complete, total_race_laps, pitstop_time, current_tyre_description,
                                            current_tyre_age, need_to_use_different_tyre, tyre_deg_curve,
                                            base_laptime, fuel_laptime_correction, max_pitstops, batch_size, detailed_logs,
                                            soft_tyre_deg_quadratic = soft_tyre_deg_quadratic, soft_tyre_deg_linear = soft_tyre_deg_linear,
                                            medium_tyre_pace_deficit = medium_tyre_pace_deficit, medium_tyre_deg_quadratic = medium_tyre_deg_quadratic, medium_tyre_deg_linear = medium_tyre_deg_linear,
                                            hard_tyre_pace_deficit = hard_tyre_pace_deficit, hard_tyre_deg_quadratic = hard_tyre_deg_quadratic, hard_tyre_deg_linear = hard_tyre_deg_linear
                                          )
for i in range(0, len(optimal_strategy.index)):
    results_df = pd.DataFrame({'lap_number': optimal_strategy.iloc[i]['lap_number_list'],
                               'tyre_stint_number': optimal_strategy.iloc[i]['tyre_stint_number_list'],
                               'tyre_description': optimal_strategy.iloc[i]['tyre_description_list'],
                               'tyre_status': optimal_strategy.iloc[i]['tyre_status_list'],
                               'lap_time': optimal_strategy.iloc[i]['lap_times_adjusted']})
    mu.plot_laptimes(results_df, 'Optimal Strategy #{0}'.format(i))
