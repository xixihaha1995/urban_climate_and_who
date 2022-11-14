
import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3


def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def get_measurements():
    if os.path.exists('measurements\\' + processed_measurements):
        return pd.read_csv('measurements\\' + processed_measurements, index_col=0, parse_dates=True)
    urban_path = r'measurements\Urban_Pomme_Ori_1_min.csv'
    rural_path = r'measurements\Rural_Ori_1_min.csv'
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

    comparison.to_csv('measurements\\' + processed_measurements)
    return comparison

def read_sql(csv_file):
    csv_name = re.search(r'(.*)\.csv', csv_file).group(1)
    current_path = '.\\shading_Bypass_saving'
    for folder in os.listdir(current_path):
        if csv_name in folder and 'ep_outputs' in folder:
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
        df = pd.read_csv(path + '\\' + csv_file, index_col=0, parse_dates=True)
        df = df[compare_start_time:compare_end_time]
        comparison['MeteoData.Pre'] = df['MeteoData.Pre']
        comparison['TempProf_' + csv_file] = df['TempProf_cur[19]']
        comparison['PresProf_' + csv_file] = df['PresProf_cur[19]']
        comparison['MeteoData.Pre_RealTempProf_' + csv_file] = (df['TempProf_cur[19]'])* \
                                                 (df['PresProf_cur[19]'] / comparison['MeteoData.Pre']) ** 0.286 - 273.15
        cvrmse_dict['CVRMSE'] = cvrmse(comparison['Urban_DBT_C'], comparison['MeteoData.Pre_RealTempProf_' + csv_file])

    if os.path.exists('shading_Bypass_saving\\comparison.xlsx'):
        os.remove('shading_Bypass_saving\\comparison.xlsx')
    writer = pd.ExcelWriter('shading_Bypass_saving\\comparison.xlsx')
    comparison.to_excel(writer, 'comparison')
    cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    cvrmse_df.to_excel(writer, 'cvrmse')
    sql_df = pd.DataFrame.from_dict(sql_dict, orient='index', columns=['total_site_energy'])
    sql_df.to_excel(writer, 'sql')
    writer.save()

def process_all_themes():
    shading_bypass_path = r'shading_Bypass_saving'
    cases = os.listdir(shading_bypass_path)
    for case in cases:
        process_one_theme(shading_bypass_path)

def plots():
    pass
    #Measurements: Rural, Urban
    #Predictions: VCWG, Bypass-Default, Bypass-Shading, Bypass-ViewFactor, Bypass-Shading-ViewFactor

def main():
    global processed_measurements, compare_start_time, compare_end_time, sql_report_name, sql_table_name, sql_row_name, sql_col_name
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
