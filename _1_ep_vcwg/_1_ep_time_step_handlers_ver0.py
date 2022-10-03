from threading import Thread
from . import _0_vcwg_ep_coordination as coordination
from .VCWG_Hydrology import VCWG_Hydro
import os

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
def _nested_ep_only(state):
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
    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_accumulated_time_index_in_seconds
        accu_hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,
                                                                                     hvac_heat_rejection_sensor_handle)

        one_zone_time_step_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)
        if  not one_zone_time_step_bool: return
        ep_last_accumulated_time_index_in_seconds = curr_sim_time_in_seconds

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)

        hvac_waste_w_m2 = accu_hvac_heat_rejection_J / accumulation_time_step_in_seconds / coordination.bld_floor_area_m2
        accu_hvac_heat_rejection_J = 0

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


        coordination.saving_data['ep_wsp_mps_wdir_deg'].append(
            [coordination.ep_wsp_mps, coordination.ep_wdir_deg])
        coordination.saving_data['debugging_canyon'].append([s_wall_Text_C + 273.15,
                                                n_wall_Text_C + 273.15,roof_Text_C + 273.15,
                                                hvac_waste_w_m2, oat_temp_c + 273.15])



def run_vcwg():
    epwFileName = 'Basel.epw'
    TopForcingFileName = None
    # VCWGParamFileName = 'initialize_Basel_BSPA_MOST.uwg'
    VCWGParamFileName = '_case5_initialize_Basel_BSPR_MOST.uwg'
    # ViewFactorFileName = '_BSPA_ViewFactor_Basel_MOST.txt'
    ViewFactorFileName = '_case5_BSPR_ViewFactor_Basel_MOST.txt'
    # Case name to append output file names with
    # case = '_BSPA_Refinement_M2_Basel_MOST'
    case = '_BSPR_Refinement_M2_Basel_MOST'

    # '''

    # epwFileName = 'TopForcing_year.epw'
    # TopForcingFileName = None
    # # TopForcingFileName = 'Vancouver2008_ERA5.csv'
    # VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = '_bypass_year_Vancouver_LCZ1'

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()
