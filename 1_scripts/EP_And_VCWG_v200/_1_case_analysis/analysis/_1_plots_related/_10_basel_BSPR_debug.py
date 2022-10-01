import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
measure_results_folder = r'..\..\cases\_0_measurements\BUBBLE'
original_prediction_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\vcwg_saving'
only_ep_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\ep_saving'
bypass_predict_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\refining_M2\vcwg_ep_saving'
all_in_one_saving_path = r'..\..\cases\_05_Basel_BSPR_ue1'
IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-06-14 22:00:00'

bypass_filename = '_BSPR_bypass_refining_M2'
original_filename = 'only_vcwg'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 100000
ue1_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]
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

mixed_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{measure_results_folder}\\BUBBLE_AT_IOP.txt',
                                                            header=0, index_col=0, skiprows=25)
# clean the measurements
mixed_all_sites_10min_clean = plt_tools.clean_bubble_iop(mixed_all_sites_10min_dirty,
                                                    start_time = IOP_start_time, end_time = IOP_end_time,
                                                    to_hourly= False)
rural_1p5_10min_c_compare = mixed_all_sites_10min_clean.iloc[:,re1_col_idx][compare_start_time:compare_end_time]

original_potential_10min_c_compare, original_real_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(original_filename, original_prediction_results_folder, p0,
                                         heights_profile, ue1_heights,compare_start_time,compare_end_time)
bypass_ver1_path = f'{bypass_predict_results_folder}\\ver1'
bypass_potential_10min_c_compare_ver1, bypass_real_10min_c_compare_ver1 = \
    plt_tools.excel_to_potential_real_df(bypass_filename, bypass_ver1_path, p0, heights_profile, ue1_heights,
                                            compare_start_time,compare_end_time)

# for each height, calculate the RMSE
original_potential_10min_c_compare_cvrmse = []
bypass_potential_10min_c_compare_ver1_cvrmse = []
for i in range(len(ue1_heights)):
    original_potential_10min_c_compare_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_all_sites_10min_c_compare.iloc[:,i], original_potential_10min_c_compare.iloc[:,i]))
    bypass_potential_10min_c_compare_ver1_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_all_sites_10min_c_compare.iloc[:,i], bypass_potential_10min_c_compare_ver1.iloc[:,i]))
# print the results
print(f"BSPR CVRMSE:{compare_start_time} to {compare_end_time}-10min Canyon Temperature. p0 {p0} pa")
for i in range(len(ue1_heights)):
    print(f'Height {ue1_heights[i]}m. Original: {original_potential_10min_c_compare_cvrmse[i]:.2f}'
            f' Bypass ver1: {bypass_potential_10min_c_compare_ver1_cvrmse[i]:.2f}')

#read only_ep oat, compare with urban and rural
only_ep_5min_K = pd.read_excel(f'{only_ep_results_folder}\\only_ep_debugging_canyon.xlsx', index_col=0, header=0)
only_ep_10min_K = plt_tools._5min_to_10min(only_ep_5min_K)
only_ep_10min_c = only_ep_10min_K - 273.15
only_ep_10min_c.index = pd.to_datetime(only_ep_10min_c.index)
# the 3rd column is OAT info
only_ep_oat_10min_c = only_ep_10min_c.iloc[:,3]
# urban_all_sites_10min_c_compare, the 0th column is the 2.6m height
urban_2p6_10min_c_compare = urban_all_sites_10min_c_compare.iloc[:,0]
merge_names = ['urban', 'rural', 'only_ep']
merge_df = [urban_2p6_10min_c_compare, rural_1p5_10min_c_compare, only_ep_oat_10min_c]
merge_df = pd.concat(merge_df, axis=1, keys=merge_names)

plt_general_info = [f'BSPR CVRMSE:{compare_start_time} to {compare_end_time}-10min Canyon Temperature. p0 {p0} pa',
                    'Date', 'Temperature (C)']
txt_info = [plt_general_info]
plt_tools.general_time_series_comparision(merge_df,txt_info, CVRMSE_display= False )
