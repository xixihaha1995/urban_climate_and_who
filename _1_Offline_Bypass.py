
import os, numpy as np, pandas as pd
from threading import Thread
from multiprocessing import Process
from VCWG_Hydrology import VCWG_Hydro
import _0_vcwg_ep_coordination as coordination

def run_ep_api(input_value):
    coordination.ep_api.state_manager.reset_state(coordination.state)
    if coordination.config['sensitivity']['uwgVariable'] == 'theta_canyon':
        if input_value == -90:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori0.idf'
        elif input_value == -56:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori+34.idf'
        elif input_value == 0:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori+90.idf'
        elif input_value == 90:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori+180.idf'
        elif input_value == 180:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori+270.idf'
    elif coordination.config['sensitivity']['uwgVariable'] == 'albedo':
        if input_value == 0.05:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.05.idf'
        elif input_value == 0.25:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.25.idf'
        elif input_value == 0.7:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.7.idf'
    else:
        idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName']
    # print(f'os.getpid(): {os.getpid()}, idfFileName: ', idfFileName)
    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    state = coordination.ep_api.state_manager.new_state()
    #coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,time_step_handlers_1.smallOffice_get_ep_results)
    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    if coordination.uwgVariableValue > 0:
        str_variable = 'positive' + str(abs(coordination.uwgVariableValue))
    elif coordination.uwgVariableValue < 0:
        str_variable = 'negative' + str(abs(coordination.uwgVariableValue))
    else:
        str_variable = '0'

    output_path = os.path.join('./A_prepost_processing/offline_saving',
                               coordination.config['_0_vcwg_ep_coordination.py']['site_location'],
                               coordination.config['sensitivity']['theme'],
                               f'{coordination.uwgVariable}_{str_variable}ep_outputs')

    idfFilePath = os.path.join('./resources/idf', idfFileName)
    sys_args = '-d', output_path, '-w', coordination.generated_epw_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

def date_time_to_epw_ith_row_in_normal_year(date_time):
    # 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    hours_in_normal_year = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
    month = date_time.month
    day = date_time.day
    hour = date_time.hour
    ith_hour = sum(hours_in_normal_year[:month - 1]) + (day - 1) * 24 + hour
    # ith_hour to ith_row
    ith_row = ith_hour + 8
    return ith_row

def generate_epw():
    epw_Template_file_path = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    epw_Template_file_path = os.path.join('./resources/epw', epw_Template_file_path)
    vcwg_outputs = pd.read_csv(coordination.vcwg_prediction_saving_path, index_col=0, parse_dates=True)
    vcwg_outputs_hourly = vcwg_outputs.resample('H').mean()
    '''
    VCWG hour is 0-23, while epw hour is 1-24
    '''
    # read text based epw file line by line
    with open(epw_Template_file_path, 'r') as f:
        lines = f.readlines()
        # iterate through vcwg_outpouts_hourly.index
        for i, date_time in enumerate(vcwg_outputs_hourly.index):
            ith_row = date_time_to_epw_ith_row_in_normal_year(date_time)
            lines[ith_row] = lines[ith_row].split(',')
            vcwg_prediction = vcwg_outputs_hourly.iloc[i]
            dry_bulb_c = vcwg_prediction['canTemp_K'] - 273.15
            relative_humidity_percentage = vcwg_prediction['rh_%']
            press_pa = vcwg_prediction['vcwg_canPress_Pa']
            humidity_ratio = coordination.psychrometric.humidity_ratio_c(coordination.state,
                dry_bulb_c, relative_humidity_percentage / 100, press_pa)
            dew_point_c = coordination.psychrometric.dew_point(coordination.state, humidity_ratio, press_pa)
            lines[ith_row][6] = str(dry_bulb_c)
            lines[ith_row][7] = str(dew_point_c)
            lines[ith_row][8] = str(relative_humidity_percentage)
            lines[ith_row][9] = str(press_pa)
            lines[ith_row] = ','.join(lines[ith_row])
    with open(coordination.generated_epw_path, 'w') as f:
        f.writelines(lines)

def run_vcwg():
    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    TopForcingFileName = None
    VCWGParamFileName = coordination.config['_1_ep_time_step_handler.py']['VCWGParamFileName']
    theme = coordination.config['sensitivity']['theme']
    ViewFactorFileName = f'{theme}{coordination.uwgVariable}{str(coordination.uwgVariableValue)}ViewFactor_Capitoul_MOST.txt'
    # Case name to append output file names with
    case = f'{theme}{coordination.uwgVariable}{str(coordination.uwgVariableValue)}Capitoul_MOST'
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


def run_offline(input_config, input_uwgVariable, input_value):
    coordination.read_ini(input_config, input_uwgVariable, input_value)
    coordination.init_ep_api()
    state = coordination.ep_api.state_manager.new_state()
    coordination.state = state
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(coordination.state)
    run_vcwg()
    generate_epw()
    run_ep_api(input_value)



