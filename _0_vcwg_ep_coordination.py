import threading, sys, configparser, os
import numpy as np, datetime

save_path_clean = False

def ini_all(input_config, input_uwgVariableValue):
    global data_saving_file,epout_saving_folder, config, project_path, save_path_clean, \
        sensor_heights,ep_trivial_path, data_saving_path,uwgVariable,controlValue, \
        ep_api, psychrometric,\
        sem0, sem1, sem2, sem3, \
        vcwg_needed_time_idx_in_seconds, \
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg, \
        ep_indoorTemp_C, ep_sensWaste_w_m2_per_footprint_area, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K, ep_wallShade_Text_K, ep_wallShade_Tint_K, \
        footprint_area_m2
    # find the project path
    config = input_config
    uwgVariable = config['sensitivity']['uwgVariable']
    controlValue = input_uwgVariableValue
    project_path = os.path.dirname(os.path.abspath(__file__))
    save_path_clean = False
    data_saving_folder = os.path.join(project_path, 'A_prepost_processing', config['sensitivity']['experiment_name'],
                                    config['sensitivity']['theme'])
    data_saving_file = os.path.join(data_saving_folder, f'{controlValue}.csv')
    if controlValue > 0:
        str_variable = 'positive' + str(abs(controlValue))
    elif controlValue < 0:
        str_variable = 'negative' + str(abs(controlValue))
    else:
        str_variable = '0'
    theme = config['sensitivity']['theme']
    epout_saving_folder = os.path.join(data_saving_folder, f'{uwgVariable}_{str_variable}ep_outputs')

    sensor_heights = [int(i) for i in config['_0_vcwg_ep_coordination.py']['sensor_height_meter'].split(',')]
    if config['Default']['operating_system'] == 'windows':
        sys.path.insert(0, 'C:/EnergyPlusV22-1-0')
    else:
        sys.path.insert(0, '/usr/local/EnergyPlus-22-1-0/'),
    from pyenergyplus.api import EnergyPlusAPI
    ep_api = EnergyPlusAPI()
    psychrometric = None

    sem0 = threading.Semaphore(1)
    sem1 = threading.Semaphore(0)
    sem2 = threading.Semaphore(0)
    sem3 = threading.Semaphore(0)

    vcwg_needed_time_idx_in_seconds = 0
    vcwg_canTemp_K = 300
    vcwg_canSpecHum_Ratio = 0
    vcwg_canPress_Pa = 0
    vcwg_wsp_mps = 0
    vcwg_wdir_deg = 0

    footprint_area_m2 = 53628 * 0.09290304 / 3

    ep_indoorTemp_C = 20
    ep_sensWaste_w_m2_per_footprint_area = 0
    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wallSun_Text_K = 300
    ep_wallSun_Tint_K = 300
    ep_wallShade_Text_K = 300
    ep_wallShade_Tint_K = 300