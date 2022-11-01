import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# 1. Config the Comparison Parameters, Read, Save.
# 2. Save the associated Urban
# 3. Specify which "model" to compare, only-vcwg1, only-vcwg2, or Bypass (TempProfile, PresProfile)
# 4. Save the organized comparison data

# 1. Config the Comparison Parameters
compare_start_time = '2008-07-01 00:00:00'
compare_end_time = '2008-07-31 23:00:00'
processed_measurements = 'Vancouver_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
measure_results_folder = r'..\_4_measurements\Vancouver'
save_intermediate_path = measure_results_folder + '\Intermediate' + '\which_epw'

# 2. Get the associated Urban and Rural
if os.path.exists(os.path.join(measure_results_folder, processed_measurements)):
    print('The processed measurements already exists, skip the processing.')
    measurements = pd.read_csv(os.path.join(measure_results_folder, processed_measurements), index_col=0)
else:
    urban_path = r'SSDTA_all_30min.csv'
    urban = pd.read_csv(os.path.join(measure_results_folder, urban_path), index_col=0)
    urban.index = pd.to_datetime(urban.index)
    urban = urban[compare_start_time:compare_end_time]

    repeated_index = urban.index[urban.index.duplicated()]
    urban = urban.drop(repeated_index)
    target_idx = pd.date_range(start=urban.index[0], end=urban.index[-1], freq= '30min')
    missing_index = target_idx.difference(urban.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    urban = urban.reindex(target_idx)

    ECCC_path = os.path.join(measure_results_folder, 'ECCC_Vancouver_2008.epw')
    ECCC_epw = pd.read_csv(ECCC_path,
                           skiprows= 8, header= None, index_col=None,)
    ECCC_epw = plt_tools.clean_epw(ECCC_epw,start_time = compare_start_time)
    ECCC_dryBulAirTemp_C_all = ECCC_epw.iloc[:, 6]
    ECCC_dryBulAirTemp_C_all.index = pd.to_datetime(ECCC_dryBulAirTemp_C_all.index)
    ECCC_dryBulAirTemp_C_hourly = ECCC_dryBulAirTemp_C_all.loc[compare_start_time:compare_end_time]
    ECCC_dryBulAirTemp_C_30min = ECCC_dryBulAirTemp_C_hourly.resample('30min').interpolate()

    ECCC_staPre_Pa_all = ECCC_epw.iloc[:, 9]
    ECCC_staPre_Pa_all.index = pd.to_datetime(ECCC_staPre_Pa_all.index)
    ECCC_staPre_Pa_all = ECCC_staPre_Pa_all.resample('30min').interpolate()


    NCDC_path = os.path.join(measure_results_folder, 'NCDC_Vancouver_2008.epw')
    NCDC_epw = pd.read_csv(NCDC_path,
                                        skiprows= 8, header= None, index_col=None,)
    NCDC_epw = plt_tools.clean_epw(NCDC_epw,
                                                    start_time = compare_start_time)
    NCDC_dryBulAirTemp_C_all = NCDC_epw.iloc[:, 6]
    NCDC_dryBulAirTemp_C_all.index = pd.to_datetime(NCDC_dryBulAirTemp_C_all.index)
    NCDC_dryBulAirTemp_C_hourly = NCDC_dryBulAirTemp_C_all.loc[compare_start_time:compare_end_time]
    NCDC_dryBulAirTemp_C_30min = NCDC_dryBulAirTemp_C_hourly.resample('30min').interpolate()

    NCDC_staPre_Pa_all = NCDC_epw.iloc[:, 9]
    NCDC_staPre_Pa_all.index = pd.to_datetime(NCDC_staPre_Pa_all.index)
    NCDC_staPre_Pa_all = NCDC_staPre_Pa_all.resample('30min').interpolate()
    # Measurements has the following columns:
    # urban(3 columns), 'ECCC_dryBulAirTemp_C', 'ECCC_staPre_Pa', 'NCDC_dryBulAirTemp_C', 'NCDC_staPre_Pa'
    # append urban with ECCC and NCDC
    measurements = urban.copy()
    measurements['ECCC_dryBulAirTemp_C'] = ECCC_dryBulAirTemp_C_30min
    measurements['ECCC_staPre_Pa'] = ECCC_staPre_Pa_all
    measurements['NCDC_dryBulAirTemp_C'] = NCDC_dryBulAirTemp_C_30min
    measurements['NCDC_staPre_Pa'] = NCDC_staPre_Pa_all
    measurements.to_csv(os.path.join(measure_results_folder, processed_measurements))

# 3. Specify which "model" to compare, Rural, only-vcwg1, only-vcwg2, or Bypass (TempProfile, PresProfile)
prediction_columns = ['TopForcing_Bypass_NCDC_RealEPW', 'TopForcing_Bypass_ECCC_RealEPW']

domain_height = 20
vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
sensor_heights = [1.2]
target_interval = [30]
p0 = 100000
selected_prediction_idx = [1]
cases_outputs = r'..\\_2_cases_input_outputs\\_07_vancouver\\'

this_case = 'TopForcing_ECCC'
prediction_folder_prefix = cases_outputs + this_case
bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
bypass_filename_prefix = 'ver1.1\\Vancouver_TopForcing_ECCC_Bypass'
epw_staPre_Pa_all = measurements['ECCC_staPre_Pa']
bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
    plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                  vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                    compare_start_time,compare_end_time, epw_staPre_Pa_all,
                                               mapped_indices = selected_prediction_idx,)
measurements['TopForcing_Bypass_ECCC_RealEPW'] = bypass_real_epw_lst_C[0]

# this_case = 'TopForcing_NCDC'
# prediction_folder_prefix = cases_outputs + this_case
# bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
# bypass_filename_prefix = 'ver1.1\\Vancouver_TopForcing_ECCC_Bypass'
# epw_staPre_Pa_all = measurements['ECCC_staPre_Pa']
# bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
#     plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
#                                                   vcwg_heights_profile, sensor_heights, target_interval,p0,
#                                                     compare_start_time,compare_end_time, epw_staPre_Pa_all,
#                                                mapped_indices = selected_prediction_idx,)
# measurements['TopForcing_Bypass_ECCC_RealEPW'] = bypass_real_epw_lst_C[0]


# prediction_folder_prefix = r'..\\_2_cases_input_outputs\\_07_vancouver\\Rural_Refined_SmallOffice_4C_CorrectTime'
# only_ep_folder= f'{prediction_folder_prefix}\\a_ep_saving'
# only_vcwg_folder = f'{prediction_folder_prefix}\\b_vcwg_saving'
# bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
# epw_atm_filename = r'Interpolated_Vancouver718920CorrectTime'
#
# only_ep_filename_prefix = 'Vancouver_RuralCorrectTime_only_ep_2008_July'
# only_vcwg_filename_prefix = 'Vancouver_Rural_CorrectTime_only_vcwg_2008_Jul'
# bypass_filename_prefix = 'ver1.1\\Vancouver_Rural_Interpolated_ByPass_2008Jul'
#

# p0 = 100000
# sensor_heights = [1.2, 26]
# target_interval = [30,30]
# selected_prediction_idx = [1,-1]
# # The rural data looks is like 5 hours later than actual time
# # Read measured then convert to target interval
# ss4_tower_ori_30min = pd.read_csv(os.path.join(measure_results_folder, ss4_tower_ori_filename),
#                                             index_col=0, parse_dates=True)
# #interpolate the missing data
# ss4_tower_ori_30min = ss4_tower_ori_30min.interpolate(method='linear')
# ss4_tower_ori_30min = ss4_tower_ori_30min.loc[compare_start_time:compare_end_time]
# epw_all_dirty = pd.read_csv( f'{prediction_folder_prefix}\\{epw_atm_filename}.epw',
#                                  skiprows= 8, header= None, index_col=None,)
# epw_all_clean = plt_tools.clean_epw(epw_all_dirty,
#                                                start_time = compare_start_time)
# epw_staPre_Pa_all = epw_all_clean.iloc[:, 9]
# epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
# epw_staPre_Pa_all.index = epw_staPre_Pa_all.index.strftime('%m-%d %H:%M:%S')
#
# epw_dryBulAirTemp_C_all = epw_all_clean.iloc[:, 6]
# epw_dryBulAirTemp_C_all.index = pd.to_datetime(epw_dryBulAirTemp_C_all.index)
# epw_dryBulAirTemp_C_hourly = epw_dryBulAirTemp_C_all.loc[compare_start_time:compare_end_time]
# # interpolate hourly data to 30 min
# epw_dryBulAirTemp_C_30min = epw_dryBulAirTemp_C_hourly.resample('30min').interpolate()
# # Measurements: 2,6,20m measured data, convert to target interval (hourly, 5min)
# measure_tdb_c_1p2m_30min = ss4_tower_ori_30min.iloc[:, 0]
# measure_tdb_c_26m_30min = ss4_tower_ori_30min.iloc[:, 1]
# # save
# if not os.path.exists(save_intermediate_path):
#     os.makedirs(save_intermediate_path)
# measure_tdb_c_1p2m_30min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_1p2m_30min.csv'))
# measure_tdb_c_26m_30min.to_csv(os.path.join(save_intermediate_path, 'measure_tdb_c_26m_30min.csv'))
#
#
# # Predictions: Read only EP, get 1.2, 26(target interval), to direct_predict
# debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
# only_ep_degC_1p2_26m_30min = debug_only_ep_5min.iloc[:, 4].resample('30T').mean() - 273.15
# only_ep_degC_1p2_26m_30min.to_csv(os.path.join(save_intermediate_path, 'only_ep_degC_1p2_26m_30min.csv'))
# # Read only VCWG (2, 6, 20m), to direct_predict, real_p0, real_epw
# only_vcwg_direct_lst_C, only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C = \
#     plt_tools.excel_to_direct_real_p0_real_epw(only_vcwg_filename_prefix, only_vcwg_folder,
#                                                vcwg_heights_profile, sensor_heights, target_interval,p0,
#                                                compare_start_time,compare_end_time, epw_staPre_Pa_all,
#                                                mapped_indices = selected_prediction_idx)
# # Read Bypass (2, 6, 20m), to direct_predict, real_p0, real_epw
# bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
#     plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
#                                                   vcwg_heights_profile, sensor_heights, target_interval,p0,
#                                                     compare_start_time,compare_end_time, epw_staPre_Pa_all,
#                                                mapped_indices = selected_prediction_idx,
#                                                )
# #pickle
# with open(os.path.join(save_intermediate_path, 'only_vcwg_direct_lst_C.pickle'), 'wb') as f:
#     pickle.dump(only_vcwg_direct_lst_C, f)
# with open(os.path.join(save_intermediate_path, 'only_vcwg_real_p0_lst_C.pickle'), 'wb') as f:
#     pickle.dump(only_vcwg_real_p0_lst_C, f)
# with open(os.path.join(save_intermediate_path, 'only_vcwg_real_epw_lst_C.pickle'), 'wb') as f:
#     pickle.dump(only_vcwg_real_epw_lst_C, f)
# with open(os.path.join(save_intermediate_path, 'bypass_direct_lst_C.pickle'), 'wb') as f:
#     pickle.dump(bypass_direct_lst_C, f)
# with open(os.path.join(save_intermediate_path, 'bypass_real_p0_lst_C.pickle'), 'wb') as f:
#     pickle.dump(bypass_real_p0_lst_C, f)
# with open(os.path.join(save_intermediate_path, 'bypass_real_epw_lst_C.pickle'), 'wb') as f:
#     pickle.dump(bypass_real_epw_lst_C, f)
# # For 1.2m, 26m:
# #   For ep, vcwg, bypass:
# #       calculate the CVRMSE for direct_predict, real_p0, real_epw
# #Create one 3d array, 0th axis dims: 2 (1.2 m, 26m heights) ,
# # 1st axis dims: 3 (ep, vcwg, bypass), 2nd axis dims: 3 (direct_predict, real_p0, real_epw)
# cvrmse_3d = plt_tools.organize_Vancouver_cvrmse(measure_tdb_c_1p2m_30min,measure_tdb_c_26m_30min,
#                              epw_dryBulAirTemp_C_30min,
#                              only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
#                              bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C)
# print("CVRMSE (%), (Rural, OnlyVCWG, Bypass)")
# print(f'1.2m, direct: {cvrmse_3d[0, :, 0]}')
# print(f'1.2m, real_p0: {cvrmse_3d[0, :, 1]}')
# print(f'1.2m, real_epw: {cvrmse_3d[0, :, 2]}')
# print(f'26m, direct: {cvrmse_3d[1, :, 0]}')
# print(f'26m, real_p0: {cvrmse_3d[1, :, 1]}')
# print(f'26m, real_epw: {cvrmse_3d[1, :, 2]}')
#
# debug_only_ep_5min = pd.read_excel(f'{only_ep_folder}\\{only_ep_filename_prefix}_debugging_canyon.xlsx', header=0, index_col=0)
# debug_only_vcwg_5min = pd.read_excel(f'{only_vcwg_folder}\\{only_vcwg_filename_prefix}_debugging_canyon.xlsx',
#                                      header=0, index_col=0)
# debug_bypass = pd.read_excel(f'{bypass_folder}\\{bypass_filename_prefix}_debugging_canyon.xlsx',
#                                 header=0, index_col=0)
# plt_tools.save_TwoHeights_debug(measure_tdb_c_1p2m_30min,measure_tdb_c_26m_30min,
#                              epw_dryBulAirTemp_C_30min,
#                              only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
#                              bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
#                               prediction_folder_prefix,
#                               debug_only_ep_5min, debug_only_vcwg_5min, debug_bypass,
#                                 debug_file_name = epw_atm_filename)
#
# plt_tools.shared_x_plot(prediction_folder_prefix, canyon_name='1p2m Direct',debug_file_name = epw_atm_filename)