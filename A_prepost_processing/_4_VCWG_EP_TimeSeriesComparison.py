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
    bias = predictions - measurements
    nmb = np.mean(bias) / np.mean(measurements)
    return nmb

plot_fontsize = 12
experiments_folder = 'CAPITOUL_VCWG_EP_Comparison'
compare_start_time = '2004-06-01 00:05:00'
compare_end_time = '2004-06-30 23:55:00'
vcwg = 'Mondouzil_Bueno_2004_Update.csv'
# ep_withCooling = 'NewEPW_WithShading_WithCooling.csv'
ep_withCooling = 'NewEPW_WithShading_WithCooling_SmallOffice.csv'
ep_withoutCooling = 'NewEPW_WithShading_WithoutCooling.csv'
vcwg_df = pd.read_csv(os.path.join(experiments_folder, vcwg),
                      index_col=0, parse_dates=True,header=0)
vcwg_df = vcwg_df[compare_start_time:compare_end_time]
ep_withCooling_df = pd.read_csv(os.path.join(experiments_folder, ep_withCooling),
                                index_col=0, parse_dates=True,header=0)
ep_withCooling_df = ep_withCooling_df[compare_start_time:compare_end_time]
ep_withoutCooling_df = pd.read_csv(os.path.join(experiments_folder, ep_withoutCooling),
                                   index_col=0, parse_dates=True,header=0)
ep_withoutCooling_df = ep_withoutCooling_df[compare_start_time:compare_end_time]
# Index(['canTemp', 'wallSun_K', 'wallShade_K', 'roof_K', 'sensWaste',
#        'MeteoData.Tatm', 'MeteoData.Pre', 'TempProf_cur[19]',
#        'PresProf_cur[19]', 'Unnamed: 10'],
#       dtype='object')
# Index(['sensWaste', 'roof_Text_c', 's_wall_Text_c', 'n_wall_Text_c',
#        'e_wall_Text_c', 'w_wall_Text_c', 'Unnamed: 7'],
#       dtype='object')
# create one excel, with sheet names: wallSun, wallShade, roof,sensWaste
vcwg_ep_comparison = pd.ExcelWriter(os.path.join(experiments_folder, 'VCWG_EP_Comparison.xlsx'))
#3. sheet: roof
df = pd.DataFrame()
df['VCWG'] = vcwg_df['roof_K'] - 273.15
df['EP_WithCooling'] = ep_withCooling_df['roof_Text_c']
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_Text_c']
df['Rural'] = vcwg_df['MeteoData.Tatm'] - 273.15
df.to_excel(vcwg_ep_comparison, sheet_name='roof')
#1. sheet: wallSun
df = pd.DataFrame()
df['VCWG'] = vcwg_df['wallSun_K'] - 273.15
df['EP_WithCooling'] = ep_withCooling_df['s_wall_Text_c']
df['EP_WithoutCooling'] = ep_withoutCooling_df['s_wall_Text_c']
df['Rural'] = vcwg_df['MeteoData.Tatm'] - 273.15
df.to_excel(vcwg_ep_comparison, sheet_name='wallSun')
#2. sheet: wallShade
df = pd.DataFrame()
df['VCWG'] = vcwg_df['wallShade_K'] - 273.15
df['EP_WithCooling'] = ep_withCooling_df['n_wall_Text_c']
df['EP_WithoutCooling'] = ep_withoutCooling_df['n_wall_Text_c']
df.to_excel(vcwg_ep_comparison, sheet_name='wallShade')

#4. sheet: sensWaste
df = pd.DataFrame()
df['VCWG'] = vcwg_df['sensWaste']
df['EP_WithCooling'] = ep_withCooling_df['sensWaste']
df['EP_WithoutCooling'] = ep_withoutCooling_df['sensWaste']
df.to_excel(vcwg_ep_comparison, sheet_name='sensWaste')
vcwg_ep_comparison.save()
themes = ['roof','wallSun', 'wallShade', 'sensWaste']
#plot the len(themes) subfigs, share x axis
_fig, _axs = plt.subplots(len(themes), 1, figsize=(10, 10), sharex=True)
_fig.subplots_adjust(right=0.76)
_global_legend = 1
for _i, _theme in enumerate(themes):
    _df = pd.read_excel(os.path.join(experiments_folder, 'VCWG_EP_Comparison.xlsx'), sheet_name=_theme, index_col=0)
    for _col in _df.columns:
        if _global_legend == 1:
            _axs[_i].plot(_df[_col], label=_col)
        else:
            _axs[_i].plot(_df[_col], label='_nolegend_')
    _global_legend = 0
    _axs[_i].set_title(_theme)
_fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=plot_fontsize)


# # comparison['sensWaste_' + csv_file] = df['sensWaste']
# # comparison['wallSun_K_' + csv_file] = df['wallSun_K']
# # comparison['wallShade_K_' + csv_file] = df['wallShade_K']
# # comparison['roof_K_' + csv_file] = df['roof_K']
# # comparison['ForcTemp_K_' + csv_file] = df['ForcTemp_K']
#
# # get all the csv file names
# # all_csv_files = [f for f in os.listdir(experiments_folder) if f.endswith('.csv')]
# all_csv_files = [ 'Oct_Bypass.csv','Bypassing_EPW.csv', 'Bypassing_IDF.csv', 'Dec_Bypass.csv',]
# themes = ['sensor_idx_20.0','ForcTemp_K','sensWaste', 'wallSun_K', 'wallShade_K', 'roof_K']
# # create new excel files, with the following sheets name:
# # 'sensWaste', 'wallSun_K', 'wallShade_K', 'roof_K', 'ForcTemp_K', sensor_idx_20.0
# cvrmse_nmb_dict = {}
# reorganized_excel = pd.ExcelWriter(os.path.join(experiments_folder, 'reorganized.xlsx'))
# # copy the "cvrmse" sheet from the original excel file
# old_cvrmse_sheet = pd.read_excel(os.path.join(experiments_folder, all_data_name), sheet_name='cvrmse', index_col=0)
# old_cvrmse_sheet.to_excel(reorganized_excel, sheet_name='cvrmse')
# for theme in themes:
#     df = pd.DataFrame()
#     for csv_file in all_csv_files:
#         # from the all_data, find the column name containg 'theme' and 'csv_file'
#         # then add the column to the new excel file
#         _target_col = [col for col in all_data.columns if theme in col and csv_file in col]
#         df[csv_file] = all_data[_target_col]
#         df.index = all_data.index
#         _target_col_2 = [col for col in all_data.columns if theme in col and 'Dec_Bypass.csv' in col]
#         df['Dec_Bypass.csv'] = all_data[_target_col_2]
#         _df1 = df['Dec_Bypass.csv']
#         _df2 = df[csv_file]
#         cvrmse_nmb_dict[theme + '_' + csv_file] = [cvrmse(_df1, _df2), normalized_mean_bias_error(_df1, _df2)]
#     df.to_excel(reorganized_excel, sheet_name=theme)
#
# # convert cvrmse_nmb_dict to one sheet
# cvrmse_nmb_df = pd.DataFrame.from_dict(cvrmse_nmb_dict, orient='index', columns=['cvrmse', 'nmb'])
# cvrmse_nmb_df.to_excel(reorganized_excel, sheet_name='Distance_To_Dec_Bypass.csv')
#
# reorganized_excel.save()
