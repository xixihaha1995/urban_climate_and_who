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


# Index(['HH:MM', 'Datasource', 'Dry Bulb Temperature {C}',
#        'Dew Point Temperature {C}', 'Relative Humidity {%}',
#        'Atmospheric Pressure {Pa}',
#        'Extraterrestrial Horizontal Radiation {Wh/m2}',
#        'Extraterrestrial Direct Normal Radiation {Wh/m2}',
#        'Horizontal Infrared Radiation Intensity from Sky {Wh/m2}',
#        'Global Horizontal Radiation {Wh/m2}',
#        'Direct Normal Radiation {Wh/m2}',
#        'Diffuse Horizontal Radiation {Wh/m2}',
#        'Global Horizontal Illuminance {lux}',
#        'Direct Normal Illuminance {lux}',
#        'Diffuse Horizontal Illuminance {lux}', 'Zenith Luminance {Cd/m2}',
#        'Wind Direction {deg}', 'Wind Speed {m/s}', 'Total Sky Cover {.1}',
#        'Opaque Sky Cover {.1}', 'Visibility {km}', 'Ceiling Height {m}',
#        'Present Weather Observation', 'Present Weather Codes',
#        'Precipitable Water {mm}', 'Aerosol Optical Depth {.001}',
#        'Snow Depth {cm}', 'Days Since Last Snow', 'Albedo {.01}',
#        'Liquid Precipitation Depth {mm}',
#        'Liquid Precipitation Quantity {hr}'],
#       dtype='object')

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

# Mo vs Bueno, Fa vs Bueno, La vs Bueno
# incoming radiation vs DNI, DHI
# net radiation vs DNI, DHI
# dry bulb temperatures

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

working_path = os.path.join('_measurements','CAPITOUL')
# initialize the excel file
_compare_excel_file = os.path.join(working_path, 'CAPITOUL_Weather_Comparison.xlsx')
if os.path.exists(_compare_excel_file):
    os.remove(_compare_excel_file)
_compare_excel = pd.ExcelWriter(_compare_excel_file)

# read the measurements, Rural_Mondouzil_Hourly.csv
if os.path.exists(os.path.join(working_path, 'Rural_Mondouzil_Hourly.csv')):
    _measurements_hourly = pd.read_csv(os.path.join(working_path, 'Rural_Mondouzil_Hourly.csv'),
                                       sep=',', index_col=0, parse_dates=True, header=0)
else:
    _measurements_file = os.path.join(working_path, 'Rural_Mondouzil_Minute.csv')
    _measurements = pd.read_csv(_measurements_file, sep=',', index_col= 0, parse_dates=True)
    # to hourly, 00:00:00 to 00:59:59 averaged at 01:00:00,ffill
    _measurements_hourly = _measurements.resample('H').bfill()
    _measurements_hourly.index = pd.to_datetime(_measurements_hourly.index, format='%d/%m/%Y %H:%M:%S')
    # drop Feb 29
    mask = _measurements_hourly.index.is_leap_year & (_measurements_hourly.index.month == 2) \
           & (_measurements_hourly.index.day == 29)
    _measurements_hourly = _measurements_hourly[~mask]
    _measurements_hourly.to_csv(os.path.join(working_path, 'Rural_Mondouzil_Hourly.csv'))
# read the EPW file, save it to csv file
_epw_file = os.path.join(working_path, 'rural_weather_data_capEPW.csv')
_epw = pd.read_csv(_epw_file, sep=',', skiprows=18, index_col= 0, parse_dates=True, header = 0, encoding= 'cp1252')
# The current index is only date, we need to add time (col = 0,HH:MM, 1-24)
# The current col = 0 is string, substract number 1 for the second character
_epw.index = pd.to_datetime(_epw.index, format='%Y-%m-%d') + \
             pd.to_timedelta(_epw.iloc[:,0].str[:2].astype(int)-1, unit='h')
_epw.index = _measurements_hourly.index


sheet_df_drybulb = pd.DataFrame({'EPW': _epw['Dry Bulb Temperature {C}'],
                                 'Measurements': _measurements_hourly.iloc[:,2]})
sheet_df_drybulb.to_excel(_compare_excel, sheet_name='dry bulb temperature comparison')

sheet_df_pressure = pd.DataFrame({'EPW': _epw['Atmospheric Pressure {Pa}'],
                                    'Measurements': _measurements_hourly.iloc[:,3]* 100})
sheet_df_pressure.to_excel(_compare_excel, sheet_name='pressure comparison')
#plot sheet_df_pressure
sheet_df_relativehumidity = pd.DataFrame({'EPW': _epw['Relative Humidity {%}'],
                                            'Measurements': _measurements_hourly.iloc[:,4]})
sheet_df_relativehumidity.to_excel(_compare_excel, sheet_name='relative humidity comparison')
#plot sheet_df_relativehumidity
sheet_df_rain = pd.DataFrame({'EPW': _epw['Liquid Precipitation Depth {mm}'],
                                'Measurements': _measurements_hourly.iloc[:,5]})
sheet_df_rain.to_excel(_compare_excel, sheet_name='rain comparison')
sheet_df_winddirection = pd.DataFrame({'EPW': _epw['Wind Direction {deg}'],
                                        'Measurements': _measurements_hourly.iloc[:,6]})
sheet_df_winddirection.to_excel(_compare_excel, sheet_name='wind direction comparison')
#plot sheet_df_winddirection
sheet_df_windspeed = pd.DataFrame({'EPW': _epw['Wind Speed {m/s}'],
                                    'Measurements': _measurements_hourly.iloc[:,7]})
sheet_df_windspeed.to_excel(_compare_excel, sheet_name='wind speed comparison')
#plot sheet_df_windspeed
sheet_df_swr = pd.DataFrame({'Direct Normal Radiation {Wh/m2}': _epw['Direct Normal Radiation {Wh/m2}'],
                             'Diffuse Horizontal Radiation {Wh/m2}': _epw['Diffuse Horizontal Radiation {Wh/m2}'],
                             'Measurements: incoming short wave radiation: watts/m2': _measurements_hourly.iloc[:,8],
                             'Measurements: outgoing short wave radiation: watts/m2': _measurements_hourly.iloc[:,9],
                             'Measurements: net short wave radiation: watts/m2':
                                 _measurements_hourly.iloc[:,8] - _measurements_hourly.iloc[:,9]})
sheet_df_swr.to_excel(_compare_excel, sheet_name='short wave radiation comparison')

sheet_df_lwr = pd.DataFrame({'Measurements: incoming long wave radiation: watts/m2': _measurements_hourly.iloc[:,10],
                                'Measurements: outgoing long wave radiation: watts/m2': _measurements_hourly.iloc[:,11],
                                'Measurements: net long wave radiation: watts/m2':
                                 _measurements_hourly.iloc[:,10] - _measurements_hourly.iloc[:,11],
                                'Horizontal Infrared Radiation Intensity from Sky {Wh/m2}': _epw['Horizontal Infrared Radiation Intensity from Sky {Wh/m2}']})
sheet_df_lwr.to_excel(_compare_excel, sheet_name='long wave radiation comparison')




cvrmse_r2 = {}
# dry bulb temperature
cvrmse_r2['dry bulb temperature'] = cvrmse(sheet_df_drybulb['EPW'], sheet_df_drybulb['Measurements'])
# pressure
cvrmse_r2['pressure'] = cvrmse(sheet_df_pressure['EPW'], sheet_df_pressure['Measurements'])
# relative humidity
cvrmse_r2['relative humidity'] = cvrmse(sheet_df_relativehumidity['EPW'], sheet_df_relativehumidity['Measurements'])
cvrmse_r2['rain'] = cvrmse(sheet_df_rain['EPW'], sheet_df_rain['Measurements'])
#swr
cvrmse_r2['swr_Direct Normal Radiation'] = cvrmse(sheet_df_swr['Direct Normal Radiation {Wh/m2}'],
                                                  sheet_df_swr['Measurements: net short wave radiation: watts/m2'])
cvrmse_r2['swr_Diffuse Horizontal Radiation'] = cvrmse(sheet_df_swr['Diffuse Horizontal Radiation {Wh/m2}'],
                                                         sheet_df_swr['Measurements: outgoing short wave radiation: watts/m2'])
# add the cvrmse_r2 to one sheet
sheet_df_cvrmse_r2 = pd.DataFrame(cvrmse_r2, index=['cvrmse_r2'])
sheet_df_cvrmse_r2.to_excel(_compare_excel, sheet_name='cvrmse_r2')

# save the excel file
_compare_excel.save()

def plot_one_sheet(sheet_name, sheet_df):
    # sheet might have 2, 3 or 4 columns, use for loop to plot them
    for i in range(sheet_df.shape[1]):
        plt.plot(sheet_df.iloc[:,i], label=sheet_df.columns[i])
    plt.legend()
    plt.title(sheet_name)
    plt.show()

# plot_one_sheet('dry bulb temperature comparison', sheet_df_drybulb)
# plot_one_sheet('pressure comparison', sheet_df_pressure)
# plot_one_sheet('relative humidity comparison', sheet_df_relativehumidity)
# plot_one_sheet('rain comparison', sheet_df_rain)
# plot_one_sheet('wind direction comparison', sheet_df_winddirection)
# plot_one_sheet('wind speed comparison', sheet_df_windspeed)
# plot_one_sheet('short wave radiation comparison', sheet_df_swr)
# plot_one_sheet('long wave radiation comparison', sheet_df_lwr)
