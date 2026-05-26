"""
main_window.py — Fenêtre principale de CodeDojo avec effet Glassmorphism & arrière-plan Lofi.
Assemble les composants modulaires : Challenges | Éditeur Java | Sensei IA
"""
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream, QThread, Signal
from PySide6.QtGui import QPainter, QPixmap, QColor

from ui.status_bar import HeaderBar
from ui.challenge_panel import ChallengePanel
from ui.editor_panel import EditorPanel
from ui.ai_panel import AIPanel


class CentralGlassWidget(QWidget):
    """
    Widget central qui dessine l'image lofi en arrière-plan étirée
    pour un effet immersif d'ambiance Dojo Lofi.
    Supporte le changement dynamique du fond via set_bg_path().
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("centralWidget")
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._bg_path = os.path.join(base, "assets", "app_bg.png")

    def set_bg_path(self, path: str):
        """Change le fond d'écran et redessine immédiatement."""
        self._bg_path = path
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        pixmap = QPixmap(self._bg_path)
        if not pixmap.isNull():
            # Redimensionne en conservant l'aspect ratio (sans étirer)
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            # Centrer le pixmap
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Fallback clair si l'image n'est pas chargée
            painter.fillRect(self.rect(), QColor("#F9F6F0"))
        painter.end()


def _load_stylesheet() -> str:
    """Charge le fichier assets/style.qss depuis la racine du projet."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qss_path = os.path.join(base, "assets", "style.qss")
    f = QFile(qss_path)
    if f.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(f)
        content = stream.readAll()
        f.close()
        return content
    return ""


class VerificationWorker(QThread):
    finished = Signal(dict)

    def __init__(self, verifier, challenge, code):
        super().__init__()
        self.verifier = verifier
        self.challenge = challenge
        self.code = code

    def run(self):
        res = self.verifier.verify(self.challenge, self.code)
        self.finished.emit(res)


class MainWindow(QMainWindow):
    SUCCESS_KEYWORDS = ['correct', 'parfait', 'bravo', 'excellent', 'félicitations']

    def __init__(self, user, repo, logout_callback=None):
        super().__init__()
        self.user = user
        self.repo = repo
        self.logout_callback = logout_callback
        self.session_id = None
        self.groq = None
        self.worker = None
        self._conversation_history = []

        from services.verification_service import VerificationService
        self.verifier = VerificationService()

        self.setWindowTitle("CodeDojo  ⛩")
        self.setMinimumSize(1000, 580)
        self.resize(1100, 620)

        self._init_groq()
        self._build_ui()
        self._load_global_stylesheet()
        self._load_challenges()

    def _init_groq(self):
        """Initialise le service d'IA (Groq ou Gemini) depuis l'environnement."""
        try:
            from services.groq_service import GroqService
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            if not api_key:
                api_key = os.environ.get("GROQ_API_KEY", "").strip()

            if not api_key:
                print("[Dojo AI] [Warning] GEMINI_API_KEY ou GROQ_API_KEY manquante dans .env")
                return

            self.groq = GroqService(api_key=api_key)
            print("[Dojo AI] [OK] Service d'intelligence artificielle initialisé avec succès.")
        except Exception as e:
            print(f"[Dojo AI] Non disponible : {e}")

    def set_background(self, path: str):
        """Change le fond d'écran de l'application à la volée."""
        central = self.centralWidget()
        if isinstance(central, CentralGlassWidget):
            central.set_bg_path(path)

    def _build_ui(self):
        # Utilisation de notre widget de fond Lofi
        root_widget = CentralGlassWidget()
        self.setCentralWidget(root_widget)

        # Layout principal avec des marges pour créer l'effet "floating"
        root = QVBoxLayout(root_widget)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # En-tête avec callbacks de masquage / affichage des panneaux, paramètres et déconnexion
        self.header = HeaderBar(
            self.user,
            self._toggle_challenges,
            self._toggle_sensei,
            self._open_settings,
            self._on_logout_click
        )
        root.addWidget(self.header)

        # Corps de l'application (contient les panneaux flottants en verre)
        body = QWidget()
        body.setAttribute(Qt.WA_TranslucentBackground)
        blay = QHBoxLayout(body)
        blay.setContentsMargins(0, 0, 0, 0)
        blay.setSpacing(14)  # Espace entre les fenêtres flottantes

        self.challenge_panel = ChallengePanel(self._on_challenge)
        self.challenge_panel.setFixedHeight(450)
        self.editor_panel = EditorPanel(self._on_submit, self._on_verify)
        self.ai_panel = AIPanel()
        self.ai_panel.setFixedHeight(500)

        # Par défaut, le tuteur IA est masqué au lancement (il apparaît quand on écrit/clique)
        self.ai_panel.setVisible(False)

        blay.addWidget(self.challenge_panel, alignment=Qt.AlignTop)
        blay.addWidget(self.editor_panel)
        blay.addWidget(self.ai_panel, alignment=Qt.AlignTop)

        root.addWidget(body)

    def _load_global_stylesheet(self):
        qss = _load_stylesheet()
        if qss:
            self.setStyleSheet(qss)
        else:
            print("[Style] [Warning] assets/style.qss introuvable.")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def _load_challenges(self):
        challenges = self.repo.get_all_challenges()
        self.challenge_panel.load(challenges)

    # ── GESTION DES VOLETS FLOTTANTS (COLLAPSIBLE) ───────────────────────────

    def _toggle_challenges(self):
        """Bascule l'affichage du volet des défis."""
        is_visible = self.challenge_panel.isVisible()
        self.challenge_panel.setVisible(not is_visible)

    def _toggle_sensei(self):
        """Bascule l'affichage du volet du Sensei IA."""
        is_visible = self.ai_panel.isVisible()
        self.ai_panel.setVisible(not is_visible)

    # ── WIRING ────────────────────────────────────────────────────────────────

    def _on_challenge(self, challenge):
        """Nouveau challenge sélectionné — réinitialise l'historique et crée la session."""
        if self.session_id and self.header._running:
            self.user.points = max(0, self.user.points - 5)
            self.repo.update_points(self.user.id, -5)
            self.header.refresh(self.user)
            self.ai_panel.setVisible(True)
            self.ai_panel.add_sensei("Tu as abandonné le défi en cours... Tu perds 5 points !")
            
        self.editor_panel.load(challenge)
        self._conversation_history = []
        if self.user.id:
            self.session_id = self.repo.create_session(self.user.id, challenge.id)
            
        # Réinitialiser et démarrer automatiquement le compteur
        self.header.reset_and_start_timer()

    def _on_submit(self, code: str, challenge):
        """L'élève soumet son code — affiche l'IA automatiquement et lance l'analyse."""
        # Affiche automatiquement l'IA si elle était cachée
        self.ai_panel.setVisible(True)

        self.ai_panel.add_user(code)
        self.ai_panel.show_thinking()

        if self.groq:
            from services.groq_worker import GroqWorker
            from ui.settings_dialog import load_settings
            
            # Lire la difficulté configurée dans settings.json
            cfg = load_settings()
            difficulty = cfg.get("ai_difficulty", "beginner")

            self.worker = GroqWorker(
                groq_service=self.groq,
                user_message="Voici mon code, qu'en penses-tu ?",
                challenge=challenge,
                submitted_code=code,
                conversation_history=list(self._conversation_history),
                difficulty=difficulty
            )
            self.worker.response_ready.connect(self._on_response)
            self.worker.error_occurred.connect(self._on_error)
            self.worker.finished.connect(self.editor_panel.enable_submit)
            self.worker.start()
        else:
            self.ai_panel.hide_thinking()
            self.ai_panel.add_sensei(
                "Le service d'IA n'est pas disponible.\n\n"
                "Ajoute GEMINI_API_KEY ou GROQ_API_KEY dans ton fichier .env et redémarre."
            )
            self.editor_panel.enable_submit()

    def _on_response(self, text: str):
        """Réponse du Sensei reçue — met à jour l'UI et l'historique."""
        self.ai_panel.hide_thinking()
        self.ai_panel.add_sensei(text)

        code = self.editor_panel.editor.toPlainText()
        self._conversation_history.append({"role": "user", "content": code})
        self._conversation_history.append({"role": "assistant", "content": text})

        if self.session_id:
            self.repo.save_message(self.session_id, 'user', code)
            self.repo.save_message(self.session_id, 'assistant', text)

        # Détection de solution correcte
        if any(kw in text.lower() for kw in self.SUCCESS_KEYWORDS):
            ch = self.editor_panel.current_challenge
            if ch and self.session_id:
                self.repo.mark_session_solved(self.session_id, ch.points)
                self.repo.update_points(self.user.id, ch.points)
                self.user = self.repo.refresh_user(self.user.id)
                self.header.refresh(self.user)
                self.ai_panel.show_success(ch.points)
                self.session_id = None
                self.header.stop_timer()

    def _on_error(self, error: str):
        """Erreur IA — affiche l'erreur."""
        self.ai_panel.hide_thinking()
        self.ai_panel.show_error(error)

    def _on_verify(self, code: str, challenge):
        """L'élève clique sur le bouton de vérification HackerRank."""
        self.ai_panel.setVisible(True)
        self.ai_panel.show_thinking()
        
        # Lancement de la vérification dans un QThread pour éviter de figer l'UI
        self.verify_worker = VerificationWorker(self.verifier, challenge, code)
        self.verify_worker.finished.connect(lambda res: self._on_verify_finished(res, challenge))
        self.verify_worker.finished.connect(self.editor_panel.enable_verify)
        self.verify_worker.start()

    def _on_verify_finished(self, result: dict, challenge):
        self.ai_panel.hide_thinking()
        self.ai_panel.add_verification_result(result)
        
        # Si le test a réussi, on marque la session comme résolue, on donne les points!
        if result.get("success", False):
            if self.session_id:
                # Enregistrer le message de succès dans la DB
                self.repo.save_message(self.session_id, 'assistant', "Code vérifié avec succès via le compilateur !")
                
                # Marquer la session résolue
                self.repo.mark_session_solved(self.session_id, challenge.points)
                self.repo.update_points(self.user.id, challenge.points)
                self.user = self.repo.refresh_user(self.user.id)
                self.header.refresh(self.user)
                self.ai_panel.show_success(challenge.points)

    # ── PARAMÈTRES & DÉCONNEXION ─────────────────────────────────────────────

    def _open_settings(self):
        """Ouvre la boîte de dialogue de configuration de l'IA."""
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        if dlg.exec():
            print("[MainWindow] Paramètres enregistrés. Reconfiguration du service IA...")
            self._init_groq()

    def _on_logout_click(self):
        """Déclenche le callback de déconnexion."""
        if self.logout_callback:
            self.logout_callback()