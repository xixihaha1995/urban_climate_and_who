
import os, sys
import pandas as pd, _0_all_plot_tools as plot_tools, matplotlib.pyplot as plt

sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI



def get_clean_airport_measurment(file_path):
    # read one file, read the second column as string
    df = pd.read_csv(file_path, header=0, index_col= 1, sep=',')
    # It has 'Year', 'Month', 'Day', 'Time', where 'Time' is in the format of 'HH:MM'
    # convert the 'Time' to 'HH:MM:SS'
    df['Date/Time'] = pd.to_datetime(df['Date/Time (LST)'])
    # set the index to be the 'Date/Time'
    df = df.set_index('Date/Time')

    repeated_index = df.index[df.index.duplicated()]
    # drop the repeated index
    df = df.drop(repeated_index)

    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='1H')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('File path:', file_path)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)

    # keep 'Temp (°C)', 'Dew Point Temp (°C)', 'Rel Hum (%)'
    df = df[['Temp (°C)', 'Dew Point Temp (°C)', 'Rel Hum (%)']]
    # interpolate the missing values
    df = df.interpolate(method='linear', axis=0).ffill().bfill()
    if df.isnull().values.any() or df.isna().values.any():
        # find the location of missing values
        # if empty or nan value, then raise an error
        raise ValueError('There is empty or nan value in the file: ' + file_path)
    return df

def get_all_epw_files():
    '''
    get all epw files in the folder
    '''
    _718920_file_template = r'..\_4_measurements\Vancouver\To_RegenerateEPW\en_climate_hourly_BC_1108447_MM-2008_P1H.csv'
    df = pd.DataFrame()
    for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        _718920_file = _718920_file_template.replace('MM', month)
        df = df.append(get_clean_airport_measurment(_718920_file))
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
            if i > 7:
                lines[i] = lines[i].split(',')
                # lines[i][0:4] is Year, Month, Day, Hour (1-24)
                year = '2008'
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
    overwriten_epw = r'..\_4_measurements\Vancouver\To_RegenerateEPW\ECCC_Vancouver_2008.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)
    return overwriten_epw

def urban_island_effect(compare_start_date,compare_end_date):
    ncdc_epw = r'..\_4_measurements\Vancouver\To_GenerateEPW\NCDC_Vancouver.epw'
    eccc_epw = r'..\_4_measurements\Vancouver\To_RegenerateEPW\ECCC_Vancouver_2008.epw'
    ncdc_rural_epw = pd.read_csv(ncdc_epw, skiprows=8, header=None, index_col= None)
    ncdc_rural_epw_all = plot_tools.clean_epw(ncdc_rural_epw)
    ncdc_rural_epw_air_temp_c = ncdc_rural_epw_all.iloc[:, 6]
    ncdc_rural_epw_air_temp_c = ncdc_rural_epw_air_temp_c[compare_start_date:compare_end_date]
    ncdc_rural_epw_air_temp_c = ncdc_rural_epw_air_temp_c.resample('30T').interpolate(method='linear', axis=0).ffill().bfill()

    eccc_rural_epw = pd.read_csv(eccc_epw, skiprows=8, header=None, index_col= None)
    eccc_rural_epw_all = plot_tools.clean_epw(eccc_rural_epw)
    eccc_rural_epw_air_temp_c = eccc_rural_epw_all.iloc[:, 6]
    eccc_rural_epw_air_temp_c = eccc_rural_epw_air_temp_c[compare_start_date:compare_end_date]
    eccc_rural_epw_air_temp_c = eccc_rural_epw_air_temp_c.resample('30T').interpolate(method='linear', axis=0).ffill().bfill()

    urban_path = r'..\_4_measurements\Vancouver\SSDTA_all_30min.csv'
    ss4_tower_ori_30min = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    ss4_tower_ori_30min = ss4_tower_ori_30min[compare_start_date:compare_end_date]

    repeated_index = ss4_tower_ori_30min.index[ss4_tower_ori_30min.index.duplicated()]
    # drop the repeated index
    ss4_tower_ori_30min = ss4_tower_ori_30min.drop(repeated_index)

    target_idx = pd.date_range(start=ss4_tower_ori_30min.index[0], end=ss4_tower_ori_30min.index[-1], freq='1H')
    missing_index = target_idx.difference(ss4_tower_ori_30min.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    ss4_tower_ori_30min = ss4_tower_ori_30min.reindex(target_idx)

    # original sampling rate is 30min, convert to 1hour
    ss4_tower_ori_30min = ss4_tower_ori_30min.astype(float)
    # convert nan to 0
    ss4_tower_ori_30min = ss4_tower_ori_30min.interpolate(method='linear')
    # create a new dataframe, nased as uhi_df, including all the columns ss4_tower_ori_30min,
    # ncdc_rural_epw_air_temp_c, eccc_epw_air_temp_c
    uhi_df = pd.concat([ss4_tower_ori_30min, ncdc_rural_epw_air_temp_c, eccc_rural_epw_air_temp_c], axis=1)
    uhi_df = uhi_df.interpolate(method='linear')
    # rename the columns, keep ss4_tower_ori_30min name, add one more column name for rural_epw_air_temp_c
    new_columns = ss4_tower_ori_30min.columns.tolist() + ['ncdc_rural_epw_air_temp_c', 'eccc_rural_epw_air_temp_c']
    uhi_df.columns = new_columns
    # save the uhi_df to excel
    uhi_df.to_excel(r'..\_4_measurements\Vancouver\To_RegenerateEPW\Vancouver_Urban_Rural_May_To_Sep_2008.xlsx')
    # plot the first and last column
    uhi_df.plot()
    plt.show()
def init_ep_api():
    global psychrometric, state
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    psychrometric = ep_api.functional.psychrometrics(state)

def main():
    # init_ep_api()
    # # get the data from all the files
    # df = get_all_epw_files()
    # # save the data to csv file
    # df.to_csv(r'..\_4_measurements\Vancouver\To_RegenerateEPW\clean_en_climate_hourly_BC_1108447_MM-2008_P1H.csv')
    # epw_file = r'..\_4_measurements\Vancouver\To_RegenerateEPW\overridingCAN_BC_Vancouver.718920_CWEC.epw'
    # overwriten_epw = overriding_epw(epw_file, df)
    urban_island_effect('2008-05-01 00:00:00', '2008-09-30 23:30:00')

if __name__ == '__main__':
    main()
