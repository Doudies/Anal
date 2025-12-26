import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def moving_average(series, window=3):
    return series.rolling(window=window).mean()

def linear_regression_forecast(series, steps=3):
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.arange(len(series), len(series) + steps).reshape(-1, 1)
    predictions = model.predict(future_X)

    return predictions
