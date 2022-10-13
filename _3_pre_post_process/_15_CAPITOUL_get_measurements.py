'''
Prediction sampling rate: 5 minutes (It should be 1 minute)
Measurement (Mini Zone 7, Cité_Administrative) sampling rate: 12 minutes (save first)
    a. There are 12 files, each file contains 1 month dat with the zone7 file name: 2004MM_zone7.tuc
    b. The first 40 lines are general information
    c. The 41th line is the column names, 4 columns separated by ';'
    d. The rest lines are the data, 4 columns separated by ';'
Measurement (Tower Roof, Pomme Road) sampling rate: 1 minute (save first)
'''
import pandas as pd, os
def read_one_file(file_path):
    # 3. read the rest lines, which are the data
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, skiprows=41, sep=';', header=None, encoding= "ISO-8859-1")
    else:
        file_path = file_path.replace('tuc', 'tui')
        data = pd.read_csv(file_path, skiprows=41, sep=';', header=None, encoding= "ISO-8859-1")
    # IDID; DD/MM/YYYY; HH:MM:SS; Tempeature (Celius degree, replace, by .); Humidity (%, replace, by .)
    # 4. convert the date and time to datetime format
    data['Date'] = pd.to_datetime(data.iloc[:, 1] + ' ' + data.iloc[:, 2])
    data.index = data['Date']
    # remove rows containing str 'na'
    data = data[~data.iloc[:, 3].str.contains('na') & ~data.iloc[:, 4].str.contains('na')]
    # 5. convert the temperature and humidity to float
    data.iloc[:, 3] = data.iloc[:, 3].apply(lambda x: x.replace(',', '.'))
    data.iloc[:, 4] = data.iloc[:, 4].apply(lambda x: x.replace(',', '.'))
    # Convert the temperature and humidity (string) to numeric
    data.iloc[:, 3] = data.iloc[:, 3].astype(float)
    data.iloc[:, 4] = data.iloc[:, 4].astype(float)
    # except the 4th and 5th columns, drop the other columns
    data = data.iloc[:, [3, 4]]
    return data

def read_all_files():
    # /_4_measurements/CAPITOUL/CAPITOUL_including_City(21mini)'
    measure_zone7_folder = '..\\_4_measurements\\CAPITOUL\\CAPITOUL_including_City(21mini)'
    df = pd.DataFrame()
    file_name_str = '2004MM_zone07.tuc' # where MM stands for the month
    for month in range(1, 13):
        file_name = file_name_str.replace('MM', str(month).zfill(2))
        file_name = os.path.join(measure_zone7_folder, file_name)
        df_month = read_one_file(file_name)
        df = pd.concat([df, df_month])
    column_names = ['Temperature_C', 'Humidity_%']
    df.columns = column_names
    return df

def main():
    df = read_all_files()
    df.to_csv('..\\_4_measurements\\CAPITOUL\\Mini_Zone7_Ori_12_min_2004.csv')

if __name__ == '__main__':
    main()