'''
Hypothesis:
1. EP cannot mimic urban well: no noon-shading, no evening-LWR.
2. VCWG can mimic urban well, noon-shading, evening-LWR, mornining-LWR.
3. EP-With-Shading can mimic the noon-shading, but not the evening-LWR, mornining-LWR.
4. EP-With-VCWG can mimic the evening-LWR, mornining-LWR, but not the noon-shading.
'''
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
# matplotlib.use('WebAgg')

'''
We have done the following experiments/measures:
(Rural), EP, VCWG, EP-With-Shading, EP-With-VCWG
We have the following catorgories for the experiments/measures:
Wallshade, Walllit, Roof

To have 3 subfigures, 
'''
def plot_one_subfigure(category,data, compare_columns, ax, fig):
    global legend_bool

    x = pd.to_datetime(data.index)
    rural = pd.read_csv(r'.\shading_saving\EP_Surface.csv', index_col=0)
    # read column 'oat_temp_c'
    rural = rural[['oat_temp_c']]
    rural = rural.loc[start_time:end_time]
    if not legend_bool:
        ax.plot(x, rural, label='Rural', color='black', linestyle='--')
    else:
        ax.plot(x, rural, color='black', linestyle='--')
    for col in compare_columns:
        if category == 'Waste':
            y = data[col]
        else:
            y = data[col] - 273.15
        if not legend_bool:
            ax.plot(x, y, label=col)
        else:
            ax.plot(x, y)
    fig.subplots_adjust(right=0.76)
    if not legend_bool:
        fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=xlabel_fontsize)
        legend_bool = True
    ax.set_title(category)
    if category == 'Waste':
        ax.set_ylabel('W/m2')
    else:
        ax.set_ylabel(' Temperature (C)')

def plot_all_subfigures(compare_columns):
    categories = ['WallshadeT', 'WalllitT', 'RoofT','Waste']
    fig, axes = plt.subplots(4, 1, figsize=(12, 4), sharex=True)
    #set x label
    for ax in axes:
        ax.tick_params(axis='x', labelsize=xlabel_fontsize)
    for i, category in enumerate(categories):
        data = pd.read_excel(r'.\shading_saving\shading.xlsx', sheet_name=category, index_col=0)
        plot_one_subfigure(category,data, compare_columns, axes[i], fig)
    plt.show()

def merge_all_shading_related_csv():
    folder_path = r'.\shading_saving'
    '''
    Create one xlsx file, shading.xlsx
    which has the the following sheets:
    WallshadeT,WalllitT,RoofT,senWaste
    
    For each sheet, the first column is the time(2004-06-01 00:05:00 to 2004-06-30 23:55:00)
    Other columns are the csv files names.
    The second column is VCWG_Shading_Surface, 
    The third column is EP_Surface,
    The fourth column is EP_Shading_Surface,
    The fifth column is EP_ViewFactor,
    The sixth column is EP_Shading_Surface_ViewFactor,
    The seventh column is Bypass,
    '''
    writer = pd.ExcelWriter(folder_path + r'\shading.xlsx', engine='xlsxwriter')
    sheet_names = ['WallshadeT', 'WalllitT', 'RoofT', 'Waste']
    columns = ['cur_datetime', 'VCWG_Shading_Surface', 'EP_Surface', 'EP_Shading_Surface', 'EP_ViewFactor',
               'EP_Shading_Surface_ViewFactor', 'Bypass']


    for sheet_name in sheet_names:
        # To write the first column from the first csv file, 'VCWG_Shading_Surface.csv'
        data = pd.read_csv(folder_path + r'\VCWG_Shading_Surface.csv', index_col=0)
        data = data.loc[start_time:end_time]
        # initialize all the columns
        for col in columns[1:]:
            data[col] = 0
        data = data[columns[1:]]
        data.to_excel(writer, sheet_name=sheet_name, index=True)
        # To write the other columns from the other csv files
        for col in columns[1:]:
            tmp = pd.read_csv(folder_path + r'\{}.csv'.format(col), index_col=0)
            tmp = tmp.loc[start_time:end_time]
            # from tmp columns, find the column name which contains the sheet_name
            tmp_col = [col for col in tmp.columns if sheet_name in col][0]
            tmp = tmp[[tmp_col]]
            tmp.columns = [col]
            data[col] = tmp[col]
        data.to_excel(writer, sheet_name=sheet_name, index=True)
    writer.save()
def main():
    merge_all_shading_related_csv()
    compare_columns = ['VCWG_Shading_Surface', 'EP_Surface', 'EP_Shading_Surface', 'EP_ViewFactor',
               'EP_Shading_Surface_ViewFactor', 'Bypass']
    # compare_columns = ['EP_ViewFactor',
    #            'EP_Shading_Surface_ViewFactor']
    plot_all_subfigures(compare_columns)

if __name__ == '__main__':
    global start_time, end_time, legend_bool, xlabel_fontsize
    xlabel_fontsize = 5
    start_time = '2004-06-01 00:05:00'
    end_time = '2004-06-30 23:55:00'
    legend_bool = False
    main()
