# app.py - FICHIER MODIFIÉ
import sys
import os
import streamlit as st

# === Fix pour importer le dossier src ===
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Configuration de l'application
st.set_page_config(
    page_title="📊 Application de Prévision des Séries Temporelles",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📈 Application de Prévision des Séries Temporelles")
st.markdown("---")

# Description
st.markdown("""
### 🚀 Projet Master ROMARIN – Application Streamlit

**Fonctionnalités disponibles :**

1. **📂 Importation** - Chargez vos fichiers CSV
2. **📊 Analyse Exploratoire** - Statistiques descriptives et visualisation
3. **📐 Tests de Stationnarité** - ADF, KPSS, décomposition
4. **📎 Modèles Classiques** - Moyennes mobiles, régression linéaire
5. **🔧 Modélisation & Prévisions** - Lissage exponentiel, Holt-Winters
6. **🧪 Tests & Validation** - Validation croisée, analyse des résidus

---

### 📌 Instructions rapides :
1. Commencez par l'onglet **"1. Importation"** pour charger vos données
2. Naviguez dans l'ordre des onglets pour l'analyse complète
3. Exportez vos résultats depuis chaque section

---
""")

# Vérification des pages disponibles
with st.expander("🔍 Vérification du système", expanded=False):
    st.write("**Système en cours d'exécution :**")
    st.write(f"- Python: {sys.version}")
    st.write(f"- Répertoire: {ROOT}")
    
    # Vérifier les pages
    pages_dir = os.path.join(ROOT, "pages")
    if os.path.exists(pages_dir):
        pages = [f for f in os.listdir(pages_dir) if f.endswith('.py')]
        st.write(f"- Pages détectées: {len(pages)}")
        for page in sorted(pages):
            st.write(f"  • {page}")
    else:
        st.error("❌ Dossier 'pages' non trouvé !")
    
    # Vérifier src
    src_dir = os.path.join(ROOT, "src")
    if os.path.exists(src_dir):
        st.success("✅ Dossier 'src' détecté")
    else:
        st.warning("⚠️ Dossier 'src' non trouvé")

# Message de navigation
st.sidebar.success("⬅️ Sélectionnez une page dans la sidebar pour commencer l'analyse.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "📊 Application Desktop - Version 1.0<br>"
    "Projet Master ROMARIN © 2024"
    "</div>",
    unsafe_allow_html=True
)