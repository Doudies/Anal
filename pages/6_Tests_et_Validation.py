import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy.stats import shapiro
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

st.set_page_config(page_title="Tests & Validation", layout="wide")


# ======================================================
#        Vérification série chargée
# ======================================================
st.title("🧪 Tests & Validation avancée")

if "series" not in st.session_state:
    st.error("Aucune série chargée. Veuillez importer les données dans la page 1.")
    st.stop()

series = st.session_state["series"]

if series is None or len(series) < 5:
    st.error("La série est vide ou trop courte.")
    st.stop()

series = series.dropna()   # *** CORRECTION ***
st.success("Série chargée avec succès !")


# ======================================================
#               Fonction MAPE robuste
# ======================================================
def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    mask = (y_true != 0) & ~np.isnan(y_true) & ~np.isnan(y_pred)
    if np.sum(mask) < 1:
        return np.nan

    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


# ======================================================
#               Split 70/30 – 80/20
# ======================================================
def split_eval(series, ratio):
    n = len(series)
    train_size = int(n * ratio)

    if train_size < 3 or train_size >= n - 1:
        return np.nan, np.nan

    train = series[:train_size]
    test  = series[train_size:]

    if len(test) < 2:
        return np.nan, np.nan

    try:
        model = SimpleExpSmoothing(train).fit()
        forecast = model.forecast(len(test))
    except:
        return np.nan, np.nan

    m = mape(test, forecast)
    rm = np.sqrt(np.nanmean((test - forecast) ** 2))

    return m, rm


# ======================================================
#               Rolling-Origin robuste
# ======================================================
def rolling_origin(series):
    m_list = []

    for i in range(3, len(series) - 1):
        train = series[:i]
        true  = series[i]

        try:
            model = SimpleExpSmoothing(train).fit()
            pred = model.forecast(1)[0]
        except:
            continue

        if true != 0:
            m_list.append(abs((true - pred) / true) * 100)

    if len(m_list) == 0:
        return np.nan

    return np.mean(m_list)


# ======================================================
#               Affichage Validation Croisée
# ======================================================
st.header("📌 Validation croisée temporelle (70/30, 80/20, Rolling-Origin)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Validation 70/30")
    m70, r70 = split_eval(series, 0.7)
    st.write(f"• **MAPE :** {np.nan_to_num(m70, nan=0):.2f}%")
    st.write(f"• **RMSE :** {np.nan_to_num(r70, nan=0):.2f}")

with col2:
    st.subheader("📍 Validation 80/20")
    m80, r80 = split_eval(series, 0.8)
    st.write(f"• **MAPE :** {np.nan_to_num(m80, nan=0):.2f}%")
    st.write(f"• **RMSE :** {np.nan_to_num(r80, nan=0):.2f}")

# Rolling Origin
st.subheader("📍 Validation Rolling-Origin")

m_ro = rolling_origin(series)
st.write(f"• **MAPE Rolling-Origin moyen :** {np.nan_to_num(m_ro, nan=0):.2f}%")

if not np.isnan(m_ro) and m_ro < 5:
    st.success("✔ Très bonne stabilité temporelle.")
elif not np.isnan(m_ro):
    st.warning("⚠ Modèle moins stable à long terme.")
else:
    st.info("Impossible de calculer correctement le Rolling-Origin.")
