"""
challenge_panel.py — Challenge list with HackerRank-style progression:
  • Beginner (10 pts) always unlocked
  • Intermediate (20 pts) unlocked after solving at least 3 beginner challenges
  • Advanced (30 pts) unlocked after solving at least 3 intermediate challenges
  • Solved challenges show a ✅ checkmark and cannot re-award points
  • Locked challenges are greyed out and unclickable
  • Includes search and filtering capabilities.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


# Thresholds to unlock the next difficulty tier
UNLOCK_THRESHOLD = 3   # solve this many beginner → unlock intermediate, etc.


class ChallengePanel(QWidget):

    def __init__(self, on_select):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.on_select = on_select
        self.setObjectName("left_panel")
        self.setMinimumWidth(170)
        self.setMaximumWidth(420)
        self._challenges = []
        self._solved_ids = set()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QLabel("  📜  Challenges", objectName="panel_header")
        hdr.setFixedHeight(40)
        lay.addWidget(hdr)

        sub = QLabel("  Java · Système de progression", objectName="panel_sub")
        sub.setFixedHeight(26)
        lay.addWidget(sub)

        # ── Barre de recherche et de filtres ───────────────────────────────
        self.filter_area = QWidget()
        self.filter_area.setObjectName("filter_area")
        self.filter_area.setFixedHeight(72)
        flay = QVBoxLayout(self.filter_area)
        flay.setContentsMargins(10, 5, 10, 5)
        flay.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un défi...")
        self.search_input.setObjectName("challenge_search")
        self.search_input.textChanged.connect(self._on_search_or_filter_changed)
        flay.addWidget(self.search_input)

        btn_lay = QHBoxLayout()
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(4)

        self.btn_all = QPushButton("Tous")
        self.btn_all.setObjectName("filter_btn_active")
        self.btn_all.setCheckable(True)
        self.btn_all.setAutoExclusive(True)
        self.btn_all.setChecked(True)
        self.btn_all.setCursor(Qt.PointingHandCursor)
        self.btn_all.clicked.connect(self._on_filter_btn_clicked)

        self.btn_unsolved = QPushButton("À faire")
        self.btn_unsolved.setObjectName("filter_btn")
        self.btn_unsolved.setCheckable(True)
        self.btn_unsolved.setAutoExclusive(True)
        self.btn_unsolved.setCursor(Qt.PointingHandCursor)
        self.btn_unsolved.clicked.connect(self._on_filter_btn_clicked)

        self.btn_solved = QPushButton("Résolus")
        self.btn_solved.setObjectName("filter_btn")
        self.btn_solved.setCheckable(True)
        self.btn_solved.setAutoExclusive(True)
        self.btn_solved.setCursor(Qt.PointingHandCursor)
        self.btn_solved.clicked.connect(self._on_filter_btn_clicked)

        btn_lay.addWidget(self.btn_all)
        btn_lay.addWidget(self.btn_unsolved)
        btn_lay.addWidget(self.btn_solved)
        flay.addLayout(btn_lay)

        lay.addWidget(self.filter_area)

        # ── Liste des challenges ──────────────────────────────────────────
        self.list = QListWidget()
        self.list.setObjectName("challenge_list")
        self.list.setSpacing(1)
        self.list.setCursor(Qt.PointingHandCursor)
        self.list.itemClicked.connect(self._on_item_clicked)
        lay.addWidget(self.list)

        # Unlock progress bar area
        self.progress_lbl = QLabel("", objectName="panel_footer")
        self.progress_lbl.setFixedHeight(40)
        self.progress_lbl.setWordWrap(True)
        self.progress_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        lay.addWidget(self.progress_lbl)

        foot = QLabel("  ✅ Résolu   🔒 Verrouillé",
                       objectName="panel_footer")
        foot.setFixedHeight(28)
        lay.addWidget(foot)

    def load(self, challenges, solved_ids: set = None):
        """
        Populate the list.
        solved_ids: set of challenge IDs the current user has already solved.
        """
        self._challenges = challenges
        self._solved_ids = solved_ids or set()
        self._refresh()

    def update_solved(self, solved_ids: set):
        """Call after a solve to refresh lock/checkmark state."""
        self._solved_ids = solved_ids
        self._refresh()

    def _on_search_or_filter_changed(self):
        self._refresh()

    def _on_filter_btn_clicked(self):
        # Update stylesheet/objectNames of the buttons to visually show active
        for btn in [self.btn_all, self.btn_unsolved, self.btn_solved]:
            if btn.isChecked():
                btn.setObjectName("filter_btn_active")
            else:
                btn.setObjectName("filter_btn")
            # Force stylesheet refresh
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        self._refresh()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _compute_unlocks(self) -> dict:
        """
        Returns {'10': True, '20': bool, '30': bool} based on solved counts.
        """
        by_pts = {10: 0, 20: 0, 30: 0}
        for ch in self._challenges:
            if ch.id in self._solved_ids:
                by_pts[ch.points] = by_pts.get(ch.points, 0) + 1

        return {
            10: True,
            20: by_pts[10] >= UNLOCK_THRESHOLD,
            30: by_pts[20] >= UNLOCK_THRESHOLD,
        }

    def _refresh(self):
        self.list.clear()
        unlocks = self._compute_unlocks()

        # Count totals per tier for progress display
        tier_total  = {10: 0, 20: 0, 30: 0}
        tier_solved = {10: 0, 20: 0, 30: 0}
        for ch in self._challenges:
            tier_total[ch.points]  = tier_total.get(ch.points, 0) + 1
            if ch.id in self._solved_ids:
                tier_solved[ch.points] = tier_solved.get(ch.points, 0) + 1

        # Filtrer la liste des challenges selon la recherche et le bouton actif
        search_txt = self.search_input.text().lower().strip()
        
        filter_type = "all"
        if self.btn_unsolved.isChecked():
            filter_type = "unsolved"
        elif self.btn_solved.isChecked():
            filter_type = "solved"

        filtered_challenges = []
        for ch in self._challenges:
            # Check search
            if search_txt and (search_txt not in ch.title.lower() and search_txt not in ch.description.lower()):
                continue
            # Check filter
            is_solved = ch.id in self._solved_ids
            if filter_type == "solved" and not is_solved:
                continue
            if filter_type == "unsolved" and is_solved:
                continue
            filtered_challenges.append(ch)

        prev_pts = None
        for ch in filtered_challenges:
            is_unlocked = unlocks.get(ch.points, False)
            is_solved   = ch.id in self._solved_ids

            # Section separator per tier
            if ch.points != prev_pts:
                self._add_separator(ch.points, tier_solved, tier_total, is_unlocked)
                prev_pts = ch.points

            # Build label
            if is_solved:
                icon = "✅"
            elif is_unlocked:
                icon = {10: "🟢", 20: "🟡", 30: "🔴"}.get(ch.points, "⚪")
            else:
                icon = "🔒"

            label = f"  {icon}  {ch.title}"
            if is_solved:
                label += "  ✓"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ch)
            item.setData(Qt.UserRole + 1, is_unlocked)  # store unlock state

            if not is_unlocked:
                item.setForeground(QColor("#888888"))
                item.setToolTip(
                    f"🔒 Verrouillé — résous {UNLOCK_THRESHOLD} challenges "
                    f"du niveau précédent pour débloquer."
                )
            elif is_solved:
                item.setForeground(QColor("#5DB85D"))
                item.setToolTip(
                    f"✅ Déjà résolu ! Tu peux réessayer, "
                    f"mais les points ne seront pas comptés à nouveau.\n"
                    f"+{ch.points} pts"
                )
            else:
                item.setToolTip(f"{ch.description}\n+{ch.points} pts")

            self.list.addItem(item)

        # Update progress hint
        self._update_progress_label(tier_solved, tier_total, unlocks)

    def _add_separator(self, pts: int, tier_solved: dict, tier_total: dict, is_unlocked: bool):
        labels = {10: "🟢  Débutant", 20: "🟡  Intermédiaire", 30: "🔴  Avancé"}
        label  = labels.get(pts, f"{pts} pts")
        solved = tier_solved.get(pts, 0)
        total  = tier_total.get(pts, 0)

        if not is_unlocked:
            text = f"  {label}  🔒  [{solved}/{total}]"
        else:
            text = f"  {label}  [{solved}/{total}]"

        sep = QListWidgetItem(text)
        sep.setFlags(Qt.NoItemFlags)                     # not selectable
        sep.setForeground(QColor("#8CA6A7"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        sep.setFont(font)
        self.list.addItem(sep)

    def _update_progress_label(self, tier_solved, tier_total, unlocks):
        lines = []
        if not unlocks[20]:
            needed = UNLOCK_THRESHOLD - tier_solved[10]
            lines.append(f"  Résous {needed} débutant(s) → 🟡 Intermédiaire")
        elif not unlocks[30]:
            needed = UNLOCK_THRESHOLD - tier_solved[20]
            lines.append(f"  Résous {needed} intermédiaire(s) → 🔴 Avancé")
        else:
            total_solved = sum(tier_solved.values())
            total        = sum(tier_total.values())
            if total_solved >= total:
                lines.append("  🏆 Tous les défis complétés !")
            else:
                lines.append(f"  {total_solved}/{total} résolus — continue !")
        self.progress_lbl.setText("\n".join(lines))

    def _on_item_clicked(self, item: QListWidgetItem):
        ch = item.data(Qt.UserRole)
        is_unlocked = item.data(Qt.UserRole + 1)
        if ch is None or not is_unlocked:
            return   # ignore separators and locked items
        self.on_select(ch)