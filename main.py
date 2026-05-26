"""
CodeDojo — Point d'entrée principal.
Flux : Splash Screen → Login → Guide (1ère fois) → Main Window
Lance avec : python main.py  (ou run.bat)
"""
import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from repository.mysql_repo import MySQLRepository
from services.auth_service import AuthService
from ui.splash_screen import SplashScreen
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def main():
    # Charger les variables d'environnement AVANT tout le reste
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)

    # Charger les paramètres utilisateur (Clé API) depuis settings.json
    try:
        from ui.settings_dialog import load_settings
        cfg = load_settings()
        api_key = cfg.get("api_key", "").strip()
        if api_key:
            # Route the key to the correct provider based on prefix
            if api_key.startswith("AIzaSy"):
                os.environ["GEMINI_API_KEY"] = api_key
                os.environ.pop("GROQ_API_KEY", None)
            else:
                os.environ["GROQ_API_KEY"] = api_key
                os.environ.pop("GEMINI_API_KEY", None)
    except Exception as e:
        print(f"[Main] Erreur chargement settings : {e}")

    app = QApplication(sys.argv)
    app.setApplicationName("CodeDojo")
    app.setStyle("Fusion")

    # Initialisation des services partagés
    repo = MySQLRepository()
    auth = AuthService(repo)

    # Références aux fenêtres (évite le garbage-collect)
    main_win_ref = [None]
    splash_ref = [None]
    login_ref = [None]

    def on_logout():
        """Déconnecte l'utilisateur et rouvre le panneau de connexion."""
        if main_win_ref[0]:
            main_win_ref[0].close()
            main_win_ref[0] = None
        login_ref[0].username.clear()
        login_ref[0].password.clear()
        login_ref[0].msg.clear()
        login_ref[0].btn_login.setEnabled(True)
        login_ref[0].btn_signup.setEnabled(True)
        login_ref[0].show()

    def on_login_success(user):
        """Callback déclenché après authentification réussie."""
        from ui.guide_dialog import GuideDialog, has_seen_guide

        # Afficher le guide si c'est la première connexion
        if not has_seen_guide(user.username):
            guide = GuideDialog(user.username, login_ref[0])
            guide.exec()  # Bloquant — attend que l'utilisateur finisse le guide

        # Ouvrir la fenêtre principale
        win = MainWindow(user, repo, logout_callback=on_logout)
        main_win_ref[0] = win
        win.showMaximized()
        login_ref[0].close()

    def on_splash_ready():
        """Callback déclenché quand le splash est terminé."""
        splash_ref[0].close()
        login_ref[0] = LoginWindow(auth, on_login_success)
        login_ref[0].show()

    # ── Lancement : Splash Screen d'abord ────────────────────────────────────
    splash_ref[0] = SplashScreen(on_splash_ready)
    splash_ref[0].show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()