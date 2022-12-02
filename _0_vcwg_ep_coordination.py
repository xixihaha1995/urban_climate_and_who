import threading, sys, pandas as pd
import numpy as np, time,os
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI

import configparser
def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    # find the project path
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_path, 'A_prepost_processing/_0_configs', config_file_name)
    config.read(config_path)

def init_ep_api():
    global ep_api
    ep_api = EnergyPlusAPI()

def init_variables_for_vcwg_ep():
    global ep_wsp_mps, ep_wdir_deg, midRiseApartmentBld_floor_area_m2, smallOfficeBld_floor_area_m2, \
    mediumOfficeBld_floor_area_m2, midRiseApart_num_of_floors, smallOffice_num_of_floors, \
        mediumOffice_num_of_floors

    ep_wsp_mps = 0
    ep_wdir_deg = 0
    midRiseApartmentBld_floor_area_m2 = 3135
    smallOfficeBld_floor_area_m2 = 511
    mediumOfficeBld_floor_area_m2 = 4982
    midRiseApart_num_of_floors = 4
    smallOffice_num_of_floors = 1
    mediumOffice_num_of_floors = 3

def init_saving_data():
    global saving_data, vcwg_ep_saving_path
    saving_data = {}
    saving_data['ep_wsp_mps_wdir_deg'] = []
    saving_data['debugging_canyon'] = []