"""
status_bar.py — Barre d'en-tête (HeaderBar) contenant le timer Pomodoro,
le score, le niveau, le nom d'utilisateur et les boutons de volets.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer

class HeaderBar(QWidget):
    def __init__(self, user, repo, on_toggle_challenges, on_toggle_sensei, on_tech, on_settings, on_logout, on_profile, on_leaderboard, on_zen_mode=None):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.user = user
        self.repo = repo
        self.on_toggle_challenges = on_toggle_challenges
        self.on_toggle_sensei = on_toggle_sensei
        self.on_tech = on_tech
        self.on_settings = on_settings
        self.on_logout = on_logout
        self.on_profile = on_profile
        self.on_leaderboard = on_leaderboard
        self.on_zen_mode = on_zen_mode
        self._seconds = 25 * 60
        self._running = False
        self._zen_active = False
        self.setFixedHeight(52)
        self.setObjectName("header")
        self._music_dialog = None   # singleton lecteur audio
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(15, 0, 15, 0)
        lay.setSpacing(10)

        # Logo Dojo
        logo = QLabel("CODEDOJO")
        logo.setObjectName("header_logo")
        lay.addWidget(logo)

        lay.addSpacing(20)

        # ── Bouton de bascule Défis (Gauche) ─────────────────────────────
        self.challenges_btn = QPushButton("Défis")
        self.challenges_btn.setObjectName("toggle_btn_header")
        self.challenges_btn.setToolTip("Afficher / Masquer la liste des défis")
        self.challenges_btn.setCursor(Qt.PointingHandCursor)
        self.challenges_btn.clicked.connect(self.on_toggle_challenges)
        lay.addWidget(self.challenges_btn)

        # ── Bouton de bascule Sensei IA (Droite) ────────────────────────
        self.sensei_btn = QPushButton("Sensei IA")
        self.sensei_btn.setObjectName("toggle_btn_header")
        self.sensei_btn.setToolTip("Afficher / Masquer le tuteur IA")
        self.sensei_btn.setCursor(Qt.PointingHandCursor)
        self.sensei_btn.clicked.connect(self.on_toggle_sensei)
        lay.addWidget(self.sensei_btn)

        # ── Bouton Fond d'écran 🖼️ ────────────────────────────────────
        self.bg_btn = QPushButton("🖼️  Fond")
        self.bg_btn.setObjectName("toggle_btn_header")
        self.bg_btn.setToolTip("Changer le fond d'écran Lofi")
        self.bg_btn.setCursor(Qt.PointingHandCursor)
        self.bg_btn.clicked.connect(self._open_bg_picker)
        lay.addWidget(self.bg_btn)

        # ── Bouton Musique 🎵 ─────────────────────────────────────────
        self.music_btn = QPushButton("🎵  Musique")
        self.music_btn.setObjectName("toggle_btn_header")
        self.music_btn.setToolTip("Lecteur de musique d'ambiance Lofi")
        self.music_btn.setCursor(Qt.PointingHandCursor)
        self.music_btn.clicked.connect(self._open_music_player)
        lay.addWidget(self.music_btn)

        # ── Bouton Classement 🏆 ─────────────────────────────────────────
        self.leaderboard_btn = QPushButton("🏆  Classement")
        self.leaderboard_btn.setObjectName("toggle_btn_header")
        self.leaderboard_btn.setToolTip("Voir le classement des guerriers du Dojo")
        self.leaderboard_btn.setCursor(Qt.PointingHandCursor)
        self.leaderboard_btn.clicked.connect(self.on_leaderboard)
        lay.addWidget(self.leaderboard_btn)

        self.tech_btn = QPushButton("Stack")
        self.tech_btn.setObjectName("tech_header_btn")
        self.tech_btn.setToolTip("Voir l'etat PySide, base de donnees et IA")
        self.tech_btn.setCursor(Qt.PointingHandCursor)
        self.tech_btn.clicked.connect(self.on_tech)
        lay.addWidget(self.tech_btn)

        # ── Bouton Mode Zen 🌿 ────────────────────────────────────────
        self.zen_btn = QPushButton("🌿  Zen")
        self.zen_btn.setObjectName("zen_btn_header")
        self.zen_btn.setToolTip("Masquer tous les panneaux — voir le paysage")
        self.zen_btn.setCursor(Qt.PointingHandCursor)
        self.zen_btn.clicked.connect(self._toggle_zen)
        lay.addWidget(self.zen_btn)

        lay.addStretch()

        # ── Pomodoro timer ──────────────────────────────────────────────
        self.timer_lbl = QLabel("25:00")
        self.timer_lbl.setObjectName("timer_label")

        self.timer_btn = QPushButton("▶")
        self.timer_btn.setObjectName("timer_btn")
        self.timer_btn.setFixedSize(26, 26)
        self.timer_btn.setCursor(Qt.PointingHandCursor)
        self.timer_btn.clicked.connect(self._toggle)
        self.timer_btn.setToolTip("Démarrer / Pauser le Pomodoro (25 min)")

        self._qt = QTimer()
        self._qt.timeout.connect(self._tick)

        lay.addWidget(self.timer_lbl)
        lay.addWidget(self.timer_btn)
        lay.addSpacing(20)

        # ── Points + Level + Username ───────────────────────────────────
        self.pts_lbl = QLabel(f"{self.user.points} pts")
        self.pts_lbl.setObjectName("points_label")
        self.lvl_lbl = QLabel(f"{self.user.get_level_name()}")
        self.lvl_lbl.setObjectName("level_label")
        backend = self.repo.backend_name() if hasattr(self.repo, "backend_name") else "DB"
        self.db_lbl = QLabel(f"DB: {backend}")
        self.db_lbl.setObjectName("db_label")
        lay.addWidget(self.pts_lbl)
        lay.addWidget(self.lvl_lbl)
        lay.addWidget(self.db_lbl)
        lay.addSpacing(15)

        self.profile_btn = QPushButton(f"🥋 {self.user.username}")
        self.profile_btn.setObjectName("toggle_btn_header")
        self.profile_btn.setToolTip("Voir ma progression, mes badges et statistiques")
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        self.profile_btn.clicked.connect(self.on_profile)
        lay.addWidget(self.profile_btn)
        lay.addSpacing(15)

        # ── Bouton Paramètres ⚙️ ──
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settings_header_btn")
        self.settings_btn.setToolTip("Paramètres (Clé API, Difficulté IA...)")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.clicked.connect(self.on_settings)
        lay.addWidget(self.settings_btn)
        lay.addSpacing(5)

        # ── Bouton Déconnexion 🚪 ──
        self.logout_btn = QPushButton("Déconnexion")
        self.logout_btn.setObjectName("logout_header_btn")
        self.logout_btn.setToolTip("Se déconnecter")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setFixedHeight(30)
        self.logout_btn.clicked.connect(self.on_logout)
        lay.addWidget(self.logout_btn)

    # ── Mode Zen ──────────────────────────────────────────────────────────
    def _toggle_zen(self):
        self._zen_active = not self._zen_active
        if self._zen_active:
            self.zen_btn.setText("🔲  Panneaux")
            self.zen_btn.setToolTip("Réafficher les panneaux")
        else:
            self.zen_btn.setText("🌿  Zen")
            self.zen_btn.setToolTip("Masquer tous les panneaux — voir le paysage")
        if self.on_zen_mode:
            self.on_zen_mode(self._zen_active)

    # ── Fond d'écran ──────────────────────────────────────────────────────
    def _open_bg_picker(self):
        from ui.background_picker import BackgroundPickerDialog
        dlg = BackgroundPickerDialog(self)
        dlg.background_chosen.connect(self._change_background)
        dlg.exec()

    def _change_background(self, path: str):
        """Émet un signal vers la fenêtre principale pour changer le fond."""
        # On remonte via la hiérarchie des parents jusqu'à MainWindow
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'set_background'):
                parent.set_background(path)
                break
            parent = parent.parent()

    # ── Lecteur de musique ────────────────────────────────────────────────
    def _open_music_player(self):
        from ui.music_player import MusicPlayerDialog
        if self._music_dialog is None:
            self._music_dialog = MusicPlayerDialog(self)
        self._music_dialog.show()
        self._music_dialog.raise_()
        self._music_dialog.activateWindow()

    # ── Timer Pomodoro ────────────────────────────────────────────────────
    def _toggle(self):
        if self._running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if not self._running:
            self._qt.start(1000)
            self.timer_btn.setText("⏸")
            self._running = True

    def stop_timer(self):
        if self._running:
            self._qt.stop()
            self.timer_btn.setText("▶")
            self._running = False

    def reset_timer(self):
        self.stop_timer()
        self._seconds = 25 * 60
        self.timer_lbl.setStyleSheet("") # Restaure le style QSS par défaut
        m, s = divmod(self._seconds, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")

    def reset_and_start_timer(self):
        self.reset_timer()
        self.start_timer()

    def _tick(self):
        self._seconds -= 1
        
        # Avertissement visuel ≤ 5 minutes (300 secondes)
        if self._seconds <= 300 and self._seconds > 0:
            if self._seconds % 2 == 0:
                self.timer_lbl.setStyleSheet("color: #FF5555; background: #FFDDDD; border: 2px solid #FF5555; border-radius: 8px; font-weight: bold;")
            else:
                self.timer_lbl.setStyleSheet("color: #FFFFFF; background: #FF5555; border: 2px solid #FF5555; border-radius: 8px; font-weight: bold;")
        else:
            self.timer_lbl.setStyleSheet("")

        if self._seconds <= 0:
            self._seconds = 25 * 60
            self._qt.stop()
            self._running = False
            self.timer_btn.setText("▶")
            self.timer_lbl.setStyleSheet("")
            
            # Notification visuelle
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Time's Up! ⏱️", 
                "Ta session Pomodoro de 25 minutes est terminée !\n\nPrends une petite pause de 5 minutes pour respirer et reposer ton esprit. 🎋"
            )
            
        m, s = divmod(self._seconds, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")

    def refresh(self, user):
        self.user = user
        self.pts_lbl.setText(f"{user.points} pts")
        self.lvl_lbl.setText(f"{user.get_level_name()}")
