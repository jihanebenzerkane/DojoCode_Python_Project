from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

class PairEditor(QWidget):
    """
    Éditeur split-screen pour le pair programming avec l'IA.
    Gauche: code de l'élève | Droite: suggestions de l'IA (read-only)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Panneau élève
        student_panel = QVBoxLayout()
        student_label = QLabel("🧑‍💻 Ton Code")
        student_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        self.student_editor = QTextEdit()
        self.student_editor.setAcceptRichText(False)
        self.student_editor.setFont(QFont("Consolas", 12))
        student_panel.addWidget(student_label)
        student_panel.addWidget(self.student_editor)
        
        # Panneau IA
        ai_panel = QVBoxLayout()
        ai_label = QLabel("🥋 Suggestion du Sensei")
        ai_label.setStyleSheet("color: #ce9178; font-weight: bold;")
        self.ai_editor = QTextEdit()
        self.ai_editor.setReadOnly(True)
        self.ai_editor.setFont(QFont("Consolas", 12))
        self.ai_editor.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                color: #dcdcaa;
                border: 2px dashed #ce9178;
            }
        """)
        ai_panel.addWidget(ai_label)
        ai_panel.addWidget(self.ai_editor)
        
        layout.addLayout(student_panel)
        layout.addLayout(ai_panel)
    
    def set_ai_suggestion(self, code: str, explanation: str):
        """Affiche une suggestion de l'IA avec explication."""
        self.ai_editor.setPlainText(f"// {explanation}\n\n{code}")
    
    def highlight_differences(self, student_code: str, ai_code: str):
        """Met en évidence les différences entre le code élève et la suggestion."""
        # Utiliser difflib pour montrer les lignes différentes
        pass