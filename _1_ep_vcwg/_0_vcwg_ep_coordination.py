import configparser, os

def ini_all(config_file_name = None, actual_file = None, _control_value = None):
    global config, data_saving_path, save_path_clean, sensor_heights, control_value
    config = configparser.ConfigParser()
    # find the project path
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if actual_file is None:
        config_path = os.path.join(project_path, '_7_configs', config_file_name)
        config.read(config_path)
        save_file_name = 'debug_saving.csv'
    else:
        config = actual_file
        control_value = _control_value
        save_file_name = config['run_vcwg()']['csv_file'] + '.csv'
    experiments_theme = config['run_vcwg()']['experiments_theme']
    data_saving_path = os.path.join(project_path, 'A_prepost_processing',
                                    experiments_theme, save_file_name)
    save_path_clean = False
    sensor_heights = [float(i) for i in config['run_vcwg()']['sensor_height_meter'].split(',')]

