# pages/1_Importation.py - VERSION CORRIGÉE
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# === Fix import src ===
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

st.title("📂 Importation des Données")
st.write("Importez votre fichier CSV contenant la série temporelle.")

# ================================
# 1. Upload du fichier
# ================================
uploaded_file = st.file_uploader(
    "Choisir un fichier CSV ou Excel", 
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        # Lire le fichier selon l'extension
        if uploaded_file.name.endswith('.csv'):
            # Essayer différents séparateurs
            try:
                df_raw = pd.read_csv(uploaded_file, sep=',')
            except:
                try:
                    df_raw = pd.read_csv(uploaded_file, sep=';')
                except:
                    df_raw = pd.read_csv(uploaded_file, sep='\t')
        else:
            df_raw = pd.read_excel(uploaded_file)
        
        # Stocker temporairement
        st.session_state["df_raw"] = df_raw
        
        # Afficher un aperçu
        st.write("### 📊 Aperçu des données importées :")
        st.dataframe(df_raw.head())
        
        # Afficher les informations
        st.write(f"**Dimensions :** {df_raw.shape[0]} lignes × {df_raw.shape[1]} colonnes")
        
        # ================================
        # 2. Détection automatique des colonnes
        # ================================
        st.write("### 🔍 Détection automatique des colonnes :")
        
        # Trouver les colonnes qui ressemblent à des dates
        date_candidates = []
        value_candidates = []
        
        for col in df_raw.columns:
            # Vérifier si la colonne contient des dates
            try:
                # Essayer de convertir en datetime
                sample = df_raw[col].dropna().iloc[0] if len(df_raw[col].dropna()) > 0 else ""
                pd.to_datetime(sample, errors='raise')
                date_candidates.append(col)
            except:
                # Vérifier si c'est numérique
                try:
                    # Essayer de convertir en float
                    sample = str(df_raw[col].dropna().iloc[0]) if len(df_raw[col].dropna()) > 0 else ""
                    # Nettoyer la chaîne
                    sample_clean = sample.replace(',', '.').replace(' ', '')
                    float(sample_clean)
                    value_candidates.append(col)
                except:
                    pass
        
        st.write(f"**Colonnes date détectées :** {date_candidates if date_candidates else 'Aucune'}")
        st.write(f"**Colonnes valeurs détectées :** {value_candidates if value_candidates else 'Aucune'}")
        
        # ================================
        # 3. Sélection manuelle des colonnes
        # ================================
        st.write("### ⚙️ Sélection manuelle des colonnes :")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélection de la colonne date
            date_col = st.selectbox(
                "Colonne Date :",
                df_raw.columns,
                index=0 if df_raw.columns[0] in date_candidates else 0,
                help="Sélectionnez la colonne contenant les dates"
            )
        
        with col2:
            # Sélection de la colonne valeur
            # Exclure la colonne date sélectionnée
            value_options = [col for col in df_raw.columns if col != date_col]
            value_col = st.selectbox(
                "Colonne Valeur :",
                value_options,
                index=0 if value_options[0] in value_candidates else 0,
                help="Sélectionnez la colonne contenant les valeurs numériques"
            )
        
        # ================================
        # 4. Options de nettoyage
        # ================================
        st.write("### 🧹 Options de nettoyage :")
        
        clean_options = st.checkbox("Appliquer le nettoyage automatique", value=True)
        
        if clean_options:
            col1, col2 = st.columns(2)
            with col1:
                remove_na = st.checkbox("Supprimer les valeurs manquantes", value=True)
            with col2:
                sort_dates = st.checkbox("Trier par date", value=True)
        
        # ================================
        # 5. Bouton de chargement
        # ================================
        if st.button("📥 Charger la série", type="primary"):
            try:
                with st.spinner("Chargement et nettoyage en cours..."):
                    df = df_raw.copy()
                    
                    # 1. Nettoyer la colonne valeur
                    st.write("**Étape 1 :** Nettoyage des valeurs numériques...")
                    
                    # Fonction de nettoyage robuste
                    def clean_numeric_value(x):
                        if pd.isna(x):
                            return np.nan
                        try:
                            # Convertir en chaîne
                            x_str = str(x)
                            # Supprimer les espaces
                            x_str = x_str.strip()
                            # Remplacer les virgules par des points
                            x_str = x_str.replace(',', '.')
                            # Supprimer les caractères non numériques (sauf . et -)
                            x_str = ''.join(char for char in x_str if char.isdigit() or char in ['.', '-'])
                            # Convertir en float
                            return float(x_str) if x_str not in ['', '.', '-'] else np.nan
                        except:
                            return np.nan
                    
                    # Appliquer le nettoyage
                    df[value_col] = df[value_col].apply(clean_numeric_value)
                    
                    # 2. Nettoyer la colonne date
                    st.write("**Étape 2 :** Conversion des dates...")
                    
                    # Essayer différents formats de date
                    date_formats = [
                        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y',
                        '%Y.%m.%d', '%d.%m.%Y', '%m.%d.%Y',
                        '%Y %m %d', '%d %m %Y', '%m %d %Y',
                        '%Y-%m', '%Y/%m', '%m-%Y', '%m/%Y'
                    ]
                    
                    date_converted = False
                    for date_format in date_formats:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col], format=date_format, errors='raise')
                            date_converted = True
                            st.write(f"✅ Format détecté: {date_format}")
                            break
                        except:
                            continue
                    
                    # Si aucun format spécifique ne fonctionne, utiliser l'inférence
                    if not date_converted:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        st.write("ℹ️ Format de date inféré automatiquement")
                    
                    # 3. Nettoyage supplémentaire
                    if remove_na:
                        initial_count = len(df)
                        df = df.dropna(subset=[date_col, value_col])
                        final_count = len(df)
                        st.write(f"**Étape 3 :** Suppression des valeurs manquantes ({initial_count - final_count} lignes supprimées)")
                    
                    # 4. Trier par date
                    if sort_dates:
                        df = df.sort_values(date_col)
                        st.write("**Étape 4 :** Tri par date effectué")
                    
                    # 5. Définir l'index et créer la série
                    df = df.set_index(date_col)
                    series = df[value_col]
                    
                    # 6. Stocker dans session_state
                    st.session_state["series"] = series
                    st.session_state["df_loaded"] = df
                    st.session_state["date_col"] = date_col
                    st.session_state["value_col"] = value_col
                    
                    # 7. Afficher les résultats
                    st.success("✅ Série chargée avec succès !")
                    
                    # Informations sur la série
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📅 Période", 
                                 f"{series.index[0].strftime('%Y-%m')} → {series.index[-1].strftime('%Y-%m')}")
                    with col2:
                        st.metric("📊 Observations", len(series))
                    with col3:
                        st.metric("🔢 Valeurs manquantes", series.isna().sum())
                    
                    # Graphique
                    st.write("### 📈 Visualisation de la série :")
                    st.line_chart(series)
                    
                    # Aperçu des données
                    with st.expander("📋 Voir les données brutes"):
                        st.dataframe(df.head(10))
                    
                    # Télécharger les données nettoyées
                    csv = df.to_csv()
                    st.download_button(
                        label="💾 Télécharger les données nettoyées (CSV)",
                        data=csv,
                        file_name="donnees_nettoyees.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {str(e)}")
                st.write("**Détails de l'erreur :**")
                st.code(str(e))
                
                # Aide au débogage
                with st.expander("🛠️ Aide au débogage"):
                    st.write("""
                    **Problèmes courants :**
                    1. **Format de date incorrect** : Vérifiez que la colonne date contient bien des dates
                    2. **Séparateur décimal** : Les nombres doivent utiliser le point (.) pas la virgule (,)
                    3. **En-têtes dupliqués** : Vérifiez que les noms de colonnes sont uniques
                    4. **Fichier corrompu** : Réenregistrez votre fichier CSV
                    
                    **Solution rapide :**
                    - Ouvrez votre fichier dans Excel/LibreOffice
                    - Vérifiez les formats de cellules
                    - Réenregistrez en CSV UTF-8
                    - Réessayez
                    """)
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {str(e)}")
        st.write("Essayez de :")
        st.write("1. Réenregistrer le fichier en CSV UTF-8")
        st.write("2. Vérifier que le séparateur est correct (, ou ;)")
        st.write("3. Ouvrir le fichier dans Excel et le réenregistrer")

else:
    # Message d'instructions
    st.info("""
    ### 📋 Instructions pour l'importation :
    
    1. **Préparez votre fichier** :
       - Format : CSV ou Excel (.xlsx, .xls)
       - Encodage : UTF-8 recommandé
       - Séparateur : Virgule (,) ou point-virgule (;)
    
    2. **Structure requise** :
       - Une colonne avec les **dates** (ex: 2020-01, 2020-02, ...)
       - Une colonne avec les **valeurs numériques** (ex: 100.5, 150.2, ...)
    
    3. **Formats de date acceptés** :
       - 2020-01-15 (AAAA-MM-JJ)
       - 15/01/2020 (JJ/MM/AAAA)
       - 2020-01 (AAAA-MM)
       - Jan-2020 (MMM-AAAA)
    
    4. **Formats numériques** :
       - Décimal avec point : 123.45 ✓
       - Décimal avec virgule : 123,45 → sera converti automatiquement
    """)
    
    # Exemple de données
    with st.expander("📝 Exemple de format CSV correct"):
        example_data = """date,valeur
2020-01,100.5
2020-02,150.2
2020-03,120.8
2020-04,180.3
2020-05,200.1"""
        st.code(example_data, language='csv')
        
        # Bouton pour télécharger l'exemple
        st.download_button(
            label="📥 Télécharger l'exemple (CSV)",
            data=example_data,
            file_name="exemple_serie_temporelle.csv",
            mime="text/csv"
        )

# ================================
# 6. Réinitialisation
# ================================
if st.button("🔄 Réinitialiser les données"):
    keys_to_remove = ['series', 'df_raw', 'df_loaded', 'date_col', 'value_col']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Données réinitialisées !")
    st.rerun()

# Footer
st.markdown("---")
st.caption("💡 Astuce : Après chargement, utilisez les autres onglets pour analyser vos données.")