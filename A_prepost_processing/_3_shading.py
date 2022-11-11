'''
Hypothesis:
1. EP cannot mimic urban well: no noon-shading, no evening-LWR.
2. VCWG can mimic urban well, noon-shading, evening-LWR, mornining-LWR.
3. EP-With-Shading can mimic the noon-shading, but not the evening-LWR, mornining-LWR.
4. EP-With-VCWG can mimic the evening-LWR, mornining-LWR, but not the noon-shading.
'''
import pandas as pd
from matplotlib import pyplot as plt

'''
We have done the following experiments/measures:
(Rural), EP, VCWG, EP-With-Shading, EP-With-VCWG
We have the following catorgories for the experiments/measures:
Wallshade, Walllit, Roof

To have 3 subfigures, 
'''
def plot_one_subfigure(data, category, ax):
    x = data['cur_datetime']
    y1 = data['oat_temp_c']
    y2 = data[[col for col in data.columns if 'EP_' + category in col]] - 273.15
    y3 = data[[col for col in data.columns if 'VCWG_' + category in col]] - 273.15
    y4 = data[[col for col in data.columns if 'EP_Shading_' + category in col]] - 273.15
    y5 = data[[col for col in data.columns if 'Bypass_' + category in col]] - 273.15
    ax.plot(x, y1, label='Rural', color='black')
    ax.plot(x, y3, label='VCWG', linestyle='--')
    ax.plot(x, y2, label='EP')
    ax.plot(x, y4, label='EP-With-Shading')
    ax.plot(x, y5, label='EP-With-VCWG')
    ax.set_title(category)
    ax.set_ylabel(' Temperature (C)')
    ax.legend()


def plot_three_subfigures(data):
    categories = ['Wallshade', 'Walllit', 'Roof']
    fig, axes = plt.subplots(3, 1, figsize=(12, 4), sharex=False)
    for i, category in enumerate(categories):
        plot_one_subfigure(data, category, axes[i])
    plt.show()

def main():
    data_path = r'.\shading_saving\Shading.xlsx'
    data = pd.read_excel(data_path)
    plot_three_subfigures(data)

if __name__ == '__main__':
    main()
