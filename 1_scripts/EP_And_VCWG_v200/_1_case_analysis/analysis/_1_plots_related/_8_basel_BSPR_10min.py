import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
results_folder = r'..\_2_saved\_1_BUBBLE_BSPR'
IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-07-09 22:00:00'

bypass_filename = '_BSPR_bypass_refining_M2'
original_filename = 'vcwg'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 98000
ue1_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]

# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_10min_clean = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
# select the 0th column as the comparison data
urban_2p6_10min_c_compare = urban_all_sites_10min_clean[compare_start_time:compare_end_time]

original_th_sensor_10min_c_compare, original_real_sensor_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(original_filename, results_folder, p0, heights_profile, ue1_heights,
                                         compare_start_time,compare_end_time)
bypass_refining_th_sensor_10min_c_compare, bypass_refining_real_sensor_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(bypass_filename, results_folder, p0, heights_profile, ue1_heights,
                                         compare_start_time,compare_end_time)
# urban_2p6_10min_c_compare are the measurements, column length is 6, which is for 6 heights
# original_real_sensor_10min_c_compare are the associated original predictions, column length is 6
# bypass_refining_real_sensor_10min_c_compare are the associated bypass predictions, column length is 6

# for each height, calculate the RMSE
original_rmse_10min_c_compare_cvrmse = []
bypass_refining_rmse_10min_c_compare_cvrmse = []
original_real_10min_c_compare_cvrmse = []
bypass_refining_real_10min_c_compare_cvrmse = []
for i in range(len(ue1_heights)):
    original_rmse_10min_c_compare_cvrmse.append(plt_tools.calculate_cvrmse(urban_2p6_10min_c_compare.iloc[:,i],
                                                original_th_sensor_10min_c_compare.iloc[:,i]))
    bypass_refining_rmse_10min_c_compare_cvrmse.append(plt_tools.calculate_cvrmse(urban_2p6_10min_c_compare.iloc[:,i],
                                                bypass_refining_th_sensor_10min_c_compare.iloc[:,i]))
    original_real_10min_c_compare_cvrmse.append(
        plt_tools.calculate_cvrmse(urban_2p6_10min_c_compare.iloc[:, i],
                                   original_real_sensor_10min_c_compare.iloc[:, i]))
    bypass_refining_real_10min_c_compare_cvrmse.append(
        plt_tools.calculate_cvrmse(urban_2p6_10min_c_compare.iloc[:, i],
                                   bypass_refining_real_sensor_10min_c_compare.iloc[:, i]))

# print the results
print(f"BSPR CVRMSE:{compare_start_time} to {compare_end_time}-10min Canyon Temperature. p0 {p0} pa")
for i in range(len(ue1_heights)):
    print(f'Height {ue1_heights[i]}m. BEMCalc-VCWG Potential: {original_rmse_10min_c_compare_cvrmse[i]}%, '
          f'BEMCalc-VCWG Real: {original_real_10min_c_compare_cvrmse[i]}%,'
          f'{bypass_filename} Potential: {bypass_refining_rmse_10min_c_compare_cvrmse[i]}%, '
          f'{bypass_filename} Real: {bypass_refining_real_10min_c_compare_cvrmse[i]}%')

# # merge them together
merged_df = pd.concat([urban_2p6_10min_c_compare,
                       original_th_sensor_10min_c_compare,original_real_sensor_10min_c_compare,
                       bypass_refining_th_sensor_10min_c_compare,bypass_refining_real_sensor_10min_c_compare],
                      axis=1)
# rename the above columns
# get ue1_heights length
heights_length = len(ue1_heights)
# add original_ to the next heights_length columns
merged_df.columns = merged_df.columns[:heights_length].tolist() + \
                    ['BEMCalc-Potential' + str(i) for i in merged_df.columns[heights_length:heights_length*2]] + \
                    ['BEMCalc-Real' + str(i) for i in merged_df.columns[heights_length*2:heights_length*3]] + \
                    ['Bypass-Potential' + str(i) for i in merged_df.columns[heights_length*3:heights_length*4]] + \
                    ['Bypass-Real' + str(i) for i in merged_df.columns[heights_length*4:heights_length*5]]
# save the merged_df to an Excel file
merged_df.to_excel(f'{results_folder}\\{bypass_filename}_10min_C_compare.xlsx')
# staggered/stacked comparison plot
plt_tools.stacked_comparison_plot(merged_df, ue1_heights)

