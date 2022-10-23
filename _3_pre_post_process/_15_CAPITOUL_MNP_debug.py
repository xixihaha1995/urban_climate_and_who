import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# Hardcoded parameters
compare_start_time = '2004-06-01 00:00:00'
compare_end_time = '2004-06-30 23:00:00'
measure_results_folder = r'..\_4_measurements\CAPITOUL'
save_intermediate_path = r'..\_4_measurements\CAPITOUL\Intermediate_MNP_LiteratureIDF'
if not os.path.exists(save_intermediate_path):
    os.makedirs(save_intermediate_path)

urban_ori_filename = r'Urban_Pomme_Ori_Processed'

prediction_folder_prefix = r'..\_2_cases_input_outputs\_08_CAPITOUL\MediumOffice_4B_Literature_MNP'
only_ep_folder= f'{prediction_folder_prefix}\\a_ep_saving'
only_vcwg_folder = f'{prediction_folder_prefix}\\b_vcwg_saving'
bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
epw_atm_filename = r'newMondouzil_tdb_td_rh_P_2004'
ruralFilename = 'Rural_Mondouzil_Processed'

only_ep_filename_prefix = 'CAPITOUL_only_ep_2004'
only_vcwg_filename_prefix = 'CAPITOUL_2004_only_vcwg'
bypass_filename_prefix = 'ver1.1\\CAPITOUL_Bypass_2004'

domain_height = 60
vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
p0 = 100000
selected_sensor_heights = [7]
target_interval_mins = [5]
# Read measured then convert to target interval
if os.path.exists(f'{save_intermediate_path}\\{urban_ori_filename}.csv'):
    pomme_5min = pd.read_csv(os.path.join(save_intermediate_path, f'{urban_ori_filename}.csv'),
                             index_col=0, parse_dates=True)
    rural_MON_5min = pd.read_csv(os.path.join(save_intermediate_path, f'{ruralFilename}.csv'),
                                    index_col=0, parse_dates=True)
else:
    pomme_ori_1min = pd.read_csv(os.path.join(measure_results_folder, 'newUrban_Pomme_Ori_1_min.csv'),
                                                index_col=0, parse_dates=True)
    pomme_ori_1min = pomme_ori_1min[compare_start_time:compare_end_time]
    pomme_5min = pomme_ori_1min.resample('5T').mean()
    pomme_5min.to_csv(os.path.join(save_intermediate_path, f'{urban_ori_filename}.csv'))

    rural_MON_ori_1min = pd.read_csv(os.path.join(measure_results_folder, 'Rural_Mondouzil_Minute.csv'),
                                                index_col=0, parse_dates=True)
    rural_MON_ori_1min = rural_MON_ori_1min[compare_start_time:compare_end_time]
    rural_MON_5min = rural_MON_ori_1min.resample('5T').mean()
    rural_MON_5min.to_csv(os.path.join(save_intermediate_path, f'{ruralFilename}.csv'))

urban_MNP_19m_5min_tdb_c = pomme_5min.iloc[:, 2]
rural_MNP_19m_5min_tdb_c = rural_MON_5min.iloc[:, 1]

epw_all_dirty = pd.read_csv( f'{prediction_folder_prefix}\\{epw_atm_filename}.epw',
                                 skiprows= 8, header= None, index_col=None,)
epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
                                               start_time = compare_start_time)
epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]
epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
epw_staPre_Pa_all.index = epw_staPre_Pa_all.index.strftime('%m-%d %H:%M:%S')


# Read only VCWG (2, 6, 20m), to direct_predict, real_p0, real_epw
only_vcwg_direct_lst_C, only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(only_vcwg_filename_prefix, only_vcwg_folder,
                                               vcwg_heights_profile, selected_sensor_heights, target_interval_mins,p0,
                                               compare_start_time,compare_end_time, epw_staPre_Pa_all)
# Read Bypass (2, 6, 20m), to direct_predict, real_p0, real_epw
bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                  vcwg_heights_profile, selected_sensor_heights, target_interval_mins,p0,
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
# For height:
#   For ep, vcwg, bypass:
#       calculate the CVRMSE for direct_predict, real_p0, real_epw
#Create one 3d array, 0th axis dims: 2 (1.2 m, 26m heights) ,
# 1st axis dims: 3 (ep, vcwg, bypass), 2nd axis dims: 3 (direct_predict, real_p0, real_epw)
urbanLst = [urban_MNP_19m_5min_tdb_c]
cvrmse_3d = plt_tools.organize_CAPITOUL_MNP_cvrmse(urbanLst, rural_MNP_19m_5min_tdb_c,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C)
print("CVRMSE (%), (Rural, OnlyVCWG, Bypass)")
print(f'19m, direct: {cvrmse_3d[0, :, 0]}')
print(f'19m, real_p0: {cvrmse_3d[0, :, 1]}')
print(f'19m, real_epw: {cvrmse_3d[0, :, 2]}')

debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_folder}\\{only_vcwg_filename_prefix}_debugging_canyon.xlsx',
                                     header=0, index_col=0)
debug_bypass = pd.read_excel(f'{bypass_folder}\\{bypass_filename_prefix}_debugging_canyon.xlsx',
                                header=0, index_col=0)
plt_tools.save_OneOrTwoHeights_debug(urbanLst,rural_MNP_19m_5min_tdb_c,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
                              prediction_folder_prefix,
                              debug_only_ep_5min, debug_only_vcwg_5min, debug_bypass,
                                sheet_names=selected_sensor_heights,
                                debug_file_name = epw_atm_filename)

plt_tools.shared_x_plot(prediction_folder_prefix, canyon_name=f'{str(selected_sensor_heights[0])}m Real EPW',
                        debug_file_name = epw_atm_filename)