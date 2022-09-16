'''
# Eventually, we need compare the Sensible heat flux and the Latent heat flux.
# Do the sensible heat fluxes first
# Sensile heat fluxes are in W/m2, file is "SSQHB_all_30min.csv"
# Latent heat fluxes are in kg/m2/s, file is "SSQEB_all_30min.csv"
# Original measurements is 30 mins interval, we need to convert to hourly
# Read sensible measurements for May - September 2008 (Ultimate goal is to compare with EP measurements)
Specifically,
measurements are available after 2008-05-07 00:00:00
EP is available after 2008-05-07 00:00:00
VCWG is available after 2008-05-07 00:00:00 (one spin up day)
'''

import pandas as pd
import _0_all_plot_tools as plt_tools
results_folder = r'vancouver'
start_time_with_spin_up = '2008-07-01 00:00:00'
start_time = '2008-07-02 00:00:00'
end_time = '2008-07-03 23:00:00'

vcwg_output_time_interval_seconds = 3600

# Read sensible measurements
df_sens_dirty = pd.read_csv(f'{results_folder}\\SSQHB_all_30min.csv', header=0, index_col=0, parse_dates=True)
df_30min_sens_measure_all = plt_tools.data_cleaning(df_sens_dirty)
df_30min_sens_measure = df_30min_sens_measure_all.loc[start_time:end_time]
df_hourly_sens_measure = plt_tools.time_interval_convertion(df_30min_sens_measure)

# read Hlfux from replicated VCWG
vcwg_original_hour_all_Hlfux = plt_tools.read_text_as_csv(f'{results_folder}'
                                                                          f'\\HfluxesVancouver_LCZ1.txt',
                                                          header=0,skiprows=2)
# select 13th column, which is HlfuxUrban, make a new dataframe
vcwg_original_hour_all_Hlfux = vcwg_original_hour_all_Hlfux.iloc[:, 12]
vcwg_original_hour_all_Hlfux_date = plt_tools.add_date_index(vcwg_original_hour_all_Hlfux,
                                                            start_time_with_spin_up, vcwg_output_time_interval_seconds)
vcwg_original_hour_all_Hlfux = vcwg_original_hour_all_Hlfux_date.loc[start_time:end_time]

# read Hlfux from VCWG-Bypass
vcwg_bypass_hour_all_Hlfux = plt_tools.read_text_as_csv(f'{results_folder}'
                                                                            f'\\Hfluxes_bypass_Vancouver_LCZ1.txt',
                                                        header=0,skiprows=2)
# select 13th column, which is HlfuxUrban, make a new dataframe
vcwg_bypass_hour_all_Hlfux = vcwg_bypass_hour_all_Hlfux.iloc[:, 12]
vcwg_bypass_hour_all_Hlfux_date = plt_tools.add_date_index(vcwg_bypass_hour_all_Hlfux,
                                                            start_time_with_spin_up, vcwg_output_time_interval_seconds)
vcwg_bypass_hour_all_Hlfux = vcwg_bypass_hour_all_Hlfux_date.loc[start_time:end_time]

# read HlufxProfiles
vcwg_original_hour_all_HlfuxProfiles = plt_tools.read_text_as_csv(f'{results_folder}'
                                                                            f'\\HfluxProf_profilesMay_Vancouver_LCZ1.txt')
# select 28.8 m, which is the height of the Sensible Heat Fluxes sensor
vcwg_original_hour_all_HlfuxProfiles_28m = plt_tools.certain_height_one_day(vcwg_original_hour_all_HlfuxProfiles, 28.8)

# sequence based index convert to date


all_df_list = [df_hourly_sens_measure, vcwg_original_hour_all_Hlfux, vcwg_bypass_hour_all_Hlfux]
all_df_name = ['Sensible Heat Flux (Best available) (28.80m)', 'VCWG-Replicate', 'VCWG-Bypass']
all_in_one_df = plt_tools.merge_multiple_df(all_df_list, all_df_name)

# all_in_one_df.to_csv(f'{results_folder}\\all_in_one_df_sens.csv')
bias_rmse_r2_rep = plt_tools.bias_rmse_r2(all_in_one_df['Sensible Heat Flux (Best available) (28.80m)'],
                                      all_in_one_df['VCWG-Replicate'])
bias_rmse_r2_bypass = plt_tools.bias_rmse_r2(all_in_one_df['Sensible Heat Flux (Best available) (28.80m)'],
                                        all_in_one_df['VCWG-Bypass'])
error_infor = [bias_rmse_r2_rep, bias_rmse_r2_bypass]
plt_tools.plot_comparison_measurement_simulated(all_in_one_df, error_infor)

print('Done')