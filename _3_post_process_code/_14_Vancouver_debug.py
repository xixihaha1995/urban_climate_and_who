import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
measure_results_folder = r'..\_2_cases_input_outputs\_0_measurements\BUBBLE'
only_vcwg_results_folder = r'..\_2_cases_input_outputs\_06_Basel_BSPA_ue2\vcwg_saving'
which_ep = '(M3ing, No Cooling)'
only_ep_results_folder = r'..\_2_cases_input_outputs\_06_Basel_BSPA_ue2\refining_M3ing\ep_saving'
bypass_predict_results_folder = r'..\_2_cases_input_outputs\_06_Basel_BSPA_ue2\refining_M3ing\vcwg_ep_saving'
debug_processed_save_folder = r'..\_2_cases_input_outputs\_06_Basel_BSPA_ue2'

IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-07-09 22:00:00'
bypass_filename_1p1 = '_BSPA_bypass_refining_M3ing'
original_filename = 'only_vcwg'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 100000
ue2_heights_dup = [3, 15.8, 3, 15.8, 22.9, 27.8, 32.9]
ue2_heights = [3, 15.8, 22.90, 27.80, 32.90]
selected_ue2_sensor_idx = 0
re1_col_idx = 7
# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{measure_results_folder}\\BUBBLE_BSPA_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=17)
# clean the measurements
urban_all_sites_10min_clean_dup = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
urban_all_sites_10min_clean = plt_tools.remove_dup_BUBBLE_Ue2(urban_all_sites_10min_clean_dup,
                                                              ue2_heights_dup, ue2_heights)
# select the 0th column as the comparison data
urban_all_sites_10min_c_compare = urban_all_sites_10min_clean[compare_start_time:compare_end_time]

original_potential_10min_c_compare, original_real_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(original_filename, only_vcwg_results_folder, p0,
                                         heights_profile, ue2_heights,compare_start_time,compare_end_time)
bypass_ver1p1_path = f'{bypass_predict_results_folder}\\ver1.1'
bypass_potential_10min_c_compare_ver1p1, bypass_real_10min_c_compare_ver1p1 = \
    plt_tools.excel_to_potential_real_df(bypass_filename_1p1, bypass_ver1p1_path, p0, heights_profile, ue2_heights,
                                            compare_start_time,compare_end_time)
urban_selected_10min_c, original_real_selected_10min_c,\
    bypass_real_selected_10min_c_ver1p1 = \
    urban_all_sites_10min_c_compare.iloc[:,selected_ue2_sensor_idx], \
    original_real_10min_c_compare.iloc[:,selected_ue2_sensor_idx], \
    bypass_real_10min_c_compare_ver1p1.iloc[:,selected_ue2_sensor_idx]

debug_only_ep_5min = pd.read_excel(f'{only_ep_results_folder}\\only_ep_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_results_folder}\\only_vcwg_debugging_canyon.xlsx', header=0, index_col=0)
debug_bypass_ver1p1_5min = pd.read_excel(f'{bypass_predict_results_folder}\\ver1.1\\{bypass_filename_1p1}_debugging_canyon.xlsx',
                                header=0, index_col=0)
debug_only_ep_10min = plt_tools._5min_to_10min(debug_only_ep_5min)
debug_only_vcwg_10min = plt_tools._5min_to_10min(debug_only_vcwg_5min)
debug_bypass_ver1p1_10min = plt_tools._5min_to_10min(debug_bypass_ver1p1_5min)

#debugging based plot
plt_tools.why_bypass_overestimated(debug_processed_save_folder,
                                   urban_selected_10min_c, original_real_selected_10min_c,
                                   bypass_real_selected_10min_c_ver1p1,
                                   debug_only_ep_10min, debug_only_vcwg_10min,debug_bypass_ver1p1_10min,
                                   which_ep,
                                   mean_bld_temp= True)