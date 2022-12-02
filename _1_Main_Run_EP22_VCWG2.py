import configparser
import os, numpy as np, pandas as pd
from multiprocessing import Process
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination
from _1_ep_vcwg.VCWG_Hydrology import VCWG_Hydro

def run_vcwg(config_file_name=None, actual_file=None, _control_value=None):
    coordination.ini_all(config_file_name,actual_file, _control_value)
    epwFileName = _control_value
    if 'None' in coordination.config['run_vcwg()']['TopForcingFileName']:
        TopForcingFileName = None
    else:
        TopForcingFileName = coordination.config['run_vcwg()']['TopForcingFileName']
    VCWGParamFileName = coordination.config['run_vcwg()']['VCWGParamFileName']
    ViewFactorFileName = _control_value[:-4] + '_viewfactor.txt'
    case = 'CAPITOUL'
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
    value_list = [i for i in config['run_vcwg()']['control_value_list'].split(',')]
    this_ini_process = []
    for value in value_list:
        p = Process(target=run_vcwg, args=(sensitivity_file_name,config, value))
        p.start()
        this_ini_process.append(p)
        # run_vcwg(sensitivity_file_name, config, value)

if __name__ == '__main__':
    sensitivity_file_name = 'CAPITOUL_Surface_Temperature.ini'
    sensitivity_file_name = 'CAPITOUL_Obsolete_VCWG.ini'
    one_ini(sensitivity_file_name)
