import threading
import time
import subprocess
import sys
import os
import webbrowser
from datetime import datetime
import signal

class DesktopAppSimple:
    def __init__(self):
        self.streamlit_process = None
        self.is_running = True
        
    def check_dependencies(self):
        """Vérifie les dépendances essentielles"""
        required_modules = ['streamlit', 'pandas', 'numpy']
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            print(f"❌ Modules manquants: {', '.join(missing)}")
            return False
        return True
    
    def start_streamlit(self):
        """Démarre Streamlit simplement"""
        try:
            print("🚀 Démarrage de l'application Streamlit...")
            
            # Commande simplifiée
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                "app.py",
                "--server.port=8501",
                "--server.headless=false",
                "--browser.serverAddress=localhost",
                "--theme.base=light"
            ]
            
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            print("✅ Application démarrée sur http://localhost:8501")
            
            # Afficher les logs
            def log_output():
                while self.is_running:
                    try:
                        line = self.streamlit_process.stdout.readline()
                        if line:
                            print(f"[App] {line.strip()}")
                    except:
                        break
            
            threading.Thread(target=log_output, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def open_browser(self):
        """Ouvre le navigateur"""
        time.sleep(2)
        try:
            webbrowser.open("http://localhost:8501")
            print("🌐 Navigateur ouvert automatiquement")
        except:
            print("➡️ Ouvrez manuellement: http://localhost:8501")
    
    def run(self):
        """Exécute l'application"""
        print("=" * 60)
        print("📊 APPLICATION STATISTIQUE")
        print("=" * 60)
        print(f"Démarrée le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Vérifier app.py
        if not os.path.exists("app.py"):
            print("❌ ERREUR: app.py non trouvé!")
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Vérifier dépendances
        if not self.check_dependencies():
            print("\n💡 Installez les dépendances avec:")
            print("pip install streamlit pandas numpy matplotlib")
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Démarrer
        if not self.start_streamlit():
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        # Ouvrir navigateur
        threading.Thread(target=self.open_browser, daemon=True).start()
        
        print("\n" + "=" * 60)
        print("✅ APPLICATION PRÊTE !")
        print("=" * 60)
        print("\n📋 COMMANDES UTILES:")
        print("• Ctrl+C → Arrêter l'application")
        print("• R → Redémarrer l'application")
        print("• Q → Quitter")
        print("\n🌐 Interface: http://localhost:8501")
        print("-" * 60)
        
        # Gestion des commandes
        try:
            while self.is_running:
                cmd = input("\nCommande [R=redémarrer, Q=quitter]: ").strip().upper()
                
                if cmd == 'Q':
                    print("🛑 Fermeture...")
                    break
                elif cmd == 'R':
                    print("🔄 Redémarrage...")
                    if self.streamlit_process:
                        self.streamlit_process.terminate()
                    self.streamlit_process = None
                    time.sleep(1)
                    self.start_streamlit()
                else:
                    print("❓ Commande inconnue. Options: R, Q")
        
        except KeyboardInterrupt:
            print("\n🛑 Interruption par l'utilisateur")
        
        finally:
            # Nettoyage
            self.is_running = False
            if self.streamlit_process:
                self.streamlit_process.terminate()
                print("✅ Application arrêtée proprement")
    
    def cleanup(self):
        """Nettoyage"""
        self.is_running = False
        if self.streamlit_process:
            self.streamlit_process.terminate()

def main():
    app = DesktopAppSimple()
    
    # Gestion de Ctrl+C
    def signal_handler(sig, frame):
        print("\n🛑 Signal d'interruption reçu")
        app.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        app.run()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        app.cleanup()
    finally:
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()