import os, pickle
import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
# 1. Config the Comparison Parameters
compare_start_time = '2004-06-01 00:00:00'
compare_end_time = '2004-06-30 23:00:00'
processed_measurements = 'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
measure_results_folder = r'..\_4_measurements\CAPITOUL'
save_intermediate_path = measure_results_folder + '\Intermediate_CVRMSE10'
if not os.path.exists(save_intermediate_path):
    os.makedirs(save_intermediate_path)

# 2. Get the associated Urban and Rural
if os.path.exists(os.path.join(measure_results_folder, processed_measurements)):
    print('The processed measurements already exists, skip the processing.')
    measurements = pd.read_csv(os.path.join(measure_results_folder, processed_measurements), index_col=0)
else:
    urban_path = r'Urban_Pomme_Ori_1_min.csv'
    urban = pd.read_csv(os.path.join(measure_results_folder, urban_path), index_col=0)
    urban.index = pd.to_datetime(urban.index)
    urban_5min = urban.resample('5min').mean()
    urban_5min = urban_5min[compare_start_time:compare_end_time]
    rural_MON_ori_1min = pd.read_csv(os.path.join(measure_results_folder, 'Rural_Mondouzil_Minute.csv'),
                                     index_col=0, parse_dates=True)
    rural_MON_5min = rural_MON_ori_1min.resample('5T').mean()
    rural_MON_5min = rural_MON_5min[compare_start_time:compare_end_time]

    urban_MNP_19m_5min_tdb_c = urban_5min.iloc[:, 2]
    rural_MNP_19m_5min_tdb_c = rural_MON_5min.iloc[:, 1]
    rural_MNP_19m_5min_Sta_pa = rural_MON_5min.iloc[:, 2] * 100
    # create the measurements
    measurements = pd.DataFrame()
    measurements['Urban_MNP_19m_5min_tdb_c'] = urban_MNP_19m_5min_tdb_c
    measurements['Rural_MNP_1p2m_5min_tdb_c'] = rural_MNP_19m_5min_tdb_c
    measurements['Rural_MNP_1p2m_5min_Sta_pa'] = rural_MNP_19m_5min_Sta_pa
    measurements.to_csv(os.path.join(measure_results_folder, processed_measurements))

# 3. Specify which "model" to compare, Rural, only-vcwg1, only-vcwg2, or Bypass (TempProfile, PresProfile)
if os.path.exists(os.path.join(save_intermediate_path, "comparison.csv")):
    comparison = pd.read_csv(os.path.join(save_intermediate_path, "comparison.csv"), index_col=0)
else:
    comparison = measurements.copy()
    prediction_columns = ['Pres_Profile_Pa','Bypass_Direct', 'Bypass_Real_P0', 'Bypass_Real_EPW']

    domain_height = 50
    vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
    sensor_heights = [19]
    target_interval = [5]
    p0 = 100000
    selected_prediction_idx = [18]
    cases_outputs = r'..\\_2_cases_input_outputs\\_08_CAPITOUL\\'

    this_case = 'CVRMSE10'
    prediction_folder_prefix = cases_outputs + this_case
    bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
    bypass_filename_prefix = 'ver1.1\\CAPITOUL_Bypass_CVRMSE10'
    staPre_Pa_all = measurements['Rural_MNP_1p2m_5min_Sta_pa']
    staPre_Pa_all.index = pd.to_datetime(staPre_Pa_all.index)
    presProf_lst_Pa = bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
        plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                      vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                        compare_start_time,compare_end_time, staPre_Pa_all,
                                                   mapped_indices=selected_prediction_idx, )
    comparison['Pres_Profile_Pa'] = presProf_lst_Pa[0]
    comparison['Bypass_Direct'] = bypass_direct_lst_C[0]
    comparison['Bypass_Real_P0'] = bypass_real_p0_lst_C[0]
    comparison['Bypass_RealEPW'] = bypass_real_epw_lst_C[0]
    comparison.to_csv(os.path.join(save_intermediate_path, "comparison.csv"))

# 4. Calculate CVRMSE, Plot the comparison
# 'Air Temperature (1.20m)', 'Air Temperature (26.00m)',
#        'Acoustic Temperature (Corrected) (28.80m)', 'ECCC_dryBulAirTemp_C',
#        'ECCC_staPre_Pa', 'NCDC_dryBulAirTemp_C', 'NCDC_staPre_Pa',
#        'TopForcing_Bypass_ECCC_RealEPW'
all_df_column_names = ['Urban19m', 'Rural_MON',
                          'Bypass_Direct', 'Bypass_Real_P0', 'Bypass_RealEPW']
rural_mon_cvrmse = plt_tools.bias_rmse_r2(comparison['Urban_MNP_19m_5min_tdb_c'], comparison['Rural_MNP_1p2m_5min_tdb_c'],
                                           'Rural_MON')
bypass_direct_cvrmse = plt_tools.bias_rmse_r2(comparison['Urban_MNP_19m_5min_tdb_c'], comparison['Bypass_Direct'],
                                                  'Bypass_Direct')
bypass_real_p0_cvrmse = plt_tools.bias_rmse_r2(comparison['Urban_MNP_19m_5min_tdb_c'], comparison['Bypass_Real_P0'],
                                                    'Bypass_Real_P0')
bypass_real_epw_cvrmse = plt_tools.bias_rmse_r2(comparison['Urban_MNP_19m_5min_tdb_c'], comparison['Bypass_RealEPW'],
                                                        'Bypass_RealEPW')

all_df_lst = [comparison['Urban_MNP_19m_5min_tdb_c'], comparison['Rural_MNP_1p2m_5min_tdb_c'],
                comparison['Bypass_Direct'], comparison['Bypass_Real_P0'], comparison['Bypass_RealEPW']]

all_df_in_one = plt_tools.merge_multiple_df(all_df_lst, all_df_column_names)
all_df_in_one.index = pd.to_datetime(all_df_in_one.index)

case_name = (f"June 2004, CAPITOUL Urban Heat Island Effect", "Date", "Temperature (C)")
txt_info = [case_name, rural_mon_cvrmse, bypass_direct_cvrmse, bypass_real_p0_cvrmse, bypass_real_epw_cvrmse]
plt_tools.general_time_series_comparision(all_df_in_one, txt_info)
