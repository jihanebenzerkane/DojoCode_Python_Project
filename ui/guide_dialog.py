"""
guide_dialog.py — Guide d'utilisation multi-pages style Lofi Town.
Modal sombre premium avec images pixel art, catégorie + numéro de page,
titre, description, dots de navigation, boutons Retour / Suivant / Commencer.
Affiché une seule fois après la première connexion.
"""
import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter, QPainterPath, QBrush


# ── Fichier de flag "guide déjà vu" ──────────────────────────────────────────
GUIDE_FLAG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".guide_seen.json"
)

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets"
)


def _asset(name):
    return os.path.join(ASSETS_DIR, name)


def has_seen_guide(username: str) -> bool:
    if os.path.exists(GUIDE_FLAG_FILE):
        try:
            with open(GUIDE_FLAG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return username in data.get("seen_users", [])
        except Exception:
            pass
    return False


def mark_guide_seen(username: str):
    data = {"seen_users": []}
    if os.path.exists(GUIDE_FLAG_FILE):
        try:
            with open(GUIDE_FLAG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    if username not in data.get("seen_users", []):
        data.setdefault("seen_users", []).append(username)
    with open(GUIDE_FLAG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Contenu des slides ───────────────────────────────────────────────────────
GUIDE_SLIDES = [
    {
        "category": "BIENVENUE",
        "page_color": "#A8B87A",
        "title": "Bienvenue sur CodeDojo !",
        "subtitle": "Ton dojo virtuel pour maîtriser Java.",
        "desc": (
            "CodeDojo est un espace d'entraînement où tu relèves "
            "des défis Java progressifs.\nLe Sensei IA te guide sans jamais "
            "te donner la réponse — apprends en cherchant !"
        ),
        "image": "guide_slide1.png",
        "emoji": "⛩️",
    },
    {
        "category": "DÉFIS",
        "page_color": "#7AB88C",
        "title": "Choisis un défi Java.",
        "subtitle": "Du plus simple au plus complexe.",
        "desc": (
            "Dans le panneau de gauche, parcours la liste des défis. "
            "Chaque défi a un niveau de difficulté :\n"
            "🟢 Facile · 🟡 Moyen · 🔴 Difficile\n"
            "Clique sur un défi pour le charger dans l'éditeur."
        ),
        "image": "guide_slide2.png",
        "emoji": "📜",
    },
    {
        "category": "ÉDITEUR & IA",
        "page_color": "#7A9AB8",
        "title": "Code, soumets, apprends.",
        "subtitle": "L'éditeur et le Sensei IA travaillent ensemble.",
        "desc": (
            "Écris ta solution Java dans l'éditeur central, "
            "puis clique sur « Soumettre ».\n"
            "Le Sensei IA analysera ton code, posera des questions "
            "et te guidera — sans jamais révéler la solution !"
        ),
        "image": "guide_slide3.png",
        "emoji": "🧘",
    },
    {
        "category": "CHRONOMÈTRE",
        "page_color": "#B8977A",
        "title": "Le temps, c'est la pression.",
        "subtitle": "25 minutes, pas une de plus !",
        "desc": (
            "Dès que tu choisis un défi, le chronomètre Pomodoro "
            "de 25 min démarre.\n"
            "Si tu abandonnes un défi en cours de route, tu perds 5 points. "
            "Choisis bien tes batailles !"
        ),
        "image": "guide_slide1.png",
        "emoji": "⏱️",
    },
    {
        "category": "PARAMÈTRES",
        "page_color": "#A87AB8",
        "title": "Configure ton expérience.",
        "subtitle": "Clé API, niveau Sensei, ambiance musicale.",
        "desc": (
            "Clique sur ⚙️ dans la barre du haut pour accéder aux réglages.\n"
            "Tu peux configurer ta clé Groq API, choisir le niveau du Sensei : "
            "Patient · Exigeant · Maître Zen, et activer la musique lofi !"
        ),
        "image": "guide_slide2.png",
        "emoji": "⚙️",
    },
]

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = "#1C1F16"   # Fond principal sombre
CARD_BG     = "#252820"   # Carte légèrement plus claire
BORDER      = "#3A3D2E"   # Bordure subtile
TEXT_MAIN   = "#F0EDD8"   # Texte principal crème
TEXT_SUB    = "#9E9B82"   # Texte secondaire
BADGE_BG    = "rgba(168, 184, 122, 0.15)"  # Badge fond
BADGE_TEXT  = "#A8B87A"   # Badge texte
DOT_ACTIVE  = "#A8B87A"   # Dot actif
DOT_INACTIVE = "#3A3D2E"  # Dot inactif
BTN_BG      = "#A8B87A"   # Bouton principal
BTN_TEXT    = "#1C1F16"   # Texte bouton
BTN_HOVER   = "#BCC98E"   # Hover bouton


def _make_rounded_pixmap(path: str, w: int, h: int, radius: int = 12) -> QPixmap:
    """Charge une image, la redimensionne et lui applique des coins arrondis."""
    src = QPixmap(path)
    if src.isNull():
        placeholder = QPixmap(w, h)
        placeholder.fill(QColor("#2A2D1E"))
        return placeholder

    src = src.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    # Centre le crop
    x = (src.width() - w) // 2
    y = (src.height() - h) // 2
    src = src.copy(x, y, w, h)

    result = QPixmap(w, h)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    path_obj = QPainterPath()
    path_obj.addRoundedRect(0, 0, w, h, radius, radius)
    painter.setClipPath(path_obj)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return result


class GuideDialog(QDialog):
    """Dialogue de guide multi-pages style Lofi Town premium."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self._current = 0
        self._total = len(GUIDE_SLIDES)
        self.setWindowTitle("Guide CodeDojo")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._build()
        self._apply_style()
        self._update_slide()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Conteneur principal ──
        container = QWidget()
        container.setObjectName("guide_container")
        root.addWidget(container)

        main = QHBoxLayout(container)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ══════════════════════════
        # Panneau gauche — Image
        # ══════════════════════════
        self._left = QWidget()
        self._left.setObjectName("guide_left")
        self._left.setFixedWidth(300)
        left_lay = QVBoxLayout(self._left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)

        self._img_lbl = QLabel()
        self._img_lbl.setObjectName("guide_img")
        self._img_lbl.setAlignment(Qt.AlignCenter)
        self._img_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_lay.addWidget(self._img_lbl)

        # Badge emoji en bas de l'image
        self._emoji_badge = QLabel()
        self._emoji_badge.setObjectName("guide_emoji_badge")
        self._emoji_badge.setAlignment(Qt.AlignCenter)
        self._emoji_badge.setFixedHeight(48)
        left_lay.addWidget(self._emoji_badge)

        main.addWidget(self._left)

        # ══════════════════════════
        # Panneau droit — Contenu
        # ══════════════════════════
        right = QWidget()
        right.setObjectName("guide_right")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(32, 28, 32, 24)
        right_lay.setSpacing(0)

        # Row 1 : Badge catégorie + page + close
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._cat_badge = QLabel()
        self._cat_badge.setObjectName("guide_cat_badge")
        top_row.addWidget(self._cat_badge)

        self._page_lbl = QLabel()
        self._page_lbl.setObjectName("guide_page_lbl")
        top_row.addWidget(self._page_lbl)

        top_row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("guide_close_btn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self._finish)
        top_row.addWidget(close_btn)

        right_lay.addLayout(top_row)
        right_lay.addSpacing(22)

        # Row 2 : Titre principal
        self._title_lbl = QLabel()
        self._title_lbl.setObjectName("guide_title")
        self._title_lbl.setWordWrap(True)
        right_lay.addWidget(self._title_lbl)
        right_lay.addSpacing(6)

        # Row 3 : Sous-titre
        self._subtitle_lbl = QLabel()
        self._subtitle_lbl.setObjectName("guide_subtitle")
        self._subtitle_lbl.setWordWrap(True)
        right_lay.addWidget(self._subtitle_lbl)
        right_lay.addSpacing(18)

        # Row 4 : Séparateur
        sep = QFrame()
        sep.setObjectName("guide_sep")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        right_lay.addWidget(sep)
        right_lay.addSpacing(18)

        # Row 5 : Description
        self._desc_lbl = QLabel()
        self._desc_lbl.setObjectName("guide_desc")
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_lay.addWidget(self._desc_lbl)

        right_lay.addStretch()

        # Row 6 : Dots + navigation
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(0)

        # Dots
        dots_row = QHBoxLayout()
        dots_row.setSpacing(8)
        dots_row.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._dot_labels = []
        for i in range(self._total):
            dot = QLabel()
            dot.setObjectName("guide_dot")
            dot.setFixedSize(8, 8)
            self._dot_labels.append(dot)
            dots_row.addWidget(dot)

        bottom_row.addLayout(dots_row)
        bottom_row.addStretch()

        self._back_btn = QPushButton("←  Retour")
        self._back_btn.setObjectName("guide_back_btn")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.setFixedHeight(38)
        self._back_btn.clicked.connect(self._prev)
        bottom_row.addWidget(self._back_btn)

        bottom_row.addSpacing(10)

        self._next_btn = QPushButton("Suivant  →")
        self._next_btn.setObjectName("guide_next_btn")
        self._next_btn.setCursor(Qt.PointingHandCursor)
        self._next_btn.setFixedSize(150, 38)
        self._next_btn.clicked.connect(self._next)
        bottom_row.addWidget(self._next_btn)

        right_lay.addLayout(bottom_row)

        main.addWidget(right)

    # ─────────────────────────────────────────────────────────────────────────

    def _update_slide(self):
        slide = GUIDE_SLIDES[self._current]

        # Image
        img_path = _asset(slide["image"])
        pm = _make_rounded_pixmap(img_path, 300, 452, radius=0)
        self._img_lbl.setPixmap(pm)

        # Emoji badge
        self._emoji_badge.setText(slide["emoji"])

        # Textes
        self._cat_badge.setText(f"  {slide['category']}  ")
        self._page_lbl.setText(f"{self._current + 1} / {self._total}")
        self._title_lbl.setText(slide["title"])
        self._subtitle_lbl.setText(slide["subtitle"])
        self._desc_lbl.setText(slide["desc"])

        # Couleur accent dynamique par slide
        accent = slide["page_color"]
        self._cat_badge.setStyleSheet(
            f"background: {accent}22; color: {accent}; "
            f"font-size: 9px; font-weight: 900; letter-spacing: 2.5px; "
            f"border-radius: 4px; padding: 3px 10px;"
        )
        self._next_btn.setStyleSheet(
            f"QPushButton {{ background: {accent}; color: #1C1F16; "
            f"border: none; border-radius: 10px; font-size: 13px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {accent}DD; }}"
            f"QPushButton:pressed {{ background: {accent}AA; }}"
        )

        # Dots
        for i, dot in enumerate(self._dot_labels):
            if i == self._current:
                dot.setStyleSheet(
                    f"background: {accent}; border-radius: 4px; min-width: 20px;"
                )
                dot.setFixedWidth(20)
            else:
                dot.setStyleSheet(
                    f"background: {DOT_INACTIVE}; border-radius: 4px; min-width: 8px;"
                )
                dot.setFixedWidth(8)

        # Navigation
        self._back_btn.setVisible(self._current > 0)
        if self._current == self._total - 1:
            self._next_btn.setText("Commencer  →")
        else:
            self._next_btn.setText("Suivant  →")

    def _next(self):
        if self._current < self._total - 1:
            self._current += 1
            self._update_slide()
        else:
            self._finish()

    def _prev(self):
        if self._current > 0:
            self._current -= 1
            self._update_slide()

    def _finish(self):
        mark_guide_seen(self.username)
        self.accept()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QWidget#guide_container {{
                background: {BG};
                border-radius: 16px;
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
            }}
            QWidget#guide_left {{
                background: {CARD_BG};
                border-right: 1px solid {BORDER};
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }}
            QLabel#guide_img {{
                border-top-left-radius: 16px;
            }}
            QLabel#guide_emoji_badge {{
                background: {CARD_BG};
                color: {TEXT_MAIN};
                font-size: 22px;
                border-top: 1px solid {BORDER};
            }}
            QWidget#guide_right {{
                background: {BG};
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }}
            QLabel#guide_page_lbl {{
                color: {TEXT_SUB};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 3px 0;
            }}
            QPushButton#guide_close_btn {{
                background: rgba(255,255,255,0.05);
                color: {TEXT_SUB};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#guide_close_btn:hover {{
                background: rgba(255,255,255,0.1);
                color: {TEXT_MAIN};
            }}
            QLabel#guide_title {{
                color: {TEXT_MAIN};
                font-size: 21px;
                font-weight: 900;
                letter-spacing: -0.3px;
                line-height: 1.2;
            }}
            QLabel#guide_subtitle {{
                color: {TEXT_SUB};
                font-size: 12px;
                font-weight: 400;
                letter-spacing: 0.3px;
            }}
            QFrame#guide_sep {{
                background: {BORDER};
                border: none;
            }}
            QLabel#guide_desc {{
                color: #C8C5A8;
                font-size: 12px;
                line-height: 1.7;
                letter-spacing: 0.2px;
            }}
            QPushButton#guide_back_btn {{
                background: transparent;
                color: {TEXT_SUB};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton#guide_back_btn:hover {{
                background: rgba(255,255,255,0.06);
                color: {TEXT_MAIN};
            }}
        """)
