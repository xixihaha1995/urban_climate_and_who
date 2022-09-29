import threading, sys, pandas as pd
import numpy as np, time
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api
    ep_api = EnergyPlusAPI()

def init_variables_for_vcwg_ep():
    global ep_wsp_mps, ep_wdir_deg
    ep_wsp_mps = 0
    ep_wdir_deg = 0

def init_saving_data(_in_vcwg_ep_saving_path = '_2_saved\BUBBLE_VCWG-EP-detailed'):
    global saving_data, vcwg_ep_saving_path
    saving_data = {}
    saving_data['ep_wsp_mps_wdir_deg'] = []

    vcwg_ep_saving_path = _in_vcwg_ep_saving_path