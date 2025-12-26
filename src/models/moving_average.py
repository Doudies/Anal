import pandas as pd

def moving_average_odd(series, k):
    """
    Moyenne mobile d'ordre impair k = 2m+1.
    Renvoie une série lissée alignée sur les dates originales.
    """
    if k % 2 == 0:
        raise ValueError("k doit être impair.")
    return series.rolling(window=k, center=True).mean()

def moving_average_even(series, k):
    """
    Moyenne mobile centrée pour k pair (k = 2m).
    On applique d'abord une MM simple, puis on centre.
    """
    if k % 2 != 0:
        raise ValueError("k doit être pair.")
    
    mm = series.rolling(window=k).mean()
    mm_centered = (mm + mm.shift(-1)) / 2
    return mm_centered

def moving_average_p(series, p):
    """
    Moyenne mobile d'ordre p (saisonnalité).
    gère pair/impair automatiquement.
    """
    if p % 2 != 0:
        # impair → centrée naturellement
        return series.rolling(window=p, center=True).mean()
    else:
        # pair → MM paire centrée
        mm = series.rolling(window=p).mean()
        return (mm + mm.shift(-1)) / 2

def extract_trend(series, p):
    return moving_average_p(series, p)

def extract_seasonality_additive(series, trend, p):
    detrended = series - trend
    season = {}

    for i in range(p):
        season[i] = detrended[i::p].mean()

    # Reconstruire une série de même longueur
    seasonal_values = []
    for i in range(len(series)):
        seasonal_values.append(season[i % p])

    return pd.Series(seasonal_values, index=series.index)
