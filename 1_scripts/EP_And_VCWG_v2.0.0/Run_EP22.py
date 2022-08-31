import sys
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
from VCWG_Hydrology import VCWG_Hydro
one_time = True
one_time_call_vcwg = True
from threading import Thread

def time_step_handler(state):
    global one_time,one_time_call_vcwg, _boiler_outlet_temp_act,_boiler_inlet_temp_act, _boiler_1_flow_act, \
        _base_1_inlet_temp_act,_base_1_outlet_temp_act, _base_1_flow_act, \
        _base_1_flow_sensor
        # _boiler_outlet_actuator2,_boiler_outlet_actuator3,_boiler_fraction_actuator, _boiler_inlet_temp_act, \

    if one_time:
        if not api.exchange.api_data_fully_ready(state):
            return
        # _base_1_inlet_temp_act = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Setpoint",
        #     "THERMAL ZONE: COMPARTMENT 1 THERMAL ZONE BASEBOARD HW INLET")
        # _base_1_outlet_temp_act = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Setpoint",
        #     "THERMAL ZONE: COMPARTMENT 1 THERMAL ZONE BASEBOARD HW OUTLET")

        _base_1_flow_act = api.exchange.get_actuator_handle(
            state, "System Node Setpoint", "Mass Flow Rate Setpoint",
            "THERMAL ZONE: COMPARTMENT 1 THERMAL ZONE BASEBOARD HW INLET")

        _base_1_flow_sensor = api.exchange.get_variable_handle(state, "System Node Mass Flow Rate",
                                        "THERMAL ZONE: COMPARTMENT 1 THERMAL ZONE BASEBOARD HW INLET")
        # api.exchange.get_variable_value(state, _base_1_flow_sensor)
        one_time = False
    warm_up = api.exchange.warmup_flag(state)
    if not warm_up:
        if one_time_call_vcwg:
            one_time_call_vcwg = False
            Thread(target=run_vcwg).start()
        print(f'EnergyPlus day: {api.exchange.day_of_month(state)}, hour: {api.exchange.hour(state)}')
        pass
        # api.exchange.set_actuator_value(state, _boiler_inlet_temp_act, 68)
        # api.exchange.set_actuator_value(state, _boiler_1_flow_act, 40)
        # api.exchange.set_actuator_value(state, _base_1_inlet_temp_act, 75)
        # api.exchange.set_actuator_value(state, _base_1_outlet_temp_act, 70)
        # api.exchange.set_actuator_value(state, _base_1_flow_act, 0.1)
        # flow_rate = api.exchange.get_variable_value(state, _base_1_flow_sensor)
        # print(flow_rate)t

def run_ep_api():

    state = api.state_manager.new_state()
    api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
    print(sys.argv)
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
    api = EnergyPlusAPI()
    Thread(target=run_ep_api).start()

