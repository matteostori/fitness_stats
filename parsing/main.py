import os

from charts.draw_charts import draw_weekly_weight_kcals, \
    draw_weekly_and_quarterly_lift_charts
import pandas as pd


path = os.environ['ECLIPSE_WORKSPACE']

def open_stats():
    file = path + 'fitness_stats/data/fitness_stats.xlsx'
    df_sheets = pd.read_excel(file, sheet_name=['Full Calendar Log', 'Weekly Calendar summary'], engine='openpyxl')

    return df_sheets

if __name__ == '__main__':
    df_sheets = open_stats()
    
    # draw_weekly_weight_kcals(df_sheets['Weekly Calendar summary'])
    # draw_weekly_lifts(df_sheets['Weekly Calendar summary'])
    draw_weekly_and_quarterly_lift_charts(df_sheets['Weekly Calendar summary'])
    
    print('end')