import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\\_2_saved\\BUBBLE'
profile_height = 2.6
start_time_with_spin_up = '2002-06-09 00:00:00'
start_time = '2002-06-10 00:00:00'
end_time = '2002-06-11 23:00:00'
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
# convert measurements C to K
measurements_hour_K = measurements_hour_C + 273.15

replicate_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profilesBasel_MOST.txt')
replicate_profile_hours_height_spin = plt_tools.certain_height_one_day(replicate_profile_hours, profile_height)
replicate_profile_hours_height_spin_date = plt_tools.add_date_index(replicate_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
replicate_profile_hours_height = replicate_profile_hours_height_spin_date.loc[start_time:end_time]

bypass_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_bypass_Basel_MOST.txt')
bypass_profile_hours_height_spin = plt_tools.certain_height_one_day(bypass_profile_hours, profile_height)
bypass_profile_hours_height_spin_date = plt_tools.add_date_index(bypass_profile_hours_height_spin,
                                                                start_time_with_spin_up,
                                                                vcwg_output_time_interval_seconds)
bypass_profile_hours_height = bypass_profile_hours_height_spin_date.loc[start_time:end_time]


all_df_names = ['measurements_hour', 'replicate_profile_hours_height', 'bypass_profile_hours_height']
all_df = [measurements_hour_K, replicate_profile_hours_height, bypass_profile_hours_height]
all_in_one_df = plt_tools.merge_multiple_df(all_df, all_df_names)

bias_rmse_r2_th_rep = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                         all_in_one_df['replicate_profile_hours_height'])
bias_rmse_r2_th_bypass = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
                                            all_in_one_df['bypass_profile_hours_height'])
case_txt = (f"Air Temperature at {profile_height}m\n", "Date", "Temperature (K)")
txt_info = [case_txt, bias_rmse_r2_th_rep, bias_rmse_r2_th_bypass]
plt_tools.plot_comparison_measurement_simulated(all_in_one_df,txt_info)



