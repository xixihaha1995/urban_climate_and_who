import datetime
import os

from scipy import signal

import _0_vcwg_ep_coordination as coordination
zone_time_step_seconds = 0
accu_hvac_heat_rejection_J = 0
ep_last_call_time_seconds = 0
get_ep_results_inited_handle = False

def api_to_csv(state):
    orig = coordination.ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(coordination.data_saving_path,'..', 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def SmallOffice_get_ep_results(state):
    global zone_time_step_seconds,\
        get_ep_results_inited_handle,\
        hvac_heat_rejection_sensor_handle,\
        roof_1_Text_handle, roof_2_Text_handle, roof_3_Text_handle, roof_4_Text_handle, roof_5_Text_handle, \
        s_wall_Text_handle, \
        n_wall_Text_handle,\
        e_wall_Text_handle,\
        w_wall_Text_handle


    if not get_ep_results_inited_handle:

        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        # Core_ZN_roof
        roof_5_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "Core_ZN_roof")

        roof_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "Perimeter_ZN_1_roof")
        roof_2_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_2_roof")
        roof_3_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_3_roof")
        roof_4_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_4_roof")

        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        e_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_2_wall_east")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        w_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_4_wall_west")

        if (hvac_heat_rejection_sensor_handle == -1 or\
                roof_1_Text_handle == -1 or roof_2_Text_handle == -1 or roof_3_Text_handle == -1
                or roof_4_Text_handle == -1 or roof_5_Text_handle == -1 or\
                s_wall_Text_handle == -1 or e_wall_Text_handle == -1 or
                n_wall_Text_handle == -1 or w_wall_Text_handle == -1):
            print('SmallOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        global ep_last_call_time_seconds, accu_hvac_heat_rejection_J
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                      hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if not one_zone_time_step_bool:
            print(f'accumulation_time_step_in_seconds = {accumulation_time_step_in_seconds}, '
                  f'zone_time_step_seconds = {zone_time_step_seconds}')
            return
        ep_last_call_time_seconds = curr_sim_time_in_seconds

        hvac_waste_w_m2_footprint = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds \
                          / coordination.footprint_area_m2
        accu_hvac_heat_rejection_J = 0
        roof_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_1_Text_handle)
        roof_2_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_2_Text_handle)
        roof_3_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_3_Text_handle)
        roof_4_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_4_Text_handle)
        roof_5_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_5_Text_handle)

        s_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Text_handle)
        e_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, e_wall_Text_handle)
        n_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Text_handle)
        w_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, w_wall_Text_handle)

        roof_Text_c = (roof_1_Text_c + roof_2_Text_c + roof_3_Text_c + roof_4_Text_c + roof_5_Text_c) / 5


        if os.path.exists(coordination.data_saving_path) and not coordination.save_path_clean:
            os.remove(coordination.data_saving_path)
            coordination.save_path_clean = True

        cur_datetime = datetime.datetime.strptime(coordination.config['__main__']['start_time'],
                                                  '%Y-%m-%d %H:%M:%S') + \
                       datetime.timedelta(seconds= curr_sim_time_in_seconds)

        if not os.path.exists(coordination.data_saving_path):
            os.makedirs(os.path.dirname(coordination.data_saving_path), exist_ok=True)
            with open(coordination.data_saving_path, 'a') as f1:
                # prepare the header string for different sensors
                header_str = 'cur_datetime,sensWaste,roof_Text_c,s_wall_Text_c,n_wall_Text_c,e_wall_Text_c,w_wall_Text_c,'
                header_str += '\n'
                f1.write(header_str)
            # write the data
        with open(coordination.data_saving_path, 'a') as f1:
            fmt1 = "%s," * 1 % (cur_datetime) + \
                   "%.3f," * 6 % (hvac_waste_w_m2_footprint,roof_Text_c,s_wall_Text_c,n_wall_Text_c,e_wall_Text_c,w_wall_Text_c) + '\n'
            f1.write(fmt1)
def MediumOffice_get_ep_results(state):
    global zone_time_step_seconds,\
        get_ep_results_inited_handle, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, zone_flr_area_handle, \
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        flr_pre1_Text_handle, flr_pre2_Text_handle, flr_pre3_Text_handle, flr_pre4_Text_handle, \
        flr_core_Text_handle, \
        roof_Text_handle, \
        s_wall_bot_1_Text_handle, s_wall_mid_1_Text_handle, s_wall_top_1_Text_handle, \
        n_wall_bot_1_Text_handle, n_wall_mid_1_Text_handle, n_wall_top_1_Text_handle, \
        e_wall_bot_1_Text_handle, e_wall_mid_1_Text_handle, e_wall_top_1_Text_handle, \
        w_wall_bot_1_Text_handle, w_wall_mid_1_Text_handle, w_wall_top_1_Text_handle, \
        s_wall_bot_1_Solar_handle, s_wall_mid_1_Solar_handle, s_wall_top_1_Solar_handle, \
        n_wall_bot_1_Solar_handle, n_wall_mid_1_Solar_handle, n_wall_top_1_Solar_handle, \
        flr_pre1_Tint_handle, flr_pre2_Tint_handle, flr_pre3_Tint_handle, flr_pre4_Tint_handle, \
        flr_core_Tint_handle, \
        roof_Tint_handle, \
        s_wall_bot_1_Tint_handle, s_wall_mid_1_Tint_handle, s_wall_top_1_Tint_handle, \
        n_wall_bot_1_Tint_handle, n_wall_mid_1_Tint_handle, n_wall_top_1_Tint_handle, \
        roof_Convection_handle, roof_netThermalRad_handle, roof_solarRad_handle, roof_hConv_handle,\
        roof_hConv_actuator_handle

    if not get_ep_results_inited_handle:

        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        # api_to_csv(state)
        get_ep_results_inited_handle = True
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                             "Site Outdoor Air Drybulb Temperature",\
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        '''
        !-Surface Outside Face Convection Heat Gain Rate per Area
        !-Surface Outside Face Net Thermal Radiation Heat Gain Rate per Area
        !-Surface Outside Face Solar Radiation Heat Gain Rate per Area
        !-Surface Outside Face Convection Heat Transfer Coefficient
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                    "Building_Roof")
        '''
        roof_Convection_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Convection Heat Gain Rate per Area",\
                                                                                  "Building_Roof")
        roof_netThermalRad_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Net Thermal Radiation Heat Gain Rate per Area",\
                                                                                     "Building_Roof")
        roof_solarRad_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Solar Radiation Heat Gain Rate per Area",\
                                                                                "Building_Roof")
        roof_hConv_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Convection Heat Transfer Coefficient",\
                                                                             "Building_Roof")
        # roof_hConv_actuator_handle
        # coordination.ep_api.exchange. \
        #     get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        roof_hConv_actuator_handle = coordination.ep_api.exchange. \
            get_actuator_handle(state, "Surface","Exterior Surface Convection Heat Transfer Coefficient",\
                                "BUILDING_ROOF")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area",\
                                                                          "CORE_MID")
        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Zone Air Temperature",\
                                                                                         "CORE_MID")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                            "Zone Air Humidity Ratio",\
                                                                                            "CORE_MID")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Cooling Rate",\
                                                                                          "CORE_MID")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Heating Rate",\
                                                                                          "CORE_MID")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Cooling Coil Electricity Rate",\
                                                                                          "VAV_2_COOLC DXCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Heating Coil Heating Rate",\
                                                                                          "CORE_MID VAV BOX REHEAT COIL")
        flr_pre1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_1_Floor")
        flr_pre2_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_2_Floor")
        flr_pre3_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_3_Floor")
        flr_pre4_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_4_Floor")
        flr_core_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Core_bot_ZN_5_Floor")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "Building_Roof")
        s_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_3_Wall_North")
        e_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_1_Wall_East")
        e_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_1_Wall_East")
        e_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_1_Wall_East")
        w_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_3_Wall_West")
        w_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_3_Wall_West")
        w_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_3_Wall_West")

        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or zone_flr_area_handle == -1 or\
                elec_bld_meter_handle == -1 or zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1 or\
                sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or\
                cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or\
                flr_pre1_Text_handle == -1 or flr_pre2_Text_handle == -1 or flr_pre3_Text_handle == -1 or\
                flr_pre4_Text_handle == -1 or flr_core_Text_handle == -1 or roof_Text_handle == -1 or\
                s_wall_bot_1_Text_handle == -1 or s_wall_mid_1_Text_handle == -1 or s_wall_top_1_Text_handle == -1 or\
                n_wall_bot_1_Text_handle == -1 or n_wall_mid_1_Text_handle == -1 or n_wall_top_1_Text_handle == -1 or\
                e_wall_bot_1_Text_handle == -1 or e_wall_mid_1_Text_handle == -1 or e_wall_top_1_Text_handle == -1 or\
                w_wall_bot_1_Text_handle == -1 or w_wall_mid_1_Text_handle == -1 or w_wall_top_1_Text_handle == -1 or \
                roof_Convection_handle == -1 or roof_netThermalRad_handle == -1 or roof_solarRad_handle == -1 or \
                roof_hConv_handle == -1 or roof_hConv_actuator_handle == -1):
            print('mediumOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)


    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        global ep_last_call_time_seconds, accu_hvac_heat_rejection_J
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                      hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if not one_zone_time_step_bool:
            print(f'accumulation_time_step_in_seconds = {accumulation_time_step_in_seconds}, '
                  f'zone_time_step_seconds = {zone_time_step_seconds}')
            return
        ep_last_call_time_seconds = curr_sim_time_in_seconds

        hvac_waste_w_m2_footprint = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds \
                          / coordination.footprint_area_m2
        accu_hvac_heat_rejection_J = 0

        coordination.ep_indoorTemp_C = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        coordination.ep_indoorHum_Ratio = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   zone_indor_spe_hum_sensor_handle)

        s_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Text_handle)
        s_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Text_handle)
        s_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Text_handle)
        n_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Text_handle)
        n_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Text_handle)
        n_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Text_handle)
        e_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, e_wall_bot_1_Text_handle)
        e_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, e_wall_mid_1_Text_handle)
        e_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, e_wall_top_1_Text_handle)
        w_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, w_wall_bot_1_Text_handle)
        w_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, w_wall_mid_1_Text_handle)
        w_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, w_wall_top_1_Text_handle)




        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)
        s_wall_Text_c = (s_wall_bot_1_Text_c + s_wall_mid_1_Text_c + s_wall_top_1_Text_c)/3
        n_wall_Text_c = (n_wall_bot_1_Text_c + n_wall_mid_1_Text_c + n_wall_top_1_Text_c)/3
        e_wall_Text_c = (e_wall_bot_1_Text_c + e_wall_mid_1_Text_c + e_wall_top_1_Text_c)/3
        w_wall_Text_c = (w_wall_bot_1_Text_c + w_wall_mid_1_Text_c + w_wall_top_1_Text_c)/3

        roof_Conv_w_m2 = coordination.ep_api.exchange.get_variable_value(state, roof_Convection_handle)
        roof_netThermalRad_w_m2 = coordination.ep_api.exchange.get_variable_value(state, roof_netThermalRad_handle)
        roof_solarRad_w_m2 = coordination.ep_api.exchange.get_variable_value(state, roof_solarRad_handle)
        roof_hConv_w_m2_K = coordination.ep_api.exchange.get_variable_value(state, roof_hConv_handle)




        if os.path.exists(coordination.data_saving_path) and not coordination.save_path_clean:
            os.remove(coordination.data_saving_path)
            coordination.save_path_clean = True

        cur_datetime = datetime.datetime.strptime(coordination.config['__main__']['start_time'],
                                                  '%Y-%m-%d %H:%M:%S') + \
                       datetime.timedelta(seconds= curr_sim_time_in_seconds)
        # if current time is between 6:00 and 18:00, override roof_hConv_actuator_handle
        # if 6 <= cur_datetime.hour < 18:
        #     coordination.ep_api.exchange.set_actuator_value(state, roof_hConv_actuator_handle, 40)

        if not os.path.exists(coordination.data_saving_path):
            os.makedirs(os.path.dirname(coordination.data_saving_path), exist_ok=True)
            with open(coordination.data_saving_path, 'a') as f1:
                # prepare the header string for different sensors
                header_str = 'cur_datetime,sensWaste,roof_Conv_w_m2,roof_netThermalRad_w_m2,roof_solarRad_w_m2,roof_hConv_w_m2_K,' \
                             'roof_Text_c,s_wall_Text_c,n_wall_Text_c,e_wall_Text_c,w_wall_Text_c,'
                header_str += '\n'
                f1.write(header_str)
            # write the data
        with open(coordination.data_saving_path, 'a') as f1:
            fmt1 = "%s," * 1 % (cur_datetime) + \
                   "%.3f," * 10 % (hvac_waste_w_m2_footprint,roof_Conv_w_m2,roof_netThermalRad_w_m2,roof_solarRad_w_m2,roof_hConv_w_m2_K,
                                  roof_Text_c,s_wall_Text_c,n_wall_Text_c,e_wall_Text_c,w_wall_Text_c) + '\n'
            f1.write(fmt1)

