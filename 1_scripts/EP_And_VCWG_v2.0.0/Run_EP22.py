import sys
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI

one_time = True

def time_step_handler(state):
    global one_time, _boiler_outlet_temp_act,_boiler_inlet_temp_act, _boiler_1_flow_act, \
        _base_1_inlet_temp_act,_base_1_outlet_temp_act, _base_1_flow_act, \
        _base_1_flow_sensor
        # _boiler_outlet_actuator2,_boiler_outlet_actuator3,_boiler_fraction_actuator, _boiler_inlet_temp_act, \

    if one_time:
        if not api.exchange.api_data_fully_ready(state):
            return
        # _boiler_fraction_actuator = api.exchange.get_actuator_handle(
        #     state, "Plant Component Boiler:HotWater","On/Off Supervisory", "MAIN BOILER")
        # _boiler_outlet_actuator2 = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Minimum Setpoint", "Main Boiler HW Outlet")
        # _boiler_outlet_actuator3 = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Maximum Setpoint", "Main Boiler HW Outlet")
        # _boiler_outlet_temp_act = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Setpoint", "Main Boiler HW Outlet")
        # _boiler_inlet_temp_act = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Temperature Setpoint", "Main Boiler HW Inlet")
        # _boiler_1_flow_act = api.exchange.get_actuator_handle(
        #     state, "System Node Setpoint", "Mass Flow Rate Setpoint", "Main Boiler HW Outlet")

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
        pass
        # api.exchange.set_actuator_value(state, _boiler_outlet_temp_act, 80)
        # api.exchange.set_actuator_value(state, _boiler_inlet_temp_act, 68)
        # api.exchange.set_actuator_value(state, _boiler_1_flow_act, 40)
        # api.exchange.set_actuator_value(state, _base_1_inlet_temp_act, 75)
        # api.exchange.set_actuator_value(state, _base_1_outlet_temp_act, 70)
        # api.exchange.set_actuator_value(state, _base_1_flow_act, 0.1)
        # flow_rate = api.exchange.get_variable_value(state, _base_1_flow_sensor)
        # print(flow_rate)

if __name__ == '__main__':
    api = EnergyPlusAPI()
    state = api.state_manager.new_state()
    api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
    print(sys.argv)
    output_path = 'ep_files\\outputs'
    weather_file = 'ep_files\\USA_CO_Golden-NREL.724666_TMY3.epw'
    idf_file = 'ep_files\\ASHRAE901_OfficeSmall_STD2019_Denver.idf'
    sys_args = '-d', output_path, '-w', weather_file, idf_file
    api.runtime.run_energyplus(state, sys_args)
