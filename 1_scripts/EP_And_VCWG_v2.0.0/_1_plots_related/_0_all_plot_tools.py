#RMSE function
import numpy as np, pandas as pd, matplotlib.pyplot as plt
def RMSE(y_true, y_pred):
    return np.sqrt(np.mean(np.square(y_pred - y_true)))

def bias_rmse_r2(df1, df2):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    r2 = 1 - np.sum(np.square(bias)) / np.sum(np.square(df1 - np.mean(df1)))
    bias_mean = np.mean(abs(bias))
    # return number with 2 decimal places
    return round(bias_mean,2), round(rmse,2), round(r2,2)

def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows=3, header= None, index_col=0, sep= '[ ^]+', engine='python')
    # set index to first column
    # df.set_index(df.iloc[:,0], inplace=True)
    return df

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

def time_interval_convertion(df):
    '''
    Original data is 30 mins interval,
    Convert it to hourly data
    Original data has [index, sensible]
    Replace sensible with hourly average
    '''
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), 2):
        df_new.loc[df.index[i]] = df.iloc[i:i+2].mean()
        # df_new.iloc[i,0] = df.iloc[i:i+2,0].mean()
    return df_new

# plot the comparisons between Vancouver Sunset dataset versus simulated (VCWGv2.0.0, VCWG-Bypass)
def plot_comparison_measurement_simulated(df, error_infor):
    figure, ax = plt.subplots(figsize=(10,5))

    ax.plot(df.iloc[:,0], label='Measurement')
    ax.plot(df.iloc[:,1], label= df.columns[1])
    ax.plot(df.iloc[:,2], label= df.columns[2])
    ax.legend()
    # add  to the plot
    # add text below the plot, outside the plot
    txt = f'Bias Mean(W m-2), RMSE(W m-2), R2(-)\n' \
          f'SUEWS:(-, 39.1, 0.77)\n' \
          f'VCWGv2.0.0:(0.65, 18.1, 0.94)\n' \
          f'{df.columns[1]}:{error_infor[0]}\n' \
          f'{df.columns[2]}:{error_infor[1]}'
    print(txt)
    ax.text(0.5, 1, txt, transform=ax.transAxes, fontsize=6,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_title('Comparison for Sensible Heat Flux (Best available) (28.80m)')
    # set x name, y name, and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Sensible Heat Flux (W/m2)')

    plt.show()

def add_date_index(df, start_date, time_interval):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval))
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
