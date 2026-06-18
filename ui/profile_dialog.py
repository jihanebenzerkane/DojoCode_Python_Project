"""
profile_dialog.py — Boîte de dialogue "Mon Profil" affichant la progression détaillée,
les statistiques par niveau, le temps de codage total et les badges d'achievements.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QScrollArea, QWidget, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class ProfileDialog(QDialog):
    def __init__(self, user, repo, parent=None):
        super().__init__(parent)
        self.user = user
        self.repo = repo
        self.setWindowTitle("Mon Profil Dojo 🥋")
        self.setMinimumSize(560, 520)
        self.setObjectName("profile_dialog")
        self._build()

    def _build(self):
        # Configurer le style de base
        self.setStyleSheet("""
            QDialog#profile_dialog {
                background-color: #F5F7EC;
                border: 3px solid #4E533C;
                border-radius: 16px;
            }
            QLabel {
                color: #4E533C;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#profile_title {
                font-size: 20px;
                font-weight: bold;
                border-bottom: 2px solid #4E533C;
                padding-bottom: 8px;
            }
            QProgressBar {
                border: 2px solid #4E533C;
                border-radius: 6px;
                text-align: center;
                background-color: #FFFFFF;
                color: #4E533C;
                font-weight: bold;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #CCD49F;
                border-radius: 4px;
            }
            QScrollArea#badge_scroll {
                border: 2px solid #4E533C;
                border-radius: 10px;
                background-color: #EAE5D9;
            }
            QWidget#badge_container {
                background-color: #EAE5D9;
            }
            QWidget.badge_card {
                background-color: #FFFFFF;
                border: 2px solid #4E533C;
                border-bottom: 4px solid #4E533C;
                border-radius: 8px;
                padding: 6px;
            }
            QWidget.badge_card_locked {
                background-color: #EAE6D8;
                border: 2px dashed #8D9078;
                border-radius: 8px;
                padding: 6px;
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
        title_lbl = QLabel("🥋   MON PROFIL DOJO", self)
        title_lbl.setObjectName("profile_title")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        # ── Top Section: Username, Level, Points ────────────────────────────
        top_layout = QHBoxLayout()
        
        info_layout = QVBoxLayout()
        user_lbl = QLabel(f"<b>Guerrier :</b> {self.user.username}", self)
        user_lbl.setStyleSheet("font-size: 15px;")
        
        level_lbl = QLabel(f"<b>Niveau :</b> {self.user.get_level_name()}", self)
        level_lbl.setStyleSheet("font-size: 14px;")
        
        info_layout.addWidget(user_lbl)
        info_layout.addWidget(level_lbl)
        
        points_layout = QVBoxLayout()
        pts_lbl = QLabel(f"<span style='font-size: 26px; font-weight: bold; color: #4E533C;'>{self.user.points}</span><br><b>points totaux</b>", self)
        pts_lbl.setAlignment(Qt.AlignCenter)
        points_layout.addWidget(pts_lbl)
        
        top_layout.addLayout(info_layout, stretch=2)
        top_layout.addLayout(points_layout, stretch=1)
        layout.addLayout(top_layout)

        # ── Level Progress Bar ──────────────────────────────────────────────
        level_progress_layout = QVBoxLayout()
        
        # Calculate level progress bounds
        # Étudiant: 0-99 -> to 100
        # Apprenti: 100-299 -> to 300
        # Pratiquant: 300-599 -> to 600
        # Maître: 600+ -> full
        pts = self.user.points
        if pts < 100:
            current_lvl = "Étudiant"
            next_lvl = "Apprenti"
            min_pts, max_pts = 0, 100
        elif pts < 300:
            current_lvl = "Apprenti"
            next_lvl = "Pratiquant"
            min_pts, max_pts = 100, 300
        elif pts < 600:
            current_lvl = "Pratiquant"
            next_lvl = "Maître"
            min_pts, max_pts = 300, 600
        else:
            current_lvl = "Maître"
            next_lvl = "Légende"
            min_pts, max_pts = 600, 1000

        diff = max_pts - min_pts
        progress_val = min(pts - min_pts, diff)
        progress_percent = int((progress_val / diff) * 100) if diff > 0 else 100

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, diff)
        progress_bar.setValue(progress_val)
        progress_bar.setFormat(f"{pts} / {max_pts} pts ({progress_percent}%)")
        
        progress_lbl = QLabel(f"<small>Progression vers le niveau <b>{next_lvl}</b></small>")
        level_progress_layout.addWidget(progress_lbl)
        level_progress_layout.addWidget(progress_bar)
        layout.addLayout(level_progress_layout)

        # ── Middle Section: Tiers & Stats ───────────────────────────────────
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(15)

        # Left: Challenge tiers progress
        tiers_layout = QVBoxLayout()
        tiers_lbl = QLabel("<b>Défis résolus par niveau :</b>")
        tiers_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        tiers_layout.addWidget(tiers_lbl)

        # Fetch solved counts
        solved_beg = self.repo.count_solved_by_points(self.user.id, 10)
        total_beg = self.repo.count_challenges_by_points(10) or 5
        
        solved_int = self.repo.count_solved_by_points(self.user.id, 20)
        total_int = self.repo.count_challenges_by_points(20) or 5
        
        solved_adv = self.repo.count_solved_by_points(self.user.id, 30)
        total_adv = self.repo.count_challenges_by_points(30) or 5

        # Beginner Progress
        beg_pb = QProgressBar(self)
        beg_pb.setRange(0, total_beg)
        beg_pb.setValue(solved_beg)
        beg_pb.setFormat(f"{solved_beg}/{total_beg}")
        beg_lbl = QLabel("<small>🟢 Débutant (10 pts)</small>")
        tiers_layout.addWidget(beg_lbl)
        tiers_layout.addWidget(beg_pb)

        # Intermediate Progress
        int_pb = QProgressBar(self)
        int_pb.setRange(0, total_int)
        int_pb.setValue(solved_int)
        int_pb.setFormat(f"{solved_int}/{total_int}")
        int_lbl = QLabel("<small>🟡 Intermédiaire (20 pts)</small>")
        tiers_layout.addWidget(int_lbl)
        tiers_layout.addWidget(int_pb)

        # Advanced Progress
        adv_pb = QProgressBar(self)
        adv_pb.setRange(0, total_adv)
        adv_pb.setValue(solved_adv)
        adv_pb.setFormat(f"{solved_adv}/{total_adv}")
        adv_lbl = QLabel("<small>🔴 Avancé (30 pts)</small>")
        tiers_layout.addWidget(adv_lbl)
        tiers_layout.addWidget(adv_pb)

        mid_layout.addLayout(tiers_layout, stretch=1)

        # Right: Time Spent & Unlocked Achievements stats
        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignTop)
        stats_lbl = QLabel("<b>Statistiques globales :</b>")
        stats_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        stats_layout.addWidget(stats_lbl)
        stats_layout.addSpacing(6)

        # Calculate time spent
        total_seconds = self.repo.get_total_time_spent(self.user.id)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        time_str = ""
        if hours > 0:
            time_str += f"{hours}h "
        time_str += f"{minutes}m {seconds}s"

        time_widget = QLabel(f"⏱️  <b>Temps d'entraînement :</b><br>&nbsp;&nbsp;&nbsp;&nbsp;{time_str}")
        time_widget.setStyleSheet("font-size: 12px; margin-bottom: 8px;")
        stats_layout.addWidget(time_widget)

        # Achievement count
        earned_ids = self.repo.get_user_achievement_ids(self.user.id)
        total_ach = len(self.repo.get_all_achievements()) or 6
        ach_pct = int((len(earned_ids) / total_ach) * 100) if total_ach > 0 else 0
        
        ach_widget = QLabel(f"🏆  <b>Succès débloqués :</b><br>&nbsp;&nbsp;&nbsp;&nbsp;{len(earned_ids)} / {total_ach} ({ach_pct}%)")
        ach_widget.setStyleSheet("font-size: 12px;")
        stats_layout.addWidget(ach_widget)

        mid_layout.addLayout(stats_layout, stretch=1)
        layout.addLayout(mid_layout)

        # ── Unlocked Achievements Grid ──────────────────────────────────────
        badge_lbl = QLabel("<b>Badge et Trophées de la Voie du Java :</b>")
        badge_lbl.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 5px;")
        layout.addWidget(badge_lbl)

        scroll = QScrollArea(self)
        scroll.setObjectName("badge_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(160)

        container = QWidget()
        container.setObjectName("badge_container")
        grid = QGridLayout(container)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setSpacing(8)

        # Load achievements dynamically
        all_ach = self.repo.get_all_achievements()
        cols = 2
        for idx, ach in enumerate(all_ach):
            row = idx // cols
            col = idx % cols
            
            is_earned = ach["id"] in earned_ids
            
            card = QWidget()
            card.setObjectName(f"ach_card_{ach['id']}")
            card_lay = QHBoxLayout(card)
            card_lay.setContentsMargins(6, 6, 6, 6)
            card_lay.setSpacing(8)
            
            icon_lbl = QLabel(ach["icon"])
            icon_lbl.setStyleSheet("font-size: 24px;")
            
            text_lay = QVBoxLayout()
            text_lay.setSpacing(2)
            
            title = QLabel(f"<b>{ach['title']}</b>")
            desc = QLabel(f"<small>{ach['description']}</small>")
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #6A6D56;")
            
            text_lay.addWidget(title)
            text_lay.addWidget(desc)
            
            card_lay.addWidget(icon_lbl)
            card_lay.addLayout(text_lay, stretch=1)
            
            if is_earned:
                card.setProperty("class", "badge_card")
                title.setStyleSheet("color: #4E533C; font-weight: bold;")
            else:
                card.setProperty("class", "badge_card_locked")
                # grey style for locked
                icon_lbl.setStyleSheet("font-size: 24px; color: #888888; background: transparent;")
                title.setStyleSheet("color: #8D9078; font-weight: bold;")
                desc.setStyleSheet("color: #9A9D86;")
                # Add locked icon visual indicator
                lock_lbl = QLabel("🔒")
                card_lay.addWidget(lock_lbl)

            grid.addWidget(card, row, col)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # ── Close Button ────────────────────────────────────────────────────
        close_btn = QPushButton("Fermer la session", self)
        close_btn.setObjectName("close_btn")
        close_btn.setText("Fermer   ✓")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
