import datetime
from threading import Thread
import _0_coordination as coordination

import os, signal

get_ep_results_inited_handle = False
overwrite_ep_weather_inited_handle = False

accu_hvac_heat_rejection_J = 0
zone_floor_area_m2 = 0
zone_time_step_seconds = 0
accumulated_hvac_heat_J = 0
save_path_clean = False
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0

def mediumOffice_get_ep_results(state):
    global get_ep_results_inited_handle, zone_time_step_seconds, accumulated_hvac_heat_J, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, zone_flr_area_handle, \
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        flr_pre1_Text_handle, flr_pre2_Text_handle, flr_pre3_Text_handle, flr_pre4_Text_handle, \
        flr_core_Text_handle, \
        roof_Text_handle, \
        s_wall_bot_1_Text_handle, s_wall_mid_1_Text_handle, s_wall_top_1_Text_handle, \
        n_wall_bot_1_Text_handle, n_wall_mid_1_Text_handle, n_wall_top_1_Text_handle, \
        s_wall_bot_1_Solar_handle, s_wall_mid_1_Solar_handle, s_wall_top_1_Solar_handle, \
        n_wall_bot_1_Solar_handle, n_wall_mid_1_Solar_handle, n_wall_top_1_Solar_handle, \
        flr_pre1_Tint_handle, flr_pre2_Tint_handle, flr_pre3_Tint_handle, flr_pre4_Tint_handle, \
        flr_core_Tint_handle, \
        roof_Tint_handle, \
        s_wall_bot_1_Tint_handle, s_wall_mid_1_Tint_handle, s_wall_top_1_Tint_handle, \
        n_wall_bot_1_Tint_handle, n_wall_mid_1_Tint_handle, n_wall_top_1_Tint_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
        get_ep_results_inited_handle = True
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                             "Site Outdoor Air Drybulb Temperature",\
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
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
        s_wall_bot_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_top_ZN_3_Wall_North")
        flr_pre1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_1_Floor")
        flr_pre2_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_2_Floor")
        flr_pre3_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_3_Floor")
        flr_pre4_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_4_Floor")
        flr_core_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_bot_ZN_5_Floor")
        roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                            "Building_Roof")
        s_wall_bot_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_top_ZN_3_Wall_North")
        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or zone_flr_area_handle == -1 or\
                elec_bld_meter_handle == -1 or zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1 or\
                sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or\
                cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or\
                flr_pre1_Text_handle == -1 or flr_pre2_Text_handle == -1 or flr_pre3_Text_handle == -1 or\
                flr_pre4_Text_handle == -1 or flr_core_Text_handle == -1 or roof_Text_handle == -1 or\
                s_wall_bot_1_Text_handle == -1 or s_wall_mid_1_Text_handle == -1 or s_wall_top_1_Text_handle == -1 or\
                n_wall_bot_1_Text_handle == -1 or n_wall_mid_1_Text_handle == -1 or n_wall_top_1_Text_handle == -1 or\
                s_wall_bot_1_Solar_handle == -1 or s_wall_mid_1_Solar_handle == -1 or s_wall_top_1_Solar_handle == -1 or\
                n_wall_bot_1_Solar_handle == -1 or n_wall_mid_1_Solar_handle == -1 or n_wall_top_1_Solar_handle == -1 or\
                flr_pre1_Tint_handle == -1 or flr_pre2_Tint_handle == -1 or flr_pre3_Tint_handle == -1 or\
                flr_pre4_Tint_handle == -1 or flr_core_Tint_handle == -1 or roof_Tint_handle == -1 or\
                s_wall_bot_1_Tint_handle == -1 or s_wall_mid_1_Tint_handle == -1 or s_wall_top_1_Tint_handle == -1 or\
                n_wall_bot_1_Tint_handle == -1 or n_wall_mid_1_Tint_handle == -1 or n_wall_top_1_Tint_handle == -1):
            print('mediumOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    if (get_ep_results_inited_handle ) and (not coordination.ep_api.exchange.warmup_flag(state)):
        global ep_last_call_time_seconds, zone_floor_area_m2
        zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = int(curr_sim_time_in_hours * 3600)  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds

        one_zone_time_step_bool = 2 > abs(accumulated_time_in_seconds - zone_time_step_seconds)
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,hvac_heat_rejection_sensor_handle)
        accumulated_hvac_heat_J += hvac_heat_rejection_J
        if not one_zone_time_step_bool:
            return
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.mediumOfficeBld_floor_area_m2

        flr_core_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_core_Text_handle)
        flr_pre1_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre1_Text_handle)
        flr_pre2_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre2_Text_handle)
        flr_pre3_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre3_Text_handle)
        flr_pre4_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre4_Text_handle)
        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)

        s_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Text_handle)
        s_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Text_handle)
        s_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Text_handle)
        n_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Text_handle)
        n_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Text_handle)
        n_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Text_handle)


        flr_core_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_core_Tint_handle)
        flr_pre1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre1_Tint_handle)
        flr_pre2_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre2_Tint_handle)
        flr_pre3_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre3_Tint_handle)
        flr_pre4_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre4_Tint_handle)
        roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_Tint_handle)

        s_wall_bot_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Tint_handle)
        s_wall_mid_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Tint_handle)
        s_wall_top_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Tint_handle)
        n_wall_bot_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Tint_handle)
        n_wall_mid_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Tint_handle)
        n_wall_top_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Tint_handle)

        s_wall_bot_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Solar_handle)
        s_wall_mid_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Solar_handle)
        s_wall_top_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Solar_handle)
        n_wall_bot_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Solar_handle)
        n_wall_mid_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Solar_handle)
        n_wall_top_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Solar_handle)

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)

        floor_Text_C = (flr_core_Text_c + flr_pre1_Text_c + flr_pre2_Text_c + flr_pre3_Text_c + flr_pre4_Text_c )/5
        floor_Tint_C = (flr_core_Tint_c + flr_pre1_Tint_c + flr_pre2_Tint_c + flr_pre3_Tint_c + flr_pre4_Tint_c )/5

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        ep_roof_Text_K = roof_Text_c + 273.15
        ep_roof_Tint_K = roof_Tint_c + 273.15

        s_wall_Solar_w_m2 = (s_wall_bot_1_Solar_w_m2 + s_wall_mid_1_Solar_w_m2 + s_wall_top_1_Solar_w_m2)/3
        n_wall_Solar_w_m2 = (n_wall_bot_1_Solar_w_m2 + n_wall_mid_1_Solar_w_m2 + n_wall_top_1_Solar_w_m2)/3

        s_wall_Text_c = (s_wall_bot_1_Text_c + s_wall_mid_1_Text_c + s_wall_top_1_Text_c)/3
        s_wall_Tint_c = (s_wall_bot_1_Tint_c + s_wall_mid_1_Tint_c + s_wall_top_1_Tint_c)/3
        n_wall_Text_c = (n_wall_bot_1_Text_c + n_wall_mid_1_Text_c + n_wall_top_1_Text_c)/3
        n_wall_Tint_c = (n_wall_bot_1_Tint_c + n_wall_mid_1_Tint_c + n_wall_top_1_Tint_c)/3

        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            ep_wallSun_Text_K = s_wall_Text_c + 273.15
            ep_wallSun_Tint_K = s_wall_Tint_c + 273.15
            ep_wallShade_Text_K = n_wall_Text_c + 273.15
            ep_wallShade_Tint_K = n_wall_Tint_c + 273.15
        else:
            ep_wallSun_Text_K = n_wall_Text_c + 273.15
            ep_wallSun_Tint_K = n_wall_Tint_c + 273.15
            ep_wallShade_Text_K = s_wall_Text_c + 273.15
            ep_wallShade_Tint_K = s_wall_Tint_c + 273.15

        data_saving_path = coordination.data_saving_path
        global save_path_clean
        if os.path.exists(data_saving_path) and not save_path_clean:
            os.remove(data_saving_path)
            save_path_clean = True
        cur_datetime = datetime.datetime.strptime(coordination.config['shading']['start_time'],
                                                  '%Y-%m-%d %H:%M:%S') + \
                       datetime.timedelta(seconds=curr_sim_time_in_seconds)

        if not os.path.exists(data_saving_path):
            os.makedirs(os.path.dirname(data_saving_path), exist_ok=True)
            with open(data_saving_path, 'a') as f1:
                header_str = 'cur_datetime,WallshadeT,WalllitT,RoofT,oat_temp_c,ep_sensWaste_w_m2_per_footprint_area,\n'
                f1.write(header_str)

        WallshadeT = ep_wallShade_Text_K
        WalllitT = ep_wallSun_Text_K
        RoofT = ep_roof_Text_K
        ep_sensWaste_w_m2_per_floor_area = accumulated_hvac_heat_J /zone_time_step_seconds \
                                           / coordination.mediumOfficeBld_floor_area_m2
        with open(data_saving_path, 'a') as f1:
            fmt1 = "%s," * 1 % (cur_datetime) + \
                   "%.3f," * 5 % (WallshadeT, WalllitT, RoofT,oat_temp_c,
                                  ep_sensWaste_w_m2_per_floor_area * int(coordination.config['shading']['n_floor'])) + '\n'
            f1.write(fmt1)

        accumulated_hvac_heat_J = 0
