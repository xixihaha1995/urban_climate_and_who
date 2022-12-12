import configparser
import threading, sys, os

def ini_all(config_file_, value_):
    global config, project_path, save_path_clean, sensor_heights,ep_trivial_path, data_saving_path,\
        ep_api, psychrometric,\
        vcwg_needed_time_idx_in_seconds, \
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg, \
        ep_indoorTemp_C, ep_sensWaste_w_m2_per_footprint_area, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K, ep_wallShade_Text_K, ep_wallShade_Tint_K, \
        mediumOfficeBld_footprint_area_m2, smallOfficeBld_footprint_area_m2,\
        footprint_area_m2
    # find the project path
    project_path = os.path.dirname(os.path.abspath(__file__))
    config = config_file_
    experiments_theme = config['Default']['experiments_theme']
    save_path_clean = False
    sensor_heights = [float(i) for i in config['Default']['sensor_height_meter'].split(',')]
    data_saving_path = os.path.join(project_path, 'A_prepost_processing',
                                    experiments_theme,f'{value_}.csv')
    ep_trivial_path = os.path.join(project_path, 'A_prepost_processing', experiments_theme, f"{value_}_ep_trivial_outputs")
    if config['Default']['operating_system'] == 'windows':
        sys.path.insert(0, 'C:/EnergyPlusV22-1-0')
    else:
        sys.path.insert(0, '/usr/local/EnergyPlus-22-1-0/'),
    from pyenergyplus.api import EnergyPlusAPI
    ep_api = EnergyPlusAPI()
    psychrometric = None

    vcwg_needed_time_idx_in_seconds = 0
    vcwg_canTemp_K = 300
    vcwg_canSpecHum_Ratio = 0
    vcwg_canPress_Pa = 0
    vcwg_wsp_mps = 0
    vcwg_wdir_deg = 0

    if "SmallOffice" in value_:
        footprint_area_m2 = 5500 * 0.09290304 / 1
    elif "MediumOffice" in value_:
        footprint_area_m2 = 53628 * 0.09290304 / 3
    elif "LargeOffice" in value_:
        footprint_area_m2 = 498588 * 0.09290304 / 12
    elif "MidriseApartment" in value_:
        footprint_area_m2 = 33740 * 0.09290304 / 4
    elif "StandAloneRetail" in value_:
        footprint_area_m2 = 24962 * 0.09290304 /1
    elif "StripMall" in value_:
        footprint_area_m2 = 22500 * 0.09290304 / 1
    elif "SuperMarket" in value_:
        footprint_area_m2 = 45000 * 0.09290304 / 1

    ep_indoorTemp_C = 20
    ep_sensWaste_w_m2_per_footprint_area = 0
    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wallSun_Text_K = 300
    ep_wallSun_Tint_K = 300
    ep_wallShade_Text_K = 300
    ep_wallShade_Tint_K = 300