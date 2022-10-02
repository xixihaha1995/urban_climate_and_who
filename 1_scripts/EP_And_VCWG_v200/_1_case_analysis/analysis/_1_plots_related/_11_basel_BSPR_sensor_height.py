import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
measure_results_folder = r'..\..\cases\_0_measurements\BUBBLE'
original_prediction_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\vcwg_saving'

IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-06-14 22:00:00'

original_filename = 'only_vcwg'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 100000
ue1_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]
ue1_2p6_height_col_idx = 0
re1_col_idx = 7

# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{measure_results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_10min_clean = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
# select the 0th column as the comparison data
urban_all_sites_10min_c_compare = urban_all_sites_10min_clean[compare_start_time:compare_end_time]

original_potential_10min_c_compare, original_real_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(original_filename, original_prediction_results_folder, p0,
                                         heights_profile, ue1_heights,compare_start_time,compare_end_time,
                                         Sensor_Height_Bool = False)

urban_2p6_10min_c_compare = urban_all_sites_10min_c_compare.iloc[:,ue1_2p6_height_col_idx]

plt_tools.which_height_match_urban_sensor(urban_2p6_10min_c_compare, original_potential_10min_c_compare)
