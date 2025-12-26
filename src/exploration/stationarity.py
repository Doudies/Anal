from statsmodels.tsa.stattools import adfuller, kpss

def adf_test(series):
    result = adfuller(series, autolag='AIC')
    return {
        "ADF Statistic": result[0],
        "p-value": result[1]
    }

def kpss_test(series):
    result = kpss(series, nlags="auto")
    return {
        "KPSS Statistic": result[0],
        "p-value": result[1]
    }
