import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
results_folder = r'..\_2_saved\BUBBLE_VCWG-EP-detailed'
IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-07-09 22:00:00'

v200_sensor_height = 2.6
heights_profile = [1.5 + i for i in range(14)]
p0 = 100000

ue1_col_idx = 0
re1_col_idx = 7
# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_10min_clean = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
# select the 0th column as the comparison data
urban_2p6_10min_ = urban_all_sites_10min_clean.iloc[:,ue1_col_idx]
urban_2p6_10min_c_compare = urban_2p6_10min_[compare_start_time:compare_end_time]

bypass_refining_th_profie_5min = pd.read_csv(f'{results_folder}\\bypass_refining_idf_canTempProfile.csv',
                                                header=0, index_col=0, parse_dates=True)
# from heights profile array, find the closed index for sensor height
sensor_idx = np.argmin(np.abs(np.array(heights_profile) - v200_sensor_height))
bypass_refining_th_sensor_5min = bypass_refining_th_profie_5min.iloc[:,sensor_idx]
bypass_refining_th_sensor_5min_K_compare = bypass_refining_th_sensor_5min[compare_start_time:compare_end_time]
bypass_refining_th_sensor_5min_K_compare_df = pd.DataFrame(bypass_refining_th_sensor_5min_K_compare)
bypass_refining_th_sensor_10min_K_compare = plt_tools._5min_to_10min(bypass_refining_th_sensor_5min_K_compare_df)
bypass_refining_th_sensor_10min_c_compare = bypass_refining_th_sensor_10min_K_compare - 273.15

bypass_refining_pres_profile_5min = pd.read_csv(f'{results_folder}\\bypass_refining_idf_canPresProfile.csv',
                                                header=0, index_col=0, parse_dates=True)
bypass_refining_pres_sensor_5min = bypass_refining_pres_profile_5min.iloc[:,sensor_idx]
bypass_refining_pres_sensor_5min_pa_compare = bypass_refining_pres_sensor_5min[compare_start_time:compare_end_time]
bypass_refining_pres_sensor_5min_pa_compare_df = pd.DataFrame(bypass_refining_pres_sensor_5min_pa_compare)
bypass_refining_pres_sensor_10min_pa_compare = plt_tools._5min_to_10min(bypass_refining_pres_sensor_5min_pa_compare_df)
# bypass_refining_pres_sensor_10min_pa_compare is df, convert to series
bypass_refining_pres_sensor_10min_pa_compare = bypass_refining_pres_sensor_10min_pa_compare.iloc[:,0]
bypass_refining_th_sensor_10min_c_compare_series = pd.Series(bypass_refining_th_sensor_10min_c_compare.iloc[:,0])
# real temperature  = potential temperature * (p0/p)^0.286
bypass_refining_real_sensor_10min_c_compare_arr = bypass_refining_th_sensor_10min_c_compare_series.values *\
                                              (bypass_refining_pres_sensor_10min_pa_compare.values/p0)**0.286
bypass_refining_real_sensor_10min_c_compare = pd.DataFrame(bypass_refining_real_sensor_10min_c_compare_arr,
                                                           index=bypass_refining_pres_sensor_10min_pa_compare.index,)
bypass_refining_real_sensor_10min_c_compare_series = pd.Series(bypass_refining_real_sensor_10min_c_compare.iloc[:,0])

original_th_profile_5min = pd.read_csv(f'{results_folder}\\vcwg_canTempProfile.csv',
                                                header=0, index_col=0, parse_dates=True)
original_th_sensor_5min = original_th_profile_5min.iloc[:,sensor_idx]
original_th_sensor_5min_K_compare = original_th_sensor_5min[compare_start_time:compare_end_time]
original_th_sensor_5min_K_compare_df = pd.DataFrame(original_th_sensor_5min_K_compare)
original_th_sensor_10min_K_compare = plt_tools._5min_to_10min(original_th_sensor_5min_K_compare_df)
original_th_sensor_10min_c_compare = original_th_sensor_10min_K_compare - 273.15

original_pres_profile_5min = pd.read_csv(f'{results_folder}\\vcwg_canPresProfile.csv',
                                                header=0, index_col=0, parse_dates=True)
original_pres_sensor_5min = original_pres_profile_5min.iloc[:,sensor_idx]
original_pres_sensor_5min_pa_compare = original_pres_sensor_5min[compare_start_time:compare_end_time]
original_pres_sensor_5min_pa_compare_df = pd.DataFrame(original_pres_sensor_5min_pa_compare)
original_pres_sensor_10min_pa_compare = plt_tools._5min_to_10min(original_pres_sensor_5min_pa_compare_df)
# original_pres_sensor_10min_pa_compare is df, convert to series
original_pres_sensor_10min_pa_compare = original_pres_sensor_10min_pa_compare.iloc[:,0]
original_th_sensor_10min_c_compare_series = pd.Series(original_th_sensor_10min_c_compare.iloc[:,0])
# real temperature  = potential temperature * (p0/p)^0.286
original_real_sensor_10min_c_compare_arr = original_th_sensor_10min_c_compare_series.values *\
                                                (original_pres_sensor_10min_pa_compare.values/p0)**0.286
original_real_sensor_10min_c_compare = pd.DataFrame(original_real_sensor_10min_c_compare_arr,
                                                    index=original_pres_sensor_10min_pa_compare.index,)
original_real_sensor_10min_c_compare_series = pd.Series(original_real_sensor_10min_c_compare.iloc[:,0])

# reshape the data

all_df_dc_lst = [urban_2p6_10min_c_compare,
                 original_th_sensor_10min_c_compare,
                 original_real_sensor_10min_c_compare,
                 bypass_refining_th_sensor_10min_c_compare,
                 bypass_refining_real_sensor_10min_c_compare]
all_df_dc_names = ['Urban(2.6 m)',
                   f'VCWG-Potential Temperature ({v200_sensor_height} m)',
                     f'VCWG-Real Temperature ({v200_sensor_height} m)',
                   f'VCWG(idf-Refining)-Potential Temperature ({v200_sensor_height} m)',
                   f'VCWG(idf-Refining)-Real Temperature ({v200_sensor_height} m)']
all_df_dc_in_one = plt_tools.merge_multiple_df(all_df_dc_lst, all_df_dc_names)

mbe_rmse_r2_th = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                        bypass_refining_th_sensor_10min_c_compare_series,
                                        'VCWG(idf-Refining)-Potential Temperature error')
mbe_rmse_r2_real = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                            bypass_refining_real_sensor_10min_c_compare_series,
                                            'VCWG(idf-Refining)-Real Temperature error')
mbe_rmse_r2_th_original = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                                original_th_sensor_10min_c_compare_series,
                                                'VCWG-Potential Temperature error')
mbe_rmse_r2_real_original = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                                    original_real_sensor_10min_c_compare_series,
                                                    'VCWG-Real Temperature error')


case_name = (f"{compare_start_time} to {compare_end_time}-Hourly Canyon Temperature. p0 {p0} pa",
             "Date", "Temperature (C)")
txt_info = [case_name, mbe_rmse_r2_th_original, mbe_rmse_r2_real_original,
            mbe_rmse_r2_th, mbe_rmse_r2_real]
# plot
plt_tools.general_time_series_comparision(all_df_dc_in_one, txt_info)



