import configparser
import os, numpy as np, pandas as pd
from multiprocessing import Process
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination
from _1_ep_vcwg.VCWG_Hydrology import VCWG_Hydro

def run_vcwg(config_file_name=None, actual_file=None, _control_value_1=None, _control_value_2=None):
    coordination.ini_all(config_file_name,actual_file, _control_value_1, _control_value_2)
    if 'None' in coordination.config['run_vcwg()']['TopForcingFileName']:
        TopForcingFileName = None
    else:
        TopForcingFileName = coordination.config['run_vcwg()']['TopForcingFileName']
    epwFileName = coordination.config['run_vcwg()']['epwFileNames']
    VCWGParamFileName = coordination.config['run_vcwg()']['VCWGParamFileName']
    ViewFactorFileName = coordination.config['run_vcwg()']['control_variable'] + \
                         '_'+ _control_value_1 + '_' + _control_value_2 + '_viewfactor.txt'
    case = coordination.config['run_vcwg()']['experiments_theme'] + '_' + _control_value_1 + '_' + _control_value_2
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()
def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path, '_7_configs',config_file_name)
    config.read(config_path)
def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    value_list_1 = [i for i in config['run_vcwg()']['control_value_list_1'].split(',')]
    value_list_2 = [i for i in config['run_vcwg()']['control_value_list_2'].split(',')]
    for _day in value_list_1:
        for _night in value_list_2:
            p = Process(target=run_vcwg, args=(sensitivity_file_name, config, _day, _night))
            p.start()
            # run_vcwg(sensitivity_file_name, config, _day, _night)


if __name__ == '__main__':
    sensitivity_file_name = 'BUBBLE_Ue2_which_fractions_debug.ini'
    one_ini(sensitivity_file_name)
