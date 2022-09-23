import os, numpy as np, pandas as pd
from threading import Thread
import _0_vcwg_ep_coordination as coordination, _01_ep_time_step_handlers

def api_to_csv(state):
    orig = api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(ep_files_path, 'api.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()

def run_ep_api():
    state = api.state_manager.new_state()
    # api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
    #                                                               _01_ep_time_step_handlers._nested_ep_then_vcwg)
    api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                  _01_ep_time_step_handlers._nested_ep_then_vcwg)
    # api.runtime.callback_end_zone_timestep_before_zone_reporting(state,
    #                                                               _01_ep_time_step_handlers._nested_ep_only)
    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")

    output_path = os.path.join(ep_files_path, 'ep_outputs')
    weather_file_path = os.path.join(ep_files_path, epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    ep_files_path = '_05_vcwg-ep-overwriting-midRiseApartment_Basel'
    epwFileName = 'Basel.epw'
    idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE.idf'

    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    coordination.init_ep_api()
    api = coordination.ep_api
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep()

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()

    vcwg_ep_saving_path = '_2_saved\BUBBLE_VCWG-EP-detailed'
    # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    from _1_plots_related import _0_all_plot_tools as plot_tools
    start_time = '2002-06-10 00:00:00'
    time_interval_sec = 300
    canTempProfile = np.array(coordination.saving_data['canTempProfile_K'])
    df_canTempProfile = pd.DataFrame(canTempProfile)
    df_canTempProfile.columns = ['(m) canTemp_' + str(0.5 + i + 1) for i in range(14)]
    df_canTemp = plot_tools.add_date_index(df_canTempProfile, start_time, time_interval_sec)
    df_canTemp.to_csv(os.path.join(vcwg_ep_saving_path, 'bypass_refining_idf_canTempProfile.csv'))

    canSpeHumProfile = np.array(coordination.saving_data['canSpecHumProfile_Ratio'])
    df_canSpeHumProfile = pd.DataFrame(canSpeHumProfile)
    df_canSpeHumProfile.columns = ['(m) canSpeHum_' + str(0.5 + i + 1) for i in range(14)]
    df_canSpeHum = plot_tools.add_date_index(df_canSpeHumProfile, start_time, time_interval_sec)
    df_canSpeHum.to_csv(os.path.join(vcwg_ep_saving_path, 'bypass_refining_idf_canSpeHumProfile.csv'))

    canPresProfile = np.array(coordination.saving_data['canPressProfile_Pa'])
    df_canPresProfile = pd.DataFrame(canPresProfile)
    df_canPresProfile.columns = ['(m) canPres_' + str(0.5 + i + 1) for i in range(14)]
    df_canPres = plot_tools.add_date_index(df_canPresProfile, start_time, time_interval_sec)
    df_canPres.to_csv(os.path.join(vcwg_ep_saving_path, 'bypass_refining_idf_canPresProfile.csv'))

    canAvged = np.array(coordination.saving_data['aveaged_temp_k_specHum_ratio_press_pa'])
    df_canAvged = pd.DataFrame(canAvged)
    df_canAvged.columns = ['Temp_K', 'SpecHum_Ratio', 'Press_Pa']
    df_canAvged = plot_tools.add_date_index(df_canAvged, start_time, time_interval_sec)
    df_canAvged.to_csv(os.path.join(vcwg_ep_saving_path, 'bypass_refining_idf_canAvged.csv'))


