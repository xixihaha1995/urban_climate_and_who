import configparser, os

def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    # find the project path
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_path, '_7_configs',config_file_name)
    config.read(config_path)
def init_saving_data():
    global saving_data
    saving_data = {}
    saving_data['TempProfile_K'] = []
    saving_data['SpecHumProfile_Ratio'] = []
    saving_data['PressProfile_Pa'] = []
    saving_data['wind_vxProfile_mps'] = []
    saving_data['wind_vyProfile_mps'] = []
    saving_data['wind_SpeedProfile_mps'] = []
    saving_data['turbulence_tkeProfile_m2s2'] = []
    saving_data['air_densityProfile_kgm3'] = []
    saving_data['sensible_heat_fluxProfile_Wm2'] = []
    saving_data['latent_heat_fluxProfile_Wm2'] = []

    saving_data['s_wall_Text_K_n_wall_Text_K'] = []
    saving_data['vcwg_wsp_mps_wdir_deg'] = []
    saving_data['can_Averaged_temp_k_specHum_ratio_press_pa'] = []
    #wallSun_Text_K, wallShade_Text_K, roof_Text_K, sensWaste_w_floor_m2, canTemp_K
    saving_data['debugging_canyon'] = []
