import os

import charts.draw_descriptive_charts as dwdesc
import charts.draw_statistical_charts as dwstat
import matplotlib.pyplot as plt
import pandas as pd


DRAW_DESCRIPTIVE = False
DRAW_STATISTICAL = True

path = os.environ['ECLIPSE_WORKSPACE']

def open_stats():
    file = path + 'fitness_stats/data/fitness_stats.xlsx'
    df_sheets = pd.read_excel(file, sheet_name=['Full Calendar Log', 'Weekly Calendar summary'], engine='openpyxl')

    # --- convert kg to tons ---
    df_sheets['Weekly Calendar summary']["Totals tons"] = df_sheets['Weekly Calendar summary']["Totals kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Leg tons"] = df_sheets['Weekly Calendar summary']["Leg kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Chest tons"] = df_sheets['Weekly Calendar summary']["Chest kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Back tons"] = df_sheets['Weekly Calendar summary']["Back kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Shoulders tons"] = df_sheets['Weekly Calendar summary']["Shoulders kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Biceps tons"] = df_sheets['Weekly Calendar summary']["Biceps kg"] / 1000 
    df_sheets['Weekly Calendar summary']["Core tons"] = df_sheets['Weekly Calendar summary']["Core kg"] / 1000 
    
    return df_sheets

if __name__ == '__main__':
    df_sheets = open_stats()
    
    # descriptive charts
    if DRAW_DESCRIPTIVE:
        dwdesc.draw_weekly_weight_kcals(df_sheets['Weekly Calendar summary'])
        dwdesc.draw_weekly_and_quarterly_lift_charts(df_sheets['Weekly Calendar summary'])

    # statistical charts
    if DRAW_STATISTICAL:
        df = dwstat.compute_fatigue_proxy(df_sheets['Weekly Calendar summary'])
        dwstat.plot_energy_vs_weight_change(df)
        dwstat.plot_muscle_radar(df)
        # dwstat.plot_sets_vs_load(df)
        dwstat.plot_running_vs_lifting(df)
        dwstat.plot_protein_effect(df)
        dwstat.plot_projection_accuracy(df)
        # dwstat.plot_correlation_heatmap(df)
        
    plt.show()