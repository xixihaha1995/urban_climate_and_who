import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\vcwg_epw_confirmation'
p0 = 98320
sensor_height = 2.6
building_height = 15
start_time_with_spin_up = '2002-06-14 00:00:00'
v132_start_timewith_spin_up = '2002-06-15 00:00:00'
start_time = '2002-06-15 00:00:00'
end_time = '2002-06-17 23:00:00'
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
potential_temp_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profilesv132_Basel_MOST.txt')
potential_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(potential_temp_profile_hours, sensor_height)
potential_temp_profile_hours_height_spin_date = plt_tools.add_date_index(potential_temp_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
potential_temp_profile_hours_height_K = potential_temp_profile_hours_height_spin_date.loc[start_time:end_time]

# Real temperature, T = Potential temperature * (presProf / p0) ** (0.286)
# read the pressure profile
presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profilesv132_Basel_MOST.txt')
presProf_hour_height_spin = plt_tools.certain_height_one_day(presProf_hour, sensor_height)
presProf_hour_height_spin_date = plt_tools.add_date_index(presProf_hour_height_spin, start_time_with_spin_up,
                                                          vcwg_output_time_interval_seconds)
presProf_hour_height = presProf_hour_height_spin_date.loc[start_time:end_time]
real_temp_profile_hours_height_K = potential_temp_profile_hours_height_K * (presProf_hour_height / p0) ** (0.286)

#v132_tUrban_Basel_MOST
v132_turban_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\v132_Tu_profiles_hourly.txt')
v132_turban_profile_hours_height_spin = plt_tools.certain_height_one_day(v132_turban_profile_hours, sensor_height)
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

# K to C
potential_temp_profile_hours_height_C = potential_temp_profile_hours_height_K - 273.15
real_temp_profile_hours_height_C = real_temp_profile_hours_height_K - 273.15
v132_turban_profile_hours_height_C = v132_turban_profile_hours_height_K - 273.15
v132_trural_profile_hours_height_C = v132_trural_profile_hours_height_K - 273.15

all_df_names = ['measurements_hour', '(v132_Basel_BUBBLE.epw)potential_temp','(v132_Basel_BUBBLE.epw)real_temp',
                'v132_turban_potential_temp','v132_trural_potential_temp']
all_df = [measurements_hour_C, potential_temp_profile_hours_height_C, real_temp_profile_hours_height_C,
            v132_turban_profile_hours_height_C, v132_trural_profile_hours_height_C]
all_in_one_df = plt_tools.merge_multiple_df(all_df, all_df_names)

case_txt = (f"Air Temperature at {sensor_height}m\n", "Date", "Temperature (K)")
plt_tools.general_time_series_comparision(all_in_one_df,case_txt)



