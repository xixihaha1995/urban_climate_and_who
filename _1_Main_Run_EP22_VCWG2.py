import os, numpy as np, pandas as pd
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination,\
    _1_ep_vcwg._1_ep_time_step_handlers_ver0 as time_step_handlers
from _3_post_process_code import _0_all_plot_tools as plot_tools

def run_ep_api():
    state = api.state_manager.new_state()
    api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers.smallOffice_nested_ep_only)

    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")

    output_path = os.path.join(ep_files_path, 'ep_optional_outputs')
    weather_file_path = os.path.join(ep_files_path, '..',epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    # ep_files_path = '_2_cases_input_outputs\\_06_Basel_BSPA_ue2\\refining_M3ing'
    ep_files_path = '_2_cases_input_outputs\\_07_vancouver\\Refined_SMALL_OFFICE'
    data_saving_path = '_2_cases_input_outputs\\_07_vancouver\\Refined_SMALL_OFFICE\\ep_saving'
    epwFileName = 'VancouverTopForcing.epw'
    # idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE-M3ing.idf'
    idfFileName = 'Vancouver_SmallOffice.idf'
    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    coordination.init_ep_api()
    api = coordination.ep_api
    coordination.init_variables_for_vcwg_ep()

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()

    case_name = 'only_ep'
    start_time = '2008-07-01 00:00:00'
    time_interval_sec = 300
    data_name_lst = ['ep_wsp_mps_wdir_deg', 'debugging_canyon']

    for data_name in data_name_lst:
        plot_tools.save_data_to_csv(coordination.saving_data, data_name,case_name,
                                    start_time, time_interval_sec, data_saving_path)