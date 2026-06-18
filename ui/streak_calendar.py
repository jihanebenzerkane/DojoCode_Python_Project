from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from datetime import datetime, timedelta

class StreakCalendar(QWidget):
    """Calendrier visuel des jours de codage (style GitHub contributions)."""
    
    def __init__(self, coding_days: list, parent=None):
        """
        coding_days: liste de dates où l'utilisateur a codé
        """
        super().__init__(parent)
        self.coding_days = set(coding_days)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(2)
        
        # 7 jours x 12 semaines
        today = QDate.currentDate()
        start_date = today.addDays(-84)  # 12 semaines
        
        for week in range(12):
            for day in range(7):
                date = start_date.addDays(week * 7 + day)
                if date > today:
                    continue
                
                cell = QLabel()
                cell.setFixedSize(12, 12)
                cell.setToolTip(date.toString("dd MMM yyyy"))
                
                if date.toPython() in self.coding_days:
                    intensity = self._get_intensity(date.toPython())
                    colors = {
                        1: "#9be9a8",
                        2: "#40c463", 
                        3: "#30a14e",
                        4: "#216e39"
                    }
                    cell.setStyleSheet(f"background-color: {colors[intensity]}; border-radius: 2px;")
                else:
                    cell.setStyleSheet("background-color: #ebedf0; border-radius: 2px;")
                
                layout.addWidget(cell, day, week)
    
    def _get_intensity(self, date) -> int:
        """Calcule l'intensité (1-4) basé sur le temps de codage ce jour."""
        # Query DB pour le temps passé ce jour
        # Return 1-4 selon les tranches
        return 2  # Default
        