"""
challenge_panel.py — Panneau de gauche affichant la liste des challenges Java.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class ChallengePanel(QWidget):
    DIFF_ICONS = {10: "🟢", 20: "🟡", 30: "🔴"}

    def __init__(self, on_select):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.on_select = on_select
        self.setObjectName("left_panel")
        self.setFixedWidth(272)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QLabel("  📜  Challenges", objectName="panel_header")
        hdr.setFixedHeight(40)
        lay.addWidget(hdr)

        sub = QLabel("  Java · Niveau Junior", objectName="panel_sub")
        sub.setFixedHeight(26)
        lay.addWidget(sub)

        self.list = QListWidget(objectName="challenge_list")
        self.list.setSpacing(1)
        self.list.setCursor(Qt.PointingHandCursor)
        self.list.itemClicked.connect(
            lambda item: self.on_select(item.data(Qt.UserRole))
        )
        lay.addWidget(self.list)

        foot = QLabel("  🟢 10pts   🟡 20pts   🔴 30pts",
                      objectName="panel_footer")
        foot.setFixedHeight(30)
        lay.addWidget(foot)

    def load(self, challenges):
        self.list.clear()
        for ch in challenges:
            icon = self.DIFF_ICONS.get(ch.points, "⚪")
            item = QListWidgetItem(f"  {icon}  {ch.title}")
            item.setData(Qt.UserRole, ch)
            item.setToolTip(f"{ch.description}\n+{ch.points} pts")
            self.list.addItem(item)
