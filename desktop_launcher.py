# desktop_launcher.py - NOUVEAU FICHIER
import webview
import threading
import time
import subprocess
import sys
import os
import webbrowser
from datetime import datetime

class DesktopApp:
    def __init__(self):
        self.streamlit_process = None
        self.is_running = False
        
    def check_dependencies(self):
        """Vérifie que toutes les dépendances sont installées"""
        required_modules = [
            'streamlit', 'pandas', 'numpy', 'matplotlib',
            'statsmodels', 'scipy', 'sklearn'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            print(f"❌ Modules manquants: {', '.join(missing)}")
            print("Installez-les avec: pip install " + " ".join(missing))
            return False
        return True
    
    def start_streamlit(self):
        """Démarre Streamlit en arrière-plan"""
        try:
            print("🚀 Démarrage du serveur Streamlit...")
            
            # Commandes pour démarrer Streamlit
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                "app.py",
                "--server.port=8501",
                "--server.headless=false",
                "--browser.serverAddress=localhost",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false",
                "--theme.base=light"
            ]
            
            # Lancer le processus
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            self.is_running = True
            print("✅ Serveur Streamlit démarré sur http://localhost:8501")
            
            # Afficher les logs en temps réel
            def log_output():
                for line in self.streamlit_process.stdout:
                    print(f"[Streamlit] {line.strip()}")
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de Streamlit: {e}")
            return False
    
    def open_browser(self):
        """Ouvre le navigateur après un délai"""
        time.sleep(3)  # Attendre que le serveur démarre
        try:
            webbrowser.open("http://localhost:8501")
            print("🌐 Navigateur ouvert automatiquement")
        except:
            print("⚠️ Impossible d'ouvrir le navigateur automatiquement")
            print("➡️ Ouvrez manuellement: http://localhost:8501")
    
    def cleanup(self):
        """Nettoyage à la fermeture"""
        print("\n🛑 Fermeture de l'application...")
        if self.streamlit_process:
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
            print("✅ Serveur Streamlit arrêté")
    
    def run(self):
        """Méthode principale pour exécuter l'application"""
        print("=" * 60)
        print("📊 APPLICATION STATISTIQUE DESKTOP")
        print("=" * 60)
        print(f"Démarrée le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Répertoire: {os.getcwd()}")
        print("-" * 60)
        
        # Vérifier les dépendances
        if not self.check_dependencies():
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Vérifier que app.py existe
        if not os.path.exists("app.py"):
            print("❌ ERREUR: app.py non trouvé dans le répertoire courant!")
            print("Assurez-vous que ce fichier existe dans le même dossier.")
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Démarrer Streamlit
        if not self.start_streamlit():
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Ouvrir le navigateur
        threading.Thread(target=self.open_browser, daemon=True).start()
        
        # Créer la fenêtre desktop avec WebView
        try:
            window = webview.create_window(
                "📈 Application d'Analyse Statistique",
                "http://localhost:8501",
                width=1400,
                height=900,
                resizable=True,
                fullscreen=False,
                min_size=(1000, 700),
                text_select=True
            )
            
            print("\n✅ Application prête!")
            print("• Interface: http://localhost:8501")
            print("• Taille: 1400x900 pixels")
            print("• Fermez la fenêtre pour quitter")
            print("-" * 60)
            
            # Démarrer l'interface WebView
            webview.start(debug=False)
            
        except Exception as e:
            print(f"❌ Erreur avec WebView: {e}")
            print("\n💡 Solution alternative:")
            print("1. Gardez cette fenêtre ouverte")
            print("2. Ouvrez manuellement: http://localhost:8501")
            print("3. Pour quitter, fermez cette fenêtre (Ctrl+C)")
            
            try:
                # Garder le programme en vie
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
        finally:
            # Nettoyer à la fermeture
            self.cleanup()

def main():
    """Point d'entrée principal"""
    app = DesktopApp()
    
    # Gestion propre de la fermeture
    try:
        app.run()
    except KeyboardInterrupt:
        app.cleanup()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        app.cleanup()
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()