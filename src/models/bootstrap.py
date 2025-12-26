import numpy as np
import pandas as pd


def bootstrap_forecast(series, model_func, n_forecast, B=300):
    """
    Intervalle de confiance à 95% via bootstrap des résidus.

    series      : pd.Series complète
    model_func  : fonction modèle → doit retourner (fit, forecast)
    n_forecast  : horizon de prévision
    B           : nombre de rééchantillonnages bootstrap
    """

    # =========================
    # 1. Prévision de base
    # =========================
    fit, base_forecast = model_func(series, n_forecast)
    fit = np.array(fit).astype(float)
    base_forecast = np.array(base_forecast).astype(float)

    # =========================
    # 2. Résidus du modèle
    # =========================
    series_vals = series.values.astype(float)

    # résidus : y_t - y_hat_(t-1)
    resid = series_vals[1:] - fit[:-1]

    sims = []

    # =========================
    # 3. Bootstrap
    # =========================
    for _ in range(B):
        boot_resid = np.random.choice(resid, size=n_forecast, replace=True)
        sims.append(base_forecast + boot_resid)

    sims = np.array(sims)

    # =========================
    # 4. IC à 95%
    # =========================
    lower = np.percentile(sims, 2.5, axis=0)
    upper = np.percentile(sims, 97.5, axis=0)

    return base_forecast, lower, upper
