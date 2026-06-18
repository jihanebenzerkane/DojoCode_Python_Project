"""
background_picker.py — Popup pour choisir un fond d'écran (image ou vidéo MP4).
Affiche les images intégrées, les vidéos trouvées dans assets/, et permet d'importer.
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea, QWidget, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor, QPainter, QFont


def _resolve(rel_path: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def _assets_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


# ── Built-in static backgrounds ────────────────────────────────────────────
BUILT_IN_IMAGES = [
    ("🌿 Dojo Lofi",    "assets/app_bg.png"),
    ("🌙 Nuit Dojo",    "assets/bg_night_dojo.png"),
    ("🌸 Sakura Dawn",  "assets/bg_sakura_dawn.png"),
]

# Video names → friendly labels
VIDEO_LABELS = {
    "0_Aesthetic_Study_3840x2160.mp4":       ("🎨 Aesthetic Study",    "#7B5EA7"),
    "0_Bali_Trip_3840x2160.mp4":             ("🌴 Bali Trip",          "#00A896"),
    "0_Sunset_Lake_3840x2160.mp4":           ("🌅 Sunset Lake",        "#E07A5F"),
    "6912727_Motion_Graphics_Motion_Graphic_3840x2160.mp4": ("✨ Motion Geo I",   "#3D405B"),
    "6913971_Motion_Graphics_Motion_Graphic_3840x2160.mp4": ("🌊 Motion Geo II",  "#264653"),
    "6917221_Motion_Graphics_Motion_Graphic_3840x2160.mp4": ("💫 Motion Geo III", "#2D6A4F"),
}


class BgThumbCard(QFrame):
    """Clickable thumbnail card for a background (image or video)."""
    clicked = Signal(str)

    def __init__(self, label: str, path: str, is_video: bool = False,
                 video_color: str = "#0A0F1E", parent=None):
        super().__init__(parent)
        self.bg_path = path
        self.setObjectName("bg_thumb_card")
        self.setFixedSize(175, 135)
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        # Thumbnail
        self.thumb = QLabel()
        self.thumb.setFixedSize(163, 95)
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setScaledContents(True)

        if is_video:
            # Draw a colored placeholder with a play icon
            px = QPixmap(163, 95)
            px.fill(QColor(video_color))
            p = QPainter(px)
            p.setPen(QColor("white"))
            f = QFont("Segoe UI", 28)
            p.setFont(f)
            p.drawText(px.rect(), Qt.AlignCenter, "▶")
            p.end()
            self.thumb.setPixmap(px)
        else:
            px = QPixmap(path)
            if not px.isNull():
                self.thumb.setPixmap(px)
            else:
                self.thumb.setText("?")

        self.thumb.setStyleSheet(
            "border: 1px solid rgba(0,212,170,0.3); border-radius: 8px;"
        )
        lay.addWidget(self.thumb)

        # Label
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #C4D8EE;")
        lay.addWidget(lbl)

    def mousePressEvent(self, event):
        self.clicked.emit(self.bg_path)
        super().mousePressEvent(event)


class BackgroundPickerDialog(QDialog):
    """Dialogue de sélection du fond d'écran — images et vidéos."""
    background_chosen = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choisir un fond  🎞️")
        self.setMinimumSize(600, 480)
        self.resize(640, 520)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._build()
        self._style()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(16)

        # Title
        title = QLabel("🎞️  Ambiance Visuelle — Fond d'écran / Vidéo")
        title.setStyleSheet(
            "font-size: 15px; font-weight: 800; color: #00D4AA;"
            "border-bottom: 1px solid rgba(0,212,170,0.3); padding-bottom: 8px;"
        )
        lay.addWidget(title)

        # Scrollable grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)

        col, row = 0, 0

        # ── Section: Static Images ──────────────────────────
        self._add_section("🖼️  Images statiques", row, col)
        row += 1

        for label, rel in BUILT_IN_IMAGES:
            path = _resolve(rel)
            card = BgThumbCard(label, path)
            card.clicked.connect(self._on_choose)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        if col != 0:
            row += 1
            col = 0

        # ── Section: Videos ──────────────────────────────────
        self._add_section("🎬  Vidéos d'ambiance (MP4 en boucle)", row, col)
        row += 1
        col = 0

        assets = _assets_dir()
        for fname in sorted(os.listdir(assets)):
            if not fname.endswith('.mp4'):
                continue
            path = os.path.join(assets, fname)
            info = VIDEO_LABELS.get(fname, (fname[:22] + "…", "#1A1A2E"))
            label, color = info
            card = BgThumbCard(label, path, is_video=True, video_color=color)
            card.clicked.connect(self._on_choose)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        scroll.setWidget(container)
        lay.addWidget(scroll)

        # Import buttons row
        btn_row = QHBoxLayout()

        import_img_btn = QPushButton("📁  Importer une image…")
        import_img_btn.setObjectName("bg_import_btn")
        import_img_btn.setCursor(Qt.PointingHandCursor)
        import_img_btn.clicked.connect(self._on_import_image)

        import_vid_btn = QPushButton("🎬  Importer une vidéo MP4…")
        import_vid_btn.setObjectName("bg_import_btn")
        import_vid_btn.setCursor(Qt.PointingHandCursor)
        import_vid_btn.clicked.connect(self._on_import_video)

        btn_row.addWidget(import_img_btn)
        btn_row.addWidget(import_vid_btn)
        lay.addLayout(btn_row)

    def _add_section(self, text: str, row: int, col: int):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: 700; color: rgba(0,212,170,0.8);"
            "padding: 4px 2px; letter-spacing: 1px;"
        )
        self.grid.addWidget(lbl, row, 0, 1, 3)

    def _on_choose(self, path: str):
        self.background_chosen.emit(path)
        self.accept()

    def _on_import_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer un fond d'écran", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self.background_chosen.emit(path)
            self.accept()

    def _on_import_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer une vidéo de fond", "",
            "Vidéo (*.mp4 *.mov *.avi *.mkv)"
        )
        if path:
            self.background_chosen.emit(path)
            self.accept()

    def _style(self):
        self.setStyleSheet("""
            QDialog {
                background: rgba(8, 14, 32, 0.97);
                color: #E2EEF9;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#bg_thumb_card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 212, 170, 0.2);
                border-radius: 12px;
            }
            QFrame#bg_thumb_card:hover {
                background: rgba(0, 212, 170, 0.1);
                border-color: rgba(0, 212, 170, 0.5);
            }
            QPushButton#bg_import_btn {
                background: rgba(255, 255, 255, 0.06);
                color: #C4D8EE;
                font-weight: 700;
                font-size: 13px;
                border: 1px solid rgba(196, 216, 238, 0.2);
                border-radius: 10px;
                padding: 9px 16px;
            }
            QPushButton#bg_import_btn:hover {
                background: rgba(0, 212, 170, 0.12);
                color: #00D4AA;
                border-color: rgba(0, 212, 170, 0.45);
            }
            QScrollBar:vertical {
                background: transparent; width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,212,170,0.3); border-radius: 4px; min-height: 20px;
            }
        """)
