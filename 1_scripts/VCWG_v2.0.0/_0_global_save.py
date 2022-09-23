import numpy as np
def init_save_arr():
    global saving_data
    saving_data = {}
    saving_data['canTempProfile_K'] = []
    saving_data['canSpecHumProfile_Ratio'] = []
    saving_data['canPressProfile_Pa'] = []
    saving_data['aveaged_temp_k_specHum_ratio_press_pa'] = []