import pandas as pd
def overriding_epw(epw_MyDIY, epw_Bueno):
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

def main():
    # read the measurement data
    epw_MyDIY = r'.\measurements\Mondouzil_tdb_td_rh_P_2004.epw'
    epw_Bueno = r'.\measurements\rural_weather_data_cap.epw'
    overriding_epw(epw_MyDIY, epw_Bueno)
    return

if __name__ == '__main__':
    main()
