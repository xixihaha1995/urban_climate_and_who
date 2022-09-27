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

bypass_filename = '_BSPR_bypass_refining_idf'
original_filename = 'vcwg'

v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 100000
ue1_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]
ue1_sensor_idx = np.argmin(np.abs(np.array(ue1_heights) - v200_sensor_height))

# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_10min_clean = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
# select the 0th column as the comparison data
urban_2p6_10min_ = urban_all_sites_10min_clean.iloc[:,ue1_sensor_idx]
urban_2p6_10min_c_compare = urban_2p6_10min_[compare_start_time:compare_end_time]

#bypass_refining_idf_TempProfile_K
bypass_refining_th_sensor_10min_c_compare_series, bypass_refining_real_sensor_10min_c_compare_series = \
    plt_tools.excel_to_potential_real_df(bypass_filename, results_folder, p0, heights_profile, v200_sensor_height,
                                         compare_start_time,compare_end_time)
original_th_sensor_10min_c_compare_series, original_real_sensor_10min_c_compare_series = \
    plt_tools.excel_to_potential_real_df(original_filename, results_folder, p0, heights_profile, v200_sensor_height,
                                         compare_start_time,compare_end_time)

all_df_dc_lst = [urban_2p6_10min_c_compare,
                 original_real_sensor_10min_c_compare_series,
                 bypass_refining_real_sensor_10min_c_compare_series]
all_df_dc_names = [f'Urban ({v200_sensor_height} m)',
                   f'VCWG-Real Temperature ({v200_sensor_height} m)',
                   f'VCWG(idf-Refining)-Real Temperature ({v200_sensor_height} m)']
all_df_dc_in_one = plt_tools.merge_multiple_df(all_df_dc_lst, all_df_dc_names)
# save the data as excel
# all_df_dc_in_one.to_excel(f'{results_folder}\\_8_basel_5min_10min_all_in_one.xlsx')
mbe_rmse_r2_real_original = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                                    original_real_sensor_10min_c_compare_series,
                                                    'VCWG-Real Temperature error')
mbe_rmse_r2_real = plt_tools.bias_rmse_r2(urban_2p6_10min_c_compare,
                                            bypass_refining_real_sensor_10min_c_compare_series,
                                            'VCWG(idf-Refining)-Real Temperature error')

case_name = (f"BSPR:{compare_start_time} to {compare_end_time}-10min Canyon Temperature. p0 {p0} pa",
             "Date", "Temperature (C)")
txt_info = [case_name,
            mbe_rmse_r2_real_original,
            mbe_rmse_r2_real]
# plot
plt_tools.general_time_series_comparision(all_df_dc_in_one, txt_info)



