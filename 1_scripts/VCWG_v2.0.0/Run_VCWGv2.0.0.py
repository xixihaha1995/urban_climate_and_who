import numpy as np

from VCWG_Hydrology import VCWG_Hydro

"""
Specify file and case names
Developed by Mohsen Moradi and Amir A. Aliabadi
Atmospheric Innovations Research (AIR) Laboratory, University of Guelph, Guelph, Canada
Last update: December 2020
"""
#Basel
# '''
epwFileName = 'Basel.epw'
TopForcingFileName = None
VCWGParamFileName = 'initialize_Basel_MOST.uwg'
ViewFactorFileName = 'ViewFactor_Basel_MOST.txt'
# Case name to append output file names with
case = 'Basel_MOST'
# '''

# epwFileName = 'ERA5_Basel.epw'
# TopForcingFileName = None
# VCWGParamFileName = 'replicate_Basel_MOST.uwg'
# ViewFactorFileName = 'ViewFactor_Basel_MOST.txt'
# # Case name to append output file names with
# case = 'replicate_Basel_MOST'

#Vancouver
'''
epwFileName = 'TopForcing_year.epw'
TopForcingFileName = None
# TopForcingFileName = 'Vancouver2008_ERA5.csv'
VCWGParamFileName = 'replicate_Vancouver_LCZ1.uwg'
ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
# Case name to append output file names with
case = 'Replicate_Vancouver_LCZ1'
'''
import _0_global_save
_0_global_save.init_save_arr()
# Initialize the UWG object and run the simulation
VCWG = VCWG_Hydro(epwFileName,TopForcingFileName,VCWGParamFileName,ViewFactorFileName,case)
VCWG.run()

vcwg_ep_saving_path = '..\EP_And_VCWG_v2.0.0\_2_saved\BUBBLE_VCWG-EP-detailed'
# Lichen: post process, such as [timestamp, waste heat] * time_steps_num
import pandas as pd, os
def add_date_index(df, start_date, time_interval_sec):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval_sec))
    date = pd.Series(date)
    # update dataframe index
    df.index = date
    return df

start_time = '2002-06-10 00:00:00'
time_interval_sec = 300
canTempProfile = np.array(_0_global_save.saving_data['canTempProfile_K'])
df_canTempProfile = pd.DataFrame(canTempProfile)
df_canTempProfile.columns = ['(m) canTemp_' + str(0.5 + i + 1) for i in range(14)]
df_canTemp = add_date_index(df_canTempProfile, start_time, time_interval_sec)
df_canTemp.to_csv(os.path.join(vcwg_ep_saving_path, 'vcwg_canTempProfile.csv'))

canSpeHumProfile = np.array(_0_global_save.saving_data['canSpecHumProfile_Ratio'])
df_canSpeHumProfile = pd.DataFrame(canSpeHumProfile)
df_canSpeHumProfile.columns = ['(m) canSpeHum_' + str(0.5 + i + 1) for i in range(14)]
df_canSpeHum = add_date_index(df_canSpeHumProfile, start_time, time_interval_sec)
df_canSpeHum.to_csv(os.path.join(vcwg_ep_saving_path, 'vcwg_canSpeHumProfile.csv'))

canPresProfile = np.array(_0_global_save.saving_data['canPressProfile_Pa'])
df_canPresProfile = pd.DataFrame(canPresProfile)
df_canPresProfile.columns = ['(m) canPres_' + str(0.5 + i + 1) for i in range(14)]
df_canPres =add_date_index(df_canPresProfile, start_time, time_interval_sec)
df_canPres.to_csv(os.path.join(vcwg_ep_saving_path, 'vcwg_canPresProfile.csv'))

canAvged = np.array(_0_global_save.saving_data['aveaged_temp_k_specHum_ratio_press_pa'])
df_canAvged = pd.DataFrame(canAvged)
df_canAvged.columns = ['Temp_K', 'SpecHum_Ratio', 'Press_Pa']
df_canAvged = add_date_index(df_canAvged, start_time, time_interval_sec)
df_canAvged.to_csv(os.path.join(vcwg_ep_saving_path, 'vcwg_canAvged.csv'))