import os, pandas as pd
def find_the_cvrmse_row_number(df, variable):
    # iterate through df.iloc[:, 0], find the row number of df_cvrmse that contains the value of df.iloc[i, 0]
    # return the row number
    meteo_row_number = 0
    for i in range(len(df.iloc[:, 0])):
        if str(variable) in str(df.iloc[i, 0]):
            meteo_row_number = i
            break
    return meteo_row_number

def process_one_file(file_path, theme, framework):
    global data_all
    print(file_path)
    # for each candidate variable, get one tuple (MeteoData_CVRMSE, Rural_Pres_CVRMSE, TotalSiteEnergy)
    df_sql = pd.read_excel(file_path, sheet_name='sql')
    df_cvrmse = pd.read_excel(file_path, sheet_name='cvrmse')
    data_all[framework][theme] = {}
    for i in range(len(df_sql)):
        # format the value to 4 decimal places
        # create one new
        cur_sql_value = df_sql.iloc[i, 1:]
        meteo_num = find_the_cvrmse_row_number(df_cvrmse, df_sql.iloc[i, 0])
        # if no index in df_cvrmse, then meteo_num = 0
        if len(df_cvrmse) == 0:
            cvrmse_value = 0
        else:
            cvrmse_value = round(df_cvrmse.iloc[meteo_num, 1] * 100, 3)
        data_all[framework][theme][str( df_sql.iloc[i, 0])] = [cvrmse_value] + [i for i in cur_sql_value]
def process_one_theme(theme, theme_path, framework):
    global data_all
    '''
    data_all, first level is theme, second level is variable, third level is value
    '''
    # detect if the theme_path is a file or a folder
    if os.path.isfile(theme_path):
        return
    files = os.listdir(theme_path)
    # open xlsx file, with '_sensitivity_analysis.xlsx' in the name
    for file in files:
        if 'sensitivity_analysis.xlsx' in file:
            file_path = os.path.join(theme_path, file)
            process_one_file(file_path, theme, framework)
def process_all_themes():
    global data_all
    data_all = {}
    data_all['online'] = {}
    # first layer keys: framework (online-bypass, offline-bypass)
    # second layer keys: theme (albedo, noCoolingAlbedo, etc.)
    # third layer: variable (MeteoData_CVRMSE, Rural_Pres_CVRMSE, TotalSiteEnergy)

    online_themes = os.listdir(experiment_path)
    for theme in online_themes:
        process_one_theme(theme, os.path.join(experiment_path, theme), 'online')
    return data_all

def save_all_data(data_all):
    df = pd.DataFrame()
    theme_order = ['albedo', 'albedoNoIDF', 'canyonWidth9ToRoofWidth', 'canyonWidthToHeight15', 'fveg_G',
                   'theta_canyon', 'NoCoolingAlbedo', 'NoCoolingAlbedoNoIDF',
                   'NoCoolingCanyonWidth9ToRoofWidth', 'NoCoolingCanyonWidthToHeight15',
                   'NoCoolingTheta_canyon', 'NoCooling_fveg_G']
    for framework, data in data_all.items():
        for theme in theme_order:
            for variable, value in data[theme].items():
                df.loc[f'{theme}, {variable}', 'cvrmse'] = value[0]
                df.loc[f'{theme}, {variable}', 'Total Site Energy[GJ]'] = value[1]
                df.loc[f'{theme}, {variable}', 'HVAC Electricity Intensity [MJ/m2]'] = value[2]
                df.loc[f'{theme}, {variable}', 'HVAC Natural Gas Intensity [MJ/m2]'] = value[3]

    # df.loc[f'{theme}, {variable}', f'{framework},meteo,cvrmse'] = data[0]
    df.to_excel(os.path.join(experiment_path, 'Offline_all_data.xlsx'))


def main():
    global experiment_path
    # experiment_path = r'sensitivity_shading_boosted'
    experiment_path = os.path.join("offline_saving_newEPW", 'CAPITOUL')
    data_all = process_all_themes()
    save_all_data(data_all)

if __name__ == '__main__':
    main()

