import modelling_utilities as mu
import sys

yr = int(sys.argv[1])
rnd = int(sys.argv[2])
dvr = sys.argv[3]

results_df = mu.download_laptimes(yr, rnd, dvr)
mu.plot_laptimes(results_df)
