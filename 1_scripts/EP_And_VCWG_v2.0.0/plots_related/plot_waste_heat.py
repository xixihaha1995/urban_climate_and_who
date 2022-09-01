# read csv, then plot
import pandas as pd
import matplotlib.pyplot as plt

# read csv
df = pd.read_csv('waste_heat_5_min.csv', header=None)
df2 = pd.read_csv('waste_heat_5_min_2.csv', header=None)
df3 = pd.read_csv('waste_heat_15_min.csv', header=None)
df4 = pd.read_csv('waste_heat_7.5_min.csv', header=None)
# plot
plt.plot(df[0], df[1], label='Zone Time Steo: 5 min')
# plt.plot(df2[0], df2[1], label='waste_heat_5_min_2')
plt.plot(df4[0], df4[1], label='Zone Time Step: 7.5 min')
plt.plot(df3[0], df3[1], label='Zone Time Step: 15 min')

plt.xlabel('Time [h]')
plt.ylabel('Heat Rejection [J]')
plt.legend()
plt.show()


