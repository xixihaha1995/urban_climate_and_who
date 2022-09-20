import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\vcwg_potential_real_confirmation'
sensor_height = 2.6
building_height = 15
start_time_with_spin_up = '2002-06-09 00:00:00'
start_time = '2002-06-10 00:00:00'
end_time = '2002-06-19 23:00:00'
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

potential_temp_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profilesreplicate_Basel_MOST.txt')
potential_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(potential_temp_profile_hours, sensor_height)
potential_temp_profile_hours_height_spin_date = plt_tools.add_date_index(potential_temp_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
potential_temp_profile_hours_height_K = potential_temp_profile_hours_height_spin_date.loc[start_time:end_time]

potential_temp_profile_hours_build_avg_spin = plt_tools.average_temperature_below_height(potential_temp_profile_hours,
                                                                                         building_height)
potential_temp_profile_hours_build_avg_spin_date = plt_tools.add_date_index(potential_temp_profile_hours_build_avg_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
potential_temp_profile_hours_build_avg_K = potential_temp_profile_hours_build_avg_spin_date.loc[start_time:end_time]

# read the real temperature profile time series from csv
real_temp_profile_hours_T = pd.read_csv(f'{results_folder}\\th_real.csv', header=None, index_col=None)
# transpose
real_temp_profile_hours = real_temp_profile_hours_T.T
#add height index from potential_profile_hours
real_temp_profile_hours_height = real_temp_profile_hours.set_index(potential_temp_profile_hours.index)
#select height
real_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(real_temp_profile_hours_height, sensor_height)
# add date index
real_temp_profile_hours_height_spin_date = plt_tools.add_date_index(real_temp_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
# select time period
real_temp_profile_hours_height_K = real_temp_profile_hours_height_spin_date.loc[start_time:end_time]

# K to C
potential_temp_profile_hours_height_C = potential_temp_profile_hours_height_K - 273.15
real_temp_profile_hours_height_C = real_temp_profile_hours_height_K - 273.15
potential_temp_profile_hours_build_avg_C = potential_temp_profile_hours_build_avg_K - 273.15

all_df_names = ['measurements_hour', 'potential_temp_profile_hours_height',
                'real_temp_profile_hours_height', 'potential_temp_profile_hours_build_avg']
all_df = [measurements_hour_C, potential_temp_profile_hours_height_C,
          real_temp_profile_hours_height_C, potential_temp_profile_hours_build_avg_C]
all_in_one_df = plt_tools.merge_multiple_df(all_df, all_df_names)

# bias_rmse_r2_th_rep = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
#                                          all_in_one_df['replicate_profile_hours_height'])
# bias_rmse_r2_th_bypass = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
#                                             all_in_one_df['bypass_profile_hours_height'])
case_txt = (f"Air Temperature at {sensor_height}m\n", "Date", "Temperature (K)")
txt_info = [case_txt, "something"]
plt_tools.plot_comparison_measurement_simulated(all_in_one_df,txt_info)



