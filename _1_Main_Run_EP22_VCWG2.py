import os, numpy as np, pandas as pd
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination
from _1_ep_vcwg import _1_ep_time_step_handlers as time_step_handlers
from _3_pre_post_process import _0_all_plot_tools as plot_tools

def run_ep_api():
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric = coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    # coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
    #                                                                                 time_step_handlers.midRiseAprt_get_ep_results)
    # coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
    #                                                                               time_step_handlers.smallOffice_get_ep_results)
    if 'mediumOffice' in coordination.config['_1_Main_Run_EP22_VCWG2.py']['time_step_handlers']:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                      time_step_handlers.mediumOffice_get_ep_results)
    if 'smallOffice' in coordination.config['_1_Main_Run_EP22_VCWG2.py']['time_step_handlers']:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                      time_step_handlers.smallOffice_get_ep_results)

    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state,  "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    output_path = os.path.join(ep_files_path, 'ep_optional_outputs')
    weather_file_path = os.path.join(ep_files_path, epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    prompt = 'Please enter the configuration file name: [case7_Vancouver_TopForcing_bypass.ini]'
    config_file_name = input(prompt) or 'case7_Vancouver_TopForcing_bypass.ini'
    coordination.read_ini(config_file_name)
    time_step_handler_ver = 1.1
    # case_name = '_BSPA_Ue2_bypass_'
    # case_name = 'Ue1_bypass'
    # case_name = 'Ue2_bypass'
    # case_name = 'Vancouver_TopForcing_ByPass_2008Jul'
    # case_name = 'Vancouver_Rural_ByPass_2008Jul'
    case_name = coordination.config['_1_Main_Run_EP22_VCWG2.py']['case_name']
    # start_time = '2002-06-10 00:00:00'
    # start_time = '2004-06-01 00:00:00'
    start_time = coordination.config['_1_Main_Run_EP22_VCWG2.py']['start_time']
    time_interval_sec = 300
    # ep_files_path = '_2_cases_input_outputs\\_05_Basel_BSPR_ue1\\MidRiseApartment_4C_Rural'
    # ep_files_path = '_2_cases_input_outputs\\_05_Basel_BSPR_ue1\\MidRiseApart_4C_Rural_LiteratureAlbedo'
    # ep_files_path = '_2_cases_input_outputs\\_06_Basel_BSPA_ue2\\refining_M3ing'
    # ep_files_path = '_2_cases_input_outputs\\_06_Basel_BSPA_ue2\\Orientation_MidRiseApart_4C'
    # ep_files_path = '_2_cases_input_outputs\\_06_Basel_BSPA_ue2\\Orientation_MidRiseApart_4C_LiteratureAlbedo'
    # ep_files_path = '_2_cases_input_outputs\\_08_CAPITOUL\\DOE_Ref_MediumOffice_4B'
    # ep_files_path = '_2_cases_input_outputs\\_08_CAPITOUL\\MediumOffice_4B_Literature_MNP'
    # ep_files_path = '_2_cases_input_outputs\\_07_vancouver\\TopForcing_Refined_SMALL_OFFICE'
    # ep_files_path = '_2_cases_input_outputs\\_07_vancouver\\Rural_Refined_Small_Office'
    ep_files_path = coordination.config['_1_Main_Run_EP22_VCWG2.py']['ep_files_path']
    # epwFileName = 'Basel.epw'
    # epwFileName = 'Mondouzil_tdb_td_rh_P_2004.epw'
    # epwFileName = 'VancouverTopForcing.epw'
    # epwFileName = 'VancouverRural718920.epw'
    # epwFileName = 'Vancouver718920CorrectTime.epw'
    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    # idfFileName = 'BUBBLE_Ue1_LiteratureAlbedo.idf'
    # idfFileName = 'BUBBLE_Ue2_LiteratureAlbedo.idf'
    # idfFileName = 'BUBBLE_Ue2.idf'
    # idfFileName = 'CAPITOUL_4B_MediumOffice.idf'
    # idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE-M3ing.idf'
    # idfFileName = 'RefBldgSmallOfficePost1980_v1.4_7.2_4C_USA_WA_SEATTLE.idf'
    # idfFileName = 'CAPITOUL_4B.idf'
    # idfFileName = 'Vancouver_SmallOffice.idf'
    idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName']

    vcwg_ep_saving_path = ep_files_path + f'\\c_vcwg_ep_saving\\ver{time_step_handler_ver}'

    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    coordination.init_ep_api()
    # api =
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep(ep_files_path, time_step_handler_ver)

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()


    # start_time = '2002-06-10 00:00:00'

    # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    data_name_lst = ['TempProfile_K', 'SpecHumProfile_Ratio', 'PressProfile_Pa', 'wind_vxProfile_mps',
                     'wind_vyProfile_mps', 'wind_SpeedProfile_mps', 'turbulence_tkeProfile_m2s2',
                     'air_densityProfile_kgm3', 'sensible_heat_fluxProfile_Wm2', 'latent_heat_fluxProfile_Wm2',
                     'can_Averaged_temp_k_specHum_ratio_press_pa','s_wall_Text_K_n_wall_Text_K','debugging_canyon']
    for data_name in data_name_lst:
        plot_tools.save_data_to_csv(coordination.saving_data, data_name,case_name,
                                    start_time, time_interval_sec, vcwg_ep_saving_path)