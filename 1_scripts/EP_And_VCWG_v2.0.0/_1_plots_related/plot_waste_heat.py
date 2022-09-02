# read csv, then plot
import pandas as pd
import matplotlib.pyplot as plt

def ep_time_to_pandas_time(dataframe, delta_t):
    start_time = '2017-July-01 00:00:00'
    date = pd.date_range(start_time, periods=len(dataframe), freq='{}S'.format(delta_t))
    date = pd.Series(date)
    # update dataframe index
    dataframe.index = date
    return dataframe

# add header to df

# read csv
df = pd.read_csv('ASHRAE901_OfficeSmall_STD2019_Denver_5min.csv', header=0, index_col=0)
df2 = pd.read_csv('ASHRAE901_OfficeSmall_STD2019_Denver_15min.csv', header=0, index_col=0)
df5 = pd.read_csv('ASHRAE901_OfficeSmall_STD2019_Denver_1min.csv', header=0, index_col=0)

df4 = pd.read_csv('5ZoneAirCooled_eachcall.csv', header=0)
df3 = pd.read_csv('5zone_ep_1min_vcwg_5min_waste_heat.csv', header=0)
# add column names

df = ep_time_to_pandas_time(df, 300)
df2 = ep_time_to_pandas_time(df2, 900)
df5 = ep_time_to_pandas_time(df5, 60)
df4 = ep_time_to_pandas_time(df4, 300)
df3 = ep_time_to_pandas_time(df3, 60)

# plot
fig, ax = plt.subplots()
# ax.plot(df5.index, df5['SimHVAC:HVAC System Total Heat Rejection Energy [J](TimeStep) '], label='1 min Accumulated (1 min EP)')
ax.plot(df3.index, df3['coordiantion.ep_accumulated_waste_heat'], label='5 min Accumulated (1 min EP+ 5 min VCWG)')
ax.plot(df4.index, df4['SimHVAC:HVAC System Total Heat Rejection Energy [J](Each Call)'], label='5 min Accumulated (5 min EP)')
# ax.plot(df2.index, df2['SimHVAC:HVAC System Total Heat Rejection Energy [J](TimeStep) '], label='15 min  EP')
# ax.plot(df3[0], df3[1], label='15 min, EP+VCWG')
ax.set(xlabel='Time [h]', ylabel='HVAC System Total Heat Rejection Energy [J]',
         title='Accumulated Waste Heat in different software (EP only, EP+VCWG)')
ax.legend()
plt.show()



