import os, numpy as np, pandas as pd
from threading import Thread
import _0_EP_VCWG._0_EP._0_vcwg_ep_coordination as coordination
from _1_case_analysis.analysis._1_plots_related import _0_all_plot_tools as plot_tools
from _0_EP_VCWG._0_Modified_VCWG200.VCWG_Hydrology import VCWG_Hydro

def run_vcwg():
    epwFileName = 'Basel.epw'
    TopForcingFileName = None
    # VCWGParamFileName = 'initialize_Basel_BSPA_MOST.uwg'
    VCWGParamFileName = '_case5_initialize_Basel_BSPR_MOST.uwg'
    # ViewFactorFileName = '_BSPA_ViewFactor_Basel_MOST.txt'
    ViewFactorFileName = '_case5_BSPR_ViewFactor_Basel_MOST.txt'
    # Case name to append output file names with
    # case = '_BSPA_Refinement_M2_Basel_MOST'
    case = '_BSPR_Only_VCWG_Basel_MOST'
    # '''
    # epwFileName = 'TopForcing_year.epw'
    # TopForcingFileName = None
    # # TopForcingFileName = 'Vancouver2008_ERA5.csv'
    # VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = '_bypass_year_Vancouver_LCZ1'

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


if __name__ == '__main__':
    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    saving_data_path = '_1_case_analysis\\cases\\_05_Basel_BSPR_ue1\\vcwg_saving'
    case_name = 'only_vcwg'
    start_time = '2002-06-10 00:00:00'
    time_interval_sec = 300

    vcwg_thread = Thread(target=run_vcwg)
    vcwg_thread.start()
    vcwg_thread.join()

    # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    data_name_lst = ['TempProfile_K', 'SpecHumProfile_Ratio', 'PressProfile_Pa', 'wind_vxProfile_mps',
                     'wind_vyProfile_mps', 'wind_SpeedProfile_mps', 'turbulence_tkeProfile_m2s2',
                     'air_densityProfile_kgm3', 'sensible_heat_fluxProfile_Wm2', 'latent_heat_fluxProfile_Wm2',
                     'can_Averaged_temp_k_specHum_ratio_press_pa','s_wall_Text_K_n_wall_Text_K', 'vcwg_wsp_mps_wdir_deg',
                     'debugging_canyon']
    for data_name in data_name_lst:
        plot_tools.save_data_to_csv(coordination.saving_data, data_name,case_name,
                                    start_time, time_interval_sec, saving_data_path)