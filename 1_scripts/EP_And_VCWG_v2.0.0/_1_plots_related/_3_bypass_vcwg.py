# Read original profile (height, time, temperature)
# Read bypass profile (height, time, temperature)
import _0_all_plot_tools as plt_tools
results_folder = r'..\\Results'
original_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profilesBasel_MOST.txt')
bypass_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_bypass_Basel_MOST.txt')
original_24_hours = plt_tools.multiple_days_hour_data_to_one_day_hour_data(original_profile_hours)
bypass_24_hours = plt_tools.multiple_days_hour_data_to_one_day_hour_data(bypass_profile_hours)

#  6 height levels
heights = [3.6, 11.3, 14.7,17.9, 22.4,31.7]
original_6_heights = plt_tools.filter_df_with_new_heights(original_24_hours, heights)
bypass_6_heights = plt_tools.filter_df_with_new_heights(bypass_24_hours, heights)
# averaged RMSE for all heights
all_rmse = []
for heigh in heights:
    all_rmse.append(plt_tools.RMSE(original_6_heights.loc[heigh], bypass_6_heights.loc[heigh]))

# Plot
plt_tools.plot_24_hours_comparison_for_multiple_heights(original_6_heights, bypass_6_heights, heights, all_rmse)
