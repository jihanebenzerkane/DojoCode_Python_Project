"""
achievement_popup.py — Animated toast-style notification for newly earned achievements.

Appears in the bottom-right of the main window, stacks if multiple achievements fire
at once, and auto-dismisses after 5 seconds.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont


class AchievementToast(QWidget):
    """
    A single floating toast notification for one achievement.
    Slides in from the right, stays for 5 s, then slides out and destroys itself.
    """

    def __init__(self, achievement: dict, parent: QWidget = None, offset_index: int = 0):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._offset_index = offset_index
        self._build(achievement)
        self._style()

    def _build(self, ach: dict):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        card = QWidget(objectName="ach_card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 12, 16, 12)
        card_lay.setSpacing(4)

        # Top row: icon + title + close button
        top = QHBoxLayout()
        top.setSpacing(10)

        icon_lbl = QLabel(ach.get("icon", "🏆"), objectName="ach_icon")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 22))
        top.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        unlock_lbl = QLabel("🎉 Succès débloqué !", objectName="ach_unlock_header")
        title_lbl  = QLabel(ach.get("title", ""), objectName="ach_title")
        text_col.addWidget(unlock_lbl)
        text_col.addWidget(title_lbl)
        top.addLayout(text_col)
        top.addStretch()

        close_btn = QPushButton("✕", objectName="ach_close")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self._dismiss)
        top.addWidget(close_btn, alignment=Qt.AlignTop)

        desc_lbl = QLabel(ach.get("description", ""), objectName="ach_desc")
        desc_lbl.setWordWrap(True)

        card_lay.addLayout(top)
        card_lay.addWidget(desc_lbl)
        lay.addWidget(card)

        self.setFixedWidth(340)
        self.adjustSize()

    def _style(self):
        self.setStyleSheet("""
            QWidget#ach_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4E533C, stop:1 #3A3E2C);
                border: 1.5px solid #CCD49F;
                border-radius: 12px;
            }
            QLabel#ach_unlock_header {
                font-size: 10px;
                font-weight: bold;
                color: #CCD49F;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QLabel#ach_title {
                font-size: 14px;
                font-weight: bold;
                color: #FEFDF4;
            }
            QLabel#ach_desc {
                font-size: 11px;
                color: #E5E8D6;
                margin-top: 4px;
            }
            QLabel#ach_icon {
                background: transparent;
            }
            QPushButton#ach_close {
                background: transparent;
                color: #8D9078;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#ach_close:hover {
                color: #FEFDF4;
            }
        """)

    def show_animated(self, parent: QWidget):
        """Position and animate the toast into view."""
        if parent is None:
            return

        self.setParent(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
        self.raise_()

        # Position: bottom-right with stacking offset
        PAD = 16
        STACK_OFFSET = 10
        pw, ph = parent.width(), parent.height()
        w, h = self.sizeHint().width(), self.sizeHint().height() + 20

        x_start = pw  # off-screen to the right
        x_end   = pw - w - PAD
        y       = ph - h - PAD - self._offset_index * (h + STACK_OFFSET)

        self.setGeometry(x_end, y, w, h)
        self.show()

        # Slide-in: animate x from off-screen to final position
        self._anim_in = QPropertyAnimation(self, b"pos")
        self._anim_in.setDuration(350)
        self._anim_in.setStartValue(QPoint(x_start, y))
        self._anim_in.setEndValue(QPoint(x_end, y))
        self._anim_in.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_in.start()

        # Auto-dismiss after 5 s
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)
        self._timer.start(5000)

    def _dismiss(self):
        """Slide out then close."""
        if not self.isVisible():
            return
        self._timer.stop() if hasattr(self, '_timer') else None

        x_end = self.x() + self.width() + 20
        self._anim_out = QPropertyAnimation(self, b"pos")
        self._anim_out.setDuration(280)
        self._anim_out.setStartValue(self.pos())
        self._anim_out.setEndValue(QPoint(x_end, self.y()))
        self._anim_out.setEasingCurve(QEasingCurve.InCubic)
        self._anim_out.finished.connect(self.close)
        self._anim_out.start()


def show_achievements(achievements: list[dict], parent: QWidget):
    """
    Show a stack of achievement toasts.
    Call after a successful solve with the list returned by AchievementService.
    """
    for i, ach in enumerate(achievements):
        toast = AchievementToast(ach, parent=parent, offset_index=i)
        # Stagger each toast by 400 ms so they don't all appear at once
        QTimer.singleShot(i * 400, lambda t=toast, p=parent: t.show_animated(p))