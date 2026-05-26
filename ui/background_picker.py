"""
background_picker.py — Popup pour choisir un fond d'écran Lofi ou importer le sien.
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea, QWidget, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


# Fonds intégrés (chemin relatif à la racine du projet)
BUILT_IN_BACKGROUNDS = [
    ("🌿 Dojo Lofi", "assets/app_bg.png"),
    ("🌙 Nuit Dojo", "assets/bg_night_dojo.png"),
    ("🌸 Sakura Dawn", "assets/bg_sakura_dawn.png"),
]


def _resolve(rel_path: str) -> str:
    """Résout un chemin relatif par rapport à la racine du projet."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


class BgThumbCard(QFrame):
    """Carte miniature cliquable représentant un fond d'écran."""
    clicked = Signal(str)

    def __init__(self, label: str, path: str, parent=None):
        super().__init__(parent)
        self.bg_path = path
        self.setObjectName("bg_thumb_card")
        self.setFixedSize(170, 130)
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        # Miniature
        self.thumb = QLabel()
        self.thumb.setFixedSize(158, 90)
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setScaledContents(True)
        px = QPixmap(path)
        if not px.isNull():
            self.thumb.setPixmap(px)
        else:
            self.thumb.setText("?")
        self.thumb.setStyleSheet(
            "border: 2px solid #4E533C; border-radius: 6px;"
        )
        lay.addWidget(self.thumb)

        # Label
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #4E533C;")
        lay.addWidget(lbl)

    def mousePressEvent(self, event):
        self.clicked.emit(self.bg_path)
        super().mousePressEvent(event)


class BackgroundPickerDialog(QDialog):
    """Dialogue de sélection du fond d'écran."""
    background_chosen = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choisir un fond d'écran  🖼️")
        self.setFixedSize(560, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._build()
        self._style()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(14)

        # Titre
        title = QLabel("🖼️  Ambiance Lofi — Choisir un fond d'écran")
        title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #4E533C;"
            "border-bottom: 2px solid #4E533C; padding-bottom: 6px;"
        )
        lay.addWidget(title)

        # Zone scrollable avec les miniatures
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)

        col = 0
        row = 0
        for label, rel in BUILT_IN_BACKGROUNDS:
            path = _resolve(rel)
            card = BgThumbCard(label, path)
            card.clicked.connect(self._on_choose)
            grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        scroll.setWidget(container)
        lay.addWidget(scroll)

        # Bouton import personnalisé
        import_btn = QPushButton("📁  Importer mon propre fond d'écran...")
        import_btn.setObjectName("bg_import_btn")
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.clicked.connect(self._on_import)
        lay.addWidget(import_btn)

    def _on_choose(self, path: str):
        self.background_chosen.emit(path)
        self.accept()

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un fond d'écran",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.background_chosen.emit(path)
            self.accept()

    def _style(self):
        self.setStyleSheet("""
            QDialog {
                background: #F5F7EC;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#bg_thumb_card {
                background: #FFFFFF;
                border: 3px solid #4E533C;
                border-radius: 10px;
            }
            QFrame#bg_thumb_card:hover {
                background: #E5E8D6;
                border-color: #8D9078;
            }
            QPushButton#bg_import_btn {
                background: #E5E8D6;
                color: #4E533C;
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #4E533C;
                border-bottom: 4px solid #4E533C;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton#bg_import_btn:hover {
                background: #CCD49F;
            }
        """)
