import configparser, os

def ini_all(config_file_name):
    global config, data_saving_path, save_path_clean, sensor_heights
    config = configparser.ConfigParser()
    # find the project path
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_path, '_7_configs',config_file_name)
    config.read(config_path)
    experiments_theme = config['run_vcwg()']['experiments_theme']
    data_saving_path = os.path.join(project_path, 'A_prepost_processing',
                                    experiments_theme,'debug_saving.csv')
    save_path_clean = False
    sensor_heights = [int(i) for i in config['run_vcwg()']['sensor_height_meter'].split(',')]

