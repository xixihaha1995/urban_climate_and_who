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

import os, sys
import pandas as pd, _0_all_plot_tools as plot_tools, matplotlib.pyplot as plt

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

def get_clean_airport_measurment(file_path):
    # read one file, read the second column as string
    df = pd.read_csv(file_path, header=0, index_col= 1, sep=',')
    # The index (date) might have some repeated entires, or missing entries. Find them.
    # 1. find the repeated entries
    df.index = pd.to_datetime(df.index)
    repeated_index = df.index[df.index.duplicated()]
    if len(repeated_index) != 0:
        print('repeated_index', repeated_index)
        raise ValueError('repeated_index')
    # 2. find the missing entries, sample rate is 1 hour
    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='1H')
    missing_index = target_idx.difference(df.index)
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)
    # only keep these columns: TMP,DEW,SLP
    df = df[['TMP', 'DEW', 'SLP']]
    # convert types to string
    df = df.astype(str)
    # For column 'TMP', return the rows index, where its last character is not '1'
    error_tmp_indices = df[df['TMP'].str[-1] != '1'].index
    # '2008-10-01T07:35:00', '2008-10-01T14:25:00', '2008-10-05T04:32:00',
    # '2008-10-06T20:44:00', '2008-10-06T21:39:00', '2008-10-07T00:24:00',
    # '2008-10-07T01:42:00', '2008-10-07T05:13:00', '2008-10-07T06:27:00',
    # '2008-10-07T07:29:00'
    error_dew_indices = df[df['DEW'].str[-1] != '1'].index
    # '2008-12-30T00:11:00', '2008-12-30T01:24:00', '2008-12-30T19:29:00',
    # '2008-12-31T03:54:00', '2008-12-31T05:45:00', '2008-12-31T06:17:00',
    # '2008-12-31T06:45:00', '2008-12-31T07:13:00', '2008-12-31T09:50:00',
    # '2008-12-31T10:25:00'
    error_slp_indices = df[df['SLP'].str[-1] != '1'].index
    # for 'TMP', 'DEW', 'SLP', find any elements, where its last character is not '1', define this element as nan
    df.loc[error_tmp_indices, 'TMP'] = float('nan')
    df.loc[error_dew_indices, 'DEW'] = float('nan')
    df.loc[error_slp_indices, 'SLP'] = float('nan')
    df = df.apply(lambda x: x.str[:-2])
# convert types to float
    df = df.astype(float)
    # interpolate the nan values
    df = df.interpolate()
    # for first two columns, divide by 10
    df.iloc[:, 0:2] = df.iloc[:, 0:2] / 10
    # for the last column, mutiply by 10
    df.iloc[:, 2] = df.iloc[:, 2] * 10
    # rename the columns 'TMP' to 'Dry Bulb Temperature {C}', 'DEW' to 'Dew Point Temperature {C}', 'SLP' to 'Atmospheric Station Pressure {Pa}'
    df = df.rename(columns={'TMP': 'Dry Bulb Temperature {C}', 'DEW': 'Dew Point Temperature {C}', 'SLP': 'Atmospheric Station Pressure {Pa}'})
    # combine the date and time, and convert to datetime format
    return df
def overriding_epw(epw_file, df_measurement):
    '''
    1. original epw file has 8760 data records
    2. measurement has 8784 data records. So drop Feb 29th data
    3. For air temperature, overwrite the epw file with the measurement data
        a. For epw, the ;7th column is the dry bulb temperature
        b. For measurement, the 1st column is the dry bulb temperature
    '''
    # read text based epw file line by line
    with open(epw_file, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            # for the 7th column, overwrite with the measurement data
            if i > 7 and i < 8761:
                lines[i] = lines[i].split(',')
                # lines[i][0:4] is Year, Month, Day, Hour (1-24)
                year = '2008'
                month = lines[i][1]
                day = lines[i][2]
                # epw is UTC-7, so add 7 hours
                hour = str(int(lines[i][3]) -1 )
                target_date_UTC_M7 = pd.to_datetime(year + '-' + month + '-' + day + ' ' + hour + ':00:00')
                target_date_UTC_0 = target_date_UTC_M7 + pd.Timedelta(hours=7)
                measurements = df_measurement.loc[target_date_UTC_0]
                dry_bulb_c = measurements['Dry Bulb Temperature {C}']
                dew_point_c = measurements['Dew Point Temperature {C}']
                sea_level_press_pa = measurements['Atmospheric Station Pressure {Pa}']

                lines[i][0] = year
                lines[i][6] = str(dry_bulb_c)
                lines[i][7] = str(dew_point_c)

                humidity_ratio = psychrometric.humidity_ratio_b(state,dew_point_c, sea_level_press_pa)
                rh = psychrometric.relative_humidity_b(state,dry_bulb_c, humidity_ratio, sea_level_press_pa)
                lines[i][8] = str(rh*100)
                lines[i][9] = str(sea_level_press_pa)
                lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'..\_4_measurements\Vancouver\To_GenerateEPW\NCDC_Vancouver.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)
    return overwriten_epw

def init_ep_api():
    global psychrometric, state
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    psychrometric = ep_api.functional.psychrometrics(state)

def urban_island_effect(overwriten_epw,compare_start_date,compare_end_date):
    rural_epw = pd.read_csv(overwriten_epw, skiprows=8, header=None, index_col= None)
    rural_epw_all = plot_tools.clean_epw(rural_epw)
    rural_epw_air_temp_c = rural_epw_all.iloc[:, 6]
    rural_epw_air_temp_c = rural_epw_air_temp_c[compare_start_date:compare_end_date]
    rural_epw_air_temp_c = rural_epw_air_temp_c.resample('30min').interpolate()

    urban_path = r'..\_4_measurements\Vancouver\SSDTA_2008-07_30min.csv'
    ss4_tower_ori_30min = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    #interpolate the missing data
    ss4_tower_ori_30min = ss4_tower_ori_30min.interpolate(method='linear')
    # create a new dataframe, nased as uhi_df, including ss4_tower_ori_30min, rural_epw_air_temp_c
    uhi_df = pd.concat([ss4_tower_ori_30min, rural_epw_air_temp_c], axis=1)
    # rename the columns, keep ss4_tower_ori_30min name, add one more column name for rural_epw_air_temp_c

    new_columns = ss4_tower_ori_30min.columns.tolist() + ['rural_epw_air_temp_c']
    uhi_df.columns = new_columns
    # save the uhi_df to csv file
    uhi_df.to_csv(r'..\_4_measurements\Vancouver\Vancouver_Urban_Rural_July_2008.csv')

def main():
    init_ep_api()
    # get the data from all the files
    _71890_file = r'..\_4_measurements\Vancouver\To_GenerateEPW\IntegratedSurfaceDataset_Vancouver_INT_Airport_2008.csv'
    # _71890_file = r'..\_4_measurements\Vancouver\IntegratedSurfaceDataset_Vancouver_Harbour_Airport_2008.csv'
    df = get_clean_airport_measurment(_71890_file)
    #plot the first column
    # df.iloc[:, 0].plot()
    # plt.show()
    # save the data to csv file
    df.to_csv(r'..\_4_measurements\Vancouver\To_GenerateEPW\clean_NCDC_Vancouver_INT_Airport_2008.csv')
    # _2_cases_input_outputs/_08_CAPITOUL/generate_epw/overriding_FRA_Bordeaux.075100_IWECEPW.csv
    epw_file = r'..\_4_measurements\Vancouver\To_GenerateEPW\overridingCAN_BC_Vancouver.718920_CWEC.epw'
    overwriten_epw = overriding_epw(epw_file, df)
    # compare_start_date = '2008-07-01 00:00:00'
    # compare_end_date = '2008-07-31 23:00:00'
    #
    # urban_island_effect(overwriten_epw,compare_start_date,compare_end_date)

if __name__ == '__main__':
    main()
