import pandas as pd
import matplotlib.pyplot as plt
from src.models.moving_average import (
    extract_trend,
    extract_seasonality_additive
)

# --------------------------------------------------------
# 1. Décomposition additive
# --------------------------------------------------------

def decomposition_additive(series, p):
    """
    Décomposition additive :
    Y = T + S + R
    """
    # Tendance
    trend = extract_trend(series, p)

    # Saison
    season = extract_seasonality_additive(series, trend, p)

    # Résidus
    residuals = series - trend - season

    return trend, season, residuals


# --------------------------------------------------------
# 2. Décomposition multiplicative
# --------------------------------------------------------

def decomposition_multiplicative(series, p):
    """
    Décomposition multiplicative :
    Y = T * S * R
    (Attention : valeurs doivent être positives)
    """
    trend = extract_trend(series, p)

    season = series / trend

    # Moyenne par période
    indices = {}
    for i in range(p):
        indices[i] = season[i::p].mean()

    seasonal_values = []
    for i in range(len(series)):
        seasonal_values.append(indices[i % p])

    season_serie = pd.Series(seasonal_values, index=series.index)

    residuals = series / (trend * season_serie)

    return trend, season_serie, residuals


# --------------------------------------------------------
# 3. Fonction d'affichage
# --------------------------------------------------------

def plot_decomposition(series, trend, season, residuals):
    plt.figure(figsize=(10, 8))

    plt.subplot(4,1,1)
    plt.plot(series)
    plt.title("Série originale")
    plt.grid(True)

    plt.subplot(4,1,2)
    plt.plot(trend)
    plt.title("Tendance")
    plt.grid(True)

    plt.subplot(4,1,3)
    plt.plot(season)
    plt.title("Saisonnalité")
    plt.grid(True)

    plt.subplot(4,1,4)
    plt.plot(residuals)
    plt.title("Résidus")
    plt.grid(True)

    plt.tight_layout()
    plt.show()
