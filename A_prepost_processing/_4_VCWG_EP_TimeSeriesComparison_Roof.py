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
vcwg = 'Only_VCWG.csv'
ep_withoutCooling = 'NewEPW_WithShading_WithoutCooling.csv'
ep_hConv = 'NewEPW_WithShading_WithoutCoolinghConv.csv'
ep_hConv_IDF = 'NewEPW_WithShading_WithoutCooling_IDF_Modified.csv'
vcwg_df = pd.read_csv(os.path.join(experiments_folder, vcwg),
                      index_col=0, parse_dates=True,header=0)
vcwg_df = vcwg_df[compare_start_time:compare_end_time]
ep_withoutCooling_df = pd.read_csv(os.path.join(experiments_folder, ep_withoutCooling),
                                   index_col=0, parse_dates=True,header=0)
ep_withoutCooling_df = ep_withoutCooling_df[compare_start_time:compare_end_time]
ep_hConv_df = pd.read_csv(os.path.join(experiments_folder, ep_hConv),
                            index_col=0, parse_dates=True,header=0)
ep_hConv_df = ep_hConv_df[compare_start_time:compare_end_time]
ep_hConv_IDF_df = pd.read_csv(os.path.join(experiments_folder, ep_hConv_IDF),
                            index_col=0, parse_dates=True,header=0)
ep_hConv_IDF_df = ep_hConv_IDF_df[compare_start_time:compare_end_time]

# Index(['canTemp', 'wallSun_K', 'wallShade_K', 'roof_K', 'sensWaste',
#        'Roof.SWRabsRoofImp', 'Roof.LWRabsRoofImp', 'Roof.LEfluxRoofImp',
#        'Roof.HfluxRoofImp', 'fluxRoof', 'MeteoData.Tatm', 'MeteoData.Pre',
#        'TempProf_cur[19]', 'PresProf_cur[19]', 'Unnamed: 15'],
#       dtype='object')
# Index(['sensWaste', 'roof_Conv_w_m2', 'roof_netThermalRad_w_m2',
#        'roof_solarRad_w_m2', 'roof_Text_c', 's_wall_Text_c', 'n_wall_Text_c',
#        'e_wall_Text_c', 'w_wall_Text_c', 'Unnamed: 10'],
#       dtype='object')
# create one excel, with sheet names: roof temperature, SWR, LWR, Convection
vcwg_ep_comparison = pd.ExcelWriter(os.path.join(experiments_folder, 'VCWG_EP_Comparison_Roof.xlsx'))
#1. sheet: roof temperature
df = pd.DataFrame()
df['VCWG'] = vcwg_df['roof_K'] - 273.15
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_Text_c']
df['EP_hConv'] = ep_hConv_df['roof_Text_c']
df['EP_hConv_IDFModified'] = ep_hConv_IDF_df['roof_Text_c']
df['Rural'] = vcwg_df['MeteoData.Tatm'] - 273.15
df.to_excel(vcwg_ep_comparison, sheet_name='roof temperature (C)')
#2. sheet: SWR
df = pd.DataFrame()
df['VCWG'] = vcwg_df['Roof.SWRabsRoofImp']
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_solarRad_w_m2']
df.to_excel(vcwg_ep_comparison, sheet_name='SWR (W m-2)')
#3. sheet: LWR
df = pd.DataFrame()
df['VCWG'] = vcwg_df['Roof.LWRabsRoofImp']
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_netThermalRad_w_m2']
df.to_excel(vcwg_ep_comparison, sheet_name='LWR (W m-2)')
#4. sheet: Convection
df = pd.DataFrame()
df['VCWG'] = -1*vcwg_df['Roof.HfluxRoofImp']
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_Conv_w_m2']
df.to_excel(vcwg_ep_comparison, sheet_name='Convection (W m-2)')
#5. sheet: hConv (W/m2/K)
df = pd.DataFrame()
df['VCWG'] = vcwg_df['hConv']
df['EP_WithoutCooling'] = ep_withoutCooling_df['roof_hConv_w_m2_K']
df.to_excel(vcwg_ep_comparison, sheet_name='hConv (W m-2 K-1)')
vcwg_ep_comparison.save()
themes = ['roof temperature (C)', 'SWR (W m-2)', 'LWR (W m-2)', 'Convection (W m-2)', 'hConv (W m-2 K-1)']
# #plot the len(themes) subfigs, share x axis
_fig, _axs = plt.subplots(len(themes), 1, figsize=(10, 10), sharex=True)
_fig.subplots_adjust(right=0.76)
_global_legend = 1
for _i, _theme in enumerate(themes):
    _df = pd.read_excel(os.path.join(experiments_folder, 'VCWG_EP_Comparison_Roof.xlsx'), sheet_name=_theme, index_col=0)
    for _col in _df.columns:
        if _global_legend == 1:
            _axs[_i].plot(_df[_col], label=_col)
        else:
            _axs[_i].plot(_df[_col], label='_nolegend_')
    _global_legend = 0
    _axs[_i].set_title(_theme)
_fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=plot_fontsize)
