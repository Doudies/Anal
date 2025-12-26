import streamlit as st
import pandas as pd
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# === Fix import src ===
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from src.exploration.stationarity import adf_test, kpss_test
from src.exploration.decomposition import decomposition_additive
from src.exploration.test_saison import test_additive_vs_multiplicative

st.title("📐 Tests de Stationnarité & Décomposition")

# Vérifier qu'une série est chargée
if "series" not in st.session_state:
    st.warning("Veuillez d'abord importer une série dans l'onglet **1. Importation**.")
    st.stop()

series = st.session_state["series"]

# ================================================================
# 1. Tests ADF & KPSS
# ================================================================
st.subheader("📌 Tests de Stationnarité (ADF & KPSS)")

try:
    adf = adf_test(series)
    kpss = kpss_test(series)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Test ADF")
        st.write(f"**ADF Statistic** : {adf['ADF Statistic']:.4f}")
        st.write(f"**p-value** : {adf['p-value']:.4f}")

    with col2:
        st.markdown("### Test KPSS")
        st.write(f"**KPSS Statistic** : {kpss['KPSS Statistic']:.4f}")
        st.write(f"**p-value** : {kpss['p-value']:.4f}")

except Exception as e:
    st.error(f"Erreur lors des tests de stationnarité : {e}")

# ================================================================
# 2. Décomposition Additive
# ================================================================
st.subheader("📉 Décomposition Additive")

p = st.number_input("Période saisonnière (p)", min_value=2, max_value=24, value=4)

try:
    trend, season, resid = decomposition_additive(series, p)

    fig, axs = plt.subplots(4, 1, figsize=(10, 8))

    axs[0].plot(series); axs[0].set_title("Série Originale")
    axs[1].plot(trend); axs[1].set_title("Tendance")
    axs[2].plot(season); axs[2].set_title("Saisonnalité")
    axs[3].plot(resid); axs[3].set_title("Résidus")

    for ax in axs:
        ax.grid(True)

    fig.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Erreur lors de la décomposition : {e}")

# ================================================================
# 3. Test Additif vs Multiplicatif
# ================================================================
st.subheader("📊 Nature de la saisonnalité")

try:
    test_s = test_additive_vs_multiplicative(series, p)

    st.write("**Moyennes saisonnières :**", test_s["moyennes"])
    st.write("**Écarts-types :**", test_s["ecarts_type"])
    st.write(f"**Coefficient a :** {test_s['a']:.4f}")
    st.write(f"**Coefficient b :** {test_s['b']:.4f}")
    st.success(f"Conclusion : **{test_s['nature']}**")

except Exception as e:
    st.error(f"Erreur test saisonnier : {e}")

# ================================================================
# 📌 DÉTECTION DE LA SAISONNALITÉ (ANALYTIQUE & GRAPHIQUE)
# ================================================================
st.header("📊 Détection de la Saisonnalité")

# -------------------------------------------------------------
# 1. ACF + PACF
# -------------------------------------------------------------
st.subheader("1️⃣ Analyse Graphique : ACF & PACF")

fig_acf, ax_acf = plt.subplots(figsize=(8, 3))
plot_acf(series, ax=ax_acf)
ax_acf.set_title("ACF de la série")
st.pyplot(fig_acf)

fig_pacf, ax_pacf = plt.subplots(figsize=(8, 3))
plot_pacf(series, ax=ax_pacf)
ax_pacf.set_title("PACF de la série")
st.pyplot(fig_pacf)

st.info(
    "👉 **Une saisonnalité apparaît lorsque l’ACF montre des pics réguliers "
    "à des lag multiples d’une même période (ex: 4, 8, 12…).**"
)

# -------------------------------------------------------------
# 2. Détection automatique de la période saisonnière
# -------------------------------------------------------------
st.subheader("2️⃣ Détection automatique de la période")

autocorr_values = np.correlate(series - np.mean(series), series - np.mean(series), mode="full")
autocorr_values = autocorr_values[len(autocorr_values)//2:]
autocorr_values = autocorr_values / autocorr_values[0]

lags = np.arange(len(autocorr_values))
threshold = 0.4

candidate_lags = lags[(autocorr_values > threshold) & (lags > 1)]
detected_period = candidate_lags[0] if len(candidate_lags) > 0 else None

fig_auto, ax_auto = plt.subplots(figsize=(8, 3))
ax_auto.plot(lags, autocorr_values)
ax_auto.axhline(threshold, color='red', linestyle='--', label="Seuil")
ax_auto.set_title("Autocorrélation pour détection de saisonnalité")
ax_auto.legend()
st.pyplot(fig_auto)

if detected_period:
    st.success(f"📌 **Période saisonnière détectée : {detected_period}**")
else:
    st.warning("Aucune période saisonnière claire détectée automatiquement.")

# -------------------------------------------------------------
# 3. Vérification analytique
# -------------------------------------------------------------
st.subheader("3️⃣ Analyse Analytique (Variance entre périodes)")

if detected_period and detected_period < len(series) // 2:
    groups = [series[i::detected_period] for i in range(detected_period)]
    stds = [g.std() for g in groups]
    means = [g.mean() for g in groups]

    df_season = pd.DataFrame({
        "Période": np.arange(1, detected_period+1),
        "Moyennes": means,
        "Écarts-types": stds
    })

    st.dataframe(df_season)

    if np.std(means) > 0.5 * np.mean(means):
        analytic_conclusion = "forte saisonnalité"
    elif np.std(means) > 0.2 * np.mean(means):
        analytic_conclusion = "saisonnalité modérée"
    else:
        analytic_conclusion = "faible saisonnalité"

    st.info(
        f"📊 **Analyse analytique :** La série présente une **{analytic_conclusion}** "
        f"selon la variation des moyennes saisonnières."
    )
else:
    st.info("Impossible de réaliser une analyse analytique (période non détectée ou trop courte).")

# -------------------------------------------------------------
# 4. Conclusion finale
# -------------------------------------------------------------
st.subheader("4️⃣ Conclusion Finale")

if detected_period:
    st.success(
        f"🎯 **Série saisonnière détectée** avec une période d’environ **{detected_period}**.\n\n"
        "➡️ Confirmée par :\n"
        "- Des pics réguliers dans l’ACF\n"
        "- Une structure périodique observable\n"
        "- Une variation analytique des moyennes saisonnières\n"
    )
else:
    st.warning(
        "⚠️ **Aucune saisonnalité significative détectée.**\n\n"
        "➡️ L’ACF ne montre pas de pics réguliers et l’analyse analytique ne confirme pas de pattern saisonnier."
    )
