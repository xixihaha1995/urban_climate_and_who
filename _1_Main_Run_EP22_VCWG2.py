import os, numpy as np, pandas as pd
from threading import Thread
import _1_ep_vcwg._0_vcwg_ep_coordination as coordination
from _1_ep_vcwg.VCWG_Hydrology import VCWG_Hydro
from _3_post_process_code import _0_all_plot_tools as plot_tools


def run_vcwg():
    # # BUBBLE, CAPITOUL, Vancouver
    # epwFileName = 'Mondouzil_tdb_td_rh_P_2004.epw'
    # epwFileName = 'Basel.epw'
    # epwFileName = 'VancouverRural718920.epw'
    epwFileName = 'Vancouver718920CorrectTime.epw'
    TopForcingFileName = None
    # VCWGParamFileName = '_case6_initialize_Basel_BSPA_MOST.uwg'
    # VCWGParamFileName = '_case8_initialize_CAPITOUL_MOST.uwg'
    # VCWGParamFileName = '_case5_initialize_Basel_BSPR_MOST.uwg'
    VCWGParamFileName = '_case7_initialize_Vancouver_withRural.uwg'
    # ViewFactorFileName = '_case6_BSPA_ViewFactor_Basel_MOST.txt'
    # ViewFactorFileName = '_case8_CAPITOUL_ViewFactor_MOST.txt'
    # ViewFactorFileName = '_case5_BSPR_ViewFactor_Basel_MOST.txt'
    ViewFactorFileName = '_case7_ViewFactor_Vancouver_LCZ1.txt'
    # Case name to append output file names with
    # case = '_Ue2_BSPA_Only_VCWG_Basel_MOST'
    # case = '_CAPITOUL_MOST'
    # case = '_BSPR_Only_VCWG_Basel_MOST'
    case = '_case7_VancouverRuralCorrectTimeOnlyVCWG_2008Jul'

    # # Vancouver
    # # '''
    # epwFileName = None
    # TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    # VCWGParamFileName = '_case7_initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = '_case7_ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = '_case7_VancouverTopForcingOnlyVCWG_2008Jul_LCZ1'
    # # '''

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


if __name__ == '__main__':
    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    # case_name = 'CAPITOUL_2004_only_vcwg'
    # case_name = 'Vancouver_TopForcing_only_vcwg_2008_Jul'
    # case_name = 'Vancouver_Rural_only_vcwg_2008_Jul'
    case_name = 'Vancouver_Rural_CorrectTime_only_vcwg_2008_Jul'
    # case_name = 'BUBBLE_Ue1_Rural_only_vcwg_2002_June'
    # case_name = 'BUBBLE_Ue2_Rural_only_vcwg_2002_June'
    # saving_data_path = '_2_cases_input_outputs\\_07_Vancouver\\vcwg_saving'
    # saving_data_path = '_2_cases_input_outputs\\_08_CAPITOUL\\DOE_Ref_MediumOffice_4B\\vcwg_saving'
    # saving_data_path = '_2_cases_input_outputs\\_07_Vancouver\\TopForcing_Refined_SMALL_OFFICE\\vcwg_saving'
    # saving_data_path = '_2_cases_input_outputs\\_07_Vancouver\\Rural_Refined_Small_Office\\vcwg_saving'
    saving_data_path = '_2_cases_input_outputs\\_07_Vancouver\\Rural_Refined_SmallOffice_4C_CorrectTime\\b_vcwg_saving'
    # saving_data_path = '_2_cases_input_outputs\\_05_Basel_BSPR_ue1\\MidRiseApartment_4C_Rural\\vcwg_saving'
    # saving_data_path = '_2_cases_input_outputs\\_06_Basel_BSPA_ue2\\Orientation_MidRiseApart_4C\\vcwg_saving'
    # start_time = '2004-06-01 00:00:00'
    start_time = '2008-07-01 00:00:00'
    # start_time = '2002-06-10 00:00:00'
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