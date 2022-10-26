'''
Read mondouzil actual measuread data.
(It is acctually measured from Jan 2004, to Feb 2005.
But we only use 2004 data.)
measurement path:_4_measurements/CAPITOUL/CAPITOUL_including_Rural(Mondouzil)/Mo_BDD/Mo_BDD/Mo_BDD_MM-2004.asc
sampling rate: 1 minute

Raw epw template: _2_cases_input_outputs/_08_CAPITOUL/generate_epw/overriding_FRA_Bordeaux.075100_IWECEPW.csv
sampling rate: 1 hour
'''

# Specifically, there are 3 steps:
# 1. read the measured data from all the 12 files, sample rate is 1 minute
# 2. convert the measured data to epw format, sample rate is 1 hour
# 3. overwrite the epw file in the epw folder of the case

import os, sys, numpy as np
import pandas as pd, _0_all_plot_tools as plot_tools

sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI

# 1. read the measured data from all the 12 files, sample rate is 1 minute
# For one file,
# 1.1. The first 9 lines are general information
# 1.2. The 10th line is the column names, in total 14 columns
# 1.3. The 11th line is the unit of each column, in total 14 columns
# 1.4. The 12th line is the code for missing value, in total 14 columns
# 1.5. The 13th line is the references of sensors, in total 14 columns
# 1.6. The 14th and 15th lines are useless information.

'''
Specifically, there are the 14 columns, separator by space.
date, format DD/MM/AAAA
time, format HHMNSS.SSS
air temperature (position 2 meters high) : Celsius
air pressure: hPa
relative humidity (position 2 meters high) : %
rain rate: mm/h
wind direction (position 10 meters high) : degree
wind speed (position 10 meters high) : m/s
incoming short wave radiation: watts/m2
outgoing short wave radiation: watts/m2
incoming long wave-Red radiation: watts/m2
outgoing long wave radiation: watts/m2
air temperature (position 6 meters high) : Celsius
air relative humidity (position 6 meters high) : Celsius
'''

def make_columns_name(_first_month_name):
    # make the column names
    # # 1.2. The 10th line is the column names, in total 14 columns
    # # 1.3. The 11th line is the unit of each column, in total 14 columns
    # combine the 10th and 11th lines as the column names
    with open(_first_month_name, 'r') as f:
        lines = f.readlines()
        # For each column name, its surrounded by two single quotes, 'column_name'; between two column names, there is a space.
        # for string between two single quotes, extract them as column names
        _10th_line = lines[9].strip().split(' ')
        # remove string only containing single quote
        _10th_line = [i for i in _10th_line if i != "'"]
        _11th_line = lines[10].strip().split("' '")
        column_name = []
        for i in range(len(_10th_line)):
            column_name.append(_10th_line[i] + '_' + _11th_line[i])
    return column_name

def get_one_file_data(file_path):
    # read one file, read the second column as string
    df = pd.read_csv(file_path, skiprows=15, header=None, sep='\t', dtype={1: str})
    #
    # convert the date and time to datetime format
    '''
    1. first column is data, format DD/MM/AAAA
    2. second column is time, format HHMNSS.SSS, fill the missing 0
    '''
    # for the 3rd column, set the outliner to nan
    df[2] = df[2].apply(lambda x: np.nan if x > 200 or x < -100 else x)
    #get one subset df by dropping the last two columns
    df = df.iloc[:, :-2]
    # find the index (row, col) of element is 9999
    # index = df[df == 9999].stack().index.tolist()
    # [(6523, 10), (7873, 10), (7874, 10), (7878, 10), (13664, 10), (23771, 10), (23772, 10), (26583, 10), (26646, 10),
    #  (26687, 10), (26688, 10), (26703, 10), (26709, 10)]
    # iterate the index, fill it with nan
    # for i in index:
    #     df.iloc[i[0], i[1]] = np.nan
    df[2] = df[2].apply(lambda x: np.nan if x > 69 or x < -69 else x)
    df[3] = df[3].apply(lambda x: np.nan if x > 1200 or x < 310 else x)
    df[4] = df[4].apply(lambda x: np.nan if x > 109 or x < 0 else x)
    df = df.replace(9999, pd.np.nan)
    # interpolate the nan with linear method
    df = df.interpolate(method='linear')
    df[0] = df[0].apply(lambda x: x.replace('/', '-'))
    df[1] = df[1].apply(lambda x: x.zfill(8))

    # combine the date and time, and convert to datetime format
    df['date_time'] = df.iloc[:, 0] + ' ' + df.iloc[:, 1]
    df['date_time'] = pd.to_datetime(df['date_time'], format='%d-%m-%Y %H%M%S.%f')
    # set the date_time as index
    df = df.set_index('date_time')
    return df

def get_all_files_data():
    # get the file path
    file_path = r'..\\_4_measurements\CAPITOUL\CAPITOUL_including_Rural(Mondouzil)\Mo_BDD\Mo_BDD'
    # get the data from all the files
    df = pd.DataFrame()
    file_name_str = 'Mo_BDD_MM-2004.asc' # where MM stands for the month
    for month in range(1, 13):
        file_name = file_name_str.replace('MM', str(month).zfill(2))
        file_name = os.path.join(file_path, file_name)
        df_month = get_one_file_data(file_name)
        df = pd.concat([df, df_month])
    #get 01 month file name by file_name_str.replace('MM', '01')
    _first_month_name = file_name_str.replace('MM', '01')
    column_name = make_columns_name(os.path.join(file_path, _first_month_name))
    # change the column name
    df.columns = column_name[:-2]
    return df
def overriding_epw(epw_csv, df_measurement):
    '''
    1. original epw file has 8760 data records
    2. measurement has 8784 data records. So drop Feb 29th data
    3. For air temperature, overwrite the epw file with the measurement data
        a. For epw, the ;7th column is the dry bulb temperature
        b. For measurement, the 1st column is the dry bulb temperature
    '''
    # read text based epw file line by line
    with open(epw_csv, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            # for the 7th column, overwrite with the measurement data
            if i > 7 and i < 8768:
                # for the 7th column, air temperature, overwrite with the measurement data, 0
                # for the 9th column, relative humidity, overwrite with the measurement data, 2
                # calculate humidity_ratio_c(state, db in C (0), rh in fraction (2), p is hPa to Pa)
                # calculate dew_point(state, humidity_ratio, p in Pa (1))
                # for the 8th column, dew point temperature, overwrite
                lines[i] = lines[i].split(',')
                year = '2004'
                month = lines[i][1]
                day = lines[i][2]
                # epw is UTC-7, so add 7 hours
                hour = str(int(lines[i][3]) - 1)
                target_date = pd.to_datetime(year + '-' + month + '-' + day + ' ' + hour + ':00:00')
                measurements = df_measurement.loc[target_date]
                dry_bulb_c = measurements[0]
                press_pa = measurements[1] * 100
                relative_humidity_percentage = measurements[2]

                humidity_ratio = psychrometric.humidity_ratio_c(state,
                    dry_bulb_c,relative_humidity_percentage / 100, press_pa)
                dew_point = psychrometric.dew_point(state, humidity_ratio, press_pa)
                lines[i][0] = year
                lines[i][6] = str(dry_bulb_c)
                lines[i][7] = str(dew_point)
                lines[i][8] = str(relative_humidity_percentage)
                lines[i][9] = str(press_pa)
                lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'..\_4_measurements\CAPITOUL\To_GenerateEPW\Mondouzil_tdb_td_rh_P_2004.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)
    return overwriten_epw

def init_ep_api():
    global psychrometric, state
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    psychrometric = ep_api.functional.psychrometrics(state)

def main():
    init_ep_api()
    # get the data from all the files
    df = get_all_files_data()
    # save the data to csv file
    df.to_csv(r'..\_4_measurements\CAPITOUL\Rural_Mondouzil_Minute.csv')
    # except the first two columns, convert the rest columns into float type
    df.iloc[:, 2:] = df.iloc[:, 2:].astype(float)
    df_hourly = df.resample('H').mean()
    df_hourly.to_csv(r'..\_4_measurements\CAPITOUL\Rural_Mondouzil_Hour.csv')
    # _2_cases_input_outputs/_08_CAPITOUL/generate_epw/overriding_FRA_Bordeaux.075100_IWECEPW.csv
    epw_csv = r'..\_4_measurements\CAPITOUL\To_GenerateEPW\overriding_FRA_Bordeaux.075100_IWEC.epw'
    overriding_epw(epw_csv, df_hourly)

if __name__ == '__main__':
    main()
