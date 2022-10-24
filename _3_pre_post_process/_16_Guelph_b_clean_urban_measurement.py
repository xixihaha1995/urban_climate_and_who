
import os, sys
import pandas as pd, _0_all_plot_tools as plot_tools, matplotlib.pyplot as plt




def get_clean_urban_site_measurment(file_path):
    # read txt file, sep are three or more spaces, skip the first row, use the second row as column names
    df = pd.read_csv(file_path, sep='\s{3,}', skiprows=1, header=0)
    # The first 5 columns are date and time, the rest are the measurements
    # column 0, format YYYY
    # column 1, format M
    # column 2, format D
    # column 3, format H
    # column 4, format M
    # convert the date and time to datetime
    df['Date'] = pd.to_datetime(df.iloc[:, 0].astype(str) + '-' + df.iloc[:, 1].astype(str) +
                                '-' + df.iloc[:, 2].astype(str) + ' ' + df.iloc[:, 3].astype(str) + ':' +
                                df.iloc[:, 4].astype(str))
    df = df.set_index('Date')
    # '10:Theta (K)', if there are nan or missing values, raise error
    if df['10:Theta (K)'].isnull().values.any() or df['10:Theta (K)'].isna().values.any():
        raise ValueError('There are nan or missing values in Theta (K)')
    # interpolate the missing values for '10:Theta (K)'
    df['10:Theta (K)'] = df['10:Theta (K)'].interpolate(method= 'linear')
    return df

def get_all_urban_files():
    '''
    get all epw files in the folder
    '''
    urban_site_file_name = r'..\_4_measurements\Guelph\Processed Data\RY1-A-30minStatisticsFiltered.txt'
    # we need to access A, B, C, D and E anemometer data
    # create one excel with 5 sheets
    writer = pd.ExcelWriter(r'..\_4_measurements\Guelph\To_Generate_Urban\clean_urban_sites_all.xlsx')
    for i in range(5):
        file_path = urban_site_file_name.replace('A', chr(ord('A') + i))
        file_path = file_path.replace('1', str(i + 1))
        df = get_clean_urban_site_measurment(file_path)
        df.to_excel(writer, sheet_name=chr(ord('A') + i))
    writer.save()

def urban_site_air_temperature():
    '''
    plot the air temperature of urban site
    '''
    # read the excel
    df = pd.read_excel(r'..\_4_measurements\Guelph\To_Generate_Urban\clean_urban_sites_all.xlsx', sheet_name=None)
    # create new dataframe to only save air temperature (K) for each anemometer
    df_air_temp = pd.DataFrame()
    for i in range(5):
        df_air_temp[chr(ord('A') + i) + ' Air temp [K]'] = df[chr(ord('A') + i)]['10:Theta (K)']
    # index
    df_air_temp.index = df['A']['Date']
    # rename the columns
    df_air_temp.columns = ['A Air temp[K](2.4m)', 'B Air temp[K](5.4m)',
                           'C Air temp[K](2.4m)', 'D Air temp[K](2.4m)', 'E Air temp[K](17m)']

    # save the dataframe to excel
    df_air_temp.to_excel(r'..\_4_measurements\Guelph\To_Generate_Urban\clean_urban_sites_air_temp_K.xlsx', sheet_name='Air Temp')

def main():
    # get the data from all the files
    get_all_urban_files()
    urban_site_air_temperature()

if __name__ == '__main__':
    main()
