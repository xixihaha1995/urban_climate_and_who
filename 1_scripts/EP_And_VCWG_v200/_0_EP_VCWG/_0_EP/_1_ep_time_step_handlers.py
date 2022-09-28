from threading import Thread
from . import _0_vcwg_ep_coordination as coordination
from .._0_Modified_VCWG200.VCWG_Hydrology import VCWG_Hydro

one_time = True
one_time_call_vcwg = True
accu_hvac_heat_rejection_J = 0
zone_time_step_seconds = 0
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0

def _nested_ep_only(state):
    global one_time, accu_hvac_heat_rejection_J,zone_time_step_seconds \
        ,hvac_heat_rejection_sensor_handle, ep_last_accumulated_time_index_in_seconds
    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)

        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")
    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        accumulation_time_step_in_seconds = curr_sim_time_in_seconds - ep_last_accumulated_time_index_in_seconds
        accumulated_bool = 1 > abs(accumulation_time_step_in_seconds - zone_time_step_seconds)

        accu_hvac_heat_rejection_J += coordination.ep_api.exchange.get_variable_value(state,
                                                                                      hvac_heat_rejection_sensor_handle)
        if accumulated_bool:
            coordination.saving_data.append([curr_sim_time_in_seconds,
                                             accu_hvac_heat_rejection_J])
            accu_hvac_heat_rejection_J = 0
            ep_last_accumulated_time_index_in_seconds = curr_sim_time_in_seconds
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
def _nested_ep_then_vcwg_ver0(state):
    global one_time,one_time_call_vcwg,oat_sensor_handle, records,\
        odb_actuator_handle, orh_actuator_handle,\
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle,\
        zone_flr_area_handle,\
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle,\
        floor_interior_conv_handle, floor_interior_lwr_otr_faces_handle, \
        floor_interior_lwr_intGain_handle, floor_interior_lwr_hvac_handle,\
        floor_interior_swr_lights_handle, floor_interior_swr_solar_handle, \
        wall_interior_conv_handle, wall_interior_lwr_otr_faces_handle, \
        wall_interior_lwr_intGain_handle, wall_interior_lwr_hvac_handle, \
        wall_interior_swr_lights_handle, wall_interior_swr_solar_handle, \
        roof_interior_conv_handle, roof_interior_lwr_otr_faces_handle, \
        roof_interior_lwr_intGain_handle, roof_interior_lwr_hvac_handle, \
        roof_interior_swr_lights_handle, roof_interior_swr_solar_handle,\
        floor_Text_handle, roof_Text_handle, \
        floor_Tint_handle, roof_Tint_handle, \
        wall_t_Text_handle, wall_t_Tint_handle, wall_m_Text_handle, wall_m_Tint_handle, wall_g_Text_handle, wall_g_Tint_handle

    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        # coordination.ep_api_to_csv(state)
        oat_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Site Outdoor Air Drybulb Temperature",
                                             "ENVIRONMENT")
        odb_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Dry Bulb",
            "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Relative Humidity",
            "Environment")

        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Temperature","T S1 APARTMENT")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Humidity Ratio","T S1 APARTMENT")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area",
                                                                          "T S1 APARTMENT")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Cooling Rate",
                                                                          "T S1 APARTMENT")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Heating Rate",
                                                                            "T S1 APARTMENT")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Cooling Coil Electricity Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_COOLCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Heating Coil Heating Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_HEATCOIL")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")

        floor_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Convection Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")

        wall_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                "Surface Inside Face Convection Heat Gain Rate per Area",
                                                "t SWall S1A")
        wall_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")

        roof_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Convection Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        floor_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t GFloor S1A")
        floor_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t GFloor S1A")
        wall_t_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t SWall S1A")
        wall_t_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t SWall S1A")
        wall_m_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                              "m SWall S1A")
        wall_m_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "m SWall S1A")
        wall_g_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "g SWall S1A")
        wall_g_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "g SWall S1A")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t Roof S1A")
        roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t Roof S1A")
    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        # Lichen: After EP warm up, start to call VCWG
        if one_time_call_vcwg:
            global zone_time_step_seconds, zone_floor_area_m2, ep_last_call_time_seconds
            zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
            zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state,zone_flr_area_handle)
            one_time_call_vcwg = False
            Thread(target=run_vcwg).start()
        '''
        Lichen: sync EP and VCWG
        1. EP: get the current time in seconds
        2. Compare EP_time_idx_in_seconds with vcwg_needed_time_idx_in_seconds
            a. if true (converged), 
                global_hvac_waste <- ep:hvac_heat_rejection_sensor_handle
                global_oat -> ep:odb_actuator_handle
                release the lock for vcwg, denoted as coordination.sem_energyplus.release()
            b. if false (converged)
                (HVAC is accumulating, probably we need run many HVAC iteration loops for the following ep time indices)
                release the lock for EP, denoted as coordination.sem_vcwg.release()
        '''
        coordination.sem_vcwg.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        # print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
        # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.blf_floor_area_m2
        coordination.ep_sensWaste_w_m2_per_floor_area += hvac_waste_w_m2

        time_index_alignment_bool =  1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            # print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
            # print("EP: vcwg_needed_time_idx_in_seconds: ", coordination.vcwg_needed_time_idx_in_seconds)
            coordination.sem_vcwg.release()
            return

        psychrometric = coordination.ep_api.functional.psychrometrics(state)
        rh = psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.blf_floor_area_m2

        floor_interior_conv = coordination.ep_api.exchange.get_variable_value(state, floor_interior_conv_handle)
        floor_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_otr_faces_handle)
        floor_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_intGain_handle)
        floor_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_hvac_handle)
        floor_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, floor_interior_swr_lights_handle)
        floor_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, floor_interior_swr_solar_handle)
        floor_flux = floor_interior_conv + floor_interior_lwr_otr_faces + floor_interior_lwr_intGain + \
                        floor_interior_lwr_hvac + floor_interior_swr_lights + floor_interior_swr_solar

        wall_interior_conv = coordination.ep_api.exchange.get_variable_value(state, wall_interior_conv_handle)
        wall_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_otr_faces_handle)
        wall_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_intGain_handle)
        wall_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_hvac_handle)
        wall_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, wall_interior_swr_lights_handle)
        wall_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, wall_interior_swr_solar_handle)
        wall_flux = wall_interior_conv + wall_interior_lwr_otr_faces + wall_interior_lwr_intGain + \
                        wall_interior_lwr_hvac + wall_interior_swr_lights + wall_interior_swr_solar
        roof_interior_conv = coordination.ep_api.exchange.get_variable_value(state, roof_interior_conv_handle)
        roof_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_otr_faces_handle)
        roof_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_intGain_handle)
        roof_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_hvac_handle)
        roof_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, roof_interior_swr_lights_handle)
        roof_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, roof_interior_swr_solar_handle)
        roof_flux = roof_interior_conv + roof_interior_lwr_otr_faces + roof_interior_lwr_intGain + \
                        roof_interior_lwr_hvac + roof_interior_swr_lights + roof_interior_swr_solar

        floor_Text_C = coordination.ep_api.exchange.get_variable_value(state, floor_Text_handle)
        floor_Tint_C = coordination.ep_api.exchange.get_variable_value(state, floor_Tint_handle)
        wall_t_Text_C = coordination.ep_api.exchange.get_variable_value(state, wall_t_Text_handle)
        wall_t_Tint_C = coordination.ep_api.exchange.get_variable_value(state, wall_t_Tint_handle)
        wall_m_Text_C = coordination.ep_api.exchange.get_variable_value(state, wall_m_Text_handle)
        wall_m_Tint_C = coordination.ep_api.exchange.get_variable_value(state, wall_m_Tint_handle)
        wall_g_Text_C = coordination.ep_api.exchange.get_variable_value(state, wall_g_Text_handle)
        wall_g_Tint_C = coordination.ep_api.exchange.get_variable_value(state, wall_g_Tint_handle)

        wall_Text_C = (wall_t_Text_C + wall_m_Text_C*2 + wall_g_Text_C) / 4
        wall_Tint_C = (wall_t_Tint_C + wall_m_Tint_C*2 + wall_g_Tint_C) / 4

        roof_Text_C = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)
        roof_Tint_C = coordination.ep_api.exchange.get_variable_value(state, roof_Tint_handle)


        coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
        coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)
        coordination.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15
        coordination.ep_wall_Text_K = wall_Text_C + 273.15
        coordination.ep_wall_Tint_K = wall_Tint_C + 273.15
        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value
        coordination.ep_floor_fluxMass_w_m2 = floor_flux
        coordination.ep_fluxWall_w_m2 = wall_flux
        coordination.ep_fluxRoof_w_m2 = roof_flux

        coordination.sem_energyplus.release()
