import pandas as pd
def overriding_epw(epw_csv, df_measurement):
    '''
    1. original epw file has 8760 data records
    2. measurement has 8784 data records. So drop Feb 29th data
    3. For air temperature, overwrite the epw file with the measurement data
        a. For epw, the ;7th column is the dry bulb temperature
        b. For measurement, the 1st column is the dry bulb temperature
    '''
    # read text based epw file line by line
    with open(epw_csv, 'r') as f:
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
                hour = str(int(lines[i][3]) - 1)
                target_date = pd.to_datetime(year + '-' + month + '-' + day + ' ' + hour + ':00:00')
                measurements = df_measurement.loc[target_date]
                # self.staInfra = numpy.array([cd[i][12] for i in range(len(cd))],
                #                             dtype=float)  # horizontal Infrared Radiation Intensity [W m^-2]
                # self.staHor = numpy.array([cd[i][13] for i in range(len(cd))],
                #                           dtype=float)  # horizontal radiation [W m^-2]
                # self.staDir = numpy.array([cd[i][14] for i in range(len(cd))],
                #                           dtype=float)  # normal solar direct radiation [W m^-2]
                # self.staDif = numpy.array([cd[i][15] for i in range(len(cd))],
                #                           dtype=float)  # horizontal solar diffuse radiation [W m^-2]
                lines[i][13] = str(0)
                lines[i][14] = str(0)
                lines[i][15] = str(max(measurements[6] - measurements[7], 0))
                # wind_deg = measurements[4]
                # wind_speed = measurements[5]
                # lines[i][20] = str(wind_deg)
                # lines[i][21] = str(wind_speed)
                lines[i] = ','.join(lines[i])
    # write the lines to the epw file
    overwriten_epw = r'.\measurements\Mondouzil_tdb_td_rh_P_wind_diff_2004.epw'
    with open(overwriten_epw, 'w') as f:
        f.writelines(lines)

def main():
    # read the measurement data
    df_measurement = pd.read_csv(r'.\measurements\CAPITPOUL_Rural_Mondouzil_Hour.csv',
        index_col=0, parse_dates=True)
    epw_csv = r'.\measurements\Mondouzil_tdb_td_rh_P_wind_2004.epw'
    overriding_epw(epw_csv, df_measurement)
    return

if __name__ == '__main__':
    main()
