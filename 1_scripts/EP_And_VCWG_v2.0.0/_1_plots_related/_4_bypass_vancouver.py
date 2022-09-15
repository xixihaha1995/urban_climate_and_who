# Eventually, we need compare the Sensible heat flux and the Latent heat flux.
# Do the sensible heat fluxes first
# Sensile heat fluxes are in W/m2, file is "SSQHB_all_30min.csv"
# Latent heat fluxes are in kg/m2/s, file is "SSQEB_all_30min.csv"
# Original measurements is 30 mins interval, we need to convert to hourly
# Read sensible measurements for May - September 2008

import pandas as pd
import _0_all_plot_tools as plt_tools

# Read sensible measurements for May - September 2008
df_dirty = pd.read_csv('SSQHB_all_30min.csv', header=0, index_col=0, parse_dates=True)

df_30min_sens_measure_all = plt_tools.data_cleaning(df_dirty)
# the original data is from 2007-07-01 00:30:00 to 2017-08-14 14:30:00
# we only need 2008-05-01 00:00:00 to 2008-09-30 23:00:00
df_30min_sens_measure = df_30min_sens_measure_all.loc['2008-05-01 00:00:00':'2008-09-30 23:00:00']


plt_tools.plot_comparison_measurement_simulated(df_30min_sens_measure, df_30min_sens_measure, 'Bypass')

print('Done')