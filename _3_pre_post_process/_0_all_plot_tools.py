#RMSE function
import copy

import numpy as np, pandas as pd, matplotlib.pyplot as plt, os
def RMSE(y_true, y_pred):
    return np.sqrt(np.mean(np.square(y_pred - y_true)))

def ep_time_to_pandas_time(df, start_time):
    '''
    for 0th column, find all the observation with 24:00:00, and change it to 00:00:00, and add one day
    0th column is date related data, however, it has rare format, so it is not easy to convert to pandas time

    extract month, day, hour, minute, second from 0th column
    0th column current format is one string, " MM/DD  HH:MM:SS"
    '''
    index_24 = df[df.iloc[:, 0].str.contains('24:00:00')].index
    # replace 24:00:00 with 00:00:00
    df.iloc[index_24, 0] = df.iloc[index_24, 0].str.replace('24:00:00', '00:00:00')
    # extract month from 0th column
    df['month'] = df.iloc[:, 0].str.extract('(\d{2})/').astype(int)
    # extract day from 0th column
    df['day'] = df.iloc[:, 0].str.extract('/(\d{2})').astype(int)
    # extract hour from 0th column
    df['hour'] = df.iloc[:, 0].str.extract('(\d{2}):').astype(int)
    # extract minute from 0th column
    df['minute'] = df.iloc[:, 0].str.extract(':(\d{2}):').astype(int)
    # extract second from 0th column, second is the last 2 index of 0th column
    df['second'] = df.iloc[:, 0].str[-2:].astype(int)
    # we dont have year, so we use the first 4 char of start_time
    df['year'] = start_time[:4]
    # convert to pandas time
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
    # add one day to index_24
    df.loc[index_24, 'date'] = df.loc[index_24, 'date'] + pd.Timedelta(days=1)
    # update dataframe index
    df.index = df['date']
    # drop 0th column, date related data
    # drop month, day, hour, minute, second, date
    df.drop(['month', 'day', 'hour', 'minute', 'second', 'date','year','Date/Time'], axis=1, inplace=True)
    #  if date is earlier than start_time, increase one year
    df.index = df.index + pd.Timedelta(days=365) * (df.index < start_time)
    return df

def clean_epw(df, start_time):
    '''
    df 0th column is year,
    df 1st column is month,
    df 2nd column is day,
    df 3rd column is hour, range from 1 to 24, make it to 0 to 23
    df 4th column is minute, always 60
    '''
    # convert hour to 0 to 23
    df.iloc[:, 3] = df.iloc[:, 3] - 1
    # convert columns year, month, day, hour, all of them is numpy.int64
    # convert to pandas time
    # combine the 4 columns to one string column, in format of 'year-month-day hour:00:00'
    df['string_combined'] = df.iloc[:, 0].astype(str) + '-' + df.iloc[:, 1].astype(str) + '-' \
                            + df.iloc[:, 2].astype(str) + ' ' + df.iloc[:, 3].astype(str) + ':00:00'
    # convert to pandas time
    df['date'] = pd.to_datetime(df['string_combined'])
    # update dataframe index
    df.index = df['date']
    df.drop(['date', 'string_combined'], axis=1, inplace=True)
    #  overwrite the index year as start_time year
    start_time_year = start_time[:4]
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S').str.replace('2012', start_time_year)
    return df
def sequence_time_to_pandas_time(dataframe, delta_t,start_time):
    date = pd.date_range(start_time, periods=len(dataframe), freq='{}S'.format(delta_t))
    date = pd.Series(date)
    # update dataframe index
    dataframe.index = date
    return dataframe

def save_CAPITOUL_debug(measure_tdb_c_2m_6m_hourly,measure_tdb_c_20m_5min,
                        only_ep_degC_2_6_hourly,only_ep_degC_20_5min,
                        only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                        bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C,
                        debug_processed_save_folder,
                        debug_only_ep, debug_only_vcwg,debug_bypass_ver1p1):
    writer = pd.ExcelWriter(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                            engine='xlsxwriter')
    #save 2m-direct
    #measure_tdb_c_2m_6m_hourly Series (719,1) to (719,)
    measure_tdb_c_2m_6m_hourly_1d = measure_tdb_c_2m_6m_hourly.squeeze()
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       f'Only EP': only_ep_degC_2_6_hourly.squeeze(),
                       'Only VCWG': only_vcwg_direct_lst_C[0],
                       'Bypass Ver1.1': bypass_direct_lst_C[0]})
    df.to_excel(writer, sheet_name='2m Direct')
    #save 2m-real_p0
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       'Only VCWG': only_vcwg_real_p0_lst_C[0],
                       'Bypass Ver1.1': bypass_real_p0_lst_C[0]})
    df.to_excel(writer, sheet_name='2m Real P0')
    #save 2m-real_epw
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       'Only VCWG': only_vcwg_real_epw_lst_C[0],
                       'Bypass Ver1.1': bypass_real_epw_lst_C[0]})
    df.to_excel(writer, sheet_name='2m Real EPW')
    #save 6m-direct
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       'Only EP': only_ep_degC_2_6_hourly.squeeze(),
                       'Only VCWG': only_vcwg_direct_lst_C[1],
                       'Bypass Ver1.1': bypass_direct_lst_C[1]})
    df.to_excel(writer, sheet_name='6m Direct')
    #save 6m-real_p0
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       'Only VCWG': only_vcwg_real_p0_lst_C[1],
                       'Bypass Ver1.1': bypass_real_p0_lst_C[1]})
    df.to_excel(writer, sheet_name='6m Real P0')
    #save 6m-real_epw
    df = pd.DataFrame({'Measurement': measure_tdb_c_2m_6m_hourly.squeeze(),
                       'Only VCWG': only_vcwg_real_epw_lst_C[1],
                       'Bypass Ver1.1': bypass_real_epw_lst_C[1]})
    df.to_excel(writer, sheet_name='6m Real EPW')
    #save 20m-direct
    df = pd.DataFrame({'Measurement': measure_tdb_c_20m_5min.squeeze(),
                       'Only EP': only_ep_degC_20_5min.squeeze(),
                       'Only VCWG': only_vcwg_direct_lst_C[2],
                       'Bypass Ver1.1': bypass_direct_lst_C[2]})
    df.to_excel(writer, sheet_name='20m Direct')
    #save 20m-real_p0
    df = pd.DataFrame({'Measurement': measure_tdb_c_20m_5min.squeeze(),
                       'Only VCWG': only_vcwg_real_p0_lst_C[2],
                       'Bypass Ver1.1': bypass_real_p0_lst_C[2]})
    df.to_excel(writer, sheet_name='20m Real P0')
    #save 20m-real_epw
    df = pd.DataFrame({'Measurement': measure_tdb_c_20m_5min.squeeze(),
                       'Only VCWG': only_vcwg_real_epw_lst_C[2],
                       'Bypass Ver1.1': bypass_real_epw_lst_C[2]})
    df.to_excel(writer, sheet_name='20m Real EPW')
    # save wall Sun
    df = pd.DataFrame({'Only EP(southFacingWall)': debug_only_ep.iloc[:, 0] - 273.15,
                       'Only VCWG (wallSun)': debug_only_vcwg.iloc[:, 0] - 273.15,
                       'Bypass Ver1.1 (wallSun)': debug_bypass_ver1p1.iloc[:, 0] - 273.15})
    df.to_excel(writer, sheet_name='wallSun_southFacingWall')
    # save wall shade
    df = pd.DataFrame({'Only EP (northFacingWall)': debug_only_ep.iloc[:, 1] - 273.15,
                       'Only VCWG (wallShade)': debug_only_vcwg.iloc[:, 1] - 273.15,
                       'Bypass Ver1.1 (wallShade)': debug_bypass_ver1p1.iloc[:, 1] - 273.15})
    df.to_excel(writer, sheet_name='wallShade_northFacingWall')
    # write the fourth sheet
    df = pd.DataFrame({'Only EP(roof)': debug_only_ep.iloc[:, 2] - 273.15,
                       'Only VCWG (roof)': debug_only_vcwg.iloc[:, 2] - 273.15,
                       'Bypass Ver1.1 (roof)': debug_bypass_ver1p1.iloc[:, 3] - 273.15})
    df.to_excel(writer, sheet_name='roof')
    # write the fifth sheet
    df = pd.DataFrame({'Only EP{which_ep} (sensHVAC)': debug_only_ep.iloc[:, 3],
                       'Only VCWG (sensWaste)': debug_only_vcwg.iloc[:, 3],
                       'Bypass Ver1.1 (sensHVAC)': debug_bypass_ver1p1.iloc[:, 4]})
    df.to_excel(writer, sheet_name='sensWaste_sensHVAC')

    writer.save()


def organize_CAPITOUL_cvrmse(measure_tdb_c_2m_6m_hourly,measure_tdb_c_20m_5min,
                             only_ep_degC_2_6_hourly,only_ep_degC_20_5min,
                             only_vcwg_direct_lst_C,only_vcwg_real_p0_lst_C, only_vcwg_real_epw_lst_C,
                             bypass_direct_lst_C, bypass_real_p0_lst_C, bypass_real_epw_lst_C):
    cvrmse_3d = np.zeros((3, 3, 3))
    # since there is no real_p0, real_epw for ep, so set them to nan
    cvrmse_3d[:, 0, 1:] = np.nan

    cvrmse_2m_ep_direct = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_ep_degC_2_6_hourly, 'only_ep_2m_6m')[
        2]
    cvrmse_6m_ep_direct = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_ep_degC_2_6_hourly, 'only_ep_2m_6m')[
        2]
    cvrmse_20m_ep_direct = bias_rmse_r2(measure_tdb_c_20m_5min, only_ep_degC_20_5min, 'only_ep_20m')[2]
    cvrmse_2m_vcwg_direct = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_direct_lst_C[0], 'only_vcwg_2m')[2]
    cvrmse_6m_vcwg_direct = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_direct_lst_C[1], 'only_vcwg_6m')[2]
    cvrmse_20m_vcwg_direct = bias_rmse_r2(measure_tdb_c_20m_5min, only_vcwg_direct_lst_C[2], 'only_vcwg_20m')[
        2]
    cvrmse_2m_vcwg_real_p0 = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_real_p0_lst_C[0], 'only_vcwg_2m')[2]
    cvrmse_6m_vcwg_real_p0 = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_real_p0_lst_C[1], 'only_vcwg_6m')[2]
    cvrmse_20m_vcwg_real_p0 = \
    bias_rmse_r2(measure_tdb_c_20m_5min, only_vcwg_real_p0_lst_C[2], 'only_vcwg_20m')[2]
    cvrmse_2m_vcwg_real_epw = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_real_epw_lst_C[0], 'only_vcwg_2m')[2]
    cvrmse_6m_vcwg_real_epw = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, only_vcwg_real_epw_lst_C[1], 'only_vcwg_6m')[2]
    cvrmse_20m_vcwg_real_epw = \
    bias_rmse_r2(measure_tdb_c_20m_5min, only_vcwg_real_epw_lst_C[2], 'only_vcwg_20m')[2]
    cvrmse_2m_bypass_direct = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_direct_lst_C[0], 'bypass_2m')[2]
    cvrmse_6m_bypass_direct = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_direct_lst_C[1], 'bypass_6m')[2]
    cvrmse_20m_bypass_direct = bias_rmse_r2(measure_tdb_c_20m_5min, bypass_direct_lst_C[2], 'bypass_20m')[2]
    cvrmse_2m_bypass_real_p0 = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_real_p0_lst_C[0], 'bypass_2m')[
        2]
    cvrmse_6m_bypass_real_p0 = bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_real_p0_lst_C[1], 'bypass_6m')[
        2]
    cvrmse_20m_bypass_real_p0 = bias_rmse_r2(measure_tdb_c_20m_5min, bypass_real_p0_lst_C[2], 'bypass_20m')[2]
    cvrmse_2m_bypass_real_epw = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_real_epw_lst_C[0], 'bypass_2m')[2]
    cvrmse_6m_bypass_real_epw = \
    bias_rmse_r2(measure_tdb_c_2m_6m_hourly, bypass_real_epw_lst_C[1], 'bypass_6m')[2]
    cvrmse_20m_bypass_real_epw = bias_rmse_r2(measure_tdb_c_20m_5min, bypass_real_epw_lst_C[2], 'bypass_20m')[
        2]

    cvrmse_3d[0, 0, 0] = cvrmse_2m_ep_direct
    cvrmse_3d[1, 0, 0] = cvrmse_6m_ep_direct
    cvrmse_3d[2, 0, 0] = cvrmse_20m_ep_direct
    cvrmse_3d[0, 1, 0] = cvrmse_2m_vcwg_direct
    cvrmse_3d[1, 1, 0] = cvrmse_6m_vcwg_direct
    cvrmse_3d[2, 1, 0] = cvrmse_20m_vcwg_direct
    cvrmse_3d[0, 1, 1] = cvrmse_2m_vcwg_real_p0
    cvrmse_3d[1, 1, 1] = cvrmse_6m_vcwg_real_p0
    cvrmse_3d[2, 1, 1] = cvrmse_20m_vcwg_real_p0
    cvrmse_3d[0, 1, 2] = cvrmse_2m_vcwg_real_epw
    cvrmse_3d[1, 1, 2] = cvrmse_6m_vcwg_real_epw
    cvrmse_3d[2, 1, 2] = cvrmse_20m_vcwg_real_epw
    cvrmse_3d[0, 2, 0] = cvrmse_2m_bypass_direct
    cvrmse_3d[1, 2, 0] = cvrmse_6m_bypass_direct
    cvrmse_3d[2, 2, 0] = cvrmse_20m_bypass_direct
    cvrmse_3d[0, 2, 1] = cvrmse_2m_bypass_real_p0
    cvrmse_3d[1, 2, 1] = cvrmse_6m_bypass_real_p0
    cvrmse_3d[2, 2, 1] = cvrmse_20m_bypass_real_p0
    cvrmse_3d[0, 2, 2] = cvrmse_2m_bypass_real_epw
    cvrmse_3d[1, 2, 2] = cvrmse_6m_bypass_real_epw
    cvrmse_3d[2, 2, 2] = cvrmse_20m_bypass_real_epw
    return cvrmse_3d
def bias_rmse_r2(df1, df2, df2_name):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    # based on df1 time index, find the corresponding df2
    df2 = df2.loc[df1.index]
    df1 = df1.values
    df2 = df2.values
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    cvrmse = rmse / np.mean(abs(df1)) * 100
    r2 = 1 - np.sum(np.square(bias)) / np.sum(np.square(df1 - np.mean(df1)))
    mean_bias_percent = np.mean(abs(bias)) / np.mean(df1) * 100

    # bias_mean = np.mean(bias)
    # df2 name
    # return number with 2 decimal places
    return df2_name, round(mean_bias_percent,2), round(cvrmse,2), round(r2,2)

def calculate_cvrmse(df1, df2):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    cvrmse = rmse / np.mean(df1) * 100
    return round(cvrmse, 2)


def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows= skiprows, header= header, index_col=index_col, sep= '[ ^]+', engine='python')
    # set index to first column
    # df.set_index(df.iloc[:,0], inplace=True)
    return df

def clean_bubble_iop(df, start_time='2018-01-01 00:00:00', end_time='2018-12-31 23:59:59',
                     to_hourly = True):
    # current index format is DD.MM.YYYY
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
    # index format is YYYY-MM-DD HH:MM:SS
    # replace HH:MM with first 5 char of 0th column, convert to datetime
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d') + ' ' + df.iloc[:,0].str[:5])
    # drop the 0th column, according to the index instead of column name
    df.drop(df.columns[0], axis=1, inplace=True)
    # except the last column, all columns are number with comma, convert them to number
    df.iloc[:, :-1] = df.iloc[:, :-1].apply(lambda x: x.str.replace(',', '')).astype(float)
    df = df[start_time:end_time]
    # convert 10 min interval to 1 hour interval
    if to_hourly:
        df = time_interval_convertion(df, original_time_interval_min=10, start_time=start_time)
    return df

def remove_dup_BUBBLE_Ue2(urban_all_sites_10min_clean, ue2_heights_dup, ue2_heights):
    urban_all_sites_10min_clean[str(ue2_heights_dup[0]) + 'm'] = \
        (urban_all_sites_10min_clean.iloc[:, 0] + urban_all_sites_10min_clean.iloc[:, 2]) / 2
    urban_all_sites_10min_clean[str(ue2_heights_dup[1]) + 'm'] = \
        (urban_all_sites_10min_clean.iloc[:, 1] + urban_all_sites_10min_clean.iloc[:, 3]) / 2
    # drop the first 4 columns
    urban_all_sites_10min_clean = urban_all_sites_10min_clean.iloc[:, 4:]
    # rename the columns
    urban_all_sites_10min_clean.columns = [str(i) + 'm' for i in ue2_heights]
    return urban_all_sites_10min_clean

def multiple_days_hour_data_to_one_day_hour_data(df):
    '''
    columns are 48 hours based sequence data,
    average them into one day 24 hours data
    '''
    # new df with 24 hours data
    columns = np.arange(24)
    df_new = pd.DataFrame(columns=columns)
    # average 48 hours data into 24 hours data
    for i in range(0,24):
        df_new[i] = df.iloc[:,i::24].mean(axis=1)
    return df_new

def certain_height_one_day(df, height):
    '''
    df index is different heights, resolution is 0.5 m
    '''
    # find the closest height
    height_index = np.argmin(np.abs(df.index - height))
    return df.iloc[height_index,:]

def average_temperature_below_height(df, height):
    '''
    df index is different heights, resolution is 0.5 m
    '''
    # find the closest height
    height_index = np.argmin(np.abs(df.index - height))
    return df.iloc[:height_index,:].mean(axis=0)

def filter_df_with_new_heights(df, heights_arr):
    # new df with heights as index
    df_new = pd.DataFrame(index=heights_arr, columns=df.columns)
    for heigh in heights_arr:
        df_new.loc[heigh] = certain_height_one_day(df, heigh)
    return df_new

def plot_24_hours_comparison_for_multiple_heights(df1, df2, height, all_rmse,case_name):
    '''
    In total, there are len(height) figures
    df index is
    '''
    fig, ax = plt.subplots(figsize=(10,5), nrows = 2, ncols = len(height) // 2, sharex=True, sharey=True)
    for i in range(len(height)):
        ax[i%2,i//2].plot(df1.columns, df1.iloc[i], label='VCWG')
        ax[i%2,i//2].plot(df2.columns,df2.iloc[i], label='Bypass')
        ax[i%2,i//2].legend()
        ax[i%2,i//2].set_title(f'Height:{height[i]}m, RMSE:{RMSE(df1.iloc[i],df2.iloc[i]):.2f}')
        # set y limit
        ax[i%2,i//2].set_ylim(270,320)

    # set x name, y name, and title
    ax[1,0].set_xlabel('Hours')
    ax[0,0].set_ylabel('Temperature (K)')
    fig.suptitle(
        f'RMSE(VCWGv2.0.0 - {case_name}):{np.mean(all_rmse):.2f}')
    plt.show()

def data_cleaning(df):
    '''
    string to number
    Nan to 0
    '''
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.fillna(0)
    return df

def _deleted_time_interval_convertion(df, original_time_interval_min = 30, need_date = False,
                             start_time = '2018-01-01 00:00:00'):
    '''
    TODO: time conversion should be based on the actual timestamps
    Original data is 30 mins interval,
    Convert it to hourly data
    Original data has [index, sensible]
    Replace sensible with hourly average
    '''
    original_time_num = 60 // original_time_interval_min
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), original_time_num):
        df_new.loc[df.index[i]] = df.iloc[i:i+original_time_num:,].mean()
        # df_new.iloc[i,0] = df.iloc[i:i+2,0].mean()
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:00:00)
    if not need_date:
        df_new.index = df_new.index.floor('H')
    else:
        df_new = add_date_index(df_new, start_time, 3600)
    return df_new
def time_interval_converstion_actual_timestamp(df):
    '''
    The df entries has actual measurement timestamps.
    Based on the target_time_interval_min, average associated entries.
    '''
    # average the entries in the same hour
    df_new = copy.deepcopy(df)
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:00:00)
    df_new.index = df_new.index.floor('H')
    # average the entries in the same hour
    df_new = df_new.groupby(df_new.index).mean()
    return df_new

def _deleted_5min_to_10min(df):
    '''
    TODO: time conversion should be based on the actual timestamps
    Original data is 5 mins interval,
    Convert it to 10 mins interval
    Original data has [index, sensible]
    Replace sensible with 10 mins average
    '''
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), 2):
        df_new.loc[df.index[i]] = df.iloc[i:i+2,].mean()
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:MM:00)
    return df_new

def _deleted_xmin_to_ymin(df, original_time_interval_min = 30,target_time_interval_min = 60):
    #TODO: time conversion should be based on the actual timestamps
    merge_nums = target_time_interval_min // original_time_interval_min
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), merge_nums):
        df_new.loc[df.index[i]] = df.iloc[i:i+merge_nums,].mean()
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:MM:00)
    return df_new

# plot the comparisons between Vancouver Sunset dataset versus simulated (VCWGv2.0.0, VCWG-Bypass)
def plot_comparison_measurement_simulated(df, txt_info):

    figure, ax = plt.subplots(figsize=(10,5))

    ax.plot(df.iloc[:,0], label='Measurement')
    ax.plot(df.iloc[:,1], label= df.columns[1])
    ax.plot(df.iloc[:,2], label= df.columns[2])
    ax.plot(df.iloc[:,3], label= df.columns[3])
    ax.plot(df.iloc[:,4], label= df.columns[4])
    ax.legend()
    # add  to the plot
    # add text below the plot, outside the plot
    # txt = f'Bias Mean(W m-2), RMSE(W m-2), R2(-)\n' \
    #       f'{df.columns[1]}:{txt_info[1]}\n' \
    #       f'{df.columns[2]}:{txt_info[2]}'
    # print(txt)
    # ax.text(0.5, 1, txt, transform=ax.transAxes, fontsize=6,
    #     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_title(txt_info[0][0])
    # set x name, y name, and title
    ax.set_xlabel(txt_info[0][1])
    ax.set_ylabel(txt_info[0][2])

    plt.show()

def general_time_series_comparision(df, txt_info, CVRMSE_display = True):
    # df has many columns, itearte to plot each column
    figure, ax = plt.subplots(figsize=(10, 5))
    for i in range(0, len(df.columns)):
        if 'Urban' in df.columns[i]:
            ax.plot(df.iloc[:,i], label= df.columns[i], color='black', linestyle='--')
        elif 'Rural' in df.columns[i]:
            ax.plot(df.iloc[:,i], label= df.columns[i], color='black', linestyle=':')
        else:
            ax.plot(df.iloc[:,i], label= df.columns[i])
    # make legend located at the best position
    ax.legend(loc='best')
    # from 1 iteraterat through all columns, make a txt for error info
    if CVRMSE_display:
        txt = 'Maximum Daily UHI effect: 5.2 K'
        txt +='\nVCWGv2.0.0 (Monthly) MeanBiasError: -0.53(K), RMSE: 0.56(K), R2: 0.98(-)'
        txt +='\nUWG Monthly MBE: -0.6(K), RMSE: 0.9(K)'
        txt += f'\nNMBE(%), CV-RMSE(%), R2(-)'

        for i in range(1, len(txt_info)):
            txt += f'\n{txt_info[i]}'
        print(txt)
        ax.text(0.05, 1, txt, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    # lim
    ax.set_ylim(10, 40)
    ax.set_title(txt_info[0][0])
    # set x name, y name, and title
    ax.set_xlabel(txt_info[0][1])
    ax.set_ylabel(txt_info[0][2])
    plt.show()

def add_date_index(df, start_date, time_interval_sec):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval_sec))
    date = pd.Series(date)
    # update dataframe index
    df.index = date
    return df

def merge_multiple_df(df_list, column_name):
    '''
    df_list is a list of dataframes
    '''
    df = pd.concat(df_list, axis=1)
    df.columns = column_name
    return df

def save_data_to_csv(saving_data, file_name,case_name, start_time, time_interval_sec, vcwg_ep_saving_path):
    data_arr = np.array(saving_data[file_name])
    df = pd.DataFrame(data_arr)
    if file_name == 'can_Averaged_temp_k_specHum_ratio_press_pa':
        df.columns = ['Temp_K', 'SpecHum_Ratio', 'Press_Pa']
    elif file_name == 'debugging_canyon':
    # 'debugging_canyon' includes wallSun, wallShade, floor, roof, sensWaste(W/per unit footprint area),
    # canTemp_ep, canTemp_vcwg
        df.columns = ['s_wall_Text_K', 'n_wall_Text_K', 'floor_K', 'roof_K', 'sensWaste_w_footprint_m2',
                      'canTemp_ep_K', 'canTemp_vcwg_K','overwriting_seconds','overwriten_seconds']
    else:
        df.columns = [f'(m) {file_name}_' + str(0.5 + i) for i in range(len(df.columns))]
    df = add_date_index(df, start_time, time_interval_sec)
    # save to excel, if non-exist, create one
    if not os.path.exists(vcwg_ep_saving_path):
        os.makedirs(vcwg_ep_saving_path)
    df.to_excel(os.path.join(vcwg_ep_saving_path, f'{case_name}_{file_name}.xlsx'))

def excel_to_direct_real_p0_real_epw(filename, results_folder, heights_profile,
                                     sensor_heights, target_interval,p0, compare_start_time,
                                     compare_end_time, epw_staPre_Pa_all):
    th_profie_5min = pd.read_excel(f'{results_folder}\\{filename}_TempProfile_K.xlsx',
                                                   sheet_name='Sheet1', header=0, index_col=0)
    pres_profile_5min = pd.read_excel(f'{results_folder}\\{filename}_PressProfile_Pa.xlsx',
                                                      sheet_name='Sheet1', header=0, index_col=0)
    th_profie_5min = th_profie_5min[compare_start_time:compare_end_time]
    pres_profile_5min = pres_profile_5min[compare_start_time:compare_end_time]
    # ue1_heights is sensor heights, heights_profile is the heights of predictions
    # find the mapped indices in heights_profile
    heights_profile = np.array(heights_profile)
    sensor_heights = np.array(sensor_heights)
    mapped_indices = [np.argmin(np.abs(heights_profile - i)) for i in sensor_heights]
    th_target_intverval_K_lst = [None for _ in range(len(mapped_indices))]
    pres_target_intverval_Pa_lst = [None for _ in range(len(mapped_indices))]
    real_p0_target_interval_K_lst = [None for _ in range(len(mapped_indices))]
    real_epw_target_interval_K_lst = [None for _ in range(len(mapped_indices))]
    for i in range(len(mapped_indices)):
        th_target_intverval_K_lst[i] = th_profie_5min.iloc[:, mapped_indices[i]].resample(f'{target_interval[i]}T').mean()
        pres_target_intverval_Pa_lst[i] = pres_profile_5min.iloc[:, mapped_indices[i]].resample(f'{target_interval[i]}T').mean()
        tmp_real_p0 = th_target_intverval_K_lst[i].values * \
                                           (pres_target_intverval_Pa_lst[i].values / p0) ** 0.286
        real_p0_target_interval_K_lst[i] = pd.Series(tmp_real_p0, index=th_target_intverval_K_lst[i].index)
        tmp_real_epw = potential_to_real(th_target_intverval_K_lst[i], pres_target_intverval_Pa_lst[i],
                                            epw_staPre_Pa_all)
        real_epw_target_interval_K_lst[i] = pd.Series(tmp_real_epw, index=th_target_intverval_K_lst[i].index)
    th_target_intverval_C_lst = [i - 273.15 for i in th_target_intverval_K_lst]
    real_p0_target_interval_C_lst = [i - 273.15 for i in real_p0_target_interval_K_lst]
    real_epw_target_interval_C_lst = [i - 273.15 for i in real_epw_target_interval_K_lst]
    return th_target_intverval_C_lst, real_p0_target_interval_C_lst, real_epw_target_interval_C_lst

def excel_to_potential_real_df(filename, results_folder, p0, heights_profile, ue1_heights,compare_start_time,
                               compare_end_time, epw_staPre_Pa_all = None, Sensor_Height_Bool = True):
    th_profie_5min = pd.read_excel(f'{results_folder}\\{filename}_TempProfile_K.xlsx',
                                                   sheet_name='Sheet1', header=0, index_col=0)
    # ue1_heights is sensor heights, heights_profile is the heights of predictions
    # find the mapped indices in heights_profile
    heights_profile = np.array(heights_profile)
    ue1_heights = np.array(ue1_heights)
    mapped_indices = [np.argmin(np.abs(heights_profile - i)) for i in ue1_heights]
    # sensor_idx = np.argmin(np.abs(np.array(heights_profile) - v200_sensor_height))
    if not Sensor_Height_Bool:
        th_sensor_5min = th_profie_5min
    else:
        th_sensor_5min = th_profie_5min.iloc[:, mapped_indices]
    th_sensor_5min_K_compare = th_sensor_5min[compare_start_time:compare_end_time]
    th_sensor_5min_K_compare_df = pd.DataFrame(th_sensor_5min_K_compare)
    th_sensor_10min_K_compare = _5min_to_10min(th_sensor_5min_K_compare_df)

    pres_profile_5min = pd.read_excel(f'{results_folder}\\{filename}_PressProfile_Pa.xlsx',
                                                      sheet_name='Sheet1', header=0, index_col=0)
    if not Sensor_Height_Bool:
        pres_sensor_5min = pres_profile_5min
    else:
        pres_sensor_5min = pres_profile_5min.iloc[:, mapped_indices]
    pres_sensor_5min_pa_compare = pres_sensor_5min[compare_start_time:compare_end_time]
    pres_sensor_5min_pa_compare_df = pd.DataFrame(pres_sensor_5min_pa_compare)
    pres_sensor_10min_pa_compare = _5min_to_10min(
        pres_sensor_5min_pa_compare_df)
    # real temperature  = th_sensor_10min_c_compare * (pres_sensor_10min_pa_compare/p0)^0.286
    # both pres_sensor_10min_pa_compare and th_sensor_10min_c_compare have 6 columns
    # get real_sensor_10min_c_compare (element wise calculation)
    # epw_staPre_Pa_all can be None or a Series, when it is None, we use p0 based real temperature
    if epw_staPre_Pa_all is None:
        real_sensor_10min_K_compare_arr = th_sensor_10min_K_compare.values *\
                                      (pres_sensor_10min_pa_compare.values / p0) ** 0.286
    else:
        real_sensor_10min_K_compare_arr = potential_to_real(th_sensor_10min_K_compare, pres_sensor_10min_pa_compare,
                                                        epw_staPre_Pa_all)
    real_sensor_10min_K_compare = pd.DataFrame(real_sensor_10min_K_compare_arr,
                                                  index=th_sensor_10min_K_compare.index,
                                                    columns=th_sensor_10min_K_compare.columns)
    th_sensor_10min_c_compare = th_sensor_10min_K_compare - 273.15
    real_sensor_10min_c_compare = real_sensor_10min_K_compare - 273.15
    return th_sensor_10min_c_compare, real_sensor_10min_c_compare

def potential_to_real(potentialProf_K, presProf_pa, epw_staPre_Pa_all):
    '''
    Both potentialProf_K and presProf_pa are 10 mins timestep from '2002-06-10 01:00:00' to '2002-07-09 22:00:00'
    rural_1p5_hour_pa is hourly timestep from '2002-01-01 00:00:00' to '2002-12-31 23:00:00'
    realProf_K = potentialProf_K * (presProf_pa / p0) ** 0.286
    Iterate through each row of potentialProf_K and presProf_pa, and find the corresponding pressure in rural_1p5_hour_pa
    To get the realProf_K
    '''
    realProf_K = potentialProf_K.copy()
    # epw_staPre_Pa_all is for the years before 2000, presProf_pa is for the year 2004
    # so we only need to find the corresponding MM-DD HH:MM:SS, and ignore the year
    # epw_staPre_Pa_all.index is formatted as 'YYYY-MM-DD HH:MM:SS', so we need to extract the MM-DD HH:MM:SS
    # from epw_staPre_Pa_all.index
    epw_staPre_Pa_all.index = pd.to_datetime(epw_staPre_Pa_all.index)
    epw_staPre_Pa_all.index = epw_staPre_Pa_all.index.strftime('%m-%d %H:%M:%S')
    for i in range(len(potentialProf_K)):
        # find the corresponding pressures
        # find the corresponding time in rural_1p5_hour_pa
        time = potentialProf_K.index[i]
        # find the corresponding pressures
        pres = presProf_pa.iloc[i]
        # find the corresponding pressure in rural_1p5_hour_pa
        # time is formatted as 'YYYY-MM-DD HH:MM:SS'
        # floor the time to the nearest hour
        time_hour = time.replace(minute=0, second=0)
        #from epw_staPre_Pa_all find the corresponding pressure according to time_hour (hourly based comparison)
        # find the corresponding pressure
        corr_p0 = epw_staPre_Pa_all.loc[time_hour.strftime('%m-%d %H:%M:%S')]
        #pres.shape(6,),potentialProf_K.iloc[i, :].shape(6,), corr_p0 is one number
        # based on element wise calculation, calculate realProf_K.iloc[i, :]
        # real = potential * (pres / p0) ** 0.286
        realProf_K.iloc[i] = potentialProf_K.iloc[i] * (pres / corr_p0) ** 0.286
    return realProf_K

def stacked_comparison_plot(merged_df, sensor_heights):
    # merged_df has 5 *  len(sensor_heights) + 1 columns
    # sensor_heights is a list of sensor heights
    # the first column is rural measurement
    # following the first len(sensor_heights) columns are urban measurements
    # following the second len(sensor_heights) columns are original predictions
    # following the third len(sensor_heights) columns are ver0 predictions
    # following the fourth len(sensor_heights) columns are ver1 predictions
    # following the fifth len(sensor_heights) columns are ver2 predictions

    # In total, there will be len(sensor_heights) plots
    # each plot has 5 lines
    # the first line is the measurements data, with linestyle='--'

    fig, ax = plt.subplots(len(sensor_heights), 1, figsize=(10, 10))
    for i in range(len(sensor_heights)):
        ax[i].plot(merged_df.iloc[:, 0], linestyle='-.', label='Rural Measurement')
        ax[i].plot(merged_df.iloc[:, 1+i], linestyle='--', label='Urban Measurement')
        ax[i].plot(merged_df.iloc[:, 1+len(sensor_heights)+i], label='Original Prediction')
        ax[i].plot(merged_df.iloc[:, 1+2*len(sensor_heights)+i], label='Ver0 Prediction')
        ax[i].plot(merged_df.iloc[:, 1+3*len(sensor_heights)+i], label='Ver1 Prediction')
        ax[i].plot(merged_df.iloc[:, 1+4*len(sensor_heights)+i], label='Ver2 Prediction')
        ax[i].set_ylabel(f'Height {sensor_heights[i]} m')
        ax[i].legend()
    ax[-1].set_xlabel('Time')
    # set the overall title
    fig.suptitle('Comparison of Potential Temperature Profiles')
    plt.show()

def which_height_match_urban_sensor(df_urban_sensor_measurement, df_prediction_50m):
    '''
    sensor height is at 2.6m
    prediction heights are from 0.5m to 49.5 m
    The following candidates might be a good match to the sensor measurements
    1. All predictions below 15m, such as 0.5m, 1.5m, 2.5m, 3.5m, etc.
    2. All averaged predictions below 15m, such as 0.5m - 1.5m, 0.5m - 2.5m, 0.5m - 3.5m, etc.
    '''
    cvrmse_at_heights=[]
    for i in range(0, 15, 1):
        cvrmse_at_heights.append(bias_rmse_r2(df_urban_sensor_measurement,
                                              df_prediction_50m.iloc[:, i], str(i)+'m CVRMSE')[2])

    cvrmse_below_heights=[]
    for i in range(0, 15, 1):
        cvrmse_below_heights.append(bias_rmse_r2(df_urban_sensor_measurement,
                                                 df_prediction_50m.iloc[:, :i+1].mean(axis=1), str(i)+'m CVRMSE')[2])

def why_bypass_overestimated(debug_processed_save_folder,
                             urban_selected_10min_c, original_real_selected_10min_c,
                             bypass_real_selected_10min_c_ver1p1,
                             debug_only_ep, debug_only_vcwg,debug_bypass_ver1p1,which_ep = '(DOE-REF)',
                             mean_bld_temp = False):
    #There are 5 figures
    #1. The first figure, canyonTemp comparison (urban_selected_10min_c, debug_only_ep_idx_3, original_real_selected_10min_c, bypass_real_selected_10min_c_ver1)
    #2. The second figure, wallSun/southFacingWall (debug_only_ep_idx_0, debug_only_vcwg_idx_0, debug_bypass_ver1_idx_0)
    #3. The third figure, wallShade/northFacingWall (debug_only_ep_idx_1, debug_only_vcwg_idx_1, debug_bypass_ver1_idx_1)
    #4. The fourth figure, roof (debug_only_ep_idx_2, debug_only_vcwg_idx_2, debug_bypass_ver1_idx_2)
    #5. The fifth figure, sensWaste/sensHVAC (debug_only_ep_idx_2, debug_only_vcwg_idx_3, debug_bypass_ver1_idx_4)

    # create in total 4 figures
    # overwrite cursor with the snapping cursor

    fig, ax = plt.subplots(5, 1, sharex=True)
    # the first figure
    if not mean_bld_temp:
        # 2.6m measurement
        ax[0].plot(urban_selected_10min_c, linestyle='-.', color = 'black', label='Urban Measurement')
        # 2.5m prediction
        ax[0].plot(original_real_selected_10min_c , linestyle='--', label='Only VCWG')
        # pretty much 1.5m rural
        ax[0].plot(debug_only_ep.iloc[:, 4] - 273.15 , label=f'Only EP{which_ep}')
        # 2.5m prediction
        # 2.5m prediction
        ax[0].plot(bypass_real_selected_10min_c_ver1p1 , label='Ver1.1 Prediction')
    else:
        # 2.6m measurement
        ax[0].plot(urban_selected_10min_c, linestyle='-.', color='black', label='Urban Measurement')
        # 14m mean prediction
        ax[0].plot(debug_only_vcwg.iloc[:, 4] - 273.15, linestyle='--', label='Only VCWG')
        # pretty much 1.5m rural
        ax[0].plot(debug_only_ep.iloc[:, 4] - 273.15, label=f'Only EP{which_ep}')
        # 14m mean prediction
        ax[0].plot(debug_bypass_ver1p1.iloc[:, 6] - 273.15, label='Ver1.1 Prediction')

    cvrmses = []
    if not mean_bld_temp:
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, original_real_selected_10min_c, 'Only VCWG'))
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, debug_only_ep.iloc[:, 4] - 273.15, f'Only EP{which_ep}'))
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, bypass_real_selected_10min_c_ver1p1, 'Ver1.1 Prediction'))
    else:
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, debug_only_vcwg.iloc[:, 4] - 273.15, 'Only VCWG'))
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, debug_only_ep.iloc[:, 4] - 273.15, f'Only EP{which_ep}'))
        cvrmses.append(bias_rmse_r2(urban_selected_10min_c, debug_bypass_ver1p1.iloc[:, 6] - 273.15, 'Ver1.1 Prediction'))
    txt = 'CVRMSE(%)\n'
    txt += f'Only VCWG: {cvrmses[0][2]:.2f}%\n'
    txt += f'Only EP{which_ep}: {cvrmses[1][2]:.2f}%\n'
    txt += f'Ver1.1 Prediction: {cvrmses[2][2]:.2f}%\n'
    print(txt)
    ax[0].set_ylabel('CanyonTemp (C)')
    # put legend outside the figure
    # ax[0].legend(bbox_to_anchor=(1.04, 1), loc='upper left', borderaxespad=0.)
    # the second figure
    ax[1].plot(debug_only_vcwg.iloc[:, 0] - 273.15, linestyle='--')
    ax[1].plot(debug_only_ep.iloc[:, 0] - 273.15 )
    ax[1].plot(debug_bypass_ver1p1.iloc[:, 0] - 273.15)
    ax[1].set_ylabel('sun/South Wall (C)')
    # ax[1].legend()
    # the third figure
    ax[2].plot(debug_only_vcwg.iloc[:, 1] - 273.15, linestyle='--')
    ax[2].plot(debug_only_ep.iloc[:, 1] - 273.15 )
    ax[2].plot(debug_bypass_ver1p1.iloc[:, 1] - 273.15)
    ax[2].set_ylabel('shade/North Wall (C)')
    # ax[2].legend()
    # the fourth figure
    ax[3].plot(debug_only_vcwg.iloc[:, 2] - 273.15, linestyle='--')
    ax[3].plot(debug_only_ep.iloc[:, 2] - 273.15 )
    ax[3].plot(debug_bypass_ver1p1.iloc[:, 3] - 273.15)
    ax[3].set_ylabel('Roof (C)')
    # ax[3].legend()
    # the fifth figure
    ax[4].plot(debug_only_vcwg.iloc[:, 3], linestyle='--')
    ax[4].plot(debug_only_ep.iloc[:, 3]  )
    ax[4].plot(debug_bypass_ver1p1.iloc[:, 4])
    ax[4].set_ylabel('sensWaste/sensHVAC (W/floorArea)')
    # ax[4].legend()
    # put legend outside the figure
    fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0.)
    #put text outside the figure
    plt.figtext(0.8, 0.7, txt, fontsize=8)
    fig.subplots_adjust(right=0.76)

    # add MouseCross
    plt.show()

    #create a new excel file
    writer = pd.ExcelWriter(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx', engine='xlsxwriter')
    #write the first sheet
    df = pd.DataFrame({'Urban Measurement': urban_selected_10min_c,
                          'Only VCWG': original_real_selected_10min_c,
                            f'Only EP{which_ep}': debug_only_ep.iloc[:, 4] - 273.15,
                            'Ver1.1 Prediction': bypass_real_selected_10min_c_ver1p1})
    df.to_excel(writer, sheet_name='CanyonTemp')
    #write the second sheet
    df = pd.DataFrame({'Only VCWG (wallSun)': debug_only_vcwg.iloc[:, 0] - 273.15,
                            f'Only EP{which_ep} (southFacingWall)': debug_only_ep.iloc[:, 0] - 273.15,
                            'Bypass Ver1.1 (wallSun)': debug_bypass_ver1p1.iloc[:, 0] - 273.15})
    df.to_excel(writer, sheet_name='wallSun_southFacingWall')
    #write the third sheet
    df = pd.DataFrame({'Only VCWG (wallShade)': debug_only_vcwg.iloc[:, 1] - 273.15,
                            f'Only EP{which_ep} (northFacingWall)': debug_only_ep.iloc[:, 1] - 273.15,
                            'Bypass Ver1.1 (wallShade)': debug_bypass_ver1p1.iloc[:, 1] - 273.15})
    df.to_excel(writer, sheet_name='wallShade_northFacingWall')
    #write the fourth sheet
    df = pd.DataFrame({'Only VCWG (roof)': debug_only_vcwg.iloc[:, 2] - 273.15,
                            f'Only EP{which_ep} (roof)': debug_only_ep.iloc[:, 2] - 273.15,
                            'Bypass Ver1.1 (roof)': debug_bypass_ver1p1.iloc[:, 3] - 273.15})
    df.to_excel(writer, sheet_name='roof')
    #write the fifth sheet
    df = pd.DataFrame({'Only VCWG (sensWaste)': debug_only_vcwg.iloc[:, 3],
                            f'Only EP{which_ep} (sensHVAC)': debug_only_ep.iloc[:, 3],
                            'Bypass Ver1.1 (sensHVAC)': debug_bypass_ver1p1.iloc[:, 4]})
    df.to_excel(writer, sheet_name='sensWaste_sensHVAC')
    #save the excel file
    writer.save()

def shared_x_plot(debug_processed_save_folder, canyon_name = '2m Direct'):
    wallSunSheet = pd.read_excel(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                                    header=0, index_col=0, sheet_name='wallSun_southFacingWall')
    wallShadeSheet = pd.read_excel(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                                    header=0, index_col=0, sheet_name='wallShade_northFacingWall')
    roofSheet = pd.read_excel(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                                    header=0, index_col=0, sheet_name='roof')
    sensWaste = pd.read_excel(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                                    header=0, index_col=0, sheet_name='sensWaste_sensHVAC')
    canyonSheet = pd.read_excel(f'{debug_processed_save_folder}\\bypass_overestimated_debugging_DOE_Ref.xlsx',
                                    header=0, index_col=0, sheet_name=canyon_name)
    fig, ax = plt.subplots(5, 1, sharex=True)
    fig.suptitle(f'canyon temperature:{canyon_name}')
    if canyon_name == '2m Direct':
        ax[0].plot(canyonSheet.iloc[:,0], linestyle='-.', color='black', label='Urban Measurement')
        ax[0].plot(canyonSheet.iloc[:,1], color = 'blue', label='OnlyEP')
        ax[0].plot(canyonSheet.iloc[:,2], linestyle='--', color = 'red', label='OnlyVCWG')
        ax[0].plot(canyonSheet.iloc[:,3], color = 'green', label='Bypass')
        ax[1].plot(wallSunSheet.iloc[:, 0], color='blue')
    else:
        ax[0].plot(canyonSheet.iloc[:,0], linestyle='-.', color='black', label='Urban Measurement')
        ax[1].plot(wallSunSheet.iloc[:, 0], color='blue', label='onlyEP')
        ax[0].plot(canyonSheet.iloc[:,1], linestyle='--', color = 'red',label='OnlyVCWG')
        ax[0].plot(canyonSheet.iloc[:,2],  color = 'green', label='Bypass')
    ax[0].set_ylabel(f'canyon {canyon_name} Tdb (C)')


    ax[1].plot(wallSunSheet.iloc[:, 1] ,linestyle='--', color = 'red')
    ax[1].plot(wallSunSheet.iloc[:, 2],  color = 'green')
    ax[1].set_ylabel('sun/South Wall (C)')

    ax[2].plot(wallShadeSheet.iloc[:, 0],color = 'blue')
    ax[2].plot(wallShadeSheet.iloc[:, 1] ,linestyle='--', color = 'red')
    ax[2].plot(wallShadeSheet.iloc[:, 2],  color = 'green')
    ax[2].set_ylabel('shade/South Wall (C)')

    ax[3].plot(roofSheet.iloc[:, 0],color = 'blue')
    ax[3].plot(roofSheet.iloc[:, 1] ,linestyle='--', color = 'red')
    ax[3].plot(roofSheet.iloc[:, 2],  color = 'green')
    ax[3].set_ylabel('roof (C)')

    ax[4].plot(sensWaste.iloc[:, 0],color = 'blue')
    ax[4].plot(sensWaste.iloc[:, 1] ,linestyle='--' , color = 'red')
    ax[4].plot(sensWaste.iloc[:, 2],  color = 'green')
    ax[4].set_ylabel('sensWaste (w/m2)')

    fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0.)
    # put text outside the figure

    # add MouseCross
    plt.show()
