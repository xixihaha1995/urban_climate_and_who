'''
Prediction sampling rate: 5 minutes (It should be 1 minute)
Measurement (Mini Zone 7, Cité_Administrative) sampling rate: 12 minutes (save first)
    a. There are 12 files, each file contains 1 month dat with the zone7 file name: 2004MM_zone7.tuc
    b. The first 40 lines are general information
    c. The 41th line is the column names, 4 columns separated by ';'
    d. The rest lines are the data, 4 columns separated by ';'
Measurement (Tower Roof, Pomme Road) sampling rate: 1 minute (save first)
'''
import numpy as np
import pandas as pd, os, matplotlib.pyplot as plt
def zone7_read_one_file(file_path):
    # 3. read the rest lines, which are the data
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, skiprows=41, sep=';', header=None, encoding= "ISO-8859-1")
    else:
        file_path = file_path.replace('tuc', 'tui')
        data = pd.read_csv(file_path, skiprows=41, sep=';', header=None, encoding= "ISO-8859-1")
    # IDID; DD/MM/YYYY; HH:MM:SS; Tempeature (Celius degree, replace, by .); Humidity (%, replace, by .)
    # 4. convert the date and time to datetime format
    data['Date'] = pd.to_datetime(data.iloc[:, 1] + data.iloc[:, 2], format=' %d/%m/%Y      %H:%M:%S')
    data.index = data['Date']
    #drop Date
    data.drop(['Date'], axis=1, inplace=True)
    # remove rows containing str 'na'
    data = data[~data.iloc[:, 3].str.contains('na') & ~data.iloc[:, 4].str.contains('na')]
    # 5. convert the temperature and humidity to float
    data.iloc[:, 3] = data.iloc[:, 3].apply(lambda x: x.replace(',', '.'))
    data.iloc[:, 4] = data.iloc[:, 4].apply(lambda x: x.replace(',', '.'))
    # Convert the temperature and humidity (string) to numeric
    data.iloc[:, 3] = data.iloc[:, 3].astype(float)
    data.iloc[:, 4] = data.iloc[:, 4].astype(float)
    # except the 4th and 5th columns, drop the other columns
    return data

def zone7_read_all_files():
    # /_4_measurements/CAPITOUL/CAPITOUL_including_City(21mini)'
    measure_zone7_folder = '..\\_4_measurements\\CAPITOUL\\CAPITOUL_including_City(21mini)'
    df = pd.DataFrame()
    file_name_str = 'YYYYMM_zone07.tuc' # where MM stands for the month
    #There are 12+2 files, from 200401 to 200502
    for year in range(2004, 2006):
        for month in range(1, 13):
            if year == 2005 and month == 3:
                break
            file_name = file_name_str.replace('YYYY', str(year))
            file_name = file_name.replace('MM', str(month).zfill(2))
            file_name = os.path.join(measure_zone7_folder, file_name)
            df_month = zone7_read_one_file(file_name)
            df = pd.concat([df, df_month])
    column_names = ['Zaehler','Datum','Zeit','Temperature_C', 'Humidity_%']
    df.columns = column_names
    return df

def pomme_columns_name():
    '''
    date, format JJ/MM/AAAA
    time, format HHMMSS.SSS
    air pressure: hPa; sensor: Vaisala PTB200.
    air temperature: Celsius; sensor MP233 VAISALA.
    relative humidity: %; sensor HMP233 VAISALA.
    Incoming short wave radiation: watts/m2; CM3 sensor of Kipp & Zonen CNR1.
    Outgoing short wave radiation: watts/m2; CM3 sensor of Kipp & Zonen CNR1.
    Incoming long wave-Red radiation: watts/m2; CG1 sensor of Kipp & Zonen CNR1.
    Outgoing long wave radiation: watts/m2; CG1 sensor of Kipp & Zonen CNR1.
    rain rate: mm/h; sensor: Optical Rain Gauge
    rate rate: mm/h; sensor: tipping bucket rain gauge
    wind direction: degree; sensor: GILL sonic anemoter, top of tower
    wind speed: m/s; sensor: GILL sonic anemoter, top of tower
    wind direction: degree; sensor: GILL sonic anemoter, intermediate level
    wind speed: m/s; sensor: GILL sonic anemoter, intermediate level
    CO2 concentration: g/m3; sensor: LICOR 7500
    Tower position
    = full extension                (height above ground: 48.05 m)
    = intermediate extension  (height above ground: 38.98 m)
    = intermediate extension  (height above ground: 38.23 m)
    = down                             (height above ground: 26.93 m)
    '''
    column_names = ['Date', 'Time', 'Air_Pressure_hPa', 'Air_Temperature_C', 'Relative_Humidity_%',
                    'Incoming_Short_Wave_Radiation_watts/m2', 'Outgoing_Short_Wave_Radiation_watts/m2',
                    'Incoming_Long_Wave-Red_Radiation_watts/m2', 'Outgoing_Long_Wave_Radiation_watts/m2',
                    'Rain_Rate_mm/h', 'Rate_Rate_mm/h', 'Wind_Direction_degree',
                    'Wind_Speed_m/s', 'Wind_Direction_degree', 'Wind_Speed_m/s', 'CO2_Concentration_g/m3', 'Tower_Position']
    return column_names
def pomme_read_one_file(file_path):
    # 3. read the rest lines, which are the data
    # separators is tab, read the first two columns as string, the rest columns as float
    data = pd.read_csv(file_path, sep='\s+', header=None, index_col= False, dtype ={0:str, 1:str})
    # drop the 3rd column, since it is always 9999
    # data.drop([2], axis=1, inplace=True)
    # DD/MM/YYYY; HHMMSS.SSS
    # 4. convert the date and time to datetime format
    data['Date'] = pd.to_datetime(data.iloc[:, 0] + data.iloc[:, 1], format='%d/%m/%Y%H%M%S.%f')
    # print all columns data types
    # print(data.dtypes)
    data.index = data['Date']
    data.drop(['Date'], axis=1, inplace=True)
    repeated_index = data.index[data.index.duplicated()]
    # drop the repeated index
    data = data.drop(repeated_index)

    target_idx = pd.date_range(start=data.index[0], end=data.index[-1], freq='1min')
    missing_index = target_idx.difference(data.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('File path:', file_path)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    data = data.reindex(target_idx)
    #except the 2nd column, replace 9999 with NaN
    data.iloc[:, 3:] = data.iloc[:, 3:].replace(9999, np.nan)
    # interpolate the missing values
    data = data.interpolate(method='linear')

    return data


def pomme_read_all_files():
    # '_4_measurements/CAPITOUL/CAPITOUL_including_City(Tower)'
    measure_pomme_folder = '..\\_4_measurements\\CAPITOUL\\CAPITOUL_including_City(Tower)'
    df = pd.DataFrame()
    file_name_str = 'TaYYYYMM_MAT_%60.asc' # where MM stands for the month
    #There are 11+2 files, from 200402 to 200502
    file_yyyymm = ['200402', '200403', '200404', '200405', '200406', '200407', '200408',
                   '200409', '200410', '200411', '200412', '200501', '200502']
    for yyyymm in file_yyyymm:
        file_name = file_name_str.replace('YYYYMM', yyyymm)
        file_name = os.path.join(measure_pomme_folder, file_name)
        df_month = pomme_read_one_file(file_name)
        df = pd.concat([df, df_month])
    column_names = pomme_columns_name()
    # drop the 3rd column name
    # column_names.pop(2)
    df.columns =column_names
    return df
def main():
    # df_zone7 = zone7_read_all_files()
    # df_zone7.to_csv('..\\_4_measurements\\CAPITOUL\\Mini_Zone7_Ori_12_min.csv')
    df_pomme = pomme_read_all_files()
    df_pomme.to_csv('..\\_4_measurements\\CAPITOUL\\Urban_Pomme_Ori_1_min.csv')
    # plot df_pomme column 'Air_Temperature_C' with index
    df_pomme['Air_Temperature_C'].plot()
    plt.show()
if __name__ == '__main__':
    main()