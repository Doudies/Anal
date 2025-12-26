import pandas as pd

def load_time_series(path, date_col, value_col):
    df = df_raw.copy()


    df[value_col] = df[value_col].astype(str).str.replace(',', '.').astype(float)
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)
    df = df.set_index(date_col)

    return df[value_col]
