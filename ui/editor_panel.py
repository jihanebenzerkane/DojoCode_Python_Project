"""
editor_panel.py — Panneau central contenant l'éditeur de code Java avec coloration syntaxique et numérotation des lignes.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QFont, QPainter, QColor

from ui.java_highlighter import JavaHighlighter


class LineNumberArea(QWidget):
    """Widget de la zone de numérotation de ligne attaché à l'éditeur."""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class QCodeEditor(QPlainTextEdit):
    """Éditeur de code avec numérotation de lignes synchronisée."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        # On peut désactiver ou appliquer un surlignage soft
        pass

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        # Background de la zone de numérotation, s'accorde au thème clair de l'éditeur
        painter.fillRect(event.rect(), QColor("#EAE5D9"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                # Couleur douce pour les numéros de ligne
                painter.setPen(QColor("#5c5c70"))
                # Police de numérotation
                painter.setFont(self.font())
                painter.drawText(0, top, self.line_number_area.width() - 6, self.fontMetrics().height(),
                                 Qt.AlignRight | Qt.AlignVCenter, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class EditorPanel(QWidget):
    def __init__(self, on_submit, on_verify):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.on_submit = on_submit
        self.on_verify = on_verify
        self.current_challenge = None
        self.setObjectName("center_panel")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.title_lbl = QLabel("  Sélectionne un challenge →")
        self.title_lbl.setObjectName("panel_header")
        self.title_lbl.setFixedHeight(40)
        lay.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(
            "  Clique sur un challenge à gauche pour commencer."
        )
        self.desc_lbl.setObjectName("desc_label")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setFixedHeight(72)
        self.desc_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lay.addWidget(self.desc_lbl)

        code_hdr = QLabel("  ✏️  Ton code Java")
        code_hdr.setObjectName("panel_sub")
        code_hdr.setFixedHeight(28)
        lay.addWidget(code_hdr)

        # ── Code editor avec numérotation et Java syntax highlighter ──────
        self.editor = QCodeEditor()
        self.editor.setObjectName("code_editor")
        self.editor.setPlaceholderText(
            "// Écris ton code Java ici...\n\n"
            "public class Solution {\n"
            "    // ton code\n"
            "}"
        )
        self.editor.setFont(QFont("Consolas", 12))
        self._highlighter = JavaHighlighter(self.editor.document())
        lay.addWidget(self.editor)

        # ── Bottom bar — line count + verify & submit buttons ─────────────
        bar = QWidget()
        bar.setObjectName("submit_bar")
        bar.setFixedHeight(52)
        blay = QHBoxLayout(bar)
        blay.setContentsMargins(14, 0, 14, 0)
        blay.setSpacing(10)

        self.lines_lbl = QLabel("0 lignes")
        self.lines_lbl.setObjectName("char_count")
        self.editor.textChanged.connect(self._update_lines)

        self.verify_btn = QPushButton("  Vérifier mon code  🧪")
        self.verify_btn.setObjectName("verify_btn")
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        self.verify_btn.setFixedHeight(38)
        self.verify_btn.clicked.connect(self._verify)

        self.submit_btn = QPushButton("  Soumettre au Sensei  ➤")
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.setFixedHeight(38)
        self.submit_btn.clicked.connect(self._submit)

        blay.addWidget(self.lines_lbl)
        blay.addStretch()
        blay.addWidget(self.verify_btn)
        blay.addWidget(self.submit_btn)
        lay.addWidget(bar)

    def load(self, challenge):
        self.current_challenge = challenge
        self.title_lbl.setText(f"  {challenge.title}   [+{challenge.points} pts]")
        self.desc_lbl.setText(f"  {challenge.description}")
        self.editor.clear()
        self.editor.setPlaceholderText(
            f"// {challenge.title}\n"
            f"// Concepts : {challenge.expected_concepts}\n\n"
            "public class Solution {\n    \n}"
        )

    def _update_lines(self):
        n = self.editor.document().lineCount()
        self.lines_lbl.setText(f"{n} ligne{'s' if n > 1 else ''}")

    def _submit(self):
        code = self.editor.toPlainText().strip()
        if not code or not self.current_challenge:
            return
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("  Envoi en cours...  ⏳")
        self.on_submit(code, self.current_challenge)

    def _verify(self):
        code = self.editor.toPlainText().strip()
        if not code or not self.current_challenge:
            return
        self.verify_btn.setEnabled(False)
        self.verify_btn.setText("  Vérification...  ⏳")
        self.on_verify(code, self.current_challenge)

    def enable_submit(self):
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("  Soumettre au Sensei  ➤")

    def enable_verify(self):
        self.verify_btn.setEnabled(True)
        self.verify_btn.setText("  Vérifier mon code  🧪")
