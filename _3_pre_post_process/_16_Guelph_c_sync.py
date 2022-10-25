
import os, sys
import pandas as pd, _0_all_plot_tools as plot_tools, matplotlib.pyplot as plt


def add_rural():
    # read the excel
    df_urban = pd.read_excel(r'..\_4_measurements\Guelph\To_Generate_Urban\Guelph_clean_urban_sites_all.xlsx',
                       sheet_name=None)
    target_date_idx = df_urban['A']['Date']
    df_rural = pd.read_csv(r'..\_4_measurements\Guelph\To_Generate_EPW\clean_en_climate_hourly_ON_6143089_MM-2018_P1H.csv',
                            index_col=0, parse_dates=True)
    # for each column of df_rural, add extra "raural" to the column name
    df_rural.columns = [col + ' (rural)' for col in df_rural.columns]
    #df_rural are hourly, resample df_rural to 15 min
    df_rural = df_rural.resample('15min').interpolate(method='linear')
    # select the same date as df_urban
    df_rural = df_rural.loc[target_date_idx]
    # for each sheet in df_urban, add the rural data
    writer = pd.ExcelWriter(r'..\_4_measurements\Guelph\To_Sync_Urban_Rural\Guelph_sync_urban_rural.xlsx')
    for i in range(5):
        # except for 'Date' column, set type to float
        df_urban[chr(ord('A') + i)].iloc[:, 1:] = df_urban[chr(ord('A') + i)].iloc[:, 1:].astype(float)
        # except for 'Date' column, interpolate the missing data
        df_urban[chr(ord('A') + i)].iloc[:, 1:] = df_urban[chr(ord('A') + i)].iloc[:, 1:].interpolate(method='linear')
        df_urban[chr(ord('A') + i)] = df_urban[chr(ord('A') + i)].set_index('Date')
        df_urban[chr(ord('A') + i)] = df_urban[chr(ord('A') + i)].join(df_rural)
        df_urban[chr(ord('A') + i)].to_excel(writer, sheet_name=chr(ord('A') + i))
    writer.save()



def main():
    # get the data from all the files
    add_rural()
if __name__ == '__main__':
    main()
