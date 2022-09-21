import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\vcwg_epw_confirmation'
p0 = 98320
sensor_height = 3.5
v132_urban_sensor_height = 7
building_height = 15
start_time_with_spin_up = '2002-06-14 00:00:00'
v132_start_timewith_spin_up = '2002-06-15 00:00:00'
start_time = '2002-06-15 00:00:00'
end_time = '2002-06-27 23:00:00'
vcwg_output_time_interval_seconds = 3600

# Read air temperature measurements
measurements_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
measurements_all_sites_hour = plt_tools.clean_bubble_iop(measurements_all_sites_10min_dirty)
# select the 0th column as the comparison data
measurements_hour_height = measurements_all_sites_hour.iloc[:,0]
# select the time period
measurements_hour_C = measurements_hour_height[start_time:end_time]

# ORIGINAL_th_profilesBasel_MOST
# th_profilesBasel_MOST
# BaselEPW_th_profilesBasel_MOST
potential_temp_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_v132_BaselEPW_Basel_MOST.txt')
potential_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(potential_temp_profile_hours,
                                                                                      sensor_height)
potential_temp_profile_hours_height_spin_date = plt_tools.add_date_index(potential_temp_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
potential_temp_profile_hours_height_K = potential_temp_profile_hours_height_spin_date.loc[start_time:end_time]

# Real temperature, T = Potential temperature * (presProf / p0) ** (0.286)
# read the pressure profile
presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profiles_v132_BaselEPW_Basel_MOST.txt')
presProf_hour_height_spin = plt_tools.certain_height_one_day(presProf_hour, sensor_height)
presProf_hour_height_spin_date = plt_tools.add_date_index(presProf_hour_height_spin, start_time_with_spin_up,
                                                          vcwg_output_time_interval_seconds)
presProf_hour_height = presProf_hour_height_spin_date.loc[start_time:end_time]
real_temp_profile_hours_height_K = potential_temp_profile_hours_height_K * (presProf_hour_height / p0) ** (0.286)

v200_BaselEPW_th_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_v200_BaselEPW_Basel_MOST.txt')
v200_BaselEPW_th_profile_hours_height_spin = plt_tools.certain_height_one_day(v200_BaselEPW_th_profile_hours, sensor_height)
v200_BaselEPW_th_profile_hours_height_spin_date = plt_tools.add_date_index(v200_BaselEPW_th_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v200_BaselEPW_th_profile_hours_height_K = v200_BaselEPW_th_profile_hours_height_spin_date.loc[start_time:end_time]

v200_BaselEPW_presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profiles_v200_BaselEPW_Basel_MOST.txt')
v200_BaselEPW_presProf_hour_height_spin = plt_tools.certain_height_one_day(v200_BaselEPW_presProf_hour, sensor_height)
v200_BaselEPW_presProf_hour_height_spin_date = plt_tools.add_date_index(v200_BaselEPW_presProf_hour_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v200_BaselEPW_presProf_hour_height = v200_BaselEPW_presProf_hour_height_spin_date.loc[start_time:end_time]
v200_BaselEPW_real_temp_profile_hours_height_K = v200_BaselEPW_th_profile_hours_height_K * \
                                                 (v200_BaselEPW_presProf_hour_height / p0) ** (0.286)

v200_ERA5_JunEpw_th_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\ORIGINAL_th_profilesBasel_MOST.txt')
v200_ERA5_JunEpw_th_profile_hours_height_spin = plt_tools.certain_height_one_day(v200_ERA5_JunEpw_th_profile_hours, sensor_height)
v200_ERA5_JunEpw_th_profile_hours_height_spin_date = plt_tools.add_date_index(v200_ERA5_JunEpw_th_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v200_ERA5_JunEpw_th_profile_hours_height_K = v200_ERA5_JunEpw_th_profile_hours_height_spin_date.loc[start_time:end_time]

#v132_tUrban_Basel_MOST
v132_turban_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\v132_Tu_profiles_hourly.txt')
v132_turban_profile_hours_height_spin = plt_tools.certain_height_one_day(v132_turban_profile_hours, v132_urban_sensor_height)
v132_turban_profile_hours_height_spin_date = plt_tools.add_date_index(v132_turban_profile_hours_height_spin,
                                                                    v132_start_timewith_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v132_turban_profile_hours_height_K = v132_turban_profile_hours_height_spin_date.loc[start_time:end_time]
#v132_tRural_Basel_MOST
v132_trural_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\v132_Tr_profiles_hourly.txt')
v132_trural_profile_hours_height_spin = plt_tools.certain_height_one_day(v132_trural_profile_hours, sensor_height)
v132_trural_profile_hours_height_spin_date = plt_tools.add_date_index(v132_trural_profile_hours_height_spin,
                                                                    v132_start_timewith_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v132_trural_profile_hours_height_K = v132_trural_profile_hours_height_spin_date.loc[start_time:end_time]

#v132_epw
v132_epw_hours = plt_tools.read_text_as_csv(f'{results_folder}\\v132_Tepw_hourly.txt')
v132_epw_hours_date = plt_tools.add_date_index(v132_epw_hours, v132_start_timewith_spin_up,
                                               vcwg_output_time_interval_seconds)
v132_epw_hours_K = v132_epw_hours_date.loc[start_time:end_time]

# K to C
potential_temp_profile_hours_height_C = potential_temp_profile_hours_height_K - 273.15
real_temp_profile_hours_height_C = real_temp_profile_hours_height_K - 273.15
v132_turban_profile_hours_height_C = v132_turban_profile_hours_height_K - 273.15
v132_trural_profile_hours_height_C = v132_trural_profile_hours_height_K - 273.15
v132_epw_hours_C = v132_epw_hours_K - 273.15
v200_BaselEPW_th_profile_hours_height_C = v200_BaselEPW_th_profile_hours_height_K - 273.15
v200_BaselEPW_real_temp_profile_hours_height_C = v200_BaselEPW_real_temp_profile_hours_height_K - 273.15
v200_ERA5_JunEpw_th_profile_hours_height_C = v200_ERA5_JunEpw_th_profile_hours_height_K - 273.15


all_df_names = ['measurements_hour',
                '(v132_Basel_BUBBLE.epw)potential_temp', '(v132_Basel_BUBBLE.epw)real_temp',
                'v200_BaselEPW_th_profile_hours_height_C', 'v200_BaselEPW_real_temp_profile_hours_height_C',
                'v200_ERA5_JunEpw_th_profile_hours_height_C',
                'v132_turban_potential_temp']
all_df = [measurements_hour_C,
          potential_temp_profile_hours_height_C, real_temp_profile_hours_height_C,
          v200_BaselEPW_th_profile_hours_height_C, v200_BaselEPW_real_temp_profile_hours_height_C,
          v200_ERA5_JunEpw_th_profile_hours_height_C,
          v132_turban_profile_hours_height_C]
all_in_one_df = plt_tools.merge_multiple_df(all_df, all_df_names)

mbe_rmse_r2_potent = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                            all_in_one_df['(v132_Basel_BUBBLE.epw)potential_temp'],
                                            '(v132_Basel_BUBBLE.epw)potential_temp')
mbe_rmse_r2_real = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                            all_in_one_df['(v132_Basel_BUBBLE.epw)real_temp'],
                                            '(v132_Basel_BUBBLE.epw)real_temp')
mbe_rmse_r2_v200_BaselEPW_th = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                                        all_in_one_df['v200_BaselEPW_th_profile_hours_height_C'],
                                                        'v200_BaselEPW_th_profile_hours_height_C')
mbe_rmse_r2_v200_BaselEPW_real = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                                        all_in_one_df['v200_BaselEPW_real_temp_profile_hours_height_C'],
                                                        'v200_BaselEPW_real_temp_profile_hours_height_C')
mbe_rmse_r2_v200_ERA5_JunEpw_th = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                                        all_in_one_df['v200_ERA5_JunEpw_th_profile_hours_height_C'],
                                                         'v200_ERA5_JunEpw_th_profile_hours_height_C')
mbe_rmse_r2_turban = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                            all_in_one_df['v132_turban_potential_temp'],
                                            'v132_turban_potential_temp')
case_txt = (f"Air Temperature at {sensor_height}m\n", "Date", "Temperature (C)")
txt_info = [case_txt,
            mbe_rmse_r2_potent, mbe_rmse_r2_real,
            mbe_rmse_r2_v200_BaselEPW_th, mbe_rmse_r2_v200_BaselEPW_real,
            mbe_rmse_r2_v200_ERA5_JunEpw_th, mbe_rmse_r2_turban]
plt_tools.general_time_series_comparision(all_in_one_df,txt_info)



