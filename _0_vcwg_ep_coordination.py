import threading, sys, configparser, os
import numpy as np, datetime

save_path_clean = False
uwgVariable, uwgVariableValue = 0, 0
sys.path.insert(0,'/usr/local/EnergyPlus-22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api, psychrometric, state
    ep_api=EnergyPlusAPI()
    psychrometric =None

def read_ini(input_config, input_uwgVariable, input_uwgVariableValue):
    global config, project_path, uwgVariable, uwgVariableValue, vcwg_prediction_saving_path, generated_epw_path
    # find the project path
    project_path = os.path.dirname(os.path.abspath(__file__))
    config = input_config
    uwgVariable = input_uwgVariable
    uwgVariableValue = input_uwgVariableValue

    # detect if the uwgVariableValue is only contain letters
    if uwgVariableValue.isalpha():
        str_variable = uwgVariableValue
    else:
        uwgVariableValue = float(uwgVariableValue)
        if uwgVariableValue > 0:
            str_variable = 'positive' + str(abs(uwgVariableValue))
        elif uwgVariableValue < 0:
            str_variable = 'negative' + str(abs(uwgVariableValue))
        else:
            str_variable = '0'

    vcwg_prediction_saving_path = os.path.join(project_path, 'A_prepost_processing', 'offline_saving_newEPW',
                                    config['_0_vcwg_ep_coordination.py']['site_location'],
                                    config['sensitivity']['theme'], f'{str_variable}.csv')
    theme = config['sensitivity']['theme']
    generated_epw_path = os.path.join(project_path, 'resources', 'epw_based_onMixed',
                                    f'{theme}_{uwgVariable}_{str_variable}.epw')


