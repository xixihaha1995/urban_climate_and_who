import os.path
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
measure_results_folder = r'..\_4_measurements\Vancouver'
only_vcwg_results_folder = r'..\_2_cases_input_outputs\_07_vancouver\vcwg_saving'
original_filename = 'only_vcwg'

which_ep = '(DOE_REF_SMALL_OFFICE)'
only_ep_results_folder = r'..\_2_cases_input_outputs\_07_vancouver\DOE_REF_SMALL_OFFICE\ep_saving'
bypass_predict_results_folder = r'..\_2_cases_input_outputs\_07_vancouver\DOE_REF_SMALL_OFFICE\vcwg_ep_saving'
bypass_filename_1p1 = '_Vancouver_bypass'

debug_processed_save_folder = r'..\_2_cases_input_outputs\_07_vancouver'

IOP_start_time = '2008-07-01 00:00:00'
IOP_end_time = '2008-07-31 23:30:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = IOP_start_time
v200_end_time = '2008-07-31 23:55:00'
compare_start_time = IOP_start_time
compare_end_time = '2008-07-31 23:00:00'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(8)]
p0 = 100300
hourly_p0 = False
vancouver_sensor_heights = [1.2, 26, 28.8]
selected_vancouver_sensor_idx = 0

epw_all_dirty = pd.read_csv( f'{debug_processed_save_folder}\\VancouverTopForcing.epw',
                                 skiprows= 8, header= None, index_col=None,)
epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
                                               start_time = compare_start_time)
# Basel_epw_all_clean shape: (8760, 35)
# select the 9th column as the comparison data
epw_staPre_Pa_all = epw_all_clean[9]

# Read air temperature measurements
if os.path.exists(f'{measure_results_folder}\\SSDTA_{compare_start_time[:7]}_30min.csv'):
    df_30min_TA_measure = pd.read_csv(f'{measure_results_folder}\\SSDTA_{compare_start_time[:7]}_30min.csv',
                                      header=0, index_col=0, parse_dates=True)
else:
    df_sens_dirty = pd.read_csv(f'{measure_results_folder}\\SSDTA_all_30min.csv', header=0, index_col=0, parse_dates=True)
    df_30min_TA_measure_all = plt_tools.data_cleaning(df_sens_dirty)
    df_30min_TA_measure = df_30min_TA_measure_all.loc[compare_start_time:compare_end_time]
    # save the selected comparison period
    df_30min_TA_measure.to_csv(f'{measure_results_folder}\\SSDTA_{compare_start_time[:7]}_30min.csv')

if hourly_p0:
    BEMCalc_potential_10min_c_compare, BEMCalc_real_10min_c_compare = \
        plt_tools.excel_to_potential_real_df(original_filename, only_vcwg_results_folder, p0,
                                             heights_profile, vancouver_sensor_heights, compare_start_time,
                                             compare_end_time, epw_staPre_Pa_all)
    bypass_ver1p1_path = f'{bypass_predict_results_folder}\\ver1.1'
    bypass_potential_10min_c_compare_ver1p1, bypass_real_10min_c_compare_ver1p1 = \
        plt_tools.excel_to_potential_real_df(bypass_filename_1p1, bypass_ver1p1_path, p0, heights_profile,
                                             vancouver_sensor_heights, compare_start_time,
                                             compare_end_time, epw_staPre_Pa_all)
else:
    BEMCalc_potential_10min_c_compare, BEMCalc_real_10min_c_compare = \
        plt_tools.excel_to_potential_real_df(original_filename, only_vcwg_results_folder, p0,
                                             heights_profile, vancouver_sensor_heights,compare_start_time,compare_end_time)
    bypass_ver1p1_path = f'{bypass_predict_results_folder}\\ver1.1'
    bypass_potential_10min_c_compare_ver1p1, bypass_real_10min_c_compare_ver1p1 = \
        plt_tools.excel_to_potential_real_df(bypass_filename_1p1, bypass_ver1p1_path, p0, heights_profile,
                                             vancouver_sensor_heights,compare_start_time,compare_end_time)
urban_selected_10min_c, original_real_selected_10min_c,\
    bypass_real_selected_10min_c_ver1p1 = \
    df_30min_TA_measure.iloc[:,selected_vancouver_sensor_idx], \
    BEMCalc_real_10min_c_compare.iloc[:,selected_vancouver_sensor_idx], \
    bypass_real_10min_c_compare_ver1p1.iloc[:,selected_vancouver_sensor_idx]

debug_only_ep_5min = pd.read_excel(f'{only_ep_results_folder}\\only_ep_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_results_folder}\\only_vcwg_debugging_canyon.xlsx', header=0, index_col=0)
debug_bypass_ver1p1_5min = pd.read_excel(f'{bypass_predict_results_folder}\\ver1.1\\{bypass_filename_1p1}_debugging_canyon.xlsx',
                                header=0, index_col=0)
debug_only_ep_10min = plt_tools._xmin_to_ymin(debug_only_ep_5min,
                                              original_time_interval_min = 5,target_time_interval_min = 30)
debug_only_vcwg_10min = plt_tools._xmin_to_ymin(debug_only_vcwg_5min,
                                                original_time_interval_min = 5,target_time_interval_min = 30)
debug_bypass_ver1p1_10min = plt_tools._xmin_to_ymin(debug_bypass_ver1p1_5min,
                                                    original_time_interval_min = 5,target_time_interval_min = 30)

#debugging based plot
plt_tools.why_bypass_overestimated(debug_processed_save_folder,
                                   urban_selected_10min_c, original_real_selected_10min_c,
                                   bypass_real_selected_10min_c_ver1p1,
                                   debug_only_ep_10min, debug_only_vcwg_10min,debug_bypass_ver1p1_10min,
                                   which_ep,
                                   mean_bld_temp= False)