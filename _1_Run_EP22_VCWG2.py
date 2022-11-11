import os
import _0_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers
from VCWG_Hydrology import VCWG_Hydro

def shading_init(input_config):
    coordination.read_ini(input_config)
    coordination.init_ep_api()
    state = coordination.ep_api.state_manager.new_state()
    coordination.state = state
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(coordination.state)
    if 'VCWG' in coordination.theme:
        run_vcwg()
    else:
        run_ep()
def run_vcwg():
    epwFileName = coordination.config['shading']['epwFileName']
    TopForcingFileName = None
    VCWGParamFileName = coordination.config['shading']['VCWGParamFileName']
    theme = coordination.config['shading']['theme']
    ViewFactorFileName = f'{theme}ViewFactor_Capitoul_MOST.txt'
    # Case name to append output file names with
    case = f'{theme}Capitoul_MOST'
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def run_ep():
    time_step_handlers.save_path_clean = False
    idfFileName = coordination.config['shading']['idfFileName']
    epwFileName = coordination.config['shading']['epwFileName']
    coordination.ep_api.state_manager.reset_state(coordination.state)
    state = coordination.ep_api.state_manager.new_state()
    coordination.state = state
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(coordination.state)
    if 'mediumOffice' in coordination.config['shading']['time_step_handlers']:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(coordination.state,
                                                                                      time_step_handlers.mediumOffice_get_ep_results)
    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    output_path = os.path.join('.\\A_prepost_processing\\shading_saving', f'{coordination.theme}_ep_outputs')
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idfFilePath = os.path.join('.\\resources\\idf', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)