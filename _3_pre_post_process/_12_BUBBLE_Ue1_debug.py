import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# Hardcoded parameters
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-07-09 22:00:00'
measure_results_folder = r'..\_4_measurements\BUBBLE'
save_intermediate_path = r'..\_4_measurements\BUBBLE\Intermediate_Ue1_LiteratureAlbedo'
if not os.path.exists(save_intermediate_path):
    os.makedirs(save_intermediate_path)

tower_ori_filename = r'BUBBLE_Ue1_Urban.csv'

prediction_folder_prefix = r'..\\_2_cases_input_outputs\\_05_Basel_BSPR_ue1\\MidRiseApart_4C_Rural_LiteratureAlbedo'
only_ep_folder= f'{prediction_folder_prefix}\\a_ep_saving'
only_vcwg_folder = f'{prediction_folder_prefix}\\b_vcwg_saving'
bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
epw_atm_filename = r'Basel'
only_ep_filename_prefix = 'BUBBLE_Ue1_LiteratureAlbedo_only_ep_2002_June'
only_vcwg_filename_prefix = 'BUBBLE_Ue1_Rural_only_vcwg_2002_June'
bypass_filename_prefix = 'ver1.1\\Ue1_bypass'

domain_height = 50
vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
p0 = 100000
# ue1_sensor_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]
ue1_selected_sensor_heights = [2.6, 13.9]
target_interval_mins = [10,10]
# Read measured then convert to target interval
tower_ori_10min = pd.read_csv(os.path.join(measure_results_folder, tower_ori_filename),
                                            index_col=0, parse_dates=True)
tower_ori_10min = tower_ori_10min.loc[compare_start_time:compare_end_time]
#save
tower_ori_10min.to_csv(os.path.join(save_intermediate_path, tower_ori_filename))

epw_all_dirty = pd.read_csv( f'{prediction_folder_prefix}\\{epw_atm_filename}.epw',
                                 skiprows= 8, header= None, index_col=None,)
epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
                                               start_time = compare_start_time)
epw_all_clean.to_csv(os.path.join(save_intermediate_path, f'{epw_atm_filename}.csv'))
epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]
epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
epw_staPre_Pa_all.index = epw_staPre_Pa_all.index.strftime('%m-%d %H:%M:%S')

# Measurements: 2,6,20m measured data, convert to target interval (hourly, 5min)
measure_tdb_c_2p6_10min = tower_ori_10min.iloc[:, 0]
measure_tdb_c_13p9_10min = tower_ori_10min.iloc[:, 1]
# save
measure_tdb_c_2p6_10min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_2p6_10min.csv'))
measure_tdb_c_13p9_10min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_13p9_10min.csv'))


# Predictions: Read only EP, get 1.2, 26(target interval), to direct_predict
debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
only_ep_degC_2p6_13p9_10min = debug_only_ep_5min.iloc[:, 4].resample('10T').mean() - 273.15
only_ep_degC_2p6_13p9_10min.to_csv(os.path.join(save_intermediate_path, 'only_ep_degC_2p6_13p9_10min.csv'))
# Read only VCWG (2, 6, 20m), to direct_predict, real_p0, real_epw
only_vcwg_direct_lst_C, only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(only_vcwg_filename_prefix, only_vcwg_folder,
                                               vcwg_heights_profile, ue1_selected_sensor_heights, target_interval_mins,p0,
                                               compare_start_time,compare_end_time, epw_staPre_Pa_all)
# Read Bypass (2, 6, 20m), to direct_predict, real_p0, real_epw
bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                  vcwg_heights_profile, ue1_selected_sensor_heights, target_interval_mins,p0,
                                                    compare_start_time,compare_end_time, epw_staPre_Pa_all)
#pickle
with open(os.path.join(save_intermediate_path, 'only_vcwg_direct_lst_C.pickle'), 'wb') as f:
    pickle.dump(only_vcwg_direct_lst_C, f)
with open(os.path.join(save_intermediate_path, 'only_vcwg_real_p0_lst_C.pickle'), 'wb') as f:
    pickle.dump(only_vcwg_real_p0_lst_C, f)
with open(os.path.join(save_intermediate_path, 'only_vcwg_real_epw_lst_C.pickle'), 'wb') as f:
    pickle.dump(only_vcwg_real_epw_lst_C, f)
with open(os.path.join(save_intermediate_path, 'bypass_direct_lst_C.pickle'), 'wb') as f:
    pickle.dump(bypass_direct_lst_C, f)
with open(os.path.join(save_intermediate_path, 'bypass_real_p0_lst_C.pickle'), 'wb') as f:
    pickle.dump(bypass_real_p0_lst_C, f)
with open(os.path.join(save_intermediate_path, 'bypass_real_epw_lst_C.pickle'), 'wb') as f:
    pickle.dump(bypass_real_epw_lst_C, f)
# For 1.2m, 26m:
#   For ep, vcwg, bypass:
#       calculate the CVRMSE for direct_predict, real_p0, real_epw
#Create one 3d array, 0th axis dims: 2 (1.2 m, 26m heights) ,
# 1st axis dims: 3 (ep, vcwg, bypass), 2nd axis dims: 3 (direct_predict, real_p0, real_epw)
cvrmse_3d = plt_tools.organize_Vancouver_cvrmse(measure_tdb_c_2p6_10min,measure_tdb_c_13p9_10min,
                             only_ep_degC_2p6_13p9_10min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C)
print("CVRMSE (%), (OnlyEP, OnlyVCWG, Bypass)")
print(f'2.6m, direct: {cvrmse_3d[0, :, 0]}')
print(f'2.6m, real_p0: {cvrmse_3d[0, :, 1]}')
print(f'2.6m, real_epw: {cvrmse_3d[0, :, 2]}')
print(f'13.9m, direct: {cvrmse_3d[1, :, 0]}')
print(f'13.9m, real_p0: {cvrmse_3d[1, :, 1]}')
print(f'13.9m, real_epw: {cvrmse_3d[1, :, 2]}')

debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_folder}\\{only_vcwg_filename_prefix}_debugging_canyon.xlsx',
                                     header=0, index_col=0)
debug_bypass = pd.read_excel(f'{bypass_folder}\\{bypass_filename_prefix}_debugging_canyon.xlsx',
                                header=0, index_col=0)
plt_tools.save_TwoHeights_debug(measure_tdb_c_2p6_10min,measure_tdb_c_13p9_10min,
                             only_ep_degC_2p6_13p9_10min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
                              prediction_folder_prefix,
                              debug_only_ep_5min, debug_only_vcwg_5min, debug_bypass,
                                sheet_names=ue1_selected_sensor_heights,
                                debug_file_name = epw_atm_filename)

plt_tools.shared_x_plot(prediction_folder_prefix, canyon_name=f'{str(ue1_selected_sensor_heights[0])}m Real EPW',
                        debug_file_name = epw_atm_filename)