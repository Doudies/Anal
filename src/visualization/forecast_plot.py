import matplotlib.pyplot as plt
import pandas as pd

def plot_forecast(series, forecast, title="Prévision"):
    """
    Affiche la série historique + les prévisions alignées.
    """

    series = series.copy()
    series.index = pd.to_datetime(series.index)   # << FIX CRITIQUE

    plt.figure(figsize=(12, 5))

    # Série historique
    plt.plot(series.index, series.values, label="Historique", linewidth=2)

    # Construire des dates futures régulières
    last_date = series.index[-1]
    future_dates = pd.date_range(start=last_date, periods=len(forecast)+1, freq="30D")[1:]

    # Prévision
    plt.plot(future_dates, forecast.values, label="Prévision", linestyle="--", marker="o", color="orange")

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Valeur")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
