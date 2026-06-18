"""
leaf_overlay.py — Animation de feuilles d'érable tombantes (effet zen Dojo).
Overlay transparent au-dessus de la MainWindow.
"""
import random
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QFont


LEAF_CHARS = ["🍂", "🍁", "🌿"]
LEAF_COLORS = [
    QColor("#C1392B"),   # Terra red
    QColor("#C9A84C"),   # Gold
    QColor("#8FAF8F"),   # Sage
    QColor("#D4745A"),   # Soft terra
]


class Leaf:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.reset(start_top=True)

    def reset(self, start_top: bool = False):
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(-100, 0) if start_top else random.uniform(-200, -10)
        self.speed = random.uniform(0.6, 1.8)
        self.drift = random.uniform(-0.4, 0.4)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.2, 1.2)
        self.char = random.choice(LEAF_CHARS)
        self.color = random.choice(LEAF_COLORS)
        self.size = random.randint(11, 18)
        self.alpha = random.randint(20, 55)
        self.sway = random.uniform(0.2, 0.8)
        self.sway_offset = random.uniform(0, 2 * math.pi)
        self._tick = 0

    def step(self):
        self._tick += 1
        self.y += self.speed
        self.x += self.drift + self.sway * math.sin(self._tick * 0.04 + self.sway_offset)
        self.rotation += self.rot_speed
        if self.y > self.height + 30:
            self.reset(start_top=True)


class LeafOverlay(QWidget):
    """
    Widget transparent plein-écran qui anime 18 feuilles tombantes.
    Placé au-dessus de tous les autres widgets (setAttribute WA_TransparentForMouseEvents).
    """

    NUM_LEAVES = 18
    FPS = 30

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(parent.rect())

        w, h = parent.width(), parent.height()
        self.leaves = [Leaf(w, h) for _ in range(self.NUM_LEAVES)]
        # Scatter them vertically at start
        for i, leaf in enumerate(self.leaves):
            leaf.y = random.uniform(0, h)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000 // self.FPS)

    def _tick(self):
        for leaf in self.leaves:
            leaf.step()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        for leaf in self.leaves:
            leaf.width = w
            leaf.height = h

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for leaf in self.leaves:
            painter.save()
            painter.translate(leaf.x, leaf.y)
            painter.rotate(leaf.rotation)
            color = QColor(leaf.color)
            color.setAlpha(leaf.alpha)
            painter.setPen(color)
            font = QFont("Segoe UI Emoji", leaf.size)
            painter.setFont(font)
            painter.drawText(-leaf.size // 2, leaf.size // 2, leaf.char)
            painter.restore()
        painter.end()
