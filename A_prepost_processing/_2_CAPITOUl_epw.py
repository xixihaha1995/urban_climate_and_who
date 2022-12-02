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
    # hour_of_day +=  4 * (15 - longitude)
    # hour_of_day +=  equation_of_time(day_of_year) / 60
    # define delta as the solar declination (degrees)

    # define B as the hour angle (degrees)
    B = 15 * (hour_of_day - 12)
    # define omega as the solar altitude (degrees)
    delta = solar_declination(day_of_year)
    omega = math.degrees(math.asin(math.sin(math.radians(latitude))
                                   * math.sin(math.radians(delta)) +
                                   math.cos(math.radians(latitude))
                                   * math.cos(math.radians(delta)) * math.cos(math.radians(B))))
    return omega

def sun_zenith_angle(day_of_year, hour_of_day):
    global toulouse_latitude, toulouse_longitude
    toulouse_latitude, toulouse_longitude = 43.6043, 1.4437
    theta_z = 90 - solar_altitude(toulouse_latitude, toulouse_longitude, day_of_year, hour_of_day)
    #theta_z is in the range(0,90)
    return theta_z

def modifying_epw(epw_old, overwriten_epw):
    with open(epw_old, 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        # for the 7th column, overwrite with the measurement data
        if i > 7 and i < 8768:
            lines[i] = lines[i].split(',')
            year = lines[i][0]
            month = lines[i][1]
            day = lines[i][2]
            # epw is UTC-7, so add 7 hours
            hour = str(int(lines[i][3]) - 1)
            day_of_year = pd.Timestamp(year + '-' + month + '-' + day).dayofyear
            theta_z = sun_zenith_angle(day_of_year, int(hour))
            DNI = float(lines[i][14])
            DNI = max(DNI, 0)
            DHI = float(lines[i][15])
            DHI = max(DHI, 0)
            GHI = DNI * math.cos(math.radians(theta_z)) + DHI
            GHI = max(GHI, 0)
            old_GHI = float(lines[i][13])
            print(f'old GHI: {old_GHI}, new GHI: {GHI}, theta_z: {theta_z}')
            lines[i][13] = str(GHI)
            lines[i][14] = str(DNI)
            lines[i][15] = str(DHI)
            lines[i] = ','.join(lines[i])
        # write the lines to the epw file
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
    experiment_folder = os.path.join(os.path.dirname(__file__), '..', '_1_ep_vcwg'
                                     ,'resources','epw')
    epw_Old = os.path.join(experiment_folder, 'Mondouzil_Bueno_2004.epw')
    overwriten_epw = os.path.join(experiment_folder, 'Mondouzil_Bueno_2004_Update.epw')
    modifying_epw(epw_Old, overwriten_epw)
    return
if __name__ == '__main__':
    main()
