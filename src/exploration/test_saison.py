import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def test_additive_vs_multiplicative(series, p):
    """
    Test saisonnier additif vs multiplicatif basé sur la régression σ = a·x̄ + b.
    p = périodicité (ex : 4 pour trimestriel, 12 pour mensuel)
    """

    # --- Regroupement par saison ---
    groups = []
    for i in range(p):
        groups.append(series[i::p])

    # Calcul des moyennes et écarts-types
    means = np.array([g.mean() for g in groups])
    stds = np.array([g.std() for g in groups])

    # --- Régression linéaire ---
    X = means.reshape(-1, 1)
    y = stds

    model = LinearRegression()
    model.fit(X, y)

    a = model.coef_[0]
    b = model.intercept_

    # Décision automatique
    if abs(a) < 1e-6:
        nature = "Additif (σ ≈ constant)"
    else:
        nature = "Multiplicatif (σ dépend de la moyenne)"

    return {
        "moyennes": means,
        "ecarts_type": stds,
        "a": a,
        "b": b,
        "nature": nature
    }
