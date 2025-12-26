import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing

# --------------------------------------------------------
# 1. Lissage exponentiel simple (SES)
# --------------------------------------------------------
def ses_forecast(series, alpha, steps=3):
    """
    Lissage exponentiel simple (SES)
    Retourne uniquement les prévisions.
    """
    model = SimpleExpSmoothing(series, initialization_method="estimated")
    fit_model = model.fit(smoothing_level=alpha, optimized=False)
    forecast = fit_model.forecast(steps).astype(float)
    return forecast


# --------------------------------------------------------
# 2. Méthode de Holt (double exponentiel)
# --------------------------------------------------------
def holt_forecast(series, alpha, beta, steps=3):
    """
    Holt (niveau + tendance)
    Retourne uniquement les prévisions.
    """
    model = ExponentialSmoothing(
        series,
        trend="add",
        initialization_method="estimated"
    )
    fit_model = model.fit(
        smoothing_level=alpha,
        smoothing_trend=beta,
        optimized=False
    )
    forecast = fit_model.forecast(steps).astype(float)
    return forecast


# --------------------------------------------------------
# 3. Holt-Winters Additif
# --------------------------------------------------------
def holt_winters_additive_forecast(series, alpha, beta, gamma, seasonal_periods=4, steps=3):
    """
    Holt-Winters Additif : Y = Trend + Saison
    """
    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=seasonal_periods,
        initialization_method="estimated"
    )
    fit_model = model.fit(
        smoothing_level=alpha,
        smoothing_trend=beta,
        smoothing_seasonal=gamma,
        optimized=False
    )
    forecast = fit_model.forecast(steps).astype(float)
    return forecast


# --------------------------------------------------------
# 4. Holt-Winters Multiplicatif
# --------------------------------------------------------
def holt_winters_multiplicative_forecast(series, alpha, beta, gamma, seasonal_periods=4, steps=3):
    """
    Holt-Winters Multiplicatif : Y = Trend * Saison
    """
    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="mul",
        seasonal_periods=seasonal_periods,
        initialization_method="estimated"
    )
    fit_model = model.fit(
        smoothing_level=alpha,
        smoothing_trend=beta,
        smoothing_seasonal=gamma,
        optimized=False
    )
    forecast = fit_model.forecast(steps).astype(float)
    return forecast
