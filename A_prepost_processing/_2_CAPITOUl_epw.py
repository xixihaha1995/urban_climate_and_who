import math
import os
import sys

import pandas as pd
def mixing_two_EPWs(epw_MyDIY, epw_Bueno):
    '''
    1. original epw file has 8760 data records
    2. measurement has 8784 data records. So drop Feb 29th data
    3. For air temperature, overwrite the epw file with the measurement data
        a. For epw, the ;7th column is the dry bulb temperature
        b. For measurement, the 1st column is the dry bulb temperature
    '''
    # read text based epw file line by line
    with open(epw_MyDIY, 'r') as f:
        lines = f.readlines()
    with open(epw_Bueno, 'r') as f:
        lines_bueno = f.readlines()
    for i in range(len(lines)):
        # for the 7th column, overwrite with the measurement data
        if i > 7 and i < 8768:
            # self.staInfra = numpy.array([cd[i][12] for i in range(len(cd))],
            #                             dtype=float)  # horizontal Infrared Radiation Intensity [W m^-2]
            # self.staHor = numpy.array([cd[i][13] for i in range(len(cd))],
            #                           dtype=float)  # horizontal radiation [W m^-2]
            # self.staDir = numpy.array([cd[i][14] for i in range(len(cd))],
            #                           dtype=float)  # normal solar direct radiation [W m^-2]
            # self.staDif = numpy.array([cd[i][15] for i in range(len(cd))],
            #                           dtype=float)  # horizontal solar diffuse radiation [W m^-2]
            # lines[i][20] = str(wind_deg)
            # lines[i][21] = str(wind_speed)

            lines[i] = lines[i].split(',')
            lines_bueno[i] = lines_bueno[i].split(',')
            lines[i][14] = lines_bueno[i][14]
            lines[i][15] = lines_bueno[i][15]
            # lines[i][20] = lines_bueno[i][20]
            lines[i][21] = lines_bueno[i][21]
            lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'.\measurements\Mondouzil_Bueno_2004.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)

def equation_of_time(day_of_year):
    # return minutes
    B = 2 * math.pi * (day_of_year - 81) / 364
    return 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

def solar_declination(day_of_year):
    # define delta as the solar declination (degrees)
    delta = 23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365)
    return delta

def solar_altitude(latitude, longitude, day_of_year, hour_of_day):
    local_civil_time_fraction = hour_of_day  + 4 * (90 - longitude)
    # define delta as the solar declination (degrees)
    # define B as the hour angle (degrees)
    B = 15 * (local_civil_time_fraction + equation_of_time(day_of_year)/60 - 12)
    # define omega as the solar altitude (degrees)
    delta = solar_declination(day_of_year)
    omega = math.asin(math.sin(latitude) * math.sin(delta) + math.cos(latitude)
                      * math.cos(delta) * math.cos(B))
    return math.degrees(omega)

def sun_zenith_angle(day_of_year, hour_of_day):
    global toulouse_latitude, toulouse_longitude
    toulouse_latitude, toulouse_longitude = 43.6043, 1.4437
    theta_z = 90 - solar_altitude(toulouse_latitude, toulouse_longitude, day_of_year, hour_of_day)
def modifying_epw(epw_old):
    with open(epw_old, 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        # for the 7th column, overwrite with the measurement data
        if i > 7 and i < 8768:
            # self.staInfra = numpy.array([cd[i][12] for i in range(len(cd))],
            #                             dtype=float)  # horizontal Infrared Radiation Intensity [W m^-2]
            # self.staHor = numpy.array([cd[i][13] for i in range(len(cd))],
            #                           dtype=float)  # horizontal radiation [W m^-2]
            # self.staDir = numpy.array([cd[i][14] for i in range(len(cd))],
            #                           dtype=float)  # normal solar direct radiation [W m^-2]
            # self.staDif = numpy.array([cd[i][15] for i in range(len(cd))],
            #                           dtype=float)  # horizontal solar diffuse radiation [W m^-2]
            # lines[i][20] = str(wind_deg)
            # lines[i][21] = str(wind_speed)

            lines[i] = lines[i].split(',')
            lines[i][14] = lines_bueno[i][14]
            lines[i][15] = lines_bueno[i][15]
            lines[i] = ','.join(lines[i])
        # write the lines to the epw file
    overwriten_epw = r'.\measurements\Mondouzil_Bueno_2004_Update.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)
def measurements_to_epw(epw_Template, df_measurement):
    '''
    dry bulb temperature:
    relative humidity:
    atmospheric pressure:
    wind direction:
    wind speed:
    dew point:
    Direct Normal Irradiance: net short-wave radiation
    Diffuse Horizontal Irradiance: outgoing short-wave radiation
    '''
    # read text based epw file line by line
    with open(epw_Template, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            # for the 7th column, overwrite with the measurement data
            if i > 7 and i < 8768:
                # for the 7th column, air temperature, overwrite with the measurement data, 0
                # for the 9th column, relative humidity, overwrite with the measurement data, 2
                # calculate humidity_ratio_c(state, db in C (0), rh in fraction (2), p is hPa to Pa)
                # calculate dew_point(state, humidity_ratio, p in Pa (1))
                # for the 8th column, dew point temperature, overwrite
                lines[i] = lines[i].split(',')
                year = '2004'
                month = lines[i][1]
                day = lines[i][2]
                # epw is UTC-7, so add 7 hours
                hour = str(int(lines[i][3]) - 1)
                target_date = pd.to_datetime(year + '-' + month + '-' + day + ' ' + hour + ':00:00')
                measurements = df_measurement.loc[target_date]
                dry_bulb_c = measurements[0]
                press_pa = measurements[1] * 100
                relative_humidity_percentage = measurements[2]

                humidity_ratio = psychrometric.humidity_ratio_c(state,
                    dry_bulb_c,relative_humidity_percentage / 100, press_pa)
                dew_point = psychrometric.dew_point(state, humidity_ratio, press_pa)
                lines[i][0] = year
                lines[i][6] = str(dry_bulb_c)
                lines[i][7] = str(dew_point)
                lines[i][8] = str(relative_humidity_percentage)
                lines[i][9] = str(press_pa)
                lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'..\_4_measurements\CAPITOUL\To_GenerateEPW\Mondouzil_tdb_td_rh_P_2004.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)
    return overwriten_epw
def init_ep_api():
    global psychrometric, state
    sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
    from pyenergyplus.api import EnergyPlusAPI
    ep_api = EnergyPlusAPI()
    state = ep_api.state_manager.new_state()
    psychrometric = ep_api.functional.psychrometrics(state)

def main():
    # read the measurement data
    init_ep_api()
    experiment_folder = os.path.join('_measurements', 'CAPITOUL')
    measurements_Mondouzil = os.path.join(experiment_folder, 'Rural_Mondouzil_Minute.csv')
    df_measurement = pd.read_csv(measurements_Mondouzil, index_col=0, parse_dates=True, header=0)
    df_measurement_ffill = df_measurement.resample('H').ffill()
    # fill the first row with the second row
    df_measurement_ffill.iloc[0] = df_measurement_ffill.iloc[1]

    epw_MyDIY = 'Mondouzil_tdb_td_rh_P_2004.epw'
    epw_Bueno = 'rural_weather_data_cap.epw'

    epw_Template_Bordeaxu = os.path.join(experiment_folder, 'overriding_FRA_Bordeaux.075100_IWEC.epw')
    # measurements_to_epw(epw_Template_Bordeaxu, measurements_Mondouzil)
    return

experiment_folder = os.path.join('_measurements', 'CAPITOUL')
measurements_Mondouzil = os.path.join(experiment_folder, 'Rural_Mondouzil_Minute.csv')
df_measurement = pd.read_csv(measurements_Mondouzil, index_col=0, parse_dates=True, header=0)
df_measurement_ffill = df_measurement.resample('H').ffill()
df_measurement_bfill = df_measurement.resample('H').bfill()
df_measurement_mean = df_measurement.resample('H').mean()
# fill the first row with the second row
df_measurement_ffill.iloc[0] = df_measurement_ffill.iloc[1]

# if __name__ == '__main__':
#     # main()
#     experiment_folder = os.path.join('_measurements', 'CAPITOUL')
#     measurements_Mondouzil = os.path.join(experiment_folder, 'Rural_Mondouzil_Minute.csv')
#     df_measurement = pd.read_csv(measurements_Mondouzil, index_col=0, parse_dates=True, header=0)
#     df_measurement_ffill = df_measurement.resample('H').ffill()
#     # fill the first row with the second row
#     df_measurement_ffill.iloc[0] = df_measurement_ffill.iloc[1]
