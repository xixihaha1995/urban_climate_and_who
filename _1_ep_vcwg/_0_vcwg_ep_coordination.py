import threading, sys, pandas as pd
import numpy as np, time
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api
    ep_api = EnergyPlusAPI()

def init_variables_for_vcwg_ep():
    global ep_wsp_mps, ep_wdir_deg, midRiseApartmentBld_floor_area_m2, smallOfficeBld_floor_area_m2
    ep_wsp_mps = 0
    ep_wdir_deg = 0
    midRiseApartmentBld_floor_area_m2 = 3135
    smallOfficeBld_floor_area_m2 = 511

def init_saving_data():
    global saving_data, vcwg_ep_saving_path
    saving_data = {}
    saving_data['ep_wsp_mps_wdir_deg'] = []
    saving_data['debugging_canyon'] = []