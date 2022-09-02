import sys,  numpy as np, pandas as pd
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
from VCWG_Hydrology import VCWG_Hydro
from threading import Thread

# Lichen: import the parent coordination class needed for EP and VCWG
import _0_vcwg_ep_coordination as coordiantion
# Lichen: init global variables used for EP each callback function
records = []
one_time = True
one_time_call_vcwg = True

def api_to_csv(state):
    orig = api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    newFile = open("_0_ep_files\\_3_available_api.csv", "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def time_step_handler(state):
    global one_time,one_time_call_vcwg, odb_actuator_handle, \
        oat_sensor_handle, hvac_heat_rejection_sensor_handle, \
        ep_last_time_index_in_seconds, records

    if one_time:
        if not api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        ep_last_time_index_in_seconds = 0
        # api_to_csv(state)
        oat_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "Site Outdoor Air Drybulb Temperature",
                                             "ENVIRONMENT")
        zone1_cooling_sensor_handle = api.exchange.get_variable_handle(state,
                                                                       "Zone Air System Sensible Cooling Rate",
                                                                       "PERIMETER_ZN_1")
        zone1_heating_sensor_handle = api.exchange.get_variable_handle(state,
                                                                       "Zone Air System Sensible Heating Rate",
                                                                       "PERIMETER_ZN_1")

        odb_actuator_handle = api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Dry Bulb",
            "Environment")

        hvac_heat_rejection_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")

    warm_up = api.exchange.warmup_flag(state)
    if not warm_up:
        # Lichen: After EP warm up, start to call VCWG
        if one_time_call_vcwg:
            one_time_call_vcwg = False
            Thread(target=run_vcwg).start()
        '''
        Lichen: sync EP and VCWG
        1. EP: get the current time in seconds
        2. EP: compare the current time with the last time
            if the current time is larger than the last time,
                then do accumulation: coordiantion.ep_accumulated_waste_heat += _this_waste_heat * 1e-4
        3. Compare EP_time_idx_in_seconds with vcwg_needed_time_idx_in_seconds
            a. if true, 
                global_hvac_waste <- ep:hvac_heat_rejection_sensor_handle
                global_oat -> ep:odb_actuator_handle
                release the lock for vcwg, denoted as coordiantion.sem_energyplus.release()
            b. if false 
                (HVAC is converging, probably we need run many HVAC iteration loops for the same ep time index)
                or
                (HVAC is accumulating, probably we need run many HVAC iteration loops for the following ep time indices)
                release the lock for EP, denoted as coordiantion.sem_vcwg.release()
        '''
        coordiantion.sem_vcwg.acquire()
        curr_sim_time_in_hours = api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        _this_waste_heat = api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)

        if curr_sim_time_in_seconds != ep_last_time_index_in_seconds:
            coordiantion.ep_accumulated_waste_heat += _this_waste_heat
            records.append([ep_last_time_index_in_seconds, curr_sim_time_in_seconds,
                            coordiantion.vcwg_needed_time_idx_in_seconds, coordiantion.ep_accumulated_waste_heat])
            ep_last_time_index_in_seconds = curr_sim_time_in_seconds
        time_index_alignment_bool =  1 > abs(curr_sim_time_in_seconds - coordiantion.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            # print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
            # print("EP: vcwg_needed_time_idx_in_seconds: ", coordiantion.vcwg_needed_time_idx_in_seconds)
            coordiantion.sem_vcwg.release()
            return
        api.exchange.set_actuator_value(state, odb_actuator_handle, coordiantion.ep_oat)
        # print(f'EP: accumulated Time [h]: {curr_sim_time_in_hours}, '
        #       f'Heat Rejection * 1e-4 [J]: {coordiantion.ep_accumulated_waste_heat }\n')
        coordiantion.sem_energyplus.release()

def run_ep_api():
    state = api.state_manager.new_state()
    # api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
    api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handler)
    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    api.exchange.request_variable(state, "Plant Supply Side Cooling Demand Rate", "SHWSYS1")
    api.exchange.request_variable(state, "Plant Supply Side Heating Demand Rate", "SHWSYS1")
    api.exchange.request_variable(state, "Zone Air System Sensible Cooling Rate", "PERIMETER_ZN_1")
    api.exchange.request_variable(state, "Zone Air System Sensible Heating Rate", "PERIMETER_ZN_1")
    output_path = '_0_ep_files\\outputs'
    weather_file = '_0_ep_files\\USA_CO_Golden-NREL.724666_TMY3.epw'
    idf_file = '_0_ep_files\\ASHRAE901_OfficeSmall_STD2019_Denver.idf'
    sys_args = '-d', output_path, '-w', weather_file, idf_file
    api.runtime.run_energyplus(state, sys_args)

def run_vcwg():
    epwFileName = None
    TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # Case name to append output file names with
    case = 'Vancouver_LCZ1'

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


if __name__ == '__main__':
    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordiantion.init_semaphore_lock_settings()
    coordiantion.init_variables_for_vcwg_ep()

    api = EnergyPlusAPI()
    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()

    # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    records_arr = np.array(records)
    # array to df
    records_df = pd.DataFrame(records_arr, columns=['last_time_in_seconds', 'curr_sim_time_in_seconds',
                                                    'vcwg_needed_time_idx_in_seconds',
                                                    'coordiantion.ep_accumulated_waste_heat'])
    records_df.to_csv('_1_plots_related\\ep_1min_vcwg_5min_waste_heat.csv', index=False)
    # save results to csv file
    # np.savetxt('_1_plots_related\\ep_1min_vcwg_5min_waste_heat.csv', records_arr, delimiter=',')

