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

import os
import pandas as pd
import numpy as np

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

def make_columns_name():
    # make the column names
    # the column names are the same as the epw file
    column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Data Source and Uncertainty Flags', 'Dry Bulb Temperature', 'Dew Point Temperature', 'Relative Humidity', 'Atmospheric Station Pressure', 'Extraterrestrial Horizontal Radiation', 'Extraterrestrial Direct Normal Radiation', 'Horizontal Infrared Radiation Intensity', 'Global Horizontal Radiation', 'Direct Normal Radiation', 'Diffuse Horizontal Radiation', 'Global Horizontal Illuminance', 'Direct Normal Illuminance', 'Diffuse Horizontal Illuminance', 'Zenith Luminance', 'Wind Direction', 'Wind Speed', 'Total Sky Cover', 'Opaque Sky Cover', 'Visibility', 'Ceiling Height', 'Present Weather Observation', 'Present Weather Codes', 'Precipitable Water', 'Aerosol Optical Depth', 'Snow Depth', 'Days Since Last Snowfall', 'Albedo', 'Liquid Precipitation Depth', 'Liquid Precipitation Quantity']
    return column_names

def get_one_file_data(file_path):
    # read one file
    df = pd.read_csv(file_path, skiprows=15, header=None)
    # convert the date and time to datetime format
    df['date_time'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d/%m/%Y %H%M%S.%f')
    # set the date_time as index
    df = df.set_index('date_time')
    # drop the date and time columns
    df = df.drop(['date', 'time'], axis=1)
    return df

def get_all_files_data():
    # get the file path
    file_path = r'_4_measurements\CAPITOUL\CAPITOUL_including_Rural(Mondouzil)\Mo_BDD\Mo_BDD'
    # get all the file names
    file_names = os.listdir(file_path)
    # get the data from all the files
    df = pd.DataFrame()
    file_name_str = 'Mo_BDD_MM-2004.asc' # where MM stands for the month
    #get 01 month file name by file_name_str.replace('MM', '01')
    _first_month_name = file_name_str.replace('MM', '01')
    column_name = make_columns_name(os.path.join(file_path, _first_month_name))
    df.columns = column_name
    for month in range(1, 13):
        file_name = file_name_str.replace('MM', str(month).zfill(2))
        file_name = os.path.join(file_path, file_name)
        df_month = get_one_file_data(file_name)
        df = pd.concat([df, df_month])
    return df
