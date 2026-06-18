"""
login_window.py — CodeDojo Login Screen
Lofi town aesthetic: warm matcha-yellow background, cozy bokeh particles,
parchment glass card, Inter/Segoe UI font.
"""
import os
import math
import random
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QColor, QFont, QLinearGradient,
    QRadialGradient, QBrush, QPen
)


# ── Lofi Town Warm Palette ─────────────────────────────────────────────────────
BG_MATCHA   = QColor(220, 229, 151)      # #DCE597 — matcha yellow-green
BG_WARM     = QColor(230, 238, 165)      # lighter matcha
PARCHMENT   = "#FFFBEF"                  # warm cream card
SAGE        = "#6B8E3C"                  # sage green
SAGE_DIM    = "rgba(107, 142, 60, 0.18)"
SAGE_MID    = "rgba(107, 142, 60, 0.50)"
WARM_BROWN  = "#3B3020"                  # dark ink
BROWN_MID   = "rgba(59, 48, 32, 0.55)"
BROWN_DIM   = "rgba(59, 48, 32, 0.18)"
TEXT_MAIN   = "#3B3020"                  # dark ink
TEXT_MUTED  = "rgba(59, 48, 32, 0.50)"
GLASS_BG    = "rgba(255, 251, 236, 0.92)"
BORDER_SOFT = "rgba(107, 142, 60, 0.25)"
BORDER_MED  = "rgba(107, 142, 60, 0.55)"
ERR_COLOR   = "#A83820"
OK_COLOR    = "#4A7A25"


class LofiBokehBackground(QWidget):
    """Animated warm bokeh circles — cozy lofi atmosphere."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tick = 0
        random.seed(7)
        self._circles = [
            {
                'x': random.random(),
                'y': random.random(),
                'r': random.uniform(18, 70),
                'speed': random.uniform(0.3, 1.0),
                'phase': random.uniform(0, math.pi * 2),
                'color_idx': random.randint(0, 3),
                'drift_x': random.uniform(-0.15, 0.15),
                'drift_y': random.uniform(-0.08, 0.08),
            }
            for _ in range(28)
        ]
        self._colors = [
            QColor(255, 240, 160, 38),   # warm gold
            QColor(180, 210, 100, 30),   # sage green
            QColor(240, 220, 130, 28),   # hay yellow
            QColor(200, 230, 140, 22),   # light lime
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(40)

    def _animate(self):
        self._tick += 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Warm matcha base gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(215, 228, 142))
        grad.setColorAt(0.35, QColor(224, 234, 158))
        grad.setColorAt(0.65, QColor(218, 232, 148))
        grad.setColorAt(1.0, QColor(208, 224, 135))
        p.fillRect(0, 0, w, h, QBrush(grad))

        # Subtle warm vignette corners
        rg1 = QRadialGradient(0, 0, w * 0.5)
        rg1.setColorAt(0.0, QColor(190, 210, 100, 18))
        rg1.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, QBrush(rg1))

        rg2 = QRadialGradient(w, h, w * 0.55)
        rg2.setColorAt(0.0, QColor(180, 200, 80, 22))
        rg2.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, QBrush(rg2))

        t = self._tick * 0.018
        for c in self._circles:
            pulse = 0.6 + 0.4 * math.sin(t * c['speed'] + c['phase'])
            cx = (c['x'] + math.sin(t * c['speed'] * 0.5 + c['phase']) * 0.04 * c['drift_x'] * 10) * w
            cy = (c['y'] + math.cos(t * c['speed'] * 0.4 + c['phase']) * 0.04 * c['drift_y'] * 10) * h
            r = c['r'] * pulse

            color = QColor(self._colors[c['color_idx']])
            alpha = int(color.alpha() * pulse)
            color.setAlpha(max(8, min(55, alpha)))

            rg = QRadialGradient(cx, cy, r)
            rg.setColorAt(0.0, color)
            rg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(rg))
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        p.end()


class LoginWindow(QWidget):
    """Full-screen lofi.town-style login window with warm parchment card."""

    def __init__(self, auth_service, on_login):
        super().__init__()
        self.auth = auth_service
        self._on_login = on_login
        self._setup()
        self._build()

    def _setup(self):
        self.setWindowTitle("CodeDojo  ⛩")
        self.setMinimumSize(860, 560)
        self.resize(960, 620)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, False)

    def _build(self):
        # Warm bokeh fills the whole window
        self._bg = LofiBokehBackground(self)
        self._bg.setGeometry(self.rect())

        # ── Central parchment glass card ────────────────────────────────
        card = QWidget(self)
        card.setObjectName("login_glass_card")
        card.setFixedSize(460, 520)
        card.setStyleSheet(f"""
            QWidget#login_glass_card {{
                background: rgba(255, 251, 236, 0.93);
                border: 1.5px solid rgba(107, 142, 60, 0.28);
                border-radius: 28px;
            }}
        """)
        card.setAttribute(Qt.WA_StyledBackground, True)

        # Soft warm glow shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(55)
        shadow.setColor(QColor(130, 165, 60, 55))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(52, 44, 52, 38)
        card_lay.setSpacing(0)

        # ── Dojo leaf icon + brand ──────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setAlignment(Qt.AlignCenter)
        leaf = QLabel("🍃")
        leaf.setStyleSheet("font-size: 26px;")
        brand_row.addWidget(leaf)
        brand_txt = QLabel("CODEDOJO")
        brand_txt.setStyleSheet(f"""
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 5px;
            color: {SAGE};
            padding-left: 4px;
        """)
        brand_row.addWidget(brand_txt)
        card_lay.addLayout(brand_row)
        card_lay.addSpacing(10)

        # Sage divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: rgba(107, 142, 60, 0.22); border-radius: 1px;")
        card_lay.addWidget(div)
        card_lay.addSpacing(26)

        # ── Title ────────────────────────────────────────────────────────
        title = QLabel("Bienvenue !")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 32px;
            font-weight: 900;
            color: {TEXT_MAIN};
            letter-spacing: -0.5px;
        """)
        card_lay.addWidget(title)

        subtitle = QLabel("Connecte-toi pour reprendre ton parcours Java ☕")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_MUTED};
            font-weight: 500;
            margin-bottom: 4px;
        """)
        subtitle.setWordWrap(True)
        card_lay.addWidget(subtitle)
        card_lay.addSpacing(22)

        # ── Input fields ─────────────────────────────────────────────────
        self.username = QLineEdit()
        self.username.setPlaceholderText("  Nom d'utilisateur")
        self.username.setFixedHeight(50)
        self.username.returnPressed.connect(self._login)
        self.username.setStyleSheet(self._field_style())
        card_lay.addWidget(self.username)
        card_lay.addSpacing(10)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("  Mot de passe")
        self.password.setFixedHeight(50)
        self.password.returnPressed.connect(self._login)
        self.password.setStyleSheet(self._field_style())
        card_lay.addWidget(self.password)
        card_lay.addSpacing(8)

        # ── Feedback message ─────────────────────────────────────────────
        self.msg = QLabel("")
        self.msg.setFixedHeight(20)
        self.msg.setStyleSheet("font-size: 12px; font-weight: 600;")
        card_lay.addWidget(self.msg)
        card_lay.addSpacing(12)

        # ── Primary button ───────────────────────────────────────────────
        self.btn_login = QPushButton("Se connecter  →")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._login)
        self.btn_login.setStyleSheet(self._btn_primary_style())
        card_lay.addWidget(self.btn_login)
        card_lay.addSpacing(14)

        # ── Divider "ou" ─────────────────────────────────────────────────
        row = QHBoxLayout()
        for i in range(2):
            line = QWidget()
            line.setFixedHeight(1)
            line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            line.setStyleSheet("background: rgba(59, 48, 32, 0.12);")
            row.addWidget(line)
            if i == 0:
                or_lbl = QLabel("ou")
                or_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; padding: 0 10px; font-weight: 600;")
                row.addWidget(or_lbl)
        card_lay.addLayout(row)
        card_lay.addSpacing(14)

        # ── Secondary button ─────────────────────────────────────────────
        self.btn_signup = QPushButton("Créer un compte")
        self.btn_signup.setFixedHeight(46)
        self.btn_signup.setCursor(Qt.PointingHandCursor)
        self.btn_signup.clicked.connect(self._signup)
        self.btn_signup.setStyleSheet(self._btn_secondary_style())
        card_lay.addWidget(self.btn_signup)

        card_lay.addStretch()

        # Footer
        footer = QLabel("CodeDojo · ENSAH 2025–2026  🌿")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"font-size: 10px; color: rgba(59, 48, 32, 0.32); font-weight: 600;")
        card_lay.addWidget(footer)

        self._card = card

    def _field_style(self):
        return f"""
            QLineEdit {{
                background: rgba(255, 251, 236, 0.90);
                border: 1.5px solid rgba(107, 142, 60, 0.30);
                border-radius: 14px;
                padding: 0px 14px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                color: {TEXT_MAIN};
            }}
            QLineEdit:focus {{
                border-color: rgba(107, 142, 60, 0.65);
                background: #FFFFFF;
            }}
            QLineEdit::placeholder {{
                color: rgba(59, 48, 32, 0.38);
            }}
        """

    def _btn_primary_style(self):
        return f"""
            QPushButton {{
                background: rgba(107, 142, 60, 0.85);
                color: #FFFBEF;
                border: 1.5px solid rgba(80, 110, 40, 0.45);
                border-radius: 14px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-weight: 800;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: rgba(125, 162, 75, 0.95);
                border-color: rgba(90, 122, 42, 0.65);
            }}
            QPushButton:pressed {{
                background: rgba(85, 115, 40, 0.95);
            }}
            QPushButton:disabled {{
                background: rgba(107, 142, 60, 0.30);
                color: rgba(255, 251, 236, 0.50);
                border-color: rgba(80, 110, 40, 0.18);
            }}
        """

    def _btn_secondary_style(self):
        return f"""
            QPushButton {{
                background: rgba(255, 251, 236, 0.70);
                color: rgba(59, 48, 32, 0.65);
                border: 1.5px solid rgba(59, 48, 32, 0.18);
                border-radius: 14px;
                font-size: 13px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: rgba(220, 229, 151, 0.70);
                color: {TEXT_MAIN};
                border-color: rgba(107, 142, 60, 0.40);
            }}
            QPushButton:pressed {{
                background: rgba(200, 215, 120, 0.80);
            }}
        """

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bg.setGeometry(self.rect())
        if hasattr(self, '_card'):
            cw = self._card.width()
            ch = self._card.height()
            self._card.move(
                (self.width() - cw) // 2,
                (self.height() - ch) // 2
            )

    # ── Logic ──────────────────────────────────────────────────────────────────

    def _login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self._set_msg("⚠️  Remplis tous les champs.", ERR_COLOR)
            return
        user, msg = self.auth.login(u, p)
        if user is not None:
            self._set_msg("🌿  Connexion réussie…", OK_COLOR)
            self.btn_login.setEnabled(False)
            self.btn_signup.setEnabled(False)
            _u = user
            QTimer.singleShot(700, lambda: self._on_login(_u))
        else:
            self._set_msg(f"❌  {msg}", ERR_COLOR)

    def _signup(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self._set_msg("⚠️  Choisis un pseudo et un mot de passe.", ERR_COLOR)
            return
        if len(p) < 4:
            self._set_msg("⚠️  Mot de passe trop court (min 4 caract.).", ERR_COLOR)
            return
        ok, msg = self.auth.register(u, p)
        if ok:
            self._set_msg("✨  Compte créé ! Connecte-toi.", OK_COLOR)
        else:
            self._set_msg(f"❌  {msg}", ERR_COLOR)

    def _set_msg(self, text: str, color: str):
        self.msg.setText(text)
        self.msg.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {color};")