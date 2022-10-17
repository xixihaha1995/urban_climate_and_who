from threading import Thread
from . import _0_vcwg_ep_coordination as coordination
from .VCWG_Hydrology import VCWG_Hydro
import os, signal

one_time = True
one_time_call_vcwg = True
accu_hvac_heat_rejection_J = 0
zone_time_step_seconds = 0
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0
def api_to_csv(state):
    orig = coordination.ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(os.path.dirname(__file__), '..','..',coordination.ep_files_path, 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def midRiseApart_nested_ep_only(state):
    global one_time,accu_hvac_heat_rejection_J,\
        zone_time_step_seconds, oat_sensor_handle, hvac_heat_rejection_sensor_handle,\
        site_wind_speed_mps_sensor_handle, site_wind_direction_deg_sensor_handle, \
        ep_last_accumulated_time_index_in_seconds, \
        gsw_wall_Text_handle, gse_office_wall_Text_handle, gs1_wall_Text_handle, gs2_wall_Text_handle, \
        msw_wall_Text_handle, mse_wall_Text_handle, ms1_wall_Text_handle, ms2_wall_Text_handle, \
        tsw_wall_Text_handle, tse_wall_Text_handle, ts1_wall_Text_handle, ts2_wall_Text_handle, \
        gnw_wall_Text_handle, gne_wall_Text_handle, gn1_wall_Text_handle, gn2_wall_Text_handle, \
        mnw_wall_Text_handle, mne_wall_Text_handle, mn1_wall_Text_handle, mn2_wall_Text_handle, \
        tnw_wall_Text_handle, tne_wall_Text_handle, tn1_wall_Text_handle, tn2_wall_Text_handle, \
        tsw_roof_Text_handle, tnw_roof_Text_handle, tse_roof_Text_handle, tne_roof_Text_handle, \
        tn1_roof_Text_handle, tn2_roof_Text_handle, ts1_roof_Text_handle, ts2_roof_Text_handle, \
        t_cor_roof_Text_handle

    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)

        site_wind_speed_mps_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                         "Site Wind Speed",
                                                         "ENVIRONMENT")
        site_wind_direction_deg_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                            "Site Wind Direction",
                                                            "ENVIRONMENT")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")

        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                             "Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
        gsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall SWA")
        gse_office_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall SEA")
        gs1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall S1A")
        gs2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall S2A")
        msw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall SWA")
        mse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                       "m SWall SEA")
        ms1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall S1A")
        ms2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall S2A")
        tsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall SWA")
        tse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                       "t SWall SEA")
        ts1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall S1A")
        ts2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall S2A")
        gnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall NWA")
        gne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall NEA")
        gn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall N1A")
        gn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall N2A")
        mnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall NWA")
        mne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall NEA")
        mn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall N1A")
        mn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall N2A")
        tnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall NWA")
        tne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall NEA")
        tn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall N1A")
        tn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall N2A")

        tsw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof SWA")
        tnw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof NWA")
        tse_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof SEA")
        tne_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof NEA")
        tn1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof N1A")
        tn2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof N2A")
        ts1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof S1A")
        ts2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof S2A")
        t_cor_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                  "Surface Outside Face Temperature",
                                                                                  "t Roof C")
        if oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or \
                site_wind_speed_mps_sensor_handle == -1 or site_wind_direction_deg_sensor_handle == -1 or \
                gsw_wall_Text_handle == -1 or gse_office_wall_Text_handle == -1 or gs1_wall_Text_handle == -1 or \
                gs2_wall_Text_handle == -1 or msw_wall_Text_handle == -1 or mse_wall_Text_handle == -1 or \
                ms1_wall_Text_handle == -1 or ms2_wall_Text_handle == -1 or tsw_wall_Text_handle == -1 or \
                tse_wall_Text_handle == -1 or ts1_wall_Text_handle == -1 or ts2_wall_Text_handle == -1 or \
                gnw_wall_Text_handle == -1 or gne_wall_Text_handle == -1 or gn1_wall_Text_handle == -1 or \
                gn2_wall_Text_handle == -1 or mnw_wall_Text_handle == -1 or mne_wall_Text_handle == -1 or \
                mn1_wall_Text_handle == -1 or mn2_wall_Text_handle == -1 or tnw_wall_Text_handle == -1 or \
                tne_wall_Text_handle == -1 or tn1_wall_Text_handle == -1 or tn2_wall_Text_handle == -1 or \
                tsw_roof_Text_handle == -1 or tnw_roof_Text_handle == -1 or tse_roof_Text_handle == -1 or \
                tne_roof_Text_handle == -1 or tn1_roof_Text_handle == -1 or tn2_roof_Text_handle == -1 or \
                ts1_roof_Text_handle == -1 or ts2_roof_Text_handle == -1 or t_cor_roof_Text_handle == -1:
            print('_nested_ep_only(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_accumulated_time_index_in_seconds
        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                     hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if  not one_zone_time_step_bool: return
        ep_last_accumulated_time_index_in_seconds = curr_sim_time_in_seconds

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)

        coordination.ep_wsp_mps = coordination.ep_api.exchange.get_variable_value(state,
                                                                                  site_wind_speed_mps_sensor_handle)
        coordination.ep_wdir_deg = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   site_wind_direction_deg_sensor_handle)

        gsw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gsw_wall_Text_handle)
        gse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_wall_Text_handle)
        gs1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs1_wall_Text_handle)
        gs2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs2_wall_Text_handle)
        msw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, msw_wall_Text_handle)
        mse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mse_wall_Text_handle)
        ms1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ms1_wall_Text_handle)
        ms2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ms2_wall_Text_handle)
        tsw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tsw_wall_Text_handle)
        tse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tse_wall_Text_handle)
        ts1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts1_wall_Text_handle)
        ts2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts2_wall_Text_handle)

        gnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gnw_wall_Text_handle)
        gne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gne_wall_Text_handle)
        gn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn1_wall_Text_handle)
        gn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn2_wall_Text_handle)
        mnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mnw_wall_Text_handle)
        mne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mne_wall_Text_handle)
        mn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mn1_wall_Text_handle)
        mn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mn2_wall_Text_handle)
        tnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tnw_wall_Text_handle)
        tne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tne_wall_Text_handle)
        tn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn1_wall_Text_handle)
        tn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn2_wall_Text_handle)

        s_wall_Text_C = (gsw_wall_Text_c + gse_wall_Text_c + gs1_wall_Text_c + gs2_wall_Text_c +
                            msw_wall_Text_c*2 + mse_wall_Text_c*2 + ms1_wall_Text_c*2 + ms2_wall_Text_c*2 +
                            tsw_wall_Text_c + tse_wall_Text_c + ts1_wall_Text_c + ts2_wall_Text_c)/16

        n_wall_Text_C = (gnw_wall_Text_c + gne_wall_Text_c + gn1_wall_Text_c + gn2_wall_Text_c +
                         mnw_wall_Text_c * 2 + mne_wall_Text_c * 2 + mn1_wall_Text_c * 2 + mn2_wall_Text_c * 2 +
                         tnw_wall_Text_c + tne_wall_Text_c + tn1_wall_Text_c + tn2_wall_Text_c) / 16

        tsw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tsw_roof_Text_handle)
        tnw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tnw_roof_Text_handle)
        tse_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tse_roof_Text_handle)
        tne_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tne_roof_Text_handle)
        tn1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn1_roof_Text_handle)
        tn2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn2_roof_Text_handle)
        ts1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts1_roof_Text_handle)
        ts2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts2_roof_Text_handle)
        t_cor_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, t_cor_roof_Text_handle)

        roof_Text_C = (tsw_roof_Text_c + tnw_roof_Text_c + tse_roof_Text_c + tne_roof_Text_c +
                       tn1_roof_Text_c + tn2_roof_Text_c + ts1_roof_Text_c + ts2_roof_Text_c + t_cor_roof_Text_c) / 9

        hvac_waste_w_m2_footprint = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds / \
                                    coordination.midRiseApartmentBld_floor_area_m2 * \
                                    coordination.midRiseApart_num_of_floors
        accu_hvac_heat_rejection_J = 0

        coordination.saving_data['ep_wsp_mps_wdir_deg'].append(
            [coordination.ep_wsp_mps, coordination.ep_wdir_deg])
        coordination.saving_data['debugging_canyon'].append([s_wall_Text_C + 273.15,
                                                n_wall_Text_C + 273.15,roof_Text_C + 273.15,
                                                hvac_waste_w_m2_footprint, oat_temp_c + 273.15])


def smallOffice_nested_ep_only(state):
    global one_time,accu_hvac_heat_rejection_J,\
        zone_time_step_seconds, oat_sensor_handle, hvac_heat_rejection_sensor_handle,\
        site_wind_speed_mps_sensor_handle, site_wind_direction_deg_sensor_handle, \
        ep_last_accumulated_time_index_in_seconds, \
        s_wall_Text_handle, n_wall_Text_handle, \
        roof_west_Text_handle, roof_east_Text_handle, roof_north_Text_handle, roof_south_Text_handle

    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                             "Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "HVAC System Total Heat Rejection Energy",
                                                             "SIMHVAC")
        site_wind_speed_mps_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Site Wind Speed",
                                                             "ENVIRONMENT")
        site_wind_direction_deg_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Site Wind Direction",
                                                             "ENVIRONMENT")
        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Perimeter_ZN_1_wall_south")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Perimeter_ZN_3_wall_north")
        roof_west_Text_handle= coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Attic_roof_west")
        roof_east_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Attic_roof_east")
        roof_north_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Attic_roof_north")
        roof_south_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Attic_roof_south")

        if oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or \
                site_wind_speed_mps_sensor_handle == -1 or site_wind_direction_deg_sensor_handle == -1 or \
                s_wall_Text_handle == -1 or n_wall_Text_handle == -1 or \
                roof_west_Text_handle == -1 or roof_east_Text_handle == -1 or \
                roof_north_Text_handle == -1 or roof_south_Text_handle == -1:
            coordination.ep_api.runtime.issue_severe(state, "Error getting variable handles")
            print('smallOffice_nested_ep_only(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_accumulated_time_index_in_seconds
        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                     hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if not one_zone_time_step_bool: return
        ep_last_accumulated_time_index_in_seconds = curr_sim_time_in_seconds

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)

        coordination.ep_wsp_mps = coordination.ep_api.exchange.get_variable_value(state,
                                                                                  site_wind_speed_mps_sensor_handle)
        coordination.ep_wdir_deg = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   site_wind_direction_deg_sensor_handle)
        s_wall_Text = coordination.ep_api.exchange.get_variable_value(state, s_wall_Text_handle)
        n_wall_Text = coordination.ep_api.exchange.get_variable_value(state, n_wall_Text_handle)
        roof_west_Text = coordination.ep_api.exchange.get_variable_value(state, roof_west_Text_handle)
        roof_east_Text = coordination.ep_api.exchange.get_variable_value(state, roof_east_Text_handle)
        roof_north_Text = coordination.ep_api.exchange.get_variable_value(state, roof_north_Text_handle)
        roof_south_Text = coordination.ep_api.exchange.get_variable_value(state, roof_south_Text_handle)

        roof_Text = (roof_west_Text + roof_east_Text + roof_north_Text + roof_south_Text) / 4

        hvac_waste_w_m2_footprint = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds \
                          / coordination.smallOfficeBld_floor_area_m2 * coordination.smallOffice_num_of_floors
        accu_hvac_heat_rejection_J = 0

        coordination.saving_data['ep_wsp_mps_wdir_deg'].append(
            [coordination.ep_wsp_mps, coordination.ep_wdir_deg])

        coordination.saving_data['debugging_canyon'].append([
            s_wall_Text + 273.15, n_wall_Text + 273.15, roof_Text + 273.15,hvac_waste_w_m2_footprint,
            oat_temp_c + 273.15])

def mediumOffice_nested_ep_only(state):
    global one_time, accu_hvac_heat_rejection_J, \
        zone_time_step_seconds, oat_sensor_handle, hvac_heat_rejection_sensor_handle, \
        site_wind_speed_mps_sensor_handle, site_wind_direction_deg_sensor_handle, \
        ep_last_accumulated_time_index_in_seconds, \
        s_wall_bot_1_Text_handle, s_wall_mid_1_Text_handle, s_wall_top_1_Text_handle,\
        n_wall_bot_1_Text_handle, n_wall_mid_1_Text_handle, n_wall_top_1_Text_handle,\
        roof_Text_handle

    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                             "Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "HVAC System Total Heat Rejection Energy",
                                                             "SIMHVAC")
        site_wind_speed_mps_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Site Wind Speed",
                                                             "ENVIRONMENT")
        site_wind_direction_deg_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Site Wind Direction",
                                                             "ENVIRONMENT")
        s_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                              "Surface Outside Face Temperature",
                                                                              "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                    "Surface Outside Face Temperature",
                                                                                    "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                    "Surface Outside Face Temperature",
                                                                                    "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                    "Surface Outside Face Temperature",
                                                                                    "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                    "Surface Outside Face Temperature",
                                                                                    "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                    "Surface Outside Face Temperature",
                                                                                    "Perimeter_top_ZN_3_Wall_North")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                  "Surface Outside Face Temperature",
                                                                                  "Building_Roof")
        if oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or \
                site_wind_speed_mps_sensor_handle == -1 or site_wind_direction_deg_sensor_handle == -1 or \
                s_wall_bot_1_Text_handle == -1 or s_wall_mid_1_Text_handle == -1 or s_wall_top_1_Text_handle == -1 or\
                n_wall_bot_1_Text_handle == -1 or n_wall_mid_1_Text_handle == -1 or n_wall_top_1_Text_handle == -1 or\
                roof_Text_handle == -1:
            print('mediumOffice_nested_ep_only(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_accumulated_time_index_in_seconds
        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                      hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if not one_zone_time_step_bool: return
        ep_last_accumulated_time_index_in_seconds = curr_sim_time_in_seconds

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)

        coordination.ep_wsp_mps = coordination.ep_api.exchange.get_variable_value(state,
                                                                                  site_wind_speed_mps_sensor_handle)
        coordination.ep_wdir_deg = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   site_wind_direction_deg_sensor_handle)
        s_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Text_handle)
        s_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Text_handle)
        s_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Text_handle)
        n_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Text_handle)
        n_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Text_handle)
        n_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Text_handle)

        s_wall_Text_c = (s_wall_bot_1_Text_c + s_wall_mid_1_Text_c + s_wall_top_1_Text_c) / 3
        n_wall_Text_c = (n_wall_bot_1_Text_c + n_wall_mid_1_Text_c + n_wall_top_1_Text_c) / 3

        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)

        hvac_waste_w_m2_footprint = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds \
                          / coordination.mediumOfficeBld_floor_area_m2 * coordination.mediumOffice_num_of_floors
        accu_hvac_heat_rejection_J = 0

        coordination.saving_data['ep_wsp_mps_wdir_deg'].append(
            [coordination.ep_wsp_mps, coordination.ep_wdir_deg])

        coordination.saving_data['debugging_canyon'].append([
            s_wall_Text_c + 273.15, n_wall_Text_c + 273.15, roof_Text_c + 273.15, hvac_waste_w_m2_footprint ,
            oat_temp_c + 273.15])

