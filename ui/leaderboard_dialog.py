"""
leaderboard_dialog.py — Boîte de dialogue "Classement" affichant les 10 meilleurs élèves
classés par points avec médailles et surbrillance de l'utilisateur actif.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

class LeaderboardDialog(QDialog):
    def __init__(self, current_user, repo, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.repo = repo
        self.setWindowTitle("Classement du Dojo 🏆")
        self.setMinimumSize(420, 460)
        self.setObjectName("leaderboard_dialog")
        self._build()

    def _build(self):
        self.setStyleSheet("""
            QDialog#leaderboard_dialog {
                background-color: #F5F7EC;
                border: 3px solid #4E533C;
                border-radius: 16px;
            }
            QLabel {
                color: #4E533C;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#title_lbl {
                font-size: 20px;
                font-weight: bold;
                border-bottom: 2px solid #4E533C;
                padding-bottom: 8px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 2px solid #4E533C;
                border-radius: 10px;
                gridline-color: #E5E8D6;
                color: #4E533C;
                font-size: 13px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #E5E8D6;
                color: #4E533C;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #4E533C;
            }
            QPushButton#close_btn {
                background: #8D9078;
                color: #FCFBF5;
                font-weight: bold;
                border: 3px solid #4E533C;
                border-radius: 10px;
                border-bottom: 5px solid #4E533C;
                padding: 6px 20px;
            }
            QPushButton#close_btn:hover {
                background: #9FA28A;
            }
            QPushButton#close_btn:pressed {
                border-bottom: 2px solid #4E533C;
                margin-top: 3px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ── Title ───────────────────────────────────────────────────────────
        title = QLabel("🏆   CLASSEMENT DU DOJO", self)
        title.setObjectName("title_lbl")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Voici les guerriers les plus avancés sur la voie du Java :", self)
        subtitle.setStyleSheet("font-size: 12px; font-weight: bold;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # ── Table Widget ────────────────────────────────────────────────────
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rang", "Guerrier", "Points"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Fit columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # Load data
        top_users = self.repo.get_top_users(10)
        self.table.setRowCount(len(top_users))

        for idx, row in enumerate(top_users):
            username = row["username"]
            points = row["points"]
            rank = idx + 1

            # Determine rank icon/text
            if rank == 1:
                rank_str = "🥇 1er"
            elif rank == 2:
                rank_str = "🥈 2e"
            elif rank == 3:
                rank_str = "🥉 3e"
            else:
                rank_str = f" {rank}e"

            is_self = username == self.current_user.username

            # Create items
            rank_item = QTableWidgetItem(rank_str)
            user_item = QTableWidgetItem(f"🥋  {username}")
            pts_item = QTableWidgetItem(f"{points} pts")

            # Center align rank and points
            rank_item.setTextAlignment(Qt.AlignCenter)
            pts_item.setTextAlignment(Qt.AlignCenter)

            # Apply fonts & colors
            if is_self:
                bg_color = QColor("#CCD49F") # Sage accent for self!
                rank_item.setBackground(bg_color)
                user_item.setBackground(bg_color)
                pts_item.setBackground(bg_color)
                
                # Make text extra bold for active user
                font = QFont()
                font.setBold(True)
                rank_item.setFont(font)
                user_item.setFont(font)
                pts_item.setFont(font)
                
                user_item.setText(f"🥋  {username} (Moi)")

            self.table.setItem(idx, 0, rank_item)
            self.table.setItem(idx, 1, user_item)
            self.table.setItem(idx, 2, pts_item)

        layout.addWidget(self.table)

        # ── Close Button ────────────────────────────────────────────────────
        close_btn = QPushButton("Fermer   ✓", self)
        close_btn.setObjectName("close_btn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
