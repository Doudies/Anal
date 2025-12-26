import numpy as np
import pandas as pd
from math import sqrt


# =====================================================================
# 1. SPLIT SIMPLE TRAIN / TEST
# =====================================================================

def time_series_train_test_split(series, test_size=4):
    series = pd.Series(series).dropna()
    n = len(series)

    if test_size >= n:
        raise ValueError("test_size doit être strictement inférieur à la taille de la série")

    train = series.iloc[: n - test_size]
    test = series.iloc[n - test_size:]

    return train, test


# =====================================================================
# 2. ALIGNEMENT TEST / FORECAST
# =====================================================================

def _to_aligned_arrays(test, forecast):
    test = pd.Series(test).astype(float)
    forecast = pd.Series(forecast).astype(float)

    if len(forecast) > len(test):
        forecast = forecast.iloc[-len(test):]
    elif len(forecast) < len(test):
        test = test.iloc[-len(forecast):]

    return test.values, forecast.values


# =====================================================================
# 3. MÉTRIQUES (MSE, MAE, MAPE, RMSE, AIC, BIC, AICc)
# =====================================================================

def compute_aicc(aic, n, k):
    """
    AIC corrigé (AICc).
    """
    # Cas impossibles
    if aic is None or np.isnan(aic):
        return None
    
    if n - k - 1 <= 0:
        return None

    # Formule AICc
    return aic + (2 * k * (k + 1)) / (n - k - 1)



def compute_metrics(test, forecast, model_type="HW"):
    y_true, y_pred = _to_aligned_arrays(test, forecast)

    mse = np.mean((y_true - y_pred) ** 2)
    mae = np.mean(np.abs(y_true - y_pred))

    if np.any(y_true == 0):
        mape = np.nan
    else:
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    rmse = sqrt(mse)

    n = len(y_true)

    # nombre de paramètres selon le modèle
    if model_type == "SES":
        k = 1
    elif model_type == "Holt":
        k = 2
    else:
        k = 3

    aic = n * np.log(mse) + 2 * k
    bic = n * np.log(mse) + k * np.log(n)
    aicc = compute_aicc(aic, n, k)

    return {
        "MSE": mse,
        "MAE": mae,
        "MAPE": mape,
        "RMSE": rmse,
        "AIC": aic,
        "BIC": bic,
        "AICc": aicc
    }


# =====================================================================
# 4. VALIDATION 70/30 ET 80/20
# =====================================================================

def time_series_split(series, ratios=[0.7, 0.8]):
    splits = []
    n = len(series)

    for r in ratios:
        train_size = int(n * r)
        train = series.iloc[:train_size]
        test = series.iloc[train_size:]
        splits.append((r, train, test))

    return splits


# =====================================================================
# 5. VALIDATION ROLLING-ORIGIN
# =====================================================================

def rolling_origin_validation(series, horizon=1):
    results = []
    n = len(series)

    for i in range(5, n - horizon):
        train = series.iloc[:i]
        test = series.iloc[i:i + horizon]
        results.append((train, test))

    return results
