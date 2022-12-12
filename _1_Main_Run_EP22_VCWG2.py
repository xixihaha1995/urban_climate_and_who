import configparser
import os
from multiprocessing import Process
from threading import Thread
import _0_vcwg_ep_coordination as coordination,\
    _1_ep_time_step_handlers_ver0 as time_step_handlers

def run_ep_api(config,experiments_theme, value):
    coordination.ini_all(config, value)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    if 'MediumOffice' in value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MediumOffice_get_ep_results)
    elif 'SmallOffice' in value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.SmallOffice_get_ep_results)
    elif 'LargeOffice' in value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.LargeOffice_get_ep_results)
    else:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.general_get_ep_results)

    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    epwFileName = coordination.config['Default']['epwFileName']
    output_path = coordination.ep_trivial_path
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idfFilePath = os.path.join(f'.\\resources\\idf\\IDF_Roof_Temperature', value+'.idf')
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)
def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path, '_0_configs',config_file_name)
    config.read(config_path)
def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    experiments_theme = config['Default']['experiments_theme']
    value_list = [i for i in config['Default']['value_list'].split(',')]
    this_ini_process = []
    nbr_of_parallel = 5
    batch_value_list = [value_list[i:i + nbr_of_parallel] for i in range(0, len(value_list), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            this_ini_process.append(Process(target=run_ep_api, args=(config, experiments_theme, value)))
        for process in this_ini_process:
            process.start()
        for process in this_ini_process:
            process.join()
        this_ini_process = []

    # for value in value_list:
    #     p = Process(target=run_ep_api, args=(config,experiments_theme, value))
    #     p.start()
    #     this_ini_process.append(p)



if __name__ == '__main__':
    one_ini('CAPITOUL_Roof_Temperature.ini')