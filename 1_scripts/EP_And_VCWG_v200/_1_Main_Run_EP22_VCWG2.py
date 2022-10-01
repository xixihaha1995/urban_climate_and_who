import os, numpy as np, pandas as pd
from threading import Thread
import _0_EP_VCWG._0_EP._0_vcwg_ep_coordination as coordination,\
    _0_EP_VCWG._0_EP._1_ep_time_step_handlers_ver0 as time_step_handlers
from _1_case_analysis.analysis._1_plots_related import _0_all_plot_tools as plot_tools

def run_ep_api():
    state = api.state_manager.new_state()
    api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers._nested_ep_only)

    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")

    output_path = os.path.join(ep_files_path, 'ep_outputs')
    weather_file_path = os.path.join(ep_files_path,'..', epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    ep_files_path = '_1_case_analysis\\cases\\_05_Basel_BSPR_ue1\\refining_M2'
    data_saving_path = '_1_case_analysis\\cases\\_05_Basel_BSPR_ue1\\ep_saving'
    epwFileName = 'Basel.epw'
    idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE-M2.idf'

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
    start_time = '2002-06-10 00:00:00'
    time_interval_sec = 300
    data_name_lst = ['ep_wsp_mps_wdir_deg', 'debugging_canyon']

    for data_name in data_name_lst:
        plot_tools.save_data_to_csv(coordination.saving_data, data_name,case_name,
                                    start_time, time_interval_sec, data_saving_path)