import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3
from shutil import copyfile

from matplotlib import pyplot as plt

def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def get_CAPITOUL_measurements():
    if os.path.exists('measurements/' + processed_measurements):
        measurements = pd.read_csv('measurements/' + processed_measurements, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements
    urban_path = r'measurements/Urban_Pomme_Ori_1_min.csv'
    rural_path = r'measurements/Rural_Ori_1_min.csv'
    urban = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    rural = pd.read_csv(rural_path, index_col=0, parse_dates=True)
    urban_5min = urban.resample('5min').mean()
    rural_5min = rural.resample('5min').mean()
    urban_5min = urban_5min[compare_start_time:compare_end_time]
    rural_5min = rural_5min[compare_start_time:compare_end_time]
    #Air_Temperature_C, tpr_air2m_c13_cal_%60'_celsius, pre_air_c13_cal_%60'_hPa
    # initialize the dataframe, with the same index as rural, and 3 columns
    comparison = pd.DataFrame(index=rural_5min.index, columns=['Urban_DBT_C', 'Rural_DBT_C'])
    comparison['Urban_DBT_C'] = urban_5min['Air_Temperature_C']
    comparison['Rural_DBT_C'] = rural_5min['tpr_air2m_c13_cal_%60\'_celsius']
    comparison['Rural_Pres_Pa'] = rural_5min['pre_air_c13_cal_%60\'_hPa'] * 100

    comparison.to_csv('measurements/' + processed_measurements)
    return comparison


def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows= skiprows, header= header, index_col=index_col, sep= '[ ^]+', engine='python')
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
    # index format is YYYY-MM-DD HH:MM:SS
    # replace HH:MM with first 5 char of 0th column, convert to datetime
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d') + ' ' + df.iloc[:,0].str[:5])
    repeated_index = df.index[df.index.duplicated()]
    df = df.drop(repeated_index)
    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='10min')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)
    # drop the 0th column, according to the index instead of column name
    df.drop(df.columns[0], axis=1, inplace=True)
    df.iloc[:, :-1] = df.iloc[:, :-1].apply(lambda x: x.str.replace(',', '')).astype(float)
    # interpolate the missing values
    df = df.interpolate(method='linear')
    return df

def clean_urban(df):
    repeated_index = df.index[df.index.duplicated()]
    df = df.drop(repeated_index)
    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='10min')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)
    df = df.interpolate(method='linear')
    return df

def get_BUUBLE_measurements():
    if os.path.exists('measurements/' + processed_measurements):
        measurements = pd.read_csv('measurements/' + processed_measurements, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements

    urban_path = r'measurements/BUBBLE_Ue1_Urban.csv'
    rural_path = r'measurements/BUBBLE_AT_IOP.txt'
    mixed_all_sites_10min = read_text_as_csv(rural_path,
                                                             header=0, index_col=0, skiprows=25)
    mixed_all_sites_10min = mixed_all_sites_10min[compare_start_time:compare_end_time]
    urban_dirty = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    urban = clean_urban(urban_dirty)
    urban = urban[compare_start_time:compare_end_time]
    #Air_Temperature_C, tpr_air2m_c13_cal_%60'_celsius, pre_air_c13_cal_%60'_hPa
    # initialize the dataframe, with the same index as rural, and 3 columns
    comparison = pd.DataFrame(index=mixed_all_sites_10min.index, columns=['Urban_DBT_C', 'Rural_DBT_C'])
    comparison['Urban_DBT_C'] = urban.iloc[:, 0]
    comparison['Rural_DBT_C'] = mixed_all_sites_10min.iloc[:, 7]

    comparison.to_csv('measurements/' + processed_measurements)
    return comparison


def read_sql(csv_file):
    csv_name = re.search(r'(.*)\.csv', csv_file).group(1)
    current_path = f'./{experiments_folder}'
    sql_path = "foo"
    for folder in os.listdir(current_path):
        if csv_name in folder and 'ep_trivial_outputs' in folder:
            sql_path = os.path.join(current_path, folder, 'eplusout.sql')
            break
    if not os.path.exists(sql_path):
        return None
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{sql_report_name}' AND TableName = '{sql_table_name}'" \
            f" AND RowName = '{sql_row_name}' AND ColumnName = '{sql_col_name}'"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
        results = cursor.execute(query).fetchall()
        if results:
            pass
        else:
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(query))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    number = float(re.findall(regex, results[0][1])[0])
    return number
def process_one_theme(path):
    if "BUBBLE" in experiments_folder:
        comparison = get_BUUBLE_measurements()
    else:
        comparison = get_CAPITOUL_measurements()
    # df1 = pd.read_csv(path + '/' + 'saving.csv', index_col=0, parse_dates=True)
    df2 = pd.read_csv(path + '/' + 'debug_saving.csv', index_col=0, parse_dates=True)
    # df1 = df1[compare_start_time:compare_end_time]
    # df2 = df2[compare_start_time:compare_end_time]
    # comparison['sensWaste'] = df1['sensWaste']
    comparison['canTemp'] = df2['canTemp']
    VCWG_cvrmse = cvrmse(comparison['Urban_DBT_C'], comparison['canTemp'] - 273.15)
    Rural_cvrmse = cvrmse(comparison['Urban_DBT_C'],comparison['Rural_DBT_C'])
    print('VCWG_cvrmse:', VCWG_cvrmse)
    print('Rural_cvrmse:', Rural_cvrmse)
    comparison['ForcingVariable[0]'] = df2['ForcingVariable[0]']
    comparison['srex_th_mean'] = df2['srex_th_mean']
    if os.path.exists(f'{experiments_folder}/debug.xlsx'):
        os.remove(f'{experiments_folder}/debug.xlsx')
    writer = pd.ExcelWriter(f'{experiments_folder}/debug.xlsx')
    comparison.to_excel(writer, 'debug')
    writer.save()

def plots():
    #Urban_DBT_C, Rural_DBT_C,sensWaste, canTemp, ForcingVariable[0], srex_th_mean
    plot_fontsize = 10
    df = pd.read_excel(f'{experiments_folder}/debug.xlsx', index_col=0, parse_dates=True)
    # plot into one subfigure: 6 timeseries
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    fig.subplots_adjust(right=0.76)

    # 'sensWaste', srex_th_mean has different scale, plot it in the second subfigure
    compare_cols = ['Urban_DBT_C', 'Rural_DBT_C', 'canTemp', 'ForcingVariable[0]']
    for col in compare_cols:
        if col == "canTemp" or col == "ForcingVariable[0]":
            axes[0].plot(df.index, df[col] - 273.15, label=col)
        else:
            axes[0].plot(df.index, df[col], label=col)
    axes[0].set_ylabel('Temperature (C)')

    axes[0].set_title('Temperature')
    srex_ax = axes[1].twinx()
    srex_ax.plot(df.index, df['srex_th_mean'], label='srex_th_mean', color='black', linestyle='--')
    # axes[1].plot(df.index, df['sensWaste'], label='sensWaste')
    # axes[1].set_ylabel('W/m2')
    fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=plot_fontsize)
    plt.show()


def main():
    global processed_measurements, compare_start_time, compare_end_time, sql_report_name, sql_table_name, sql_row_name, sql_col_name
    global experiments_folder
    # experiments_folder = 'BUBBLE_debug'
    # compare_start_time = '2002-06-10 01:00:00'
    # compare_end_time = '2002-07-09 21:50:00'
    experiments_folder = 'CAPITOUL_epw_wind_diffSol_debug'
    compare_start_time = '2004-06-01 01:00:00'
    compare_end_time = '2004-06-30 22:55:00'
    processed_measurements = 'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                             + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    process_one_theme(experiments_folder)
    plots()
if __name__ == '__main__':
    main()
