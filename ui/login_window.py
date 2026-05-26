"""
login_window.py — Fenêtre de connexion CodeDojo.
Layout : Panneau formulaire gauche (crème) | Image lofi anime droite.
Inspiré de lofi.cafe — minimaliste, épuré, chaleureux.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap, QColor, QFont


# ── Palette Zen Sunset — Inspirée de l'image de fond ────────────────────────
ZEN_BG       = "#F9F6F0"       # Crème sablé clair de la terrasse
ZEN_PANEL    = "#FFFFFF"       # Blanc pur pour les conteneurs
ZEN_BORDER   = "#D0C9BC"       # Bordures sablées douces
SAGE         = "#5D7F81"       # Vert sauge de l'arbre
SAGE_LIGHT   = "#8CA6A7"       # Sage clair pour reflets
TERRA        = "#D97A3E"       # Orange coucher de soleil chaleureux
TERRA_GLOW   = "#E89F3E"       # Hover jaune soleil
INK          = "#2A3B3C"       # Texte foncé bleu-vert ardoise
INK_SOFT     = "#5E7B7D"       # Texte secondaire atténué
RED_ERR      = "#C1392B"       # Erreur rouge
GREEN_OK     = "#4E8C4E"       # Succès vert
FIELD_BG     = "rgba(255, 255, 255, 0.85)" # Champ clair semi-transparent
FIELD_BORDER = "#D8D2C4"


class ImagePanel(QWidget):
    """Panneau droit : affiche l'image en respectant ses proportions (sans déformation)."""

    # Dimensions réelles de assets/login.png : 512 × 1024 px
    # On affiche à hauteur fixe 600 px → largeur = 512 * 600 / 1024 = 300 px
    IMG_W, IMG_H = 512, 1024
    DISPLAY_H    = 600
    DISPLAY_W    = IMG_W * DISPLAY_H // IMG_H   # = 300

    def __init__(self, img_path: str, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(img_path)
        self.setFixedSize(self.DISPLAY_W, self.DISPLAY_H)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if not self._pixmap.isNull():
            # Mise à l'échelle en conservant le ratio exact — aucun étirage
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            # Centrer si des marges apparaissent
            x = (self.width()  - scaled.width())  // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(self.rect(), QColor("#0E1117"))
        painter.end()


class LoginWindow(QWidget):
    """Fenêtre de login split-screen : formulaire épuré + illustration lofi."""

    def __init__(self, auth_service, on_login):
        super().__init__()
        self.auth = auth_service
        self._on_login = on_login   # callback(user) appelé après connexion réussie
        self._setup()
        self._build()
        self._style()

    def _setup(self):
        self.setWindowTitle("CodeDojo  ⛩")
        # Largeur = 420 (formulaire) + 300 (image 512×1024 à h=600) = 720
        self.setFixedSize(720, 600)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ══ PANNEAU GAUCHE — Formulaire ══════════════════════════════════════
        left = QWidget()
        left.setFixedWidth(420)
        left.setObjectName("left_panel_login")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(60, 70, 60, 40)
        left_lay.setSpacing(0)
        left_lay.setAlignment(Qt.AlignTop)

        # Branding: petit torii subtil + titre "Sign in"
        torii_lbl = QLabel("⛩  CodeDojo", objectName="brand_lbl")
        left_lay.addWidget(torii_lbl)
        left_lay.addSpacing(40)

        title = QLabel("Se connecter", objectName="form_title")
        left_lay.addWidget(title)
        left_lay.addSpacing(28)

        # ── Username ──────────────────────────────────────────────────────────
        self.username = QLineEdit(objectName="login_field")
        self.username.setPlaceholderText("Nom d'utilisateur")
        self.username.setFixedHeight(46)
        self.username.returnPressed.connect(self._login)
        left_lay.addWidget(self.username)
        left_lay.addSpacing(10)

        # ── Password ──────────────────────────────────────────────────────────
        self.password = QLineEdit(objectName="login_field")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Mot de passe")
        self.password.setFixedHeight(46)
        self.password.returnPressed.connect(self._login)
        left_lay.addWidget(self.password)
        left_lay.addSpacing(6)

        # Message d'erreur / succès
        self.msg = QLabel("", objectName="login_msg")
        self.msg.setWordWrap(True)
        self.msg.setFixedHeight(28)
        left_lay.addWidget(self.msg)
        left_lay.addSpacing(6)

        # ── Bouton principal Sign In ───────────────────────────────────────────
        self.btn_login = QPushButton("Se connecter", objectName="login_btn_primary")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._login)
        left_lay.addWidget(self.btn_login)
        left_lay.addSpacing(20)

        # ── Divider "ou" ──────────────────────────────────────────────────────
        divider_row = QHBoxLayout()
        line_l = QWidget(objectName="divider_line")
        line_l.setFixedHeight(1)
        line_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        or_lbl = QLabel("ou", objectName="divider_or")
        line_r = QWidget(objectName="divider_line")
        line_r.setFixedHeight(1)
        line_r.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        divider_row.addWidget(line_l)
        divider_row.addSpacing(10)
        divider_row.addWidget(or_lbl)
        divider_row.addSpacing(10)
        divider_row.addWidget(line_r)
        left_lay.addLayout(divider_row)
        left_lay.addSpacing(18)

        # ── Bouton secondaire Sign Up ──────────────────────────────────────────
        self.btn_signup = QPushButton("Créer un compte", objectName="login_btn_secondary")
        self.btn_signup.setFixedHeight(44)
        self.btn_signup.setCursor(Qt.PointingHandCursor)
        self.btn_signup.clicked.connect(self._signup)
        left_lay.addWidget(self.btn_signup)

        left_lay.addStretch()

        # Bas de page
        footer = QLabel("CodeDojo · ENSAH 2025–2026", objectName="login_footer_label")
        footer.setAlignment(Qt.AlignCenter)
        left_lay.addWidget(footer)

        # ══ PANNEAU DROIT — Image Anime ══════════════════════════════════════
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base, "assets", "login.png")
        self.image_panel = ImagePanel(img_path)

        root.addWidget(left)
        root.addWidget(self.image_panel)

    def _style(self):
        self.setStyleSheet(f"""
            /* Base — toute la fenêtre */
            QWidget {{
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
                background: transparent;
            }}

            /* Panneau gauche — crème sablé clair */
            QWidget#left_panel_login {{
                background: {ZEN_BG};
                border-right: 1px solid {ZEN_BORDER};
            }}

            /* Branding ⛩ CodeDojo */
            QLabel#brand_lbl {{
                font-size: 15px;
                font-weight: bold;
                color: {SAGE};
                letter-spacing: 2px;
            }}

            /* Titre  */
            QLabel#form_title {{
                font-size: 26px;
                font-weight: bold;
                color: {INK};
                letter-spacing: -0.5px;
            }}

            /* Champs de saisie clairs et nets */
            QLineEdit#login_field {{
                background: {FIELD_BG};
                border: 1.5px solid {FIELD_BORDER};
                border-radius: 10px;
                padding: 0px 16px;
                font-size: 14px;
                color: {INK};
                selection-background-color: {TERRA};
            }}
            QLineEdit#login_field:focus {{
                border: 1.5px solid {TERRA};
                background: #FFFFFF;
            }}
            QLineEdit#login_field[placeholderText] {{
                color: {INK_SOFT};
            }}

            /* Message feedback */
            QLabel#login_msg {{
                font-size: 12px;
                font-weight: bold;
            }}

            /* Bouton principal — terracotta / orange soleil */
            QPushButton#login_btn_primary {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {TERRA}, stop:1 {TERRA_GLOW});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QPushButton#login_btn_primary:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {TERRA_GLOW}, stop:1 #FFAE42);
            }}
            QPushButton#login_btn_primary:pressed {{ background: #B65E2A; }}
            QPushButton#login_btn_primary:disabled {{
                background: {ZEN_BORDER};
                color: {INK_SOFT};
            }}

            /* Bouton secondaire — outline sage */
            QPushButton#login_btn_secondary {{
                background: transparent;
                color: {SAGE};
                border: 1.5px solid rgba(93, 127, 129, 0.4);
                border-radius: 10px;
                font-size: 13px;
            }}
            QPushButton#login_btn_secondary:hover {{
                background: rgba(93, 127, 129, 0.1);
                color: {INK};
                border-color: {SAGE};
            }}

            /* Divider */
            QWidget#divider_line {{
                background: {ZEN_BORDER};
            }}
            QLabel#divider_or {{
                font-size: 11px;
                color: {INK_SOFT};
                font-weight: bold;
                letter-spacing: 1px;
            }}

            /* Pied de page */
            QLabel#login_footer_label {{
                font-size: 10px;
                color: {INK_SOFT};
            }}
        """)

    # ── LOGIQUE ───────────────────────────────────────────────────────────────

    def _login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self._set_msg("⚠️ Remplis tous les champs.", RED_ERR)
            return
        user, msg = self.auth.login(u, p)   # user=User obj on success, None on fail
        if user is not None:
            self._set_msg("🥋 Accès autorisé…", GREEN_OK)
            self.btn_login.setEnabled(False)
            self.btn_signup.setEnabled(False)
            _u = user   # capture in local var to avoid late-binding in lambda
            QTimer.singleShot(700, lambda: self._on_login(_u))
        else:
            self._set_msg(f"❌ {msg}", RED_ERR)

    def _signup(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self._set_msg("⚠️ Choisis un pseudo et un mot de passe.", RED_ERR)
            return
        if len(p) < 4:
            self._set_msg("⚠️ Mot de passe trop court (min 4 caract.).", RED_ERR)
            return
        ok, msg = self.auth.register(u, p)
        if ok:
            self._set_msg("✨ Compte créé ! Connecte-toi.", GREEN_OK)
        else:
            self._set_msg(f"❌ {msg}", RED_ERR)

    def _set_msg(self, text: str, color: str):
        self.msg.setText(text)
        self.msg.setStyleSheet(f"color: {color};")