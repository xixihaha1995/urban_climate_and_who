# Mo vs Bueno, Fa vs Bueno, La vs Bueno
# incoming radiation vs DNI, DHI
# net radiation vs DNI, DHI
# dry bulb temperatures

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
import os
import pandas as pd
'''
The above 14 columns are measurements, measured in one minute interval.
We have one EPW file, measured in one hour interval.
This script is used to compare the measurements in one minute interval with the measurements in one hour interval.
We need to intialize one excel file, which contains the following sheets:
1. dry bulb temperature comparison
2. pressure comparison
3. relative humidity comparison
4. wind direction comparison
5. wind speed comparison
6. short wave radiation comparison
7. long wave radiation comparison
'''
working_path = os.path.join('_measurements','CAPITOUL')
# initialize the excel file
_compare_excel_file = os.path.join(working_path, 'CAPITOUL_Weather_Comparison.xlsx')
if os.path.exists(_compare_excel_file):
    os.remove(_compare_excel_file)
_compare_excel = pd.ExcelWriter(_compare_excel_file)

# read the measurements
_measurements_file = os.path.join(working_path, 'Rural_Mondouzil_Minute.csv')
_measurements = pd.read_csv(_measurements_file, sep=',', index_col= 0, parse_dates=True)
# to hourly
_measurements_hourly = _measurements.resample('H').mean()
_measurements_hourly.index = pd.to_datetime(_measurements_hourly.index, format='%d/%m/%Y %H:%M:%S')
# read the EPW file, save it to csv file
_epw_file = os.path.join(working_path, 'rural_weather_data_cap.csv')
_epw = pd.read_csv(_epw_file, sep=',', skiprows=18, index_col= 0, parse_dates=True, header = 0)

