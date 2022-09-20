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
    ep_files_path = '_02_ep_midRiseApartment_Basel'
    epwFileName = 'ERA5_Basel.epw'
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
    # # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    # records_arr = np.array(coordination.saving_data)
    # # # array to df
    # records_df = pd.DataFrame(records_arr, columns=['last_time_in_seconds', 'curr_sim_time_in_seconds',
    #                                                 'coordination.ep_accumulated_waste_heat'])
    # saved_records_name = ep_files_path + '/records_df.csv'
    # records_df.to_csv(saved_records_name, index=False)

