'''
Themes todo:
1. VCWG_Oct vs EP_Oct
2. VCWG_Dec vs EP_Dec
3. VCWG_Dec vs Bypass_Dec
'''
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def normalized_mean_bias_error(measurements, predictions):
    bias = measurements - predictions
    nmb = np.mean(bias) / np.mean(measurements)
    return nmb

plot_fontsize = 12
experiments_folder = 'Material_BLD_hConv'
compare_start_time = '2004-06-01 00:05:00'
compare_end_time = '2004-06-30 23:55:00'
vcwg = 'Only_VCWG.csv'

vcwg_df = pd.read_csv(os.path.join(experiments_folder, vcwg),
                      index_col=0, parse_dates=True,header=0)
vcwg_df = vcwg_df[compare_start_time:compare_end_time]
vcwg_ep_comparison = pd.ExcelWriter(os.path.join(experiments_folder, 'VCWG_EP_Comparison_Roof.xlsx'))
#1. sheet: roof temperature
df = pd.DataFrame()
df['VCWG'] = vcwg_df['roof_K'] - 273.15
df['Rural'] = vcwg_df['MeteoData.Tatm'] - 273.15
df_nmbe = {}
#From experiments_folder, read all csv, and column name is 'roof_Text_c', add to df
for file in os.listdir(experiments_folder):
    if file.endswith('.csv'):
        if file != vcwg:
            df[file[:-4]] = pd.read_csv(os.path.join(experiments_folder, file),
                                        index_col=0, parse_dates=True,header=0)['roof_Text_c']
            temp_nmbe = normalized_mean_bias_error(df['VCWG'], df[file[:-4]])
            df_nmbe[file[:-4]] = temp_nmbe
            #print the nmbe between vcwg and EP
            print(file[:-4], temp_nmbe)
df = df[compare_start_time:compare_end_time]

df.to_excel(vcwg_ep_comparison, sheet_name='roof temperature (C)')
df_nmbe = pd.DataFrame.from_dict(df_nmbe, orient='index', columns=['NMBE'])
# Find the largest nmbe, and print the name
print('The largest nmbe is', df_nmbe['NMBE'].max(), 'in', df_nmbe['NMBE'].idxmax())
vcwg_ep_comparison.save()
