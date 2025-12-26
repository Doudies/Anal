import webview
import threading
import time
import subprocess
import sys
import os
import webbrowser

def run_streamlit():
    """Lance Streamlit en arrière-plan"""
    try:
        # Démarrer Streamlit avec le fichier principal
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", 
                       "--server.port=8501", "--server.headless=false", 
                       "--browser.serverAddress=localhost", "--theme.base=light"],
                      check=True)
    except Exception as e:
        print(f"Erreur Streamlit: {e}")

def open_browser():
    """Ouvre automatiquement le navigateur"""
    time.sleep(2)  # Attendre que Streamlit démarre
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    print("🚀 Démarrage de l'application statistique...")
    
    # Vérifier que app.py existe
    if not os.path.exists("app.py"):
        print("❌ Erreur: app.py non trouvé")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Démarrer Streamlit dans un thread
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Ouvrir le navigateur
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Créer la fenêtre desktop
    window = webview.create_window(
        "📊 Application Statistique - Analyse de Séries Temporelles",
        "http://localhost:8501",
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    
    print("✅ Application prête. Fermez la fenêtre pour quitter.")
    webview.start()