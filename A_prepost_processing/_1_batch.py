
import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3


def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def get_measurements():
    if os.path.exists(os.path.join('measurements', processed_measurements)):
        measurements = pd.read_csv(os.path.join('measurements', processed_measurements), index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements
    urban_path = os.path.join('measurements', 'Urban_Pomme_Ori_1_min.csv')
    rural_path = os.path.join('measurements', 'Rural_Ori_1_min.csv')
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

    comparison.to_csv(os.path.join('measurements', processed_measurements))
    return comparison

def read_sql(path,number):
    if number == 0:
        csv_name = '_0ep_outputs'
    elif number > 0:
        csv_name = '_positive' + str(number) + 'ep_outputs'
    else:
        csv_name = '_negative' + str(abs(number)) + 'ep_outputs'
    # from all the folders in the current path, find the one that contains the csv file
    sql_path = 'None'
    for folder in os.listdir(path):
        if csv_name in folder and 'ep_outputs' in folder:
            sql_path = os.path.join(path, folder, 'eplusout.sql')
            break

    if not os.path.exists(sql_path):
        return None
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())

    totalEnergyQuery = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{sql_report_name}' AND TableName = '{sql_table_name}'" \
            f" AND RowName = '{sql_row_name}' AND ColumnName = '{sql_col_name}'"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
        totalEnergyRes = cursor.execute(totalEnergyQuery).fetchall()
        if totalEnergyRes:
            pass
        else:
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(totalEnergyQuery))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    totalEnergy = float(re.findall(regex, totalEnergyRes[0][1])[0])

    hvac_electricity_query = f"SELECT * FROM TabularDataWithStrings " \
                             f"WHERE ReportName = '{sql_report_name}'" \
                             f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                             f"AND ColumnName = 'Electricity Intensity'"
    hvac_electricity_query_results = cursor.execute(hvac_electricity_query).fetchall()
    hvac_electricity = float(re.findall(regex, hvac_electricity_query_results[0][1])[0])
    hvac_gas_query = f"SELECT * FROM TabularDataWithStrings " \
                        f"WHERE ReportName = '{sql_report_name}'" \
                        f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                        f"AND ColumnName = 'Natural Gas Intensity'"
    hvac_gas_query_results = cursor.execute(hvac_gas_query).fetchall()
    hvac_gas = float(re.findall(regex, hvac_gas_query_results[0][1])[0])
    return totalEnergy, hvac_electricity, hvac_gas
def process_one_theme(theme, path, offline_bool = False):
    #find all csv files in the path, which does not contain 'save'
    csv_files = []
    for file in os.listdir(path):
        if file.endswith('.csv') and 'save' not in file:
            csv_files.append(file)
    #process each csv file
    comparison = get_measurements()
    cvrmse_dict = {}
    sql_dict = {}
    for csv_file in csv_files:
        df = pd.read_csv(os.path.join(path ,csv_file), index_col=0, parse_dates=True)
        df = df[compare_start_time:compare_end_time]
        comparison['MeteoData.Pre'] = df['MeteoData.Pre']
        comparison['TempProf_' + csv_file] = df['TempProf_cur[19]']
        comparison['PresProf_' + csv_file] = df['PresProf_cur[19]']
        comparison['MeteoData.Pre_RealTempProf_' + csv_file] = (df['TempProf_cur[19]'])* \
                                                 (df['PresProf_cur[19]'] / comparison['MeteoData.Pre']) ** 0.286 - 273.15
        # from string csv_file extract float number based on regex
        # extract the number from the csv file name: such as '0.1.csv' -> 0.1, '-0.1.csv' -> -0.1
        regex = r'(-?\d+\.?\d*)'
        number = float(re.findall(regex, csv_file)[0])
        key_name = str(number)
        cvrmse_dict[key_name] = cvrmse(comparison['Urban_DBT_C'], comparison['MeteoData.Pre_RealTempProf_' + csv_file])
        sql_dict[key_name] = (read_sql(path,number))
    # create new Excel file, where the first sheet is the comparison, and the second sheet is the cvrmse
    # third sheet is sql data
    if os.path.exists(os.path.join(path, 'sensitivity_analysis.xlsx')):
        os.remove(os.path.join(path, 'sensitivity_analysis.xlsx'))
    writer = pd.ExcelWriter(os.path.join(path, 'sensitivity_analysis.xlsx'), engine='xlsxwriter')

    comparison.to_excel(writer, 'comparison')
    cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    cvrmse_df.to_excel(writer, 'cvrmse')
    sql_df = pd.DataFrame.from_dict(sql_dict, orient='index', columns=['Total Site Energy[GJ]',
                                                                       'HVAC Electricity Intensity [MJ/m2]',
                                                                       'HVAC Natural Gas Intensity [MJ/m2]'])
    sql_df.to_excel(writer, 'sql')
    writer.save()

def process_all_themes():

    online_themes = os.listdir(experiments_folder)
    for online_theme in online_themes:
        process_one_theme(online_theme, os.path.join(experiments_folder, online_theme))

def main():
    global processed_measurements, compare_start_time, compare_end_time, \
        sql_report_name, sql_table_name, sql_row_name, sql_col_name, experiments_folder
    experiments_folder = r'sensitivity_shading_boosted'
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'
    compare_start_time = '2004-06-01 00:05:00'
    compare_end_time = '2004-06-30 22:55:00'
    processed_measurements = 'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                             + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    process_all_themes()
if __name__ == '__main__':
    main()
