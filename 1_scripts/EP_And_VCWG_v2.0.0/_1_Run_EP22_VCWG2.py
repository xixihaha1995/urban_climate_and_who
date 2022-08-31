import sys, _0_vcwg_ep_coordination as coordiantion
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
from VCWG_Hydrology import VCWG_Hydro
one_time = True
one_time_call_vcwg = True
from threading import Thread

def api_to_csv(state):
    orig = api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    newFile = open("ep_files\\_3_available_api.csv", "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def time_step_handler(state):
    global one_time,one_time_call_vcwg, odb_actuator_handle, \
        oat_sensor_handle, hvac_heat_rejection_sensor_handle, plant_cooling_sensor_handle, \
        zone1_cooling_sensor_handle, zone1_heating_sensor_handle

    if one_time:
        if not api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        api_to_csv(state)
        odb_actuator_handle = api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Dry Bulb",
            "Environment")

        oat_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "Site Outdoor Air Drybulb Temperature",
                                             "ENVIRONMENT")
        hvac_heat_rejection_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")
        zone1_cooling_sensor_handle = api.exchange.get_variable_handle(state,
                                                                       "Zone Air System Sensible Cooling Rate",
                                                                       "PERIMETER_ZN_1")
        zone1_heating_sensor_handle = api.exchange.get_variable_handle(state,
                                                                       "Zone Air System Sensible Heating Rate",
                                                                       "PERIMETER_ZN_1")

    warm_up = api.exchange.warmup_flag(state)
    if not warm_up:
        if one_time_call_vcwg:
            one_time_call_vcwg = False
            Thread(target=run_vcwg).start()

        coordiantion.sem_vcwg.acquire()
        temp_ep_oat = api.exchange.get_variable_value(state, oat_sensor_handle)
        # print(f'EP: original OAT: {temp_ep_oat}')
        # print(f'EP: vcwg updated canTemp:{coordiantion.ep_oat}')
        cooling_demand = api.exchange.get_variable_value(state, zone1_cooling_sensor_handle)
        heating_demand = api.exchange.get_variable_value(state, zone1_heating_sensor_handle)
        waste_heat = api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)
        print(f'EP: Heat Rejection: {waste_heat}')
        coordiantion.ep_hvac_demand = waste_heat

        print(f'EP: day:{api.exchange.day_of_month(state)}, hour:{api.exchange.hour(state)}, '
              f'minute:{api.exchange.minutes(state)}')
        api.exchange.set_actuator_value(state, odb_actuator_handle, coordiantion.ep_oat)
        coordiantion.sem_energyplus.release()

def run_ep_api():
    state = api.state_manager.new_state()
    api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    api.exchange.request_variable(state, "Plant Supply Side Cooling Demand Rate", "SHWSYS1")
    api.exchange.request_variable(state, "Plant Supply Side Heating Demand Rate", "SHWSYS1")
    api.exchange.request_variable(state, "Zone Air System Sensible Cooling Rate", "PERIMETER_ZN_1")
    api.exchange.request_variable(state, "Zone Air System Sensible Heating Rate", "PERIMETER_ZN_1")
    output_path = 'ep_files\\outputs'
    weather_file = 'ep_files\\USA_CO_Golden-NREL.724666_TMY3.epw'
    idf_file = 'ep_files\\ASHRAE901_OfficeSmall_STD2019_Denver.idf'
    sys_args = '-d', output_path, '-w', weather_file, idf_file
    api.runtime.run_energyplus(state, sys_args)
def run_vcwg():

    epwFileName = None
    TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # Case name to append output file names with
    case = 'Vancouver_LCZ1'
    # '''

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

if __name__ == '__main__':
    coordiantion.init_semaphore_settings()
    coordiantion.init_temp_waste_heat()
    api = EnergyPlusAPI()
    Thread(target=run_ep_api).start()

