from threading import Thread
import _0_vcwg_ep_coordination as coordination
from VCWG_Hydrology import VCWG_Hydro
import os, signal

get_ep_results_inited_handle = False
overwrite_ep_weather_inited_handle = False
called_vcwg_bool = False

accu_hvac_heat_rejection_J = 0
zone_floor_area_m2 = 0
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0

def api_to_csv(state):
    orig = coordination.ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join('A_prepost_processing',coordination.config['shading']['experiments'],
                            f'{coordination.uwgVariableValue}api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()

def run_vcwg():
    epwFileName = coordination.config['shading']['epwFileName']
    TopForcingFileName = None
    VCWGParamFileName = coordination.config['_1_ep_time_step_handler.py']['VCWGParamFileName']
    idf_suffix = coordination.uwgVariableValue
    ViewFactorFileName = f'ShadingBypass_{idf_suffix}ViewFactor_Capitoul_MOST.txt'
    # Case name to append output file names with
    case = f'ShadingBypass_{idf_suffix}_Capitoul_MOST'
    '''
    epwFileName = None
    TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    VCWGParamFileName = 'initialize_Vancouver_LCZ1_2.uwg'
    ViewFactorFileName = 'viewfactor_Vancouver.txt'
    # Case name to append output file names with
    case = 'Vancouver_LCZ1'
    '''
    '''
    epwFileName = 'Guelph_2018.epw'
    TopForcingFileName = None
    VCWGParamFileName = 'initialize_Guelph.uwg'
    ViewFactorFileName = 'viewfactor_Guelph.txt'
    # Case name to append output file names with
    case = 'Guelph_2018'
    '''
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def overwrite_ep_weather(state):
    global overwrite_ep_weather_inited_handle, odb_actuator_handle, orh_actuator_handle, \
        wsped_mps_actuator_handle, wdir_deg_actuator_handle,zone_flr_area_handle,\
        called_vcwg_bool


    if not overwrite_ep_weather_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        api_to_csv(state)
        overwrite_ep_weather_inited_handle = True
        odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Relative Humidity", "Environment")
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Site Outdoor Air Drybulb Temperature", "Environment")
        orh_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Site Outdoor Air Humidity Ratio","Environment")
    # zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area", "CORE_ZN")
        #if one of the above handles is less than 0, then the actuator is not available
        # the entire program (multithread cooperation) should be terminated here, system exit with print messagePYTHO
        #if odb_actuator_handle < 0 or orh_actuator_handle < 0 or zone_flr_area_handle < 0:
        if odb_actuator_handle < 0 or orh_actuator_handle < 0:
            print('ovewrite_ep_weather(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        if not called_vcwg_bool:
            global zone_floor_area_m2
            #zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
            called_vcwg_bool = True
            Thread(target=run_vcwg).start()
        # Wait for the upstream (VCWG upload canyon info to Parent) to finish
        coordination.sem1.acquire()
        # EP download the canyon info from Parent
        #psychrometric = coordination.ep_api.functional.psychrometrics(state)
        rh = 100*coordination.psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
        coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
        print(f'EP: set odb to {coordination.vcwg_canTemp_K - 273.15}')
        coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)
        # Notify the downstream (EP upload EP results to Parent) to start
        #coordination.sem1.release()#
        coordination.sem2.release()#


def get_ep_results(state):
    global get_ep_results_inited_handle, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, \
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, zone_flr_area_handle,\
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        gsw_flr_Text_handle, gnw_flr_Text_handle, gse_office_flr_Text_handle, gne_flr_Text_handle, \
        gn1_flr_Text_handle, gn2_flr_Text_handle, gs1_flr_Text_handle, gs2_flr_Text_handle, \
        tsw_roof_Text_handle, tnw_roof_Text_handle, tse_roof_Text_handle, tne_roof_Text_handle, \
        tn1_roof_Text_handle, tn2_roof_Text_handle, ts1_roof_Text_handle, ts2_roof_Text_handle, \
        t_cor_roof_Text_handle,\
        gsw_flr_Tint_handle, gnw_flr_Tint_handle, gse_office_flr_Tint_handle, gne_flr_Tint_handle, \
        gn1_flr_Tint_handle, gn2_flr_Tint_handle, gs1_flr_Tint_handle, gs2_flr_Tint_handle, \
        tsw_roof_Tint_handle, tnw_roof_Tint_handle, tse_roof_Tint_handle, tne_roof_Tint_handle, \
        tn1_roof_Tint_handle, tn2_roof_Tint_handle, ts1_roof_Tint_handle, ts2_roof_Tint_handle, \
        t_cor_roof_Tint_handle,\
        gsw_wall_Text_handle, gse_office_wall_Text_handle, gs1_wall_Text_handle, gs2_wall_Text_handle,\
        msw_wall_Text_handle, mse_wall_Text_handle, ms1_wall_Text_handle, ms2_wall_Text_handle,\
        tsw_wall_Text_handle, tse_wall_Text_handle, ts1_wall_Text_handle, ts2_wall_Text_handle,\
        gnw_wall_Text_handle, gne_wall_Text_handle, gn1_wall_Text_handle, gn2_wall_Text_handle,\
        mnw_wall_Text_handle, mne_wall_Text_handle, mn1_wall_Text_handle, mn2_wall_Text_handle,\
        tnw_wall_Text_handle, tne_wall_Text_handle, tn1_wall_Text_handle, tn2_wall_Text_handle,\
        gsw_wall_Tint_handle, gse_office_wall_Tint_handle, gs1_wall_Tint_handle, gs2_wall_Tint_handle,\
        msw_wall_Tint_handle, mse_wall_Tint_handle, ms1_wall_Tint_handle, ms2_wall_Tint_handle,\
        tsw_wall_Tint_handle, tse_wall_Tint_handle, ts1_wall_Tint_handle, ts2_wall_Tint_handle,\
        gnw_wall_Tint_handle, gne_wall_Tint_handle, gn1_wall_Tint_handle, gn2_wall_Tint_handle,\
        mnw_wall_Tint_handle, mne_wall_Tint_handle, mn1_wall_Tint_handle, mn2_wall_Tint_handle,\
        tnw_wall_Tint_handle, tne_wall_Tint_handle, tn1_wall_Tint_handle, tn2_wall_Tint_handle,\
        gsw_solar_handle, gse_office_solar_handle, gs1_solar_handle, gs2_solar_handle,\
        msw_solar_handle, mse_solar_handle, ms1_solar_handle, ms2_solar_handle,\
        tsw_solar_handle, tse_solar_handle, ts1_solar_handle, ts2_solar_handle,\
        gnw_solar_handle, gne_solar_handle, gn1_solar_handle, gn2_solar_handle,\
        mnw_solar_handle, mne_solar_handle, mn1_solar_handle, mn2_solar_handle,\
        tnw_solar_handle, tne_solar_handle, tn1_solar_handle, tn2_solar_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        #api_to_csv(state)
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Site Outdoor Air Drybulb Temperature", "Environment")
        gsw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor SWA")
        gnw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor NWA")
        gse_office_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor SEA")
        gne_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor NEA")
        gn1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor N1A")
        gn2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor N2A")
        gs1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor S1A")
        gs2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g GFloor S2A")
        tsw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof SWA")
        tnw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof NWA")
        tse_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof SEA")
        tne_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof NEA")
        tn1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof N1A")
        tn2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof N2A")
        ts1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof S1A")
        ts2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof S2A")
        t_cor_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t Roof C")
        gsw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor SWA")
        gnw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor NWA")
        gse_office_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor SEA")
        gne_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor NEA")
        gn1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor N1A")
        gn2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor N2A")
        gs1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor S1A")
        gs2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g GFloor S2A")
        tsw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof SWA")
        tnw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof NWA")
        tse_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof SEA")
        tne_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof NEA")
        tn1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof N1A")
        tn2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof N2A")
        ts1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof S1A")
        ts2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof S2A")
        t_cor_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t Roof C")

        gsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g SWall SWA")
        gse_office_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g SWall SEA")
        gs1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g SWall S1A")
        gs2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g SWall S2A")
        msw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m SWall SWA")
        mse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m SWall SEA")
        ms1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m SWall S1A")
        ms2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m SWall S2A")
        tsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t SWall SWA")
        tse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t SWall SEA")
        ts1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t SWall S1A")
        ts2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t SWall S2A")
        gnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g NWall NWA")
        gne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g NWall NEA")
        gn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g NWall N1A")
        gn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "g NWall N2A")
        mnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m NWall NWA")
        mne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m NWall NEA")
        mn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m NWall N1A")
        mn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "m NWall N2A")
        tnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t NWall NWA")
        tne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t NWall NEA")
        tn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t NWall N1A")
        tn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "t NWall N2A")
        gsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g SWall SWA")
        gse_office_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g SWall SEA")
        gs1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g SWall S1A")
        gs2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g SWall S2A")
        msw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m SWall SWA")
        mse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m SWall SEA")
        ms1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m SWall S1A")
        ms2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m SWall S2A")
        tsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t SWall SWA")
        tse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t SWall SEA")
        ts1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t SWall S1A")
        ts2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t SWall S2A")
        gnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g NWall NWA")
        gne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g NWall NEA")
        gn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g NWall N1A")
        gn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "g NWall N2A")
        mnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m NWall NWA")
        mne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m NWall NEA")
        mn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m NWall N1A")
        mn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "m NWall N2A")
        tnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t NWall NWA")
        tne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t NWall NEA")
        tn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t NWall N1A")
        tn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature", "t NWall N2A")
        gsw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g SWall SWA")
        gse_office_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g SWall SEA")
        gs1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g SWall S1A")
        gs2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g SWall S2A")
        msw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m SWall SWA")
        mse_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m SWall SEA")
        ms1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m SWall S1A")
        ms2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m SWall S2A")
        tsw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t SWall SWA")
        tse_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t SWall SEA")
        ts1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t SWall S1A")
        ts2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t SWall S2A")
        gnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g NWall NWA")
        gne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g NWall NEA")
        gn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g NWall N1A")
        gn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "g NWall N2A")
        mnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m NWall NWA")
        mne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m NWall NEA")
        mn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m NWall N1A")
        mn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "m NWall N2A")
        tnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t NWall NWA")
        tne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t NWall NEA")
        tn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t NWall N1A")
        tn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area", "t NWall N2A")

        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Temperature","T S1 APARTMENT")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Humidity Ratio","T S1 APARTMENT")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area", "T S1 APARTMENT")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Cooling Rate", "T S1 APARTMENT")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Heating Rate", "T S1 APARTMENT")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Cooling Coil Electricity Rate", "SPLITSYSTEMAC:23_UNITARY_PACKAGE_COOLCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Heating Coil Heating Rate", "SPLITSYSTEMAC:23_UNITARY_PACKAGE_HEATCOIL")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")
        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or elec_bld_meter_handle == -1 or \
            zone_indor_temp_sensor_handle == -1 or zone_indor_spe_hum_sensor_handle == -1 or zone_flr_area_handle == -1 or \
            sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or \
            cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or
            gsw_flr_Text_handle == -1 or gnw_flr_Text_handle == -1 or gse_office_flr_Text_handle == -1 or gne_flr_Text_handle == -1 or \
            gn1_flr_Text_handle == -1 or gn2_flr_Text_handle == -1 or gs1_flr_Text_handle == -1 or gs2_flr_Text_handle == -1 or \
            tsw_roof_Text_handle == -1 or tnw_roof_Text_handle == -1 or tse_roof_Text_handle == -1 or tne_roof_Text_handle == -1 or \
            tn1_roof_Text_handle == -1 or tn2_roof_Text_handle == -1 or ts1_roof_Text_handle == -1 or ts2_roof_Text_handle == -1 or \
            t_cor_roof_Text_handle == -1 or \
            gsw_flr_Tint_handle == -1 or gnw_flr_Tint_handle == -1 or gse_office_flr_Tint_handle == -1 or gne_flr_Tint_handle == -1 or \
            gn1_flr_Tint_handle == -1 or gn2_flr_Tint_handle == -1 or gs1_flr_Tint_handle == -1 or gs2_flr_Tint_handle == -1 or \
            tsw_roof_Tint_handle == -1 or tnw_roof_Tint_handle == -1 or tse_roof_Tint_handle == -1 or tne_roof_Tint_handle == -1 or \
            tn1_roof_Tint_handle == -1 or tn2_roof_Tint_handle == -1 or ts1_roof_Tint_handle == -1 or ts2_roof_Tint_handle == -1 or \
            t_cor_roof_Tint_handle == -1 or \
            gsw_wall_Text_handle == -1 or gse_office_wall_Text_handle == -1 or gs1_wall_Text_handle == -1 or gs2_wall_Text_handle == -1 or \
            msw_wall_Text_handle == -1 or mse_wall_Text_handle == -1 or ms1_wall_Text_handle == -1 or ms2_wall_Text_handle == -1 or \
            tsw_wall_Text_handle == -1 or tse_wall_Text_handle == -1 or ts1_wall_Text_handle == -1 or ts2_wall_Text_handle == -1 or \
            gnw_wall_Text_handle == -1 or gne_wall_Text_handle == -1 or gn1_wall_Text_handle == -1 or gn2_wall_Text_handle == -1 or \
            mnw_wall_Text_handle == -1 or mne_wall_Text_handle == -1 or mn1_wall_Text_handle == -1 or mn2_wall_Text_handle == -1 or \
            tnw_wall_Text_handle == -1 or tne_wall_Text_handle == -1 or tn1_wall_Text_handle == -1 or tn2_wall_Text_handle == -1 or \
            gsw_wall_Tint_handle == -1 or gse_office_wall_Tint_handle == -1 or gs1_wall_Tint_handle == -1 or gs2_wall_Tint_handle == -1 or \
            msw_wall_Tint_handle == -1 or mse_wall_Tint_handle == -1 or ms1_wall_Tint_handle == -1 or ms2_wall_Tint_handle == -1 or \
            tsw_wall_Tint_handle == -1 or tse_wall_Tint_handle == -1 or ts1_wall_Tint_handle == -1 or ts2_wall_Tint_handle == -1 or \
            gnw_wall_Tint_handle == -1 or gne_wall_Tint_handle == -1 or gn1_wall_Tint_handle == -1 or gn2_wall_Tint_handle == -1 or \
            mnw_wall_Tint_handle == -1 or mne_wall_Tint_handle == -1 or mn1_wall_Tint_handle == -1 or mn2_wall_Tint_handle == -1 or \
            tnw_wall_Tint_handle == -1 or tne_wall_Tint_handle == -1 or tn1_wall_Tint_handle == -1 or tn2_wall_Tint_handle == -1 or \
            gsw_solar_handle == -1 or gse_office_solar_handle == -1 or gs1_solar_handle == -1 or gs2_solar_handle == -1 or \
            msw_solar_handle == -1 or mse_solar_handle == -1 or ms1_solar_handle == -1 or ms2_solar_handle == -1 or \
            tsw_solar_handle == -1 or tse_solar_handle == -1 or ts1_solar_handle == -1 or ts2_solar_handle == -1 or \
            gnw_solar_handle == -1 or gne_solar_handle == -1 or gn1_solar_handle == -1 or gn2_solar_handle == -1 or \
            mnw_solar_handle == -1 or mne_solar_handle == -1 or mn1_solar_handle == -1 or mn2_solar_handle == -1 or \
            tnw_solar_handle == -1 or tne_solar_handle == -1 or tn1_solar_handle == -1 or tn2_solar_handle == -1):
            print(oat_sensor_handle, hvac_heat_rejection_sensor_handle, elec_bld_meter_handle,\
            zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, zone_flr_area_handle,\
            sens_cool_demand_sensor_handle,sens_heat_demand_sensor_handle,\
            cool_consumption_sensor_handle, heat_consumption_sensor_handle,\
            gsw_flr_Text_handle, gnw_flr_Text_handle, gse_office_flr_Text_handle, gne_flr_Text_handle, \
            gn1_flr_Text_handle, gn2_flr_Text_handle, gs1_flr_Text_handle, gs2_flr_Text_handle,\
            tsw_roof_Text_handle, tnw_roof_Text_handle, tse_roof_Text_handle, tne_roof_Text_handle,\
            tn1_roof_Text_handle, tn2_roof_Text_handle, ts1_roof_Text_handle, ts2_roof_Text_handle,\
            t_cor_roof_Text_handle,\
            gsw_flr_Tint_handle, gnw_flr_Tint_handle, gse_office_flr_Tint_handle, gne_flr_Tint_handle,\
            gn1_flr_Tint_handle, gn2_flr_Tint_handle, gs1_flr_Tint_handle, gs2_flr_Tint_handle,\
            tsw_roof_Tint_handle, tnw_roof_Tint_handle, tse_roof_Tint_handle, tne_roof_Tint_handle,\
            tn1_roof_Tint_handle , tn2_roof_Tint_handle, ts1_roof_Tint_handle, ts2_roof_Tint_handle,\
            t_cor_roof_Tint_handle,\
            gsw_wall_Text_handle, gse_office_wall_Text_handle, gs1_wall_Text_handle, gs2_wall_Text_handle,\
            msw_wall_Text_handle, mse_wall_Text_handle, ms1_wall_Text_handle,ms2_wall_Text_handle,\
            tsw_wall_Text_handle, tse_wall_Text_handle, ts1_wall_Text_handle,ts2_wall_Text_handle,\
            gnw_wall_Text_handle, gne_wall_Text_handle, gn1_wall_Text_handle, gn2_wall_Text_handle,\
            mnw_wall_Text_handle, mne_wall_Text_handle, mn1_wall_Text_handle, mn2_wall_Text_handle,\
            tnw_wall_Text_handle, tne_wall_Text_handle, tn1_wall_Text_handle, tn2_wall_Text_handle,\
            gsw_wall_Tint_handle, gse_office_wall_Tint_handle, gs1_wall_Tint_handle, gs2_wall_Tint_handle,\
            msw_wall_Tint_handle, mse_wall_Tint_handle, ms1_wall_Tint_handle, ms2_wall_Tint_handle,\
            tsw_wall_Tint_handle, tse_wall_Tint_handle, ts1_wall_Tint_handle, ts2_wall_Tint_handle,\
            gnw_wall_Tint_handle, gne_wall_Tint_handle, gn1_wall_Tint_handle, gn2_wall_Tint_handle,\
            mnw_wall_Tint_handle, mne_wall_Tint_handle, mn1_wall_Tint_handle, mn2_wall_Tint_handle,\
            tnw_wall_Tint_handle, tne_wall_Tint_handle, tn1_wall_Tint_handle, tn2_wall_Tint_handle,\
            gsw_solar_handle, gse_office_solar_handle, gs1_solar_handle, gs2_solar_handle,\
            msw_solar_handle, mse_solar_handle, ms1_solar_handle, ms2_solar_handle,\
            tsw_solar_handle, tse_solar_handle, ts1_solar_handle, ts2_solar_handle,\
            gnw_solar_handle, gne_solar_handle, gn1_solar_handle, gn2_solar_handle,\
            mnw_solar_handle, mne_solar_handle,mn1_solar_handle,mn2_solar_handle,\
            tnw_solar_handle, tne_solar_handle,tn1_solar_handle, tn2_solar_handle)


            print('get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)


    # get EP results, upload to coordination
    if called_vcwg_bool:
        # called vcwg,sem0, sem1
        global ep_last_call_time_seconds
        #wait for the upstream (EP download canyon from Parent) to finish
        coordination.sem2.acquire()
        #EP start uploading EP results to Parent
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600        # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.midRiseApartmentBld_floor_area_m2
        coordination.ep_sensWaste_w_m2_per_floor_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)
        if not time_index_alignment_bool:
            # if the accumulated time is less than zone time step, then we return here, and wait for the next call
            coordination.sem2.release()
            return

        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / coordination.midRiseApartmentBld_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / coordination.midRiseApartmentBld_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / coordination.midRiseApartmentBld_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / coordination.midRiseApartmentBld_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.midRiseApartmentBld_floor_area_m2


        gsw_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gsw_flr_Text_handle)
        gnw_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gnw_flr_Text_handle)
        gse_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_flr_Text_handle)
        gne_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gne_flr_Text_handle)
        gn1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn1_flr_Text_handle)
        gn2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn2_flr_Text_handle)
        gs1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs1_flr_Text_handle)
        gs2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs2_flr_Text_handle)

        gsw_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gsw_flr_Tint_handle)
        gnw_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gnw_flr_Tint_handle)
        gse_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_flr_Tint_handle)
        gne_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gne_flr_Tint_handle)
        gn1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn1_flr_Tint_handle)
        gn2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn2_flr_Tint_handle)
        gs1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs1_flr_Tint_handle)
        gs2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs2_flr_Tint_handle)

        floor_Text_C = (gsw_flr_Text_c + gnw_flr_Text_c + gse_flr_Text_c + gne_flr_Text_c +
                        gn1_flr_Text_c + gn2_flr_Text_c + gs1_flr_Text_c + gs2_flr_Text_c)/8
        floor_Tint_C = (gsw_flr_Tint_c + gnw_flr_Tint_c + gse_flr_Tint_c + gne_flr_Tint_c +
                        gn1_flr_Tint_c + gn2_flr_Tint_c + gs1_flr_Tint_c + gs2_flr_Tint_c)/8

        tsw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tsw_roof_Text_handle)
        tnw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tnw_roof_Text_handle)
        tse_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tse_roof_Text_handle)
        tne_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tne_roof_Text_handle)
        tn1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn1_roof_Text_handle)
        tn2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn2_roof_Text_handle)
        ts1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts1_roof_Text_handle)
        ts2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts2_roof_Text_handle)
        t_cor_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, t_cor_roof_Text_handle)

        tsw_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tsw_roof_Tint_handle)
        tnw_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tnw_roof_Tint_handle)
        tse_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tse_roof_Tint_handle)
        tne_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tne_roof_Tint_handle)
        tn1_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn1_roof_Tint_handle)
        tn2_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn2_roof_Tint_handle)
        ts1_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts1_roof_Tint_handle)
        ts2_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts2_roof_Tint_handle)
        t_cor_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, t_cor_roof_Tint_handle)


        roof_Text_C = (tsw_roof_Text_c + tnw_roof_Text_c + tse_roof_Text_c + tne_roof_Text_c +
                        tn1_roof_Text_c + tn2_roof_Text_c + ts1_roof_Text_c + ts2_roof_Text_c + t_cor_roof_Text_c)/9
        roof_Tint_C = (tsw_roof_Tint_c + tnw_roof_Tint_c + tse_roof_Tint_c + tne_roof_Tint_c +
                          tn1_roof_Tint_c + tn2_roof_Tint_c + ts1_roof_Tint_c + ts2_roof_Tint_c + t_cor_roof_Tint_c)/9

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

        gsw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gsw_wall_Tint_handle)
        gse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_wall_Tint_handle)
        gs1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs1_wall_Tint_handle)
        gs2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs2_wall_Tint_handle)
        msw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, msw_wall_Tint_handle)
        mse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mse_wall_Tint_handle)
        ms1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ms1_wall_Tint_handle)
        ms2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ms2_wall_Tint_handle)
        tsw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tsw_wall_Tint_handle)
        tse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tse_wall_Tint_handle)
        ts1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts1_wall_Tint_handle)
        ts2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts2_wall_Tint_handle)

        s_wall_Text_C = (gsw_wall_Text_c + gse_wall_Text_c + gs1_wall_Text_c + gs2_wall_Text_c +
                            msw_wall_Text_c*2 + mse_wall_Text_c*2 + ms1_wall_Text_c*2 + ms2_wall_Text_c*2 +
                            tsw_wall_Text_c + tse_wall_Text_c + ts1_wall_Text_c + ts2_wall_Text_c)/16
        s_wall_Tint_C = (gsw_wall_Tint_c + gse_wall_Tint_c + gs1_wall_Tint_c + gs2_wall_Tint_c +
                        msw_wall_Tint_c*2 + mse_wall_Tint_c*2 + ms1_wall_Tint_c*2 + ms2_wall_Tint_c*2 +
                        tsw_wall_Tint_c + tse_wall_Tint_c + ts1_wall_Tint_c + ts2_wall_Tint_c)/16

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

        gnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gnw_wall_Tint_handle)
        gne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gne_wall_Tint_handle)
        gn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn1_wall_Tint_handle)
        gn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn2_wall_Tint_handle)
        mnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mnw_wall_Tint_handle)
        mne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mne_wall_Tint_handle)
        mn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mn1_wall_Tint_handle)
        mn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mn2_wall_Tint_handle)
        tnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tnw_wall_Tint_handle)
        tne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tne_wall_Tint_handle)
        tn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn1_wall_Tint_handle)
        tn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn2_wall_Tint_handle)

        n_wall_Text_C = (gnw_wall_Text_c + gne_wall_Text_c + gn1_wall_Text_c + gn2_wall_Text_c +
                         mnw_wall_Text_c*2 + mne_wall_Text_c*2 + mn1_wall_Text_c*2 + mn2_wall_Text_c*2 +
                         tnw_wall_Text_c + tne_wall_Text_c + tn1_wall_Text_c + tn2_wall_Text_c)/16
        n_wall_Tint_C = (gnw_wall_Tint_c + gne_wall_Tint_c + gn1_wall_Tint_c + gn2_wall_Tint_c +
                         mnw_wall_Tint_c*2 + mne_wall_Tint_c*2 + mn1_wall_Tint_c*2 + mn2_wall_Tint_c*2 +
                         tnw_wall_Tint_c + tne_wall_Tint_c + tn1_wall_Tint_c + tn2_wall_Tint_c)/16

        gsw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gsw_solar_handle)
        gse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gse_office_solar_handle)
        gs1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gs1_solar_handle)
        gs2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gs2_solar_handle)
        msw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, msw_solar_handle)
        mse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mse_solar_handle)
        ms1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ms1_solar_handle)
        ms2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ms2_solar_handle)
        tsw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tsw_solar_handle)
        tse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tse_solar_handle)
        ts1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ts1_solar_handle)
        ts2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ts2_solar_handle)

        gnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gnw_solar_handle)
        gne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gne_solar_handle)
        gn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gn1_solar_handle)
        gn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gn2_solar_handle)
        mnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mnw_solar_handle)
        mne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mne_solar_handle)
        mn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mn1_solar_handle)
        mn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mn2_solar_handle)
        tnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tnw_solar_handle)
        tne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tne_solar_handle)
        tn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tn1_solar_handle)
        tn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tn2_solar_handle)

        s_wall_solar_w_m2 = (gsw_solar_w_m2 + gse_solar_w_m2 + gs1_solar_w_m2 + gs2_solar_w_m2 +
                             msw_solar_w_m2*2 + mse_solar_w_m2*2 + ms1_solar_w_m2*2 + ms2_solar_w_m2*2 +
                             tsw_solar_w_m2 + tse_solar_w_m2 + ts1_solar_w_m2 + ts2_solar_w_m2)/16

        n_wall_solar_w_m2 = (gnw_solar_w_m2 + gne_solar_w_m2 + gn1_solar_w_m2 + gn2_solar_w_m2 +
                             mnw_solar_w_m2*2 + mne_solar_w_m2*2 + mn1_solar_w_m2*2 + mn2_solar_w_m2*2 +
                             tnw_solar_w_m2 + tne_solar_w_m2 + tn1_solar_w_m2 + tn2_solar_w_m2)/16

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
        print(f"EP OAT: {oat_temp_c}")
        coordination.ep_oaTemp_C = oat_temp_c

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        if s_wall_solar_w_m2 > n_wall_solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_C + 273.15
            coordination.ep_wallSun_Tint_K = s_wall_Tint_C + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_C + 273.15
            coordination.ep_wallShade_Tint_K = n_wall_Tint_C + 273.15
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_C + 273.15
            coordination.ep_wallSun_Tint_K = n_wall_Tint_C + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_C + 273.15
            coordination.ep_wallShade_Tint_K = s_wall_Tint_C + 273.15

        coordination.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2
        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value
        #Notify to the downstream (VCWG download EP results) to start
        coordination.sem3.release()

def smallOffice_get_ep_results(state):
    global get_ep_results_inited_handle, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, \
        zone_flr_area_handle,zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        core_flr_Text_handle, pre1_flr_Text_handle, pre2_flr_Text_handle, \
        pre3_flr_Text_handle, pre4_flr_Text_handle, \
        core_flr_Tint_handle, pre1_flr_Tint_handle, pre2_flr_Tint_handle, \
        pre3_flr_Tint_handle, pre4_flr_Tint_handle, \
        roof_west_Text_handle, roof_east_Text_handle, roof_north_Text_handle, roof_south_Text_handle,\
        roof_west_Tint_handle, roof_east_Tint_handle, roof_north_Tint_handle, roof_south_Tint_handle,\
        s_wall_Text_handle, n_wall_Text_handle, \
        s_wall_Tint_handle, n_wall_Tint_handle, \
        s_wall_Solar_handle, n_wall_Solar_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
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
                                                                          "CORE_ZN")
        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Zone Air Temperature",\
                                                                                         "CORE_ZN")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                            "Zone Air Humidity Ratio",\
                                                                                            "CORE_ZN")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Cooling Rate",\
                                                                                          "CORE_ZN")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Heating Rate",\
                                                                                          "CORE_ZN")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Cooling Coil Electricity Rate",\
                                                                                          "PSZ-AC:1_COOLC DXCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Heating Coil Heating Rate",\
                                                                                          "PSZ-AC:1_HEATC")
        core_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Outside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Outside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                  "Surface Outside Face Temperature",\
                                                                                  "Attic_roof_north")
        roof_south_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                  "Surface Outside Face Temperature",\
                                                                                  "Attic_roof_south")
        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        s_wall_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                "Perimeter_ZN_1_wall_south")
        n_wall_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                            "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                            "Perimeter_ZN_3_wall_north")
        core_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_north")
        roof_south_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_south")
        s_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        core_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_north")
        roof_south_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_south")
        s_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or\
                elec_bld_meter_handle == -1 or zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1 or\
                sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or\
                cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or\
                core_flr_Text_handle == -1 or pre1_flr_Text_handle == -1 or pre2_flr_Text_handle == -1 or\
                pre3_flr_Text_handle == -1 or pre4_flr_Text_handle == -1 or roof_west_Text_handle == -1 or\
                roof_east_Text_handle == -1 or roof_north_Text_handle == -1 or roof_south_Text_handle == -1 or\
                s_wall_Text_handle == -1 or n_wall_Text_handle == -1 or s_wall_Solar_handle == -1 or\
                n_wall_Solar_handle == -1 or core_flr_Tint_handle == -1 or pre1_flr_Tint_handle == -1 or\
                pre2_flr_Tint_handle == -1 or pre3_flr_Tint_handle == -1 or pre4_flr_Tint_handle == -1 or\
                roof_west_Tint_handle == -1 or roof_east_Tint_handle == -1 or roof_north_Tint_handle == -1 or\
                roof_south_Tint_handle == -1 or s_wall_Tint_handle == -1 or n_wall_Tint_handle == -1 or\
                s_wall_Solar_handle == -1 or n_wall_Solar_handle == -1):
            print('smallOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds, zone_floor_area_m2
        zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,
                                                                                hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.smallOfficeBld_floor_area_m2
        coordination.ep_sensWaste_w_m2_per_floor_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)
        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.smallOfficeBld_floor_area_m2

        core_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, core_flr_Text_handle)
        pre1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre1_flr_Text_handle)
        pre2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre2_flr_Text_handle)
        pre3_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre3_flr_Text_handle)
        pre4_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre4_flr_Text_handle)

        roof_west_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_west_Text_handle)
        roof_east_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_east_Text_handle)
        roof_north_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_north_Text_handle)
        roof_south_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_south_Text_handle)

        s_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Text_handle)
        n_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Text_handle)

        core_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, core_flr_Tint_handle)
        pre1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre1_flr_Tint_handle)
        pre2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre2_flr_Tint_handle)
        pre3_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre3_flr_Tint_handle)
        pre4_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre4_flr_Tint_handle)

        roof_west_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_west_Tint_handle)
        roof_east_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_east_Tint_handle)
        roof_north_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_north_Tint_handle)
        roof_south_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_south_Tint_handle)

        s_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Tint_handle)
        n_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Tint_handle)

        s_wall_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_Solar_handle)
        n_wall_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_Solar_handle)

        coordination.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2
        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
        coordination.overwriten_time_index = curr_sim_time_in_seconds
        print(f"EP OAT: {oat_temp_c}")
        coordination.ep_oaTemp_C = oat_temp_c

        floor_Text_C =(core_flr_Text_c + pre1_flr_Text_c + pre2_flr_Text_c + pre3_flr_Text_c + pre4_flr_Text_c) / 5
        roof_Text_C = (roof_west_Text_c + roof_east_Text_c + roof_north_Text_c + roof_south_Text_c) / 4
        floor_Tint_C = (core_flr_Tint_c + pre1_flr_Tint_c + pre2_flr_Tint_c + pre3_flr_Tint_c + pre4_flr_Tint_c) / 5
        roof_Tint_C = (roof_west_Tint_c + roof_east_Tint_c + roof_north_Tint_c + roof_south_Tint_c) / 4

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = s_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = n_wall_Tint_c + 273.15
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = n_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = s_wall_Tint_c + 273.15

        coordination.sem3.release()

def mediumOffice_get_ep_results(state):
    global get_ep_results_inited_handle, oat_sensor_handle, \
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
        n_wall_bot_1_Tint_handle, n_wall_mid_1_Tint_handle, n_wall_top_1_Tint_handle,\
        surd_south_temp_actuator_handle, surd_north_temp_actuator_handle, \
        surd_east_temp_actuator_handle, surd_west_temp_actuator_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True

        surd_south_temp_actuator_handle = odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "SURROUNDING TEMP SCH SOUTH")
        surd_north_temp_actuator_handle = odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "SURROUNDING TEMP SCH NORTH")
        surd_east_temp_actuator_handle = odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "SURROUNDING TEMP SCH EAST")
        surd_west_temp_actuator_handle = odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "SURROUNDING TEMP SCH WEST")

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
                n_wall_bot_1_Tint_handle == -1 or n_wall_mid_1_Tint_handle == -1 or n_wall_top_1_Tint_handle == -1) or \
                surd_south_temp_actuator_handle == -1 or surd_north_temp_actuator_handle == -1 or \
                surd_east_temp_actuator_handle == -1 or surd_west_temp_actuator_handle == -1:
            print('mediumOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds, zone_floor_area_m2

        coordination.sem2.acquire()
        zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.mediumOfficeBld_one_floor_area_m2
        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

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
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.mediumOfficeBld_one_floor_area_m2

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



        coordination.ep_elecTotal_w_m2_per_footprint_area = elec_bld_meter_w_m2
        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
        coordination.overwriten_time_index = curr_sim_time_in_seconds
        # print(f"EP OAT: {oat_temp_c}")
        coordination.ep_oaTemp_C = oat_temp_c

        floor_Text_C = (flr_core_Text_c + flr_pre1_Text_c + flr_pre2_Text_c + flr_pre3_Text_c + flr_pre4_Text_c )/5
        floor_Tint_C = (flr_core_Tint_c + flr_pre1_Tint_c + flr_pre2_Tint_c + flr_pre3_Tint_c + flr_pre4_Tint_c )/5

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_c + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_c + 273.15

        s_wall_Solar_w_m2 = (s_wall_bot_1_Solar_w_m2 + s_wall_mid_1_Solar_w_m2 + s_wall_top_1_Solar_w_m2)/3
        n_wall_Solar_w_m2 = (n_wall_bot_1_Solar_w_m2 + n_wall_mid_1_Solar_w_m2 + n_wall_top_1_Solar_w_m2)/3

        s_wall_Text_c = (s_wall_bot_1_Text_c + s_wall_mid_1_Text_c + s_wall_top_1_Text_c)/3
        s_wall_Tint_c = (s_wall_bot_1_Tint_c + s_wall_mid_1_Tint_c + s_wall_top_1_Tint_c)/3
        n_wall_Text_c = (n_wall_bot_1_Text_c + n_wall_mid_1_Text_c + n_wall_top_1_Text_c)/3
        n_wall_Tint_c = (n_wall_bot_1_Tint_c + n_wall_mid_1_Tint_c + n_wall_top_1_Tint_c)/3

        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = s_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = n_wall_Tint_c + 273.15

            coordination.ep_api.exchange.set_actuator_value(state, surd_south_temp_actuator_handle, coordination.ep_wallShade_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_east_temp_actuator_handle, coordination.ep_wallShade_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_north_temp_actuator_handle, coordination.ep_wallSun_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_west_temp_actuator_handle, coordination.ep_wallSun_Text_K - 273.15)
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = n_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = s_wall_Tint_c + 273.15

            coordination.ep_api.exchange.set_actuator_value(state, surd_south_temp_actuator_handle, coordination.ep_wallSun_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_east_temp_actuator_handle, coordination.ep_wallSun_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_north_temp_actuator_handle, coordination.ep_wallShade_Text_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, surd_west_temp_actuator_handle, coordination.ep_wallShade_Text_K - 273.15)

        coordination.sem3.release()