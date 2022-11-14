from multiprocessing import Process
import os, configparser, _1_Run_EP22_VCWG2 as ByPass


def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path,'A_prepost_processing', 'configs',config_file_name)
    config.read(config_path)
def for_loop_all_ini():
    ini_files = [
        "Shading_EP_ShadingSurface_ViewFactor.ini",
        "Shading_EP_ViewFactor.ini",
        "Shading_EP_ShadingSurface.ini",
        "Shading_EP.ini",
        # "Shading_VCWG.ini",
    ]
    for ini_file in ini_files:
        read_ini(ini_file)
        # ByPass.shading_init(config)
        p = Process(target=ByPass.shading_init, args=(config,))
        p.start()
if __name__ == '__main__':
    for_loop_all_ini()