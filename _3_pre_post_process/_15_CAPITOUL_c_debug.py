import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# Hardcoded parameters
compare_start_time = '2004-06-01 00:00:00'
compare_end_time = '2004-06-30 23:00:00'
measure_results_folder = r'..\_4_measurements\CAPITOUL'
zone7_ori_filename = r'Mini_Zone7_Ori_12_min.csv'
Pomme_ori_filename= r'Pomme_Ori_1_min.csv'
only_ep_folder= r'..\_2_cases_input_outputs\_08_CAPITOUL\DOE_Ref_MediumOffice_4B\ep_saving'
only_vcwg_folder = r'..\_2_cases_input_outputs\_08_CAPITOUL\DOE_Ref_MediumOffice_4B\vcwg_saving'
bypass_folder = r'..\_2_cases_input_outputs\_08_CAPITOUL\DOE_Ref_MediumOffice_4B\vcwg_ep_saving'
epw_atm_filename = r'Mondouzil_tdb_td_rh_P_2004'
only_ep_filename_prefix = 'CAPITOUL_only_ep_2004'
only_vcwg_filename_prefix = 'CAPITOUL_2004_only_vcwg'
bypass_filename_prefix = 'ver1.1\CAPITOUL_Bypass_2004_minutely'
debug_processed_save_folder = r'..\_2_cases_input_outputs\_08_CAPITOUL\DOE_Ref_MediumOffice_4B'
domain_height = 60
vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
p0 = 100000
sensor_heights = [2, 6, 20]
target_interval = [10,10,5]
# Read measured(Zone7, Pomme), then convert to target interval (hourly, 5min)
if os.path.exists(os.path.join(measure_results_folder, 'Mini_Zone7_Processed_10min.csv')):
    zone7_hourly = pd.read_csv(os.path.join(measure_results_folder, 'Mini_Zone7_Processed_10min.csv'),
                                                index_col=0, parse_dates=True)
    pomme_5min = pd.read_csv(os.path.join(measure_results_folder, 'Pomme_Processed_5min.csv'),
                                                index_col=0, parse_dates=True)
    epw_all_clean = pd.read_csv(os.path.join(measure_results_folder, f'{epw_atm_filename}.csv'),
                                                index_col=0, parse_dates=True)
    epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]
    measure_tdb_c_2m_6m_10min = pd.read_csv(os.path.join(measure_results_folder, 'measure_tdb_c_2m_6m_10min.csv'),
                                                index_col=0, parse_dates=True)
    measure_tdb_c_20m_5min = pd.read_csv(os.path.join(measure_results_folder, 'measure_tdb_c_20m_5min.csv'),
                                                index_col=0, parse_dates=True)
    only_ep_degC_2_6_10min = pd.read_csv(os.path.join(measure_results_folder, 'only_ep_degC_2_6_10min.csv'),
                                                index_col=0, parse_dates=True)
    only_ep_degC_20_5min = pd.read_csv(os.path.join(measure_results_folder, 'only_ep_degC_20_5min.csv'),
                                                index_col=0, parse_dates=True)
    only_vcwg_direct_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'only_vcwg_direct_lst_C.pickle'), 'rb'))
    only_vcwg_real_p0_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'only_vcwg_real_p0_lst_C.pickle'), 'rb'))
    only_vcwg_real_epw_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'only_vcwg_real_epw_lst_C.pickle'), 'rb'))
    bypass_direct_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'bypass_direct_lst_C.pickle'), 'rb'))
    bypass_real_p0_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'bypass_real_p0_lst_C.pickle'), 'rb'))
    bypass_real_epw_lst_C = pickle.load(open(os.path.join(measure_results_folder, 'bypass_real_epw_lst_C.pickle'), 'rb'))
else:
    zone7_ori_12min = pd.read_csv(os.path.join(measure_results_folder, zone7_ori_filename),
                                                index_col=0, parse_dates=True)
    zone7_ori_12min = zone7_ori_12min[compare_start_time:compare_end_time]
    # resample 12min to 10min, fill the missing value with interpolation
    zone7_1min = zone7_ori_12min.resample('1T').interpolate()
    zone7_10min = zone7_1min.resample('10T').mean()
    zone7_10min.to_csv(os.path.join(measure_results_folder, 'Mini_Zone7_Processed_10min.csv'))
    pomme_ori_1min = pd.read_csv(os.path.join(measure_results_folder, Pomme_ori_filename),
                                                index_col=0, parse_dates=True)
    pomme_ori_1min = pomme_ori_1min[compare_start_time:compare_end_time]
    pomme_5min = pomme_ori_1min.resample('5T').mean()
    pomme_5min.to_csv(os.path.join(measure_results_folder, 'Pomme_Processed_5min.csv'))

    epw_all_dirty = pd.read_csv( f'{debug_processed_save_folder}\\{epw_atm_filename}.epw',
                                     skiprows= 8, header= None, index_col=None,)
    epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
                                                   start_time = compare_start_time)
    epw_all_clean.to_csv(os.path.join(measure_results_folder, f'{epw_atm_filename}.csv'))
    epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]

# Measurements: 2,6,20m measured data, convert to target interval (hourly, 5min)
    measure_tdb_c_2m_6m_10min = zone7_10min.iloc[:, 1]
    measure_tdb_c_20m_5min = pomme_5min.iloc[:, 2]
    # save
    measure_tdb_c_2m_6m_10min.to_csv(os.path.join(measure_results_folder, 'measure_tdb_c_2m_6m_10min.csv'))
    measure_tdb_c_20m_5min.to_csv(os.path.join(measure_results_folder, 'measure_tdb_c_20m_5min.csv'))
# Predictions: Read only EP, get 2, 6, 20(target interval), to direct_predict
    debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
    only_ep_degC_2_6_10min = debug_only_ep_5min.iloc[:, 4].resample('10T').mean() - 273.15
    only_ep_degC_20_5min = debug_only_ep_5min.iloc[:, 4] - 273.15
    only_ep_degC_20_5min.to_csv(os.path.join(measure_results_folder, 'only_ep_degC_20_5min.csv'))
    only_ep_degC_2_6_10min.to_csv(os.path.join(measure_results_folder, 'only_ep_degC_2_6_10min.csv'))
    # Read only VCWG (2, 6, 20m), to direct_predict, real_p0, real_epw
    only_vcwg_direct_lst_C, only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C = \
        plt_tools.excel_to_direct_real_p0_real_epw(only_vcwg_filename_prefix, only_vcwg_folder,
                                                   vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                   compare_start_time,compare_end_time, epw_staPre_Pa_all)
    # Read Bypass (2, 6, 20m), to direct_predict, real_p0, real_epw
    bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
        plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                      vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                        compare_start_time,compare_end_time, epw_staPre_Pa_all)
    #pickle
    with open(os.path.join(measure_results_folder, 'only_vcwg_direct_lst_C.pickle'), 'wb') as f:
        pickle.dump(only_vcwg_direct_lst_C, f)
    with open(os.path.join(measure_results_folder, 'only_vcwg_real_p0_lst_C.pickle'), 'wb') as f:
        pickle.dump(only_vcwg_real_p0_lst_C, f)
    with open(os.path.join(measure_results_folder, 'only_vcwg_real_epw_lst_C.pickle'), 'wb') as f:
        pickle.dump(only_vcwg_real_epw_lst_C, f)
    with open(os.path.join(measure_results_folder, 'bypass_direct_lst_C.pickle'), 'wb') as f:
        pickle.dump(bypass_direct_lst_C, f)
    with open(os.path.join(measure_results_folder, 'bypass_real_p0_lst_C.pickle'), 'wb') as f:
        pickle.dump(bypass_real_p0_lst_C, f)
    with open(os.path.join(measure_results_folder, 'bypass_real_epw_lst_C.pickle'), 'wb') as f:
        pickle.dump(bypass_real_epw_lst_C, f)
# For 2, 6, 20m:
#   For ep, vcwg, bypass:
#       calculate the CVRMSE for direct_predict, real_p0, real_epw
#Create one 3d array, 0th axis dims: 3 (2, 6, 20 m heights) ,
# 1st axis dims: 3 (ep, vcwg, bypass), 2nd axis dims: 3 (direct_predict, real_p0, real_epw)
cvrmse_3d = plt_tools.organize_CAPITOUL_cvrmse(measure_tdb_c_2m_6m_10min,measure_tdb_c_20m_5min,
                             only_ep_degC_2_6_10min,only_ep_degC_20_5min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C)
print("CVRMSE (%), (OnlyEP, OnlyVCWG, Bypass)")
print(f'2m, direct: {cvrmse_3d[0, :, 0]}')
print(f'2m, real_p0: {cvrmse_3d[0, :, 1]}')
print(f'2m, real_epw: {cvrmse_3d[0, :, 2]}')
print(f'6m, direct: {cvrmse_3d[1, :, 0]}')
print(f'6m, real_p0: {cvrmse_3d[1, :, 1]}')
print(f'6m, real_epw: {cvrmse_3d[1, :, 2]}')
print(f'20m, direct: {cvrmse_3d[2, :, 0]}')
print(f'20m, real_p0: {cvrmse_3d[2, :, 1]}')
print(f'20m, real_epw: {cvrmse_3d[2, :, 2]}')
debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_folder}\\{only_vcwg_filename_prefix}_debugging_canyon.xlsx',
                                     header=0, index_col=0)
debug_bypass = pd.read_excel(f'{bypass_folder}\\{bypass_filename_prefix}_debugging_canyon.xlsx',
                                header=0, index_col=0)
plt_tools.save_CAPITOUL_debug(measure_tdb_c_2m_6m_10min,measure_tdb_c_20m_5min,
                             only_ep_degC_2_6_10min,only_ep_degC_20_5min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
                              debug_processed_save_folder,
                              debug_only_ep_5min, debug_only_vcwg_5min, debug_bypass)

plt_tools.shared_x_plot(debug_processed_save_folder, canyon_name='2m Direct')