import os, numpy as np, pandas as pd
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination
from _1_ep_vcwg.VCWG_Hydrology import VCWG_Hydro

def run_vcwg():
    epwFileName = coordination.config['run_vcwg()']['epwFileName']
    if 'None' in coordination.config['run_vcwg()']['TopForcingFileName']:
        TopForcingFileName = None
    else:
        TopForcingFileName = coordination.config['run_vcwg()']['TopForcingFileName']
    VCWGParamFileName = coordination.config['run_vcwg()']['VCWGParamFileName']
    ViewFactorFileName = coordination.config['run_vcwg()']['ViewFactorFileName']
    case = 'CAPITOUL'
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


if __name__ == '__main__':
    configFileName = 'CAPITOUL_debug.ini'
    coordination.ini_all(configFileName)
    time_interval_sec = 300
    vcwg_thread = Thread(target=run_vcwg)
    vcwg_thread.start()
    vcwg_thread.join()