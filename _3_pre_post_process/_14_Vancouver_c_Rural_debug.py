import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# Hardcoded parameters
compare_start_time = '2008-07-01 00:00:00'
compare_end_time = '2008-07-31 23:00:00'
measure_results_folder = r'..\_4_measurements\Vancouver'
save_intermediate_path = r'..\_4_measurements\Vancouver\Intermediate_RuralCorrectTimeCorrectIDF'
ss4_tower_ori_filename = r'SSDTA_2008-07_30min.csv'

prediction_folder_prefix = r'..\\_2_cases_input_outputs\\_07_vancouver\\Rural_Refined_SmallOffice_4C_CorrectTime'
only_ep_folder= f'{prediction_folder_prefix}\\a_ep_saving'
only_vcwg_folder = f'{prediction_folder_prefix}\\b_vcwg_saving'
bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
epw_atm_filename = r'Interpolated_Vancouver718920CorrectTime'

only_ep_filename_prefix = 'Vancouver_RuralCorrectTime_only_ep_2008_July'
only_vcwg_filename_prefix = 'Vancouver_Rural_CorrectTime_only_vcwg_2008_Jul'
bypass_filename_prefix = 'ver1.1\\Vancouver_Rural_Interpolated_ByPass_2008Jul'

domain_height = 20
vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
p0 = 100000
sensor_heights = [1.2, 26]
target_interval = [30,30]
selected_prediction_idx = [1,-1]
# The rural data looks is like 5 hours later than actual time
# Read measured then convert to target interval
ss4_tower_ori_30min = pd.read_csv(os.path.join(measure_results_folder, ss4_tower_ori_filename),
                                            index_col=0, parse_dates=True)
ss4_tower_ori_30min = ss4_tower_ori_30min.loc[compare_start_time:compare_end_time]
epw_all_dirty = pd.read_csv( f'{prediction_folder_prefix}\\{epw_atm_filename}.epw',
                                 skiprows= 8, header= None, index_col=None,)
epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
                                               start_time = compare_start_time)
epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]
epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
epw_staPre_Pa_all.index = epw_staPre_Pa_all.index.strftime('%m-%d %H:%M:%S')

epw_dryBulAirTemp_C_all = epw_all_clean.iloc[:, 6]
epw_dryBulAirTemp_C_all.index = pd.to_datetime(epw_dryBulAirTemp_C_all.index)
epw_dryBulAirTemp_C_hourly = epw_dryBulAirTemp_C_all.loc[compare_start_time:compare_end_time]
# interpolate hourly data to 30 min
epw_dryBulAirTemp_C_30min = epw_dryBulAirTemp_C_hourly.resample('30min').interpolate()
# Measurements: 2,6,20m measured data, convert to target interval (hourly, 5min)
measure_tdb_c_1p2m_30min = ss4_tower_ori_30min.iloc[:, 0]
measure_tdb_c_26m_30min = ss4_tower_ori_30min.iloc[:, 1]
# save
if not os.path.exists(save_intermediate_path):
    os.makedirs(save_intermediate_path)
measure_tdb_c_1p2m_30min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_1p2m_30min.csv'))
measure_tdb_c_26m_30min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_26m_30min.csv'))


# Predictions: Read only EP, get 1.2, 26(target interval), to direct_predict
debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
only_ep_degC_1p2_26m_30min = debug_only_ep_5min.iloc[:, 4].resample('30T').mean() - 273.15
only_ep_degC_1p2_26m_30min.to_csv(os.path.join(save_intermediate_path, 'only_ep_degC_1p2_26m_30min.csv'))
# Read only VCWG (2, 6, 20m), to direct_predict, real_p0, real_epw
only_vcwg_direct_lst_C, only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(only_vcwg_filename_prefix, only_vcwg_folder,
                                               vcwg_heights_profile, sensor_heights, target_interval,p0,
                                               compare_start_time,compare_end_time, epw_staPre_Pa_all,
                                               mapped_indices = selected_prediction_idx)
# Read Bypass (2, 6, 20m), to direct_predict, real_p0, real_epw
bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                  vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                    compare_start_time,compare_end_time, epw_staPre_Pa_all,
                                               mapped_indices = selected_prediction_idx,
                                               )
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
cvrmse_3d = plt_tools.organize_Vancouver_cvrmse(measure_tdb_c_1p2m_30min,measure_tdb_c_26m_30min,
                             epw_dryBulAirTemp_C_30min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C)
print("CVRMSE (%), (Rural, OnlyVCWG, Bypass)")
print(f'1.2m, direct: {cvrmse_3d[0, :, 0]}')
print(f'1.2m, real_p0: {cvrmse_3d[0, :, 1]}')
print(f'1.2m, real_epw: {cvrmse_3d[0, :, 2]}')
print(f'26m, direct: {cvrmse_3d[1, :, 0]}')
print(f'26m, real_p0: {cvrmse_3d[1, :, 1]}')
print(f'26m, real_epw: {cvrmse_3d[1, :, 2]}')

debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_folder}\\{only_vcwg_filename_prefix}_debugging_canyon.xlsx',
                                     header=0, index_col=0)
debug_bypass = pd.read_excel(f'{bypass_folder}\\{bypass_filename_prefix}_debugging_canyon.xlsx',
                                header=0, index_col=0)
plt_tools.save_TwoHeights_debug(measure_tdb_c_1p2m_30min,measure_tdb_c_26m_30min,
                             epw_dryBulAirTemp_C_30min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
                              prediction_folder_prefix,
                              debug_only_ep_5min, debug_only_vcwg_5min, debug_bypass,
                                debug_file_name = epw_atm_filename)

plt_tools.shared_x_plot(prediction_folder_prefix, canyon_name='1p2m Direct',debug_file_name = epw_atm_filename)