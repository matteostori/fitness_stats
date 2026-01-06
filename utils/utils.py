import pandas as pd

def yearweek_to_yyyymmm(yw):
    """
    Convert Yearweek numeric format (YYYYW or YYYYWW) to 'YYYY-MMM'.
    Example:
        20252  -> '2025-Feb'
        202410 -> '2024-Mar'  (week 10 of 2024)
    """
    yw = str(int(yw))  # ensure string
    year = int(yw[:4])
    week = int(yw[4:])
    
    # Convert ISO week to datetime (Monday of that week)
    dt = pd.to_datetime(f'{year}-W{week}-1', format='%G-W%V-%u')
    
    return dt.strftime('%Y-%b')