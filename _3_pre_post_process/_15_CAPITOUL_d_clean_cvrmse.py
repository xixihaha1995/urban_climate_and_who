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
if os.path.exists(os.path.join(save_intermediate_path, "comparison.csv")):
    comparison = pd.read_csv(os.path.join(save_intermediate_path, "comparison.csv"), index_col=0)
else:
    comparison = measurements.copy()
    prediction_columns = ['Rural_Bypass_NCDC_RealEPW', 'Rural_Bypass_ECCC_RealEPW']

    domain_height = 20
    vcwg_heights_profile = [0.5 + i for i in range(domain_height)]
    sensor_heights = [1.2]
    target_interval = [30]
    p0 = 100000
    selected_prediction_idx = [1]
    cases_outputs = r'..\\_2_cases_input_outputs\\_07_vancouver\\'

    this_case = 'Rural_ECCC'
    prediction_folder_prefix = cases_outputs + this_case
    bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
    bypass_filename_prefix = 'ver1.1\\Vancouver_Rural_ECCC_Bypass'
    epw_staPre_Pa_all = measurements['ECCC_staPre_Pa']
    epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
    bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
        plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                      vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                        compare_start_time,compare_end_time, epw_staPre_Pa_all,
                                                   mapped_indices = selected_prediction_idx,)
    comparison['Rural_Bypass_ECCC_RealEPW'] = bypass_real_epw_lst_C[0]


    this_case = 'Rural_Refined_SmallOffice_4C_CorrectTime'
    prediction_folder_prefix = cases_outputs + this_case
    bypass_folder = f'{prediction_folder_prefix}\\c_vcwg_ep_saving'
    bypass_filename_prefix = 'ver1.1\\Vancouver_Rural_Interpolated_ByPass_2008Jul'
    epw_staPre_Pa_all = measurements['NCDC_staPre_Pa']
    epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
    bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C = \
        plt_tools.excel_to_direct_real_p0_real_epw(bypass_filename_prefix, bypass_folder,
                                                      vcwg_heights_profile, sensor_heights, target_interval,p0,
                                                        compare_start_time,compare_end_time, epw_staPre_Pa_all,
                                                   mapped_indices = selected_prediction_idx,)
    comparison['Rural_Bypass_NCDC_RealEPW'] = bypass_real_epw_lst_C[0]
    # save measurements into intermediate folder
    comparison.to_csv(os.path.join(save_intermediate_path, "comparison.csv"))

# 4. Calculate CVRMSE, Plot the comparison
# 'Air Temperature (1.20m)', 'Air Temperature (26.00m)',
#        'Acoustic Temperature (Corrected) (28.80m)', 'ECCC_dryBulAirTemp_C',
#        'ECCC_staPre_Pa', 'NCDC_dryBulAirTemp_C', 'NCDC_staPre_Pa',
#        'TopForcing_Bypass_ECCC_RealEPW'
all_df_column_names = ['Urban1.2m', 'Rural_NCDC', 'Rural_ECCC',
                       'Rural_Bypass_NCDC_RealEPW',
                       'Rural_Bypass_ECCC_RealEPW']
rural_ncdc_cvrmse = plt_tools.bias_rmse_r2(comparison['Air Temperature (1.20m)'], comparison['NCDC_dryBulAirTemp_C'],
                                           'Rural_NCDC')
rural_eccc_cvrmse = plt_tools.bias_rmse_r2(comparison['Air Temperature (1.20m)'], comparison['ECCC_dryBulAirTemp_C'],
                                             'Rural_ECCC')
bypass_ncdc_cvrmse = plt_tools.bias_rmse_r2(comparison['Air Temperature (1.20m)'],
                                            comparison['Rural_Bypass_NCDC_RealEPW'],
                                            'Rural_Bypass_NCDC_RealEPW')
bypass_eccc_cvrmse = plt_tools.bias_rmse_r2(comparison['Air Temperature (1.20m)'],
                                            comparison['Rural_Bypass_ECCC_RealEPW'],
                                            'Rural_Bypass_ECCC_RealEPW')

all_df_lst = [comparison['Air Temperature (1.20m)'],
              comparison['NCDC_dryBulAirTemp_C'], comparison['ECCC_dryBulAirTemp_C'],
              comparison['Rural_Bypass_NCDC_RealEPW'],
              comparison['Rural_Bypass_ECCC_RealEPW']]

all_df_in_one = plt_tools.merge_multiple_df(all_df_lst, all_df_column_names)
all_df_in_one.index = pd.to_datetime(all_df_in_one.index)

case_name = (f"July_2008, Urban Heat Island Effect", "Date", "Temperature (C)")
txt_info = [case_name, rural_ncdc_cvrmse, rural_eccc_cvrmse, bypass_ncdc_cvrmse
            , bypass_eccc_cvrmse]
plt_tools.general_time_series_comparision(all_df_in_one, txt_info)
