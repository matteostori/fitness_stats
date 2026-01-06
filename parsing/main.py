import os

from charts.draw_charts import draw_daily, draw_weekly
import pandas as pd

    
path = os.environ['ECLIPSE_WORKSPACE']

def open_stats():
    file = path + 'fitness_stats/data/fitness_stats.xlsx'
    df_sheets = pd.read_excel(file, sheet_name=['Full Calendar Log', 'Weekly Calendar summary'], engine='openpyxl')

    return df_sheets

if __name__ == '__main__':
    df_sheets = open_stats()
    
    # draw_daily(df_sheets['Full Calendar Log'])
    draw_weekly(df_sheets['Weekly Calendar summary'])
    
    print('end')