
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


def get_clean_airport_measurment(file_path):
    # read one file, read the second column as string
    df = pd.read_csv(file_path, header=0, index_col= 1, sep=',')
    # It has 'Year', 'Month', 'Day', 'Time', where 'Time' is in the format of 'HH:MM'
    # convert the 'Time' to 'HH:MM:SS'
    df['Date/Time'] = pd.to_datetime(df['Date/Time (LST)'])
    # set the index to be the 'Date/Time'
    df = df.set_index('Date/Time')
    # keep 'Temp (°C)', 'Dew Point Temp (°C)', 'Rel Hum (%)'
    df = df[['Temp (°C)', 'Dew Point Temp (°C)', 'Rel Hum (%)']]
    # dtypes are float64, float64, int64
    # find the location of missing values
    # if empty or nan value, then raise an error

    if df.isnull().values.any() or df.isna().values.any():
        raise ValueError('There is empty or nan value in the file: ' + file_path)
    return df

def get_all_epw_files():
    '''
    get all epw files in the folder
    '''
    _71833_file_template = r'..\_4_measurements\Guelph\en_climate_hourly_ON_6143089_MM-2018_P1H.csv'
    # we need 07, 08, 09 month data
    df = pd.DataFrame()
    for month in ['07', '08', '09']:
        _71833_file = _71833_file_template.replace('MM', month)
        df_month = get_clean_airport_measurment(_71833_file)
        df = pd.concat([df, df_month])
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
            # replace the July, August, September data
            if i > 4351 and i < 6560:
                lines[i] = lines[i].split(',')
                # lines[i][0:4] is Year, Month, Day, Hour (1-24)
                year = '2018'
                month = lines[i][1]
                day = lines[i][2]
                # epw is UTC-7, so add 7 hours
                hour = str(int(lines[i][3]) -1 )
                target_date_UTC_M7 = pd.to_datetime(year + '-' + month + '-' + day + ' ' + hour + ':00:00')
                measurements = df_measurement.loc[target_date_UTC_M7]
                # 'Temp (°C)', 'Dew Point Temp (°C)', 'Rel Hum (%)'
                dry_bulb_c = measurements['Temp (°C)']
                dew_point_c = measurements['Dew Point Temp (°C)']
                rel_hum_percentage = measurements['Rel Hum (%)']

                lines[i][0] = year
                lines[i][6] = str(dry_bulb_c)
                lines[i][7] = str(dew_point_c)
                lines[i][8] = str(rel_hum_percentage)
                lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'..\_4_measurements\Guelph\Guelph_2018.epw'
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
    df = get_all_epw_files()
    # save the data to csv file
    df.to_csv(r'..\_4_measurements\Guelph\clean_en_climate_hourly_ON_6143089_MM-2018_P1H.csv')
    epw_file = r'..\_4_measurements\Guelph\overriding_ERA5_Guelph.epw'
    overriding_epw(epw_file, df)

if __name__ == '__main__':
    main()
