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


def levenshtein(epw_file, param):
    # calculate the distance between two strings
    if len(epw_file) > len(param):
        epw_file, param = param, epw_file
    distances = range(len(epw_file) + 1)
    for index2, char2 in enumerate(param):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(epw_file):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1 + 1], newDistances[-1])))
        distances = newDistances
    return distances[-1]


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
    if not os.path.exists(os.path.join(project_path, 'resources', 'epw_based_onMixed')):
        os.makedirs(os.path.join(project_path, 'resources', 'epw_based_onMixed'))
    generated_epw_path = os.path.join(project_path, 'resources', 'epw_based_onMixed',
                                    f'{theme}_{uwgVariable}_{str_variable}.epw')


