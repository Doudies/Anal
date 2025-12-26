import numpy as np

def grid_search_holt(series, alphas, betas, horizon, holt_func):
    """
    Recherche par grille simple pour Holt ou Holt-Winters (paramètres α, β).
    holt_func doit être une fonction : f(train, alpha, beta, horizon) -> (fit, forecast)
    """
    best_score = float("inf")
    best_params = None

    # split train/test
    n = len(series)
    train = series.iloc[:-horizon]
    test = series.iloc[-horizon:]

    test = test.astype(float).values

    for a in alphas:
        for b in betas:
            try:
                _, f = holt_func(train, a, b, horizon)
                f = np.array(f, dtype=float)

                # MSE
                mse = np.mean((test - f)**2)

                if mse < best_score:
                    best_score = mse
                    best_params = (a, b)
            except:
                pass

    return best_params, best_score
