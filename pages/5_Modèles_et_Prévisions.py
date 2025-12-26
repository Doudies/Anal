import streamlit as st
import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing, Holt
from statsmodels.graphics.tsaplots import plot_acf

# === Fix import src ===
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from src.models.smoothing_manual import (
    ses_forecast,
    holt_forecast,
    holt_winters_additive_forecast,
    holt_winters_multiplicative_forecast
)
def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


# ----------------------------------------------------------
# Vérification que la série existe
# ----------------------------------------------------------
if "series" not in st.session_state:
    st.warning("Veuillez d'abord importer une série dans l'onglet 1.")
    st.stop()

series = st.session_state["series"].sort_index()

st.title("🔧 Modélisation & Prévisions")
st.markdown("---")

# ================================================================
# SECTION 1 — PRÉVISION MANUELLE (VERSION PROPRE)
# ================================================================
st.header("1️⃣ Prévision manuelle")
st.write("Définissez les paramètres du modèle et visualisez la prévision correspondante.")

# -------------------------------------------------------------
# 1. CHOIX DU MODÈLE
# -------------------------------------------------------------
st.subheader("📌 Choix du modèle")

model_name = st.selectbox(
    "Sélectionnez un modèle :",
    [
        "SES (Simple Exponential Smoothing)",
        "Holt (Double Exponential)",
        "Holt-Winters Additif",
        "Holt-Winters Multiplicatif"
    ]
)

# -------------------------------------------------------------
# 2. PARAMÈTRES DU MODÈLE
# -------------------------------------------------------------
st.subheader("⚙️ Paramètres du modèle")

with st.expander("Paramètres du modèle", expanded=True):

    horizon = st.number_input(
        "Nombre de périodes à prévoir",
        min_value=1, max_value=36, value=6
    )

    alpha = st.slider("α (niveau)", 0.01, 1.0, 0.4)
    beta = None
    gamma = None

    if model_name != "SES (Simple Exponential Smoothing)":
        beta = st.slider("β (tendance)", 0.01, 1.0, 0.3)

    if "Holt-Winters" in model_name:
        gamma = st.slider("γ (saisonnalité)", 0.01, 1.0, 0.2)

# -------------------------------------------------------------
# 3. BOUTON POUR LANCER LA PRÉVISION
# -------------------------------------------------------------
if st.button("📉 Lancer la prévision manuelle", type="primary"):

    try:

        # ============================================================
        # — CALCUL PRÉVISION
        # ============================================================
        if model_name == "SES (Simple Exponential Smoothing)":
            forecast = ses_forecast(series, alpha, horizon)

        elif model_name == "Holt (Double Exponential)":
            forecast = holt_forecast(series, alpha, beta, horizon)

        elif model_name == "Holt-Winters Additif":
            forecast = holt_winters_additive_forecast(series, alpha, beta, gamma, horizon)

        elif model_name == "Holt-Winters Multiplicatif":
            forecast = holt_winters_multiplicative_forecast(series, alpha, beta, gamma, horizon)

        st.session_state["forecast_manual"] = forecast
        st.success("Prévision manuelle calculée !")

        # ============================================================
        # — DATES FUTURES
        # ============================================================
        last_date = series.index[-1]
        future_dates = pd.date_range(last_date, periods=horizon+1, freq="MS")[1:]

        df_forecast_manual = pd.DataFrame({
            "Date": future_dates,
            "Prévision manuelle": forecast
        }).set_index("Date")

        # ---------------------- AFFICHAGE PREVISION ----------------------
        with st.expander("📈 Visualisation : Historique + Prévision manuelle", expanded=True):

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(series.index, series.values, label="Historique", linewidth=2)
            ax.plot(future_dates, forecast, label="Prévision manuelle", linestyle="--", marker="o")

            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

            st.write("### 📄 Tableau des prévisions")
            st.dataframe(df_forecast_manual)

        # ============================================================
        # — ANALYSE DES RÉSIDUS (STATS MODELS)
        # ============================================================
        with st.expander("🔍 Analyse des résidus du modèle manuel"):

            if model_name == "SES (Simple Exponential Smoothing)":
                fit_model = SimpleExpSmoothing(series).fit(smoothing_level=alpha, optimized=False)
                k = 1

            elif model_name == "Holt (Double Exponential)":
                fit_model = ExponentialSmoothing(series, trend="add").fit(
                    smoothing_level=alpha, smoothing_trend=beta, optimized=False)
                k = 2

            elif model_name == "Holt-Winters Additif":
                fit_model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=4).fit(
                    smoothing_level=alpha, smoothing_trend=beta, smoothing_seasonal=gamma, optimized=False)
                k = 3

            else:
                fit_model = ExponentialSmoothing(series, trend="add", seasonal="mul", seasonal_periods=4).fit(
                    smoothing_level=alpha, smoothing_trend=beta, smoothing_seasonal=gamma, optimized=False)
                k = 3

            residuals = fit_model.resid

            st.write("### 📌 Résidus dans le temps")
            fig_r, ax_r = plt.subplots(figsize=(10, 3))
            ax_r.plot(residuals.index, residuals.values, marker="o")
            ax_r.axhline(0, color="red", linestyle="--")
            ax_r.grid(True)
            st.pyplot(fig_r)

            st.write("### 📊 Histogramme des résidus")
            fig_h, ax_h = plt.subplots(figsize=(10, 3))
            ax_h.hist(residuals, bins=10, edgecolor="black")
            st.pyplot(fig_h)

            st.write("### 🔄 Autocorrélation (ACF)")
            fig_acf, ax_acf = plt.subplots(figsize=(10, 3))
            plot_acf(residuals.dropna(), ax=ax_acf)
            st.pyplot(fig_acf)

        # ============================================================
        # — MÉTRIQUES
        # ============================================================
        with st.expander("📊 Métriques du modèle manuel"):

            RSS = np.sum(residuals**2)
            n = len(series)

            AIC = 2*k + n*np.log(RSS/n)
            AICc = AIC + (2*k*(k+1)) / (n - k - 1) if (n - k - 1) > 0 else np.inf
            BIC = k*np.log(n) + n*np.log(RSS/n)
            MSE = RSS / n
            mape_val = mape(series, forecast)

            df_manual_metrics = pd.DataFrame({
                "Metric": ["MSE", "AIC", "AICc", "BIC", "MAPE (%)"],
                "Valeur": [MSE, AIC, AICc, BIC, mape_val]
            })

            st.dataframe(df_manual_metrics)

            pretty_name = {
                "SES (Simple Exponential Smoothing)": "SES",
                "Holt (Double Exponential)": "Holt",
                "Holt-Winters Additif": "HW Additif",
                "Holt-Winters Multiplicatif": "HW Multiplicatif"
            }

            chosen = pretty_name.get(model_name, model_name)
            st.success(f"🥇 **Meilleur modèle manuel : {chosen}**")

    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")

st.markdown("---")

# ================================================================
# SECTION 2 — GRID SEARCH AUTOMATIQUE
# ================================================================
st.header("2️⃣ Grid Search automatique (optimisation des paramètres)")

def compute_aicc(aic, n, k):
    if n - k - 1 <= 0:
        return np.nan
    return aic + (2 * k * (k + 1)) / (n - k - 1)

def grid_search(series):
    alphas = np.linspace(0.1, 0.9, 9)
    betas = np.linspace(0.1, 0.9, 9)
    gammas = np.linspace(0.1, 0.9, 9)

    results = []

    # ========== SES ==========
    best_ses = None
    best_ses_mse = float("inf")
    for a in alphas:
        try:
            m = SimpleExpSmoothing(series).fit(smoothing_level=a, optimized=False)
            mse = np.mean((series - m.fittedvalues) ** 2)
            if mse < best_ses_mse:
                best_ses_mse = mse
                best_ses = m
        except:
            pass

    if best_ses:
        n = len(series)
        k = 1
        results.append(["SES", best_ses_mse, best_ses.aic,
                        compute_aicc(best_ses.aic, n, k), best_ses.bic])

    # ========== HOLT ==========
    best_holt = None
    best_holt_mse = float("inf")
    for a in alphas:
        for b in betas:
            try:
                m = ExponentialSmoothing(series, trend="add").fit(
                    smoothing_level=a, smoothing_trend=b, optimized=False
                )
                mse = np.mean((series - m.fittedvalues) ** 2)
                if mse < best_holt_mse:
                    best_holt_mse = mse
                    best_holt = m
            except:
                pass

    if best_holt:
        n = len(series)
        k = 2
        results.append(["Holt", best_holt_mse, best_holt.aic,
                        compute_aicc(best_holt.aic, n, k), best_holt.bic])

    # ========== HW ADDITIF ==========
    best_add = None
    best_add_mse = float("inf")
    for a in alphas:
        for b in betas:
            for g in gammas:
                try:
                    m = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=4).fit(
                        smoothing_level=a, smoothing_trend=b,
                        smoothing_seasonal=g, optimized=False
                    )
                    mse = np.mean((series - m.fittedvalues) ** 2)
                    if mse < best_add_mse:
                        best_add_mse = mse
                        best_add = m
                except:
                    pass

    if best_add:
        n = len(series); k = 3
        results.append(["HW Additif", best_add_mse, best_add.aic,
                        compute_aicc(best_add.aic, n, k), best_add.bic])

    # ========== HW MULTIPLICATIF ==========
    best_mul = None
    best_mul_mse = float("inf")
    for a in alphas:
        for b in betas:
            for g in gammas:
                try:
                    m = ExponentialSmoothing(series, trend="add", seasonal="mul", seasonal_periods=4).fit(
                        smoothing_level=a, smoothing_trend=b,
                        smoothing_seasonal=g, optimized=False
                    )
                    mse = np.mean((series - m.fittedvalues) ** 2)
                    if mse < best_mul_mse:
                        best_mul_mse = mse
                        best_mul = m
                except:
                    pass

    if best_mul:
        n = len(series); k = 3
        results.append(["HW Multiplicatif", best_mul_mse, best_mul.aic,
                        compute_aicc(best_mul.aic, n, k), best_mul.bic])

    return pd.DataFrame(results, columns=["Modèle", "MSE", "AIC", "AICc", "BIC"]), \
           best_ses, best_holt, best_add, best_mul


# ------------------------------
# Bouton GRID SEARCH
# ------------------------------
if st.button("🚀 Lancer Grid Search Automatique"):

    df_gs, m_ses, m_holt, m_add, m_mul = grid_search(series)
    st.session_state["grid_results"] = df_gs
    st.session_state["best_models"] = {
        "SES": m_ses,
        "Holt": m_holt,
        "HW Additif": m_add,
        "HW Multiplicatif": m_mul
    }
    st.success("Grid Search terminé !")

# ------------------------------
# Affichage tableau Grid Search
# ------------------------------
if "grid_results" in st.session_state:
    st.subheader("📊 Résultats du Grid Search")
    st.dataframe(st.session_state["grid_results"])

    best_row = st.session_state["grid_results"].sort_values("AICc").iloc[0]
    best_model_name = best_row["Modèle"]

    st.success(f"🥇 Meilleur modèle optimal : **{best_model_name}**")
    # === Enregistrer pour page Résidus ===
    if "best_models" in st.session_state:
        st.session_state["best_fitted_model"] = st.session_state["best_models"][best_model_name]

st.markdown("---")

# ================================================================
# SECTION 3 — OPTIMISATION AVANCÉE (Intervalles de confiance)
# ================================================================
st.header("3️⃣ Optimisation avancée")

st.subheader("📌 Intervalles de confiance des prévisions")

if "best_fitted_model" not in st.session_state or st.session_state["best_fitted_model"] is None:
    st.warning("Aucun modèle optimal disponible. Lancez d’abord le Grid Search.")
else:
    model_opt = st.session_state["best_fitted_model"]

    # ---------------------------
    # Paramètre : Horizon
    # ---------------------------
    horizon_ci = st.number_input("Horizon des prévisions :", min_value=1, max_value=36, value=6)

    try:
        # ---------------------------------------------------------
        # Prévision brute
        # ---------------------------------------------------------
        forecast_ci = model_opt.forecast(horizon_ci)

        # Réindexation temporelle correcte
        last_date = series.index[-1]
        future_index = pd.date_range(last_date, periods=horizon_ci+1, freq="MS")[1:]
        forecast_ci.index = future_index

        # ---------------------------------------------------------
        # IC via RMSE
        # ---------------------------------------------------------
        resid = model_opt.resid
        rmse = np.sqrt(np.mean(resid**2))
        z = 1.96

        lower = forecast_ci - z * rmse
        upper = forecast_ci + z * rmse

        df_ci = pd.DataFrame({
            "Prévision": forecast_ci.values,
            "Borne inférieure (95%)": lower.values,
            "Borne supérieure (95%)": upper.values
        }, index=forecast_ci.index)

        # ---------------------------------------------------------
        #  EXPANDER 1 : Tableau IC
        # ---------------------------------------------------------
        with st.expander("📄 Tableau des intervalles de confiance (95%)", expanded=True):
            st.dataframe(df_ci)

        # ---------------------------------------------------------
        #  EXPANDER 2 : Graphique IC
        # ---------------------------------------------------------
        with st.expander("📈 Prévisions avec intervalles de confiance"):
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(series.index, series.values, label="Historique")
            ax.plot(forecast_ci.index, forecast_ci.values, marker="o", label="Prévision")

            ax.fill_between(forecast_ci.index, lower, upper,
                            color="gray", alpha=0.3, label="IC 95%")

            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")

# ================================================================
# SECTION 4 — COMPARAISON FINALE (Manuel vs Optimal)
# ================================================================
st.header("4️⃣ Comparaison finale (Manuel vs Optimal)")

if "forecast_manual" in st.session_state and "grid_results" in st.session_state:

    st.subheader("📌 Tableau comparatif AICc")

    # === AICc du modèle manuel ===
    if model_name == "SES (Simple Exponential Smoothing)":
        fit_m = SimpleExpSmoothing(series).fit(smoothing_level=alpha, optimized=False); k = 1

    elif model_name == "Holt (Double Exponential)":
        fit_m = ExponentialSmoothing(series, trend="add").fit(
            smoothing_level=alpha, smoothing_trend=beta, optimized=False
        ); k = 2

    elif model_name == "Holt-Winters Additif":
        fit_m = ExponentialSmoothing(series, trend="add", seasonal="add",
                                     seasonal_periods=4).fit(
            smoothing_level=alpha, smoothing_trend=beta,
            smoothing_seasonal=gamma, optimized=False
        ); k = 3

    else:  # HW Multiplicatif
        fit_m = ExponentialSmoothing(series, trend="add", seasonal="mul",
                                     seasonal_periods=4).fit(
            smoothing_level=alpha, smoothing_trend=beta,
            smoothing_seasonal=gamma, optimized=False
        ); k = 3

    RSS_m = np.sum((series - fit_m.fittedvalues)**2)
    n = len(series)
    AIC_m = 2*k + n*np.log(RSS_m/n)
    AICc_m = compute_aicc(AIC_m, n, k)

    # === AICc optimal depuis Grid Search ===
    df_gs = st.session_state["grid_results"]
    best_row = df_gs.sort_values("AICc").iloc[0]
    best_model_name = best_row["Modèle"]

    AICc_opt = best_row["AICc"]

    df_compare = pd.DataFrame({
        "Modèle": ["Manuel", "Optimal"],
        "AICc": [AICc_m, AICc_opt]
    })
    st.dataframe(df_compare)

    # ----------------------------------------------------------
    # Conclusion
    # ----------------------------------------------------------
    if AICc_opt < AICc_m:
        st.success("🏆 **Le modèle optimal est meilleur que le modèle manuel.**")
    else:
        st.info("ℹ️ Le modèle manuel est aussi bon ou meilleur que le modèle optimal.")
    
# ================================================================
# 5 Analyse des résidus du modèle optimal
# ================================================================
st.header("5️⃣ Analyse des résidus du modèle optimal")

# Vérifier si best_fitted_model existe
if "best_fitted_model" not in st.session_state or st.session_state["best_fitted_model"] is None:
    st.warning("Aucun modèle optimal détecté. Lancez d’abord la sélection automatique sur cette page.")
else:
    model_opt = st.session_state["best_fitted_model"]

    # Récupération des fitted values
    try:
        fitted_vals = model_opt.fittedvalues
    except:
        st.error("Impossible de récupérer les valeurs ajustées du modèle optimal.")
        fitted_vals = None

    if fitted_vals is not None:
        residuals = series - fitted_vals

        # -----------------------------
        # Résidus dans le temps
        # -----------------------------
        with st.expander("📌 Résidus dans le temps", expanded=False):
            fig_rt, ax_rt = plt.subplots(figsize=(10, 4))
            ax_rt.plot(residuals.index, residuals.values, marker="o", linewidth=1.5)
            ax_rt.axhline(0, color="red", linestyle="--", linewidth=1)
            ax_rt.set_title("Résidus du modèle optimal")
            ax_rt.grid(True)
            st.pyplot(fig_rt)

        # -----------------------------
        # Histogramme
        # -----------------------------
        with st.expander("📊 Histogramme des résidus"):
            fig_res, ax_res = plt.subplots(figsize=(10, 4))
            ax_res.hist(residuals.dropna(), bins=10, edgecolor="black")
            ax_res.set_title("Distribution des résidus")
            ax_res.grid(True)
            st.pyplot(fig_res)

        # -----------------------------
        # Autocorrélation (ACF)
        # -----------------------------
        with st.expander("🔄 Autocorrélation des résidus (ACF)"):
            fig_acf, ax_acf = plt.subplots(figsize=(10, 4))
            plot_acf(residuals.dropna(), ax=ax_acf)
            ax_acf.set_title("ACF des résidus")
            st.pyplot(fig_acf)

        # -----------------------------
        # Tests statistiques
        # -----------------------------
        with st.expander("🧪 Tests statistiques"):

            choix_test = st.multiselect(
                "Sélectionnez les tests à exécuter :",
                ["Shapiro-Wilk (normalité)", "Ljung-Box (autocorrélation)"],
                default=["Shapiro-Wilk (normalité)", "Ljung-Box (autocorrélation)"]
            )

            # Shapiro-Wilk
            if "Shapiro-Wilk (normalité)" in choix_test:
                try:
                    shapiro_stat, shapiro_p = shapiro(residuals.dropna())
                    st.write(f"**Shapiro-Wilk p-value : {shapiro_p:.4f}**")
                except:
                    st.warning("⚠ Test de Shapiro-Wilk impossible (échantillon trop petit).")

            # Ljung-Box
            if "Ljung-Box (autocorrélation)" in choix_test:
                try:
                    lb = acorr_ljungbox(residuals.dropna(), lags=[min(5, len(residuals)-1)], return_df=True)
                    st.write(f"**Ljung-Box p-value : {lb['lb_pvalue'].iloc[0]:.4f}**")
                except:
                    st.warning("⚠ Test Ljung-Box impossible.")

