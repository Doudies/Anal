import matplotlib.pyplot as plt

def describe_series(series):
    stats = {
        "count": series.count(),
        "mean": series.mean(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max()
    }
    return stats

def plot_series(series):
    plt.plot(series)
    plt.title("Série temporelle")
    plt.xlabel("Date")
    plt.ylabel("Valeurs")
    plt.grid(True)
    plt.show()
