import sys,  numpy as np, pandas as pd, os
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
# time step in seconds
time_step_seconds = 0
# floor area in m2
blf_floor_area_m2 = 3135
zone_floor_area_m2 = 0

def api_to_csv(state):
    orig = api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(ep_files_path, 'api.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def time_step_handler(state):
    global one_time,one_time_call_vcwg,ep_last_time_index_in_seconds ,oat_sensor_handle, records,\
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
        if not api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        ep_last_time_index_in_seconds = 0
        # api_to_csv(state)
        oat_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "Site Outdoor Air Drybulb Temperature",
                                             "ENVIRONMENT")
        odb_actuator_handle = api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Dry Bulb",
            "Environment")
        orh_actuator_handle = api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Relative Humidity",
            "Environment")

        zone_indor_temp_sensor_handle = api.exchange.get_variable_handle(state,"Zone Air Temperature","T S1 APARTMENT")
        zone_indor_spe_hum_sensor_handle = api.exchange.get_variable_handle(state,"Zone Air Humidity Ratio","T S1 APARTMENT")
        zone_flr_area_handle =  api.exchange.get_internal_variable_handle(state, "Zone Floor Area",
                                                                          "T S1 APARTMENT")
        sens_cool_demand_sensor_handle = api.exchange.get_variable_handle(state,"Zone Air System Sensible Cooling Rate",
                                                                          "T S1 APARTMENT")
        sens_heat_demand_sensor_handle = api.exchange.get_variable_handle(state,"Zone Air System Sensible Heating Rate",
                                                                            "T S1 APARTMENT")
        cool_consumption_sensor_handle = api.exchange.get_variable_handle(state,"Cooling Coil Electricity Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_COOLCOIL")
        heat_consumption_sensor_handle = api.exchange.get_variable_handle(state,"Heating Coil Heating Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_HEATCOIL")
        hvac_heat_rejection_sensor_handle = \
            api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")
        elec_bld_meter_handle = api.exchange.get_meter_handle(state, "Electricity:Building")

        floor_interior_conv_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Convection Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_otr_faces_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_intGain_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_hvac_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_lights_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_solar_handle = \
            api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")

        wall_interior_conv_handle = \
            api.exchange.get_variable_handle(state,
                                                "Surface Inside Face Convection Heat Gain Rate per Area",
                                                "t SWall S1A")
        wall_interior_lwr_otr_faces_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_intGain_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_hvac_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_lights_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_solar_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")

        roof_interior_conv_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Convection Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_otr_faces_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_intGain_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_hvac_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_lights_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_solar_handle = \
            api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        floor_Text_handle = api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t GFloor S1A")
        floor_Tint_handle = api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t GFloor S1A")
        wall_t_Text_handle = api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t SWall S1A")
        wall_t_Tint_handle = api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t SWall S1A")
        wall_m_Text_handle = api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                              "m SWall S1A")
        wall_m_Tint_handle = api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "m SWall S1A")
        wall_g_Text_handle = api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "g SWall S1A")
        wall_g_Tint_handle = api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "g SWall S1A")
        roof_Text_handle = api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                "t Roof S1A")
        roof_Tint_handle = api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                "t Roof S1A")


    warm_up = api.exchange.warmup_flag(state)
    if not warm_up:
        # Lichen: After EP warm up, start to call VCWG
        if one_time_call_vcwg:
            global time_step_seconds, zone_floor_area_m2
            time_step_seconds = 3600 / api.exchange.num_time_steps_in_hour(state)
            zone_floor_area_m2 = api.exchange.get_internal_variable_value(state,zone_flr_area_handle)
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
        print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
        # if curr_sim_time_in_seconds != ep_last_time_index_in_seconds:
        #     print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
        #     print("EP: ep_last_time_index_in_seconds: ", ep_last_time_index_in_seconds)
        #     coordiantion.ep_accumulated_waste_heat += _this_waste_heat
        #     records.append([ep_last_time_index_in_seconds, curr_sim_time_in_seconds,
        #                     coordiantion.vcwg_needed_time_idx_in_seconds, coordiantion.ep_accumulated_waste_heat])
        #     ep_last_time_index_in_seconds = curr_sim_time_in_seconds
        time_index_alignment_bool =  1 > abs(curr_sim_time_in_seconds - coordiantion.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
            print("EP: vcwg_needed_time_idx_in_seconds: ", coordiantion.vcwg_needed_time_idx_in_seconds)
            coordiantion.sem_vcwg.release()
            return

        psychrometric = api.functional.psychrometrics(state)
        rh = psychrometric.relative_humidity_b(state, coordiantion.vcwg_canTemp_K - 273.15,
                                               coordiantion.vcwg_canSpecHum_Ratio, coordiantion.vcwg_canPress_Pa)
        zone_indor_temp_value = api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = api.exchange.get_variable_value(state, zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = api.exchange.get_variable_value(state, sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = api.exchange.get_variable_value(state, sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = api.exchange.get_variable_value(state, cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = api.exchange.get_variable_value(state, heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / blf_floor_area_m2

        hvac_heat_rejection_J = api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / time_step_seconds/blf_floor_area_m2

        floor_interior_conv = api.exchange.get_variable_value(state, floor_interior_conv_handle)
        floor_interior_lwr_otr_faces = api.exchange.get_variable_value(state, floor_interior_lwr_otr_faces_handle)
        floor_interior_lwr_intGain = api.exchange.get_variable_value(state, floor_interior_lwr_intGain_handle)
        floor_interior_lwr_hvac = api.exchange.get_variable_value(state, floor_interior_lwr_hvac_handle)
        floor_interior_swr_lights = api.exchange.get_variable_value(state, floor_interior_swr_lights_handle)
        floor_interior_swr_solar = api.exchange.get_variable_value(state, floor_interior_swr_solar_handle)
        floor_flux = floor_interior_conv + floor_interior_lwr_otr_faces + floor_interior_lwr_intGain + \
                        floor_interior_lwr_hvac + floor_interior_swr_lights + floor_interior_swr_solar

        wall_interior_conv = api.exchange.get_variable_value(state, wall_interior_conv_handle)
        wall_interior_lwr_otr_faces = api.exchange.get_variable_value(state, wall_interior_lwr_otr_faces_handle)
        wall_interior_lwr_intGain = api.exchange.get_variable_value(state, wall_interior_lwr_intGain_handle)
        wall_interior_lwr_hvac = api.exchange.get_variable_value(state, wall_interior_lwr_hvac_handle)
        wall_interior_swr_lights = api.exchange.get_variable_value(state, wall_interior_swr_lights_handle)
        wall_interior_swr_solar = api.exchange.get_variable_value(state, wall_interior_swr_solar_handle)
        wall_flux = wall_interior_conv + wall_interior_lwr_otr_faces + wall_interior_lwr_intGain + \
                        wall_interior_lwr_hvac + wall_interior_swr_lights + wall_interior_swr_solar
        roof_interior_conv = api.exchange.get_variable_value(state, roof_interior_conv_handle)
        roof_interior_lwr_otr_faces = api.exchange.get_variable_value(state, roof_interior_lwr_otr_faces_handle)
        roof_interior_lwr_intGain = api.exchange.get_variable_value(state, roof_interior_lwr_intGain_handle)
        roof_interior_lwr_hvac = api.exchange.get_variable_value(state, roof_interior_lwr_hvac_handle)
        roof_interior_swr_lights = api.exchange.get_variable_value(state, roof_interior_swr_lights_handle)
        roof_interior_swr_solar = api.exchange.get_variable_value(state, roof_interior_swr_solar_handle)
        roof_flux = roof_interior_conv + roof_interior_lwr_otr_faces + roof_interior_lwr_intGain + \
                        roof_interior_lwr_hvac + roof_interior_swr_lights + roof_interior_swr_solar

        floor_Text_C = api.exchange.get_variable_value(state, floor_Text_handle)
        floor_Tint_C = api.exchange.get_variable_value(state, floor_Tint_handle)
        wall_t_Text_C = api.exchange.get_variable_value(state, wall_t_Text_handle)
        wall_t_Tint_C = api.exchange.get_variable_value(state, wall_t_Tint_handle)
        wall_m_Text_C = api.exchange.get_variable_value(state, wall_m_Text_handle)
        wall_m_Tint_C = api.exchange.get_variable_value(state, wall_m_Tint_handle)
        wall_g_Text_C = api.exchange.get_variable_value(state, wall_g_Text_handle)
        wall_g_Tint_C = api.exchange.get_variable_value(state, wall_g_Tint_handle)

        wall_Text_C = (wall_t_Text_C + wall_m_Text_C + wall_g_Text_C) / 3
        wall_Tint_C = (wall_t_Tint_C + wall_m_Tint_C + wall_g_Tint_C) / 3

        roof_Text_C = api.exchange.get_variable_value(state, roof_Text_handle)
        roof_Tint_C = api.exchange.get_variable_value(state, roof_Tint_handle)


        api.exchange.set_actuator_value(state, odb_actuator_handle, coordiantion.vcwg_canTemp_K - 273.15)
        api.exchange.set_actuator_value(state, orh_actuator_handle, rh)
        coordiantion.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2
        coordiantion.ep_sensWaste_w_m2_per_floor_area = hvac_waste_w_m2
        coordiantion.ep_floor_Text_K = floor_Text_C + 273.15
        coordiantion.ep_floor_Tint_K = floor_Tint_C + 273.15
        coordiantion.ep_wall_Text_K = wall_Text_C + 273.15
        coordiantion.ep_wall_Tint_K = wall_Tint_C + 273.15
        coordiantion.ep_roof_Text_K = roof_Text_C + 273.15
        coordiantion.ep_roof_Tint_K = roof_Tint_C + 273.15

        coordiantion.ep_indoorTemp_C = zone_indor_temp_value
        coordiantion.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordiantion.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordiantion.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordiantion.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordiantion.ep_heatConsump_w_m2 = heat_consumption_w_m2_value
        coordiantion.ep_floor_fluxMass_w_m2 = floor_flux
        coordiantion.ep_fluxWall_w_m2 = wall_flux
        coordiantion.ep_fluxRoof_w_m2 = roof_flux

        coordiantion.sem_energyplus.release()

def run_ep_api():
    state = api.state_manager.new_state()
    # api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
    api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handler)
    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    # api.exchange.request_variable(state, "Plant Supply Side Cooling Demand Rate", "SHWSYS1")
    # api.exchange.request_variable(state, "Plant Supply Side Heating Demand Rate", "SHWSYS1")
    # api.exchange.request_variable(state, "Zone Air System Sensible Cooling Rate", "PERIMETER_ZN_1")
    # api.exchange.request_variable(state, "Zone Air System Sensible Heating Rate", "PERIMETER_ZN_1")

    # api.exchange.request_variable(state, "Surface Inside Face Convection Heat Gain Rate per Area", "g EWall SEA")
    # api.exchange.request_variable(state, "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area", "g EWall SEA")
    # api.exchange.request_variable(state, "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area", "g EWall SWA")
    # api.exchange.request_variable(state, "Surface Inside Face System Radiation Heat Gain Rate per Area", "g EWall SWA")
    # api.exchange.request_variable(state, "Surface Inside Face Lights Radiation Heat Gain Rate per Area", "g EWall NWA")
    # api.exchange.request_variable(state, "Surface Inside Face Solar Radiation Heat Gain Rate per Area", "g EWall NWA")

    global ep_files_path
    ep_files_path = '_02_ep_midRiseApartment'

    epwFileName = 'ERA5_Basel_Jun.epw'
    idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE.idf'

    output_path = os.path.join(ep_files_path, 'ep_outputs')
    weather_file_path = os.path.join(ep_files_path, epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    api.runtime.run_energyplus(state, sys_args)

def run_vcwg():
    epwFileName = 'ERA5_Basel_Jun.epw'
    TopForcingFileName = None
    VCWGParamFileName = 'initialize_Basel_MOST.uwg'
    ViewFactorFileName = 'ViewFactor_Basel_MOST.txt'
    # Case name to append output file names with
    case = '_bypass_3in1_Basel_MOST'

    # epwFileName = None
    # TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    # VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = 'Vancouver_LCZ1'

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

    # # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    # records_arr = np.array(records)
    # # array to df
    # records_df = pd.DataFrame(records_arr, columns=['last_time_in_seconds', 'curr_sim_time_in_seconds',
    #                                                 'vcwg_needed_time_idx_in_seconds',
    #                                                 'coordiantion.ep_accumulated_waste_heat'])
    # saved_records_name = ep_files_path + '/records_df.csv'
    # saved_records_path = os.path.join('_1_plots_related',saved_records_name)
    # records_df.to_csv(saved_records_path, index=False)

