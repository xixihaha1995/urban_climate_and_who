import threading, sys, configparser, os
import numpy as np, datetime

save_path_clean = False
uwgVariable, uwgVariableValue = 0, 0
sys.path.insert(0,'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api, psychrometric
    ep_api=EnergyPlusAPI()
    psychrometric =None

def read_ini(input_config):
    global config, project_path, sensor_heights, uwgVariable, uwgVariableValue, \
        theme, data_saving_path, mediumOfficeBld_floor_area_m2
    # find the project path
    project_path = os.path.dirname(os.path.abspath(__file__))
    config = input_config
    sensor_heights = [int(i) for i in config['shading']['sensor_height_meter'].split(',')]
    theme = config['shading']['theme']
    data_saving_path = os.path.join(project_path, 'A_prepost_processing', 'shading_saving',
                                    f'{theme}.csv')
    mediumOfficeBld_floor_area_m2 = 4982