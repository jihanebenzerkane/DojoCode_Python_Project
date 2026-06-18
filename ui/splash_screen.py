"""
splash_screen.py — Écran de démarrage (splash) style Lofi Town.
Logo centré, texte de chargement animé avec des points, puis bouton "Commencer".
"""
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap


# Palette Lofi Town exacte — matcha warm
SPLASH_BG    = "#DCE597"   # lofi.town signature matcha yellow-green
SPLASH_TEXT  = "#3B3020"   # warm dark ink
SPLASH_BTN   = "#6B8E3C"   # sage green button
SPLASH_BTN_H = "#85A852"   # hover sage
SPLASH_WHITE = "#FFFBEF"   # warm parchment cream


LOADING_PHRASES = [
    "Préparation du Dojo",
    "Aiguisage du katana",
    "Infusion du thé matcha",
    "Méditation en cours",
    "Invocation du Sensei IA",
]


class SplashScreen(QWidget):
    """Écran d'accueil animé avec logo et texte de chargement."""

    def __init__(self, on_ready_callback):
        super().__init__()
        self._on_ready = on_ready_callback
        self._dot_count = 0
        self._phrase_idx = 0
        self._loading_done = False
        self._setup()
        self._build()
        self._style()
        self._start_loading()

    def _setup(self):
        self.setWindowTitle("CodeDojo  ⛩")
        self.setFixedSize(720, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignCenter)

        lay.addStretch(3)

        # ── Logo ⛩ ──
        self.logo_lbl = QLabel("⛩")
        self.logo_lbl.setObjectName("splash_logo_emoji")
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.logo_lbl)

        lay.addSpacing(10)

        # ── Titre ──
        self.title_lbl = QLabel("CodeDojo")
        self.title_lbl.setObjectName("splash_title")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.title_lbl)

        lay.addSpacing(6)

        # ── Sous-titre ──
        self.subtitle_lbl = QLabel("L'art du code, un défi à la fois")
        self.subtitle_lbl.setObjectName("splash_subtitle")
        self.subtitle_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.subtitle_lbl)

        lay.addStretch(2)

        # ── Texte de chargement ──
        self.loading_lbl = QLabel("Préparation du Dojo...")
        self.loading_lbl.setObjectName("splash_loading")
        self.loading_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.loading_lbl)

        lay.addSpacing(20)

        # ── Bouton Commencer (caché initialement) ──
        self.play_btn = QPushButton("▶  Commencer")
        self.play_btn.setObjectName("splash_play_btn")
        self.play_btn.setFixedSize(200, 48)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setVisible(False)
        self.play_btn.clicked.connect(self._on_play)
        lay.addWidget(self.play_btn, alignment=Qt.AlignCenter)

        lay.addStretch(2)

        # ── Footer ──
        foot = QLabel("ENSAH · 2025–2026")
        foot.setObjectName("splash_footer")
        foot.setAlignment(Qt.AlignCenter)
        lay.addWidget(foot)
        lay.addSpacing(20)

    def _style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {SPLASH_BG};
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
            }}
            QLabel#splash_logo_emoji {{
                font-size: 64px;
                color: {SPLASH_TEXT};
            }}
            QLabel#splash_title {{
                font-size: 42px;
                font-weight: 900;
                color: {SPLASH_TEXT};
                letter-spacing: 4px;
            }}
            QLabel#splash_subtitle {{
                font-size: 13px;
                color: {SPLASH_TEXT};
                letter-spacing: 3px;
                font-weight: bold;
            }}
            QLabel#splash_loading {{
                font-size: 12px;
                color: {SPLASH_TEXT};
                letter-spacing: 2px;
                font-weight: bold;
            }}
            QPushButton#splash_play_btn {{
                background: {SPLASH_BTN};
                color: {SPLASH_WHITE};
                border: 2px solid rgba(90, 89, 68, 0.5);
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton#splash_play_btn:hover {{
                background: {SPLASH_BTN_H};
                border-color: {SPLASH_TEXT};
            }}
            QPushButton#splash_play_btn:pressed {{
                background: {SPLASH_TEXT};
            }}
            QLabel#splash_footer {{
                font-size: 10px;
                color: rgba(90, 89, 68, 0.6);
                letter-spacing: 1px;
            }}
        """)

    def _start_loading(self):
        """Anime le texte de chargement pendant 3 secondes, puis affiche le bouton."""
        self._dot_timer = QTimer(self)
        self._dot_timer.timeout.connect(self._animate_dots)
        self._dot_timer.start(400)

        # Changer la phrase toutes les 600ms
        self._phrase_timer = QTimer(self)
        self._phrase_timer.timeout.connect(self._next_phrase)
        self._phrase_timer.start(700)

        # Finir le chargement après 3.5s
        QTimer.singleShot(3500, self._show_play_button)

    def _animate_dots(self):
        self._dot_count = (self._dot_count + 1) % 4
        phrase = LOADING_PHRASES[self._phrase_idx]
        dots = "." * self._dot_count
        self.loading_lbl.setText(f"{phrase}{dots}")

    def _next_phrase(self):
        if not self._loading_done:
            self._phrase_idx = (self._phrase_idx + 1) % len(LOADING_PHRASES)

    def _show_play_button(self):
        self._loading_done = True
        self._dot_timer.stop()
        self._phrase_timer.stop()
        self.loading_lbl.setText("Le Dojo est prêt !")

        # Afficher le bouton avec un fade-in
        self.play_btn.setVisible(True)
        effect = QGraphicsOpacityEffect(self.play_btn)
        self.play_btn.setGraphicsEffect(effect)
        self._fade_anim = QPropertyAnimation(effect, b"opacity")
        self._fade_anim.setDuration(600)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._fade_anim.start()

    def _on_play(self):
        self._on_ready()

    def paintEvent(self, event):
        """Dessine le fond pastel uni."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(SPLASH_BG))
        painter.end()
