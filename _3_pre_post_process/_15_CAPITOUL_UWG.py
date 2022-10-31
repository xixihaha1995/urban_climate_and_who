import _0_all_plot_tools as plt_tools, pandas as pd

results_path = r'..\_4_measurements\CAPITOUL\UWG_Involved\UWG_Involved_Annual.xlsx'
results_df = pd.read_excel(results_path, sheet_name='UWG_Involved_MedOffice', index_col=0, parse_dates=True)


rural_cvrmse = plt_tools.bias_rmse_r2(results_df['Measurement'], results_df['Rural'], 'Rural')
VCWG_cvrmse = plt_tools.bias_rmse_r2(results_df['Measurement'], results_df['Only VCWG-Canyon20'], 'Only VCWG')
bypass_VCWG_cvrmse = plt_tools.bias_rmse_r2(results_df['Measurement'], results_df['Bypass Ver1.1-Annual-Roof13'],
                                            'Bypass VCWG')
UWG_cvrmse = plt_tools.bias_rmse_r2(results_df['Measurement'], results_df['UWG_CanTemp_C'], 'UWG')

all_df_lst = [results_df['Measurement'],
              results_df['Rural'], results_df['Only VCWG-Canyon20'], results_df['Bypass Ver1.1-Annual-Roof13'],
                    results_df['UWG_CanTemp_C']]
all_df_dc_names = ['Urban', 'Rural', 'Only VCWG', 'Bypass VCWG', 'UWG']
all_df_in_one = plt_tools.merge_multiple_df(all_df_lst, all_df_dc_names)

case_name = (f"2004-Annual, Urban Heat Island Effect", "Date", "Temperature (C)")
txt_info = [case_name, rural_cvrmse, VCWG_cvrmse, bypass_VCWG_cvrmse, UWG_cvrmse]

plt_tools.general_time_series_comparision(all_df_in_one, txt_info)