import matplotlib.pyplot as plt
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf

def residual_plot(y_true, y_pred, model_name):
    resid = np.array(y_true) - np.array(y_pred)

    # 3 graphiques alignés
    plt.figure(figsize=(14, 4))

    # 1) Série des résidus
    plt.subplot(1, 3, 1)
    plt.plot(resid, marker='o')
    plt.axhline(0, color='red', linestyle='--')
    plt.title(f"Résidus - {model_name}")

    # 2) Histogramme
    plt.subplot(1, 3, 2)
    plt.hist(resid, bins=8, edgecolor='black')
    plt.title("Histogramme des résidus")

    # 3) ACF des résidus
    plt.subplot(1, 3, 3)
    plot_acf(resid, ax=plt.gca(), lags=min(10, len(resid)-1))
    plt.title("ACF des résidus")

    plt.tight_layout()
    plt.show()
