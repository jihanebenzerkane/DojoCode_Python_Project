"""
guide_dialog.py — Guide d'utilisation multi-pages style Lofi Town.
Fond sombre, catégorie + numéro de page, titre, description, dots de navigation,
boutons Retour / Suivant / Commencer.
Affiché une seule fois après la première connexion.
"""
import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont


# ── Fichier de flag "guide déjà vu" ──────────────────────────────────────────
GUIDE_FLAG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".guide_seen.json"
)


def has_seen_guide(username: str) -> bool:
    """Vérifie si l'utilisateur a déjà vu le guide."""
    if os.path.exists(GUIDE_FLAG_FILE):
        try:
            with open(GUIDE_FLAG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return username in data.get("seen_users", [])
        except Exception:
            pass
    return False


def mark_guide_seen(username: str):
    """Marque le guide comme vu pour cet utilisateur."""
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
        "icon": "⛩",
        "title": "Bienvenue sur CodeDojo !",
        "desc": "CodeDojo est ton dojo virtuel pour maîtriser Java.\n"
                "Le Sensei IA te guide à travers des défis progressifs\n"
                "sans jamais te donner la réponse directement.",
    },
    {
        "category": "DÉFIS",
        "icon": "📜",
        "title": "Choisis un défi Java.",
        "desc": "Dans le panneau de gauche, clique sur un défi pour\n"
                "le charger dans l'éditeur. Chaque défi a un niveau\n"
                "de difficulté : 🟢 Facile · 🟡 Moyen · 🔴 Difficile.",
    },
    {
        "category": "ÉDITEUR",
        "icon": "💻",
        "title": "Écris ton code Java.",
        "desc": "L'éditeur central est ton espace de travail.\n"
                "Écris ta solution Java, puis clique sur « Soumettre »\n"
                "pour que le Sensei IA analyse ton code.",
    },
    {
        "category": "SENSEI IA",
        "icon": "🧘",
        "title": "Le Sensei te guide.",
        "desc": "Le Sensei IA apparaît à droite et analyse ton code.\n"
                "Il te pose des questions, donne des indices,\n"
                "mais ne révèle jamais la solution. Apprends en cherchant !",
    },
    {
        "category": "CHRONOMÈTRE",
        "icon": "⏱",
        "title": "Le temps, c'est la pression.",
        "desc": "Dès que tu choisis un défi, le chronomètre Pomodoro\n"
                "de 25 min démarre automatiquement. Si tu quittes\n"
                "le défi en cours, tu perds 5 points !",
    },
    {
        "category": "PARAMÈTRES",
        "icon": "⚙️",
        "title": "Configure ton expérience.",
        "desc": "Clique sur ⚙️ dans la barre du haut pour régler\n"
                "ta clé API et le niveau de difficulté du Sensei :\n"
                "Patient (Débutant) · Exigeant · Maître Zen (Avancé).",
    },
]


# ── Palette ──────────────────────────────────────────────────────────────────
DARK_BG      = "#2B2D31"
DARK_CARD    = "#313338"
DARK_BORDER  = "#3E4047"
WHITE        = "#FFFFFF"
GRAY         = "#9B9DA2"
ACCENT       = "#D97A3E"
ACCENT_HOVER = "#E89F3E"
DOT_ACTIVE   = "#FFFFFF"
DOT_INACTIVE = "#555861"


class GuideDialog(QDialog):
    """Dialogue de guide multi-pages inspiré de Lofi Town."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self._current = 0
        self._total = len(GUIDE_SLIDES)
        self.setWindowTitle("Guide CodeDojo  ⛩")
        self.setFixedSize(560, 420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._build()
        self._style()
        self._update_slide()

    def _build(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(28, 24, 28, 20)
        self._root.setSpacing(0)

        # ── Row 1 : Catégorie + Numéro ──
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        self.cat_badge = QLabel()
        self.cat_badge.setObjectName("guide_cat_badge")
        top_row.addWidget(self.cat_badge)

        self.page_lbl = QLabel()
        self.page_lbl.setObjectName("guide_page_lbl")
        top_row.addWidget(self.page_lbl)
        top_row.addStretch()

        # Bouton fermer
        close_btn = QPushButton("✕")
        close_btn.setObjectName("guide_close_btn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self._finish)
        top_row.addWidget(close_btn)

        self._root.addLayout(top_row)
        self._root.addSpacing(14)

        # ── Row 2 : Titre ──
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("guide_title")
        self.title_lbl.setWordWrap(True)
        self._root.addWidget(self.title_lbl)
        self._root.addSpacing(16)

        # ── Row 3 : Carte descriptive ──
        self.desc_card = QWidget()
        self.desc_card.setObjectName("guide_desc_card")
        card_lay = QVBoxLayout(self.desc_card)
        card_lay.setContentsMargins(24, 24, 24, 24)

        self.icon_lbl = QLabel()
        self.icon_lbl.setObjectName("guide_icon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(self.icon_lbl)
        card_lay.addSpacing(12)

        self.desc_lbl = QLabel()
        self.desc_lbl.setObjectName("guide_desc")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        card_lay.addWidget(self.desc_lbl)

        self._root.addWidget(self.desc_card)
        self._root.addStretch()

        # ── Row 4 : Dots ──
        self.dots_row = QHBoxLayout()
        self.dots_row.setSpacing(8)
        self.dots_row.setAlignment(Qt.AlignLeft)
        self._dot_labels = []
        for i in range(self._total):
            dot = QLabel("●")
            dot.setObjectName("guide_dot")
            dot.setFixedSize(14, 14)
            dot.setAlignment(Qt.AlignCenter)
            self._dot_labels.append(dot)
            self.dots_row.addWidget(dot)

        self._root.addLayout(self.dots_row)
        self._root.addSpacing(14)

        # ── Row 5 : Navigation ──
        nav_row = QHBoxLayout()
        nav_row.setSpacing(12)

        self.back_btn = QPushButton("←  Retour")
        self.back_btn.setObjectName("guide_nav_back")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._prev)
        nav_row.addWidget(self.back_btn)

        nav_row.addStretch()

        self.next_btn = QPushButton("Suivant  →")
        self.next_btn.setObjectName("guide_nav_next")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setFixedSize(160, 40)
        self.next_btn.clicked.connect(self._next)
        nav_row.addWidget(self.next_btn)

        self._root.addLayout(nav_row)

    def _update_slide(self):
        slide = GUIDE_SLIDES[self._current]

        self.cat_badge.setText(f"  {slide['category']}  ")
        self.page_lbl.setText(f"{self._current + 1} SUR {self._total}")
        self.title_lbl.setText(f"{slide['icon']}  {slide['title']}")
        self.icon_lbl.setText(slide["icon"])
        self.desc_lbl.setText(slide["desc"])

        # Dots
        for i, dot in enumerate(self._dot_labels):
            if i == self._current:
                dot.setStyleSheet(f"color: {DOT_ACTIVE}; font-size: 10px;")
            else:
                dot.setStyleSheet(f"color: {DOT_INACTIVE}; font-size: 8px;")

        # Navigation buttons
        self.back_btn.setVisible(self._current > 0)
        if self._current == self._total - 1:
            self.next_btn.setText("Commencer  →")
        else:
            self.next_btn.setText("Suivant  →")

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

    def _style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {DARK_BG};
                border-radius: 16px;
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
            }}
            QLabel#guide_cat_badge {{
                background: rgba(217, 122, 62, 0.2);
                color: {ACCENT};
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 2px;
                border-radius: 4px;
                padding: 3px 10px;
            }}
            QLabel#guide_page_lbl {{
                color: {GRAY};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton#guide_close_btn {{
                background: transparent;
                color: {GRAY};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#guide_close_btn:hover {{
                color: {WHITE};
            }}
            QLabel#guide_title {{
                color: {WHITE};
                font-size: 22px;
                font-weight: 900;
                letter-spacing: -0.3px;
            }}
            QWidget#guide_desc_card {{
                background: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 12px;
            }}
            QLabel#guide_icon {{
                font-size: 42px;
            }}
            QLabel#guide_desc {{
                color: {GRAY};
                font-size: 13px;
                line-height: 1.6;
                letter-spacing: 0.2px;
            }}
            QPushButton#guide_nav_back {{
                background: transparent;
                color: {GRAY};
                border: none;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton#guide_nav_back:hover {{
                color: {WHITE};
            }}
            QPushButton#guide_nav_next {{
                background: {ACCENT};
                color: {WHITE};
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QPushButton#guide_nav_next:hover {{
                background: {ACCENT_HOVER};
            }}
            QPushButton#guide_nav_next:pressed {{
                background: #B65E2A;
            }}
        """)
