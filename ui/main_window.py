"""
main_window.py — Fenêtre principale de CodeDojo.
Assemble : Challenges | Éditeur Java | Sensei IA

v2 changes:
  - Solved-once guard: points awarded only on FIRST solve per challenge
  - Unlock system: intermediate/advanced tiers unlock progressively
  - Achievement system: prizes displayed as animated toasts
"""
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt, QFile, QTextStream, QThread, Signal
from PySide6.QtGui import QPainter, QPixmap, QColor

from ui.status_bar import HeaderBar
from ui.challenge_panel import ChallengePanel
from ui.editor_panel import EditorPanel
from ui.ai_panel import AIPanel


class CentralGlassWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("centralWidget")
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._bg_path = os.path.join(base, "assets", "app_bg.png")

    def set_bg_path(self, path: str):
        self._bg_path = path
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        pixmap = QPixmap(self._bg_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(self.rect(), QColor("#F9F6F0"))
        painter.end()


def _load_stylesheet() -> str:
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
    # Keywords used as a heuristic for AI-path success detection
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
        from services.achievement_service import AchievementService
        self.verifier = VerificationService()
        self.achievement_svc = AchievementService(repo)

        self.setWindowTitle("CodeDojo  ⛩")
        self.setMinimumSize(1000, 580)
        self.resize(1100, 620)

        self._build_ui()
        self._init_groq()
        self._load_global_stylesheet()
        self._load_challenges()

    # ── Init helpers ──────────────────────────────────────────────────────────

    def _init_groq(self):
        """Initialise le service d'IA (Groq ou Gemini) depuis l'environnement."""
        try:
            from services.groq_service import GroqService
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            if api_key:
                provider_label = "Google Gemini · gemini-1.5-flash · Méthode socratique"
            else:
                api_key = os.environ.get("GROQ_API_KEY", "").strip()
                provider_label = "Groq · LLaMA 3.3 · Méthode socratique"

            if not api_key:
                print("[Dojo AI] [Warning] Aucune clé API configurée.")
                return

            self.groq = GroqService(api_key=api_key)
            if hasattr(self, 'ai_panel'):
                self.ai_panel.set_provider_label(provider_label)
            print("[Dojo AI] [OK] Service IA initialisé.")
        except Exception as e:
            print(f"[Dojo AI] Non disponible : {e}")

    def _build_ui(self):
        root_widget = CentralGlassWidget()
        self.setCentralWidget(root_widget)

        root = QVBoxLayout(root_widget)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        self.header = HeaderBar(
            self.user,
            self._toggle_challenges,
            self._toggle_sensei,
            self._open_settings,
            self._on_logout_click
        )
        root.addWidget(self.header)

        body = QWidget()
        body.setAttribute(Qt.WA_TranslucentBackground)
        blay = QHBoxLayout(body)
        blay.setContentsMargins(0, 0, 0, 0)
        blay.setSpacing(14)

        self.challenge_panel = ChallengePanel(self._on_challenge)
        self.challenge_panel.setFixedHeight(450)
        self.editor_panel = EditorPanel(self._on_submit, self._on_verify)
        self.ai_panel = AIPanel()
        self.ai_panel.setFixedHeight(500)
        self.ai_panel.setVisible(False)

        blay.addWidget(self.challenge_panel, alignment=Qt.AlignTop)
        blay.addWidget(self.editor_panel)
        blay.addWidget(self.ai_panel, alignment=Qt.AlignTop)
        root.addWidget(body)

    def _load_global_stylesheet(self):
        qss = _load_stylesheet()
        if qss:
            self.setStyleSheet(qss)

    def _load_challenges(self):
        """Load challenges and mark which ones the current user has already solved."""
        challenges = self.repo.get_all_challenges()
        solved_ids = self.repo.get_solved_challenge_ids(self.user.id)
        self.challenge_panel.load(challenges, solved_ids)

    def _refresh_challenge_panel(self):
        """Refresh lock/checkmark state after a solve."""
        solved_ids = self.repo.get_solved_challenge_ids(self.user.id)
        self.challenge_panel.update_solved(solved_ids)

    # ── Panel toggles ─────────────────────────────────────────────────────────

    def _toggle_challenges(self):
        self.challenge_panel.setVisible(not self.challenge_panel.isVisible())

    def _toggle_sensei(self):
        self.ai_panel.setVisible(not self.ai_panel.isVisible())

    def set_background(self, path: str):
        central = self.centralWidget()
        if isinstance(central, CentralGlassWidget):
            central.set_bg_path(path)

    # ── Challenge selection ───────────────────────────────────────────────────

    def _on_challenge(self, challenge):
        """Challenge selected — reset history, create session, start timer."""
        # Penalize abandoning an active unsolved session
        if self.session_id is not None and self.header._running:
            self.user.points = max(0, self.user.points - 5)
            self.repo.update_points(self.user.id, -5)
            self.user = self.repo.refresh_user(self.user.id)
            self.header.refresh(self.user)
            self.ai_panel.setVisible(True)
            self.ai_panel.add_sensei("Tu as abandonné le défi en cours… Tu perds 5 points !")
            self.session_id = None

        self.editor_panel.load(challenge)
        self._conversation_history = []

        if self.user.id:
            self.session_id = self.repo.create_session(self.user.id, challenge.id)

        # Show "already solved" hint in AI panel
        if self.repo.has_solved(self.user.id, challenge.id):
            self.ai_panel.setVisible(True)
            self.ai_panel.add_sensei(
                f"✅ Tu as déjà résolu «{challenge.title}».\n\n"
                "Tu peux t'entraîner à nouveau, mais les points ne seront "
                "pas comptés une deuxième fois. Bonne pratique !"
            )

        self.header.reset_and_start_timer()

    # ── AI submit path ────────────────────────────────────────────────────────

    def _on_submit(self, code: str, challenge):
        """Submit code to Sensei AI for socratic feedback."""
        self.ai_panel.setVisible(True)
        self.ai_panel.add_user(code)
        self.ai_panel.show_thinking()

        if self.groq:
            from services.groq_worker import GroqWorker
            from ui.settings_dialog import load_settings
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
                "Configure ta clé API dans Paramètres et redémarre."
            )
            self.editor_panel.enable_submit()

    def _on_response(self, text: str):
        """Sensei response received — update UI and conversation history."""
        self.ai_panel.hide_thinking()
        self.ai_panel.add_sensei(text)

        code = self.editor_panel.editor.toPlainText()
        self._conversation_history.append({"role": "user", "content": code})
        self._conversation_history.append({"role": "assistant", "content": text})

        if self.session_id:
            self.repo.save_message(self.session_id, 'user', code)
            self.repo.save_message(self.session_id, 'assistant', text)

        # Heuristic success detection via AI keywords
        if any(kw in text.lower() for kw in self.SUCCESS_KEYWORDS):
            ch = self.editor_panel.current_challenge
            if ch and self.session_id:
                self._award_solve(ch, via="ai")

    def _on_error(self, error: str):
        self.ai_panel.hide_thinking()
        self.ai_panel.show_error(error)

    # ── Verify (compiler) path ────────────────────────────────────────────────

    def _on_verify(self, code: str, challenge):
        """Submit code to Java compiler for HackerRank-style test runner."""
        self.ai_panel.setVisible(True)
        self.ai_panel.show_thinking()

        self.verify_worker = VerificationWorker(self.verifier, challenge, code)
        self.verify_worker.finished.connect(
            lambda res: self._on_verify_finished(res, challenge)
        )
        self.verify_worker.finished.connect(self.editor_panel.enable_verify)
        self.verify_worker.start()

    def _on_verify_finished(self, result: dict, challenge):
        self.ai_panel.hide_thinking()
        self.ai_panel.add_verification_result(result)

        if result.get("success", False):
            if self.session_id:
                self.repo.save_message(
                    self.session_id, 'assistant',
                    "Code vérifié avec succès via le compilateur !"
                )
            self._award_solve(challenge, via="verify")

    # ── Core solve logic (SINGLE SOURCE OF TRUTH) ─────────────────────────────

    def _award_solve(self, challenge, via: str = "verify"):
        """
        Called when a challenge is solved (by either the AI path or verify path).

        Rules:
          • mark_challenge_solved() returns True only on FIRST solve.
          • Points are awarded ONLY if it's a first solve.
          • Achievements are always evaluated (they check their own conditions).
          • The challenge panel is refreshed so the ✅ appears immediately.
        """
        is_first_solve = self.repo.mark_challenge_solved(self.user.id, challenge.id)

        if self.session_id:
            points_to_record = challenge.points if is_first_solve else 0
            self.repo.mark_session_solved(self.session_id, points_to_record)

        if is_first_solve:
            self.repo.update_points(self.user.id, challenge.points)
            self.user = self.repo.refresh_user(self.user.id)
            self.header.refresh(self.user)
            self.ai_panel.show_success(challenge.points)
        else:
            # Re-solve: refresh user data but no points
            self.user = self.repo.refresh_user(self.user.id)
            self.ai_panel.show_already_solved()

        # Always check achievements (they have their own guards against re-award)
        new_achievements = self.achievement_svc.evaluate_after_solve(
            self.user, challenge, self.session_id
        )
        if new_achievements:
            from ui.achievement_popup import show_achievements
            show_achievements(new_achievements, parent=self.centralWidget())

        # Refresh challenge panel locks and checkmarks
        self._refresh_challenge_panel()

        # Clean up session state
        self.session_id = None
        self.header.stop_timer()

    # ── Settings & logout ─────────────────────────────────────────────────────

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        if dlg.exec():
            self._init_groq()

    def _on_logout_click(self):
        if self.logout_callback:
            self.logout_callback()