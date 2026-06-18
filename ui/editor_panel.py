"""
editor_panel.py — Panneau central contenant l'éditeur de code Java avec coloration syntaxique et numérotation des lignes.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QMessageBox, QTextEdit, QSplitter
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QTextCursor

from ui.java_highlighter import JavaHighlighter
from services.draft_service import DraftService

JAVA_BOILERPLATES = {
    'Hello Dojo': (
        "public class Solution {\n"
        "    public static String sayHello() {\n"
        "        // Écris ton code ici\n"
        "        return \"\";\n"
        "    }\n"
        "}"
    ),
    'Pair ou Impair': (
        "public class Solution {\n"
        "    public static boolean isEven(int n) {\n"
        "        // Écris ton code ici\n"
        "        return false;\n"
        "    }\n"
        "}"
    ),
    'Maximum de deux nombres': (
        "public class Solution {\n"
        "    public static int max(int a, int b) {\n"
        "        // Écris ton code ici\n"
        "        return 0;\n"
        "    }\n"
        "}"
    ),
    'Somme d\'un tableau': (
        "public class Solution {\n"
        "    public static int sumArray(int[] arr) {\n"
        "        // Écris ton code ici\n"
        "        return 0;\n"
        "    }\n"
        "}"
    ),
    'Inverser une chaine': (
        "public class Solution {\n"
        "    public static String reverseString(String s) {\n"
        "        // Écris ton code ici\n"
        "        return \"\";\n"
        "    }\n"
        "}"
    ),
    'Compter les voyelles': (
        "public class Solution {\n"
        "    public static int countVowels(String s) {\n"
        "        // Écris ton code ici\n"
        "        return 0;\n"
        "    }\n"
        "}"
    ),
    'Fibonacci': (
        "public class Solution {\n"
        "    public static int fibonacci(int n) {\n"
        "        // Écris ton code ici\n"
        "        return 0;\n"
        "    }\n"
        "}"
    ),
    'Palindrome': (
        "public class Solution {\n"
        "    public static boolean isPalindrome(String s) {\n"
        "        // Écris ton code ici\n"
        "        return false;\n"
        "    }\n"
        "}"
    ),
    'Tableau trie': (
        "public class Solution {\n"
        "    public static boolean isSorted(int[] arr) {\n"
        "        // Écris ton code ici\n"
        "        return false;\n"
        "    }\n"
        "}"
    ),
    'Occurrence d\'un caractere': (
        "public class Solution {\n"
        "    public static int charCount(String s, char c) {\n"
        "        // Écris ton code ici\n"
        "        return 0;\n"
        "    }\n"
        "}"
    ),
    'FizzBuzz': (
        "import java.util.List;\n"
        "import java.util.ArrayList;\n\n"
        "public class Solution {\n"
        "    public static List<String> fizzBuzz(int n) {\n"
        "        // Écris ton code ici\n"
        "        return new ArrayList<>();\n"
        "    }\n"
        "}"
    ),
    'Nombre premier': (
        "public class Solution {\n"
        "    public static boolean isPrime(int n) {\n"
        "        // Écris ton code ici\n"
        "        return false;\n"
        "    }\n"
        "}"
    ),
    'Anagramme': (
        "public class Solution {\n"
        "    public static boolean isAnagram(String s1, String s2) {\n"
        "        // Écris ton code ici\n"
        "        return false;\n"
        "    }\n"
        "}"
    ),
    'Factorielle': (
        "public class Solution {\n"
        "    public static int factorial(int n) {\n"
        "        // Écris ton code ici\n"
        "        return 1;\n"
        "    }\n"
        "}"
    ),
    'Deux sommes': (
        "import java.util.HashMap;\n\n"
        "public class Solution {\n"
        "    public static int[] twoSum(int[] nums, int target) {\n"
        "        // Écris ton code ici\n"
        "        return new int[2];\n"
        "    }\n"
        "}"
    )
}


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
    """Éditeur de code avec numérotation de lignes synchronisée et raccourcis clavier."""
    submit_requested = Signal()
    verify_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)

    def keyPressEvent(self, event):
        # Ctrl+Enter -> Soumettre au Sensei
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.submit_requested.emit()
            event.accept()
            return
        # Ctrl+Shift+V -> Vérifier le code
        elif event.key() == Qt.Key_V and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.verify_requested.emit()
            event.accept()
            return
        # Ctrl+/ -> Commenter / décommenter
        elif event.key() == Qt.Key_Slash and event.modifiers() == Qt.ControlModifier:
            self.toggle_comment()
            event.accept()
            return
        super().keyPressEvent(event)

    def toggle_comment(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            # Commenter/décommenter une seule ligne
            cursor.select(QTextCursor.LineUnderCursor)
            text = cursor.selectedText()
            block = cursor.block()
            text = block.text()
            stripped = text.lstrip()
            if stripped.startswith("//"):
                idx = text.find("//")
                length_to_remove = 2
                if len(text) > idx + 2 and text[idx + 2] == ' ':
                    length_to_remove = 3
                new_text = text[:idx] + text[idx + length_to_remove:]
            else:
                indent_len = len(text) - len(stripped)
                new_text = text[:indent_len] + "// " + stripped

            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            cursor.insertText(new_text)
            cursor.endEditBlock()
        else:
            # Commenter/décommenter plusieurs lignes
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()

            cursor.setPosition(start_pos)
            start_block = cursor.blockNumber()
            cursor.setPosition(end_pos)
            end_block = cursor.blockNumber()

            cursor.beginEditBlock()
            for block_num in range(start_block, end_block + 1):
                block = self.document().findBlockByNumber(block_num)
                if not block.isValid():
                    continue
                text = block.text()
                stripped = text.lstrip()
                if not stripped:  # ignorer les lignes vides
                    continue

                temp_cursor = QTextCursor(block)
                if stripped.startswith("//"):
                    idx = text.find("//")
                    length_to_remove = 2
                    if len(text) > idx + 2 and text[idx + 2] == ' ':
                        length_to_remove = 3
                    new_text = text[:idx] + text[idx + length_to_remove:]
                else:
                    indent_len = len(text) - len(stripped)
                    new_text = text[:indent_len] + "// " + stripped

                temp_cursor.movePosition(QTextCursor.StartOfBlock)
                temp_cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                temp_cursor.insertText(new_text)
            cursor.endEditBlock()

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
        pass

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#EAE5D9"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#5c5c70"))
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
        self.user_id = None
        self._loading = False
        self.draft_svc = DraftService()
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

        code_hdr = QLabel("  ✏️  Ton code Java (Ctrl+Enter : Soumettre | Ctrl+Shift+V : Vérifier)")
        code_hdr.setObjectName("panel_sub")
        code_hdr.setFixedHeight(28)
        lay.addWidget(code_hdr)

        # ── Séparateur redimensionnable pour l'éditeur et la console ──
        self.splitter = QSplitter(Qt.Vertical)
        lay.addWidget(self.splitter)

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
        self.splitter.addWidget(self.editor)

        # Connecter les raccourcis clavier
        self.editor.submit_requested.connect(self._submit)
        self.editor.verify_requested.connect(self._verify)

        # ── Console (masquée par défaut) ─────────────
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet("background-color: #1E1E1E; color: #00FF00; padding: 5px;")
        self.console.setText("> Terminal d'exécution prêt...\n> Appuie sur 'Vérifier mon code' pour compiler.\n")
        self.console.setVisible(False)
        self.splitter.addWidget(self.console)

        # ── Bottom bar — line count + verify & submit buttons ─────────────
        bar = QWidget()
        bar.setObjectName("submit_bar")
        bar.setFixedHeight(52)
        blay = QHBoxLayout(bar)
        blay.setContentsMargins(14, 0, 14, 0)
        blay.setSpacing(10)

        self.status_lbl = QLabel("Ln 1, Col 1  |  ☕ Java")
        self.status_lbl.setObjectName("char_count")
        self.editor.textChanged.connect(self._auto_save_draft)
        self.editor.cursorPositionChanged.connect(self._update_status)

        self.console_btn = QPushButton("  Console  💻")
        self.console_btn.setObjectName("console_btn")
        self.console_btn.setCursor(Qt.PointingHandCursor)
        self.console_btn.setFixedHeight(38)
        self.console_btn.clicked.connect(self._toggle_console)

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

        blay.addWidget(self.status_lbl)
        blay.addStretch()
        blay.addWidget(self.console_btn)
        blay.addWidget(self.verify_btn)
        blay.addWidget(self.submit_btn)
        lay.addWidget(bar)

    def load(self, challenge, user_id):
        self._loading = True
        self.current_challenge = challenge
        self.user_id = user_id

        self.title_lbl.setText(f"  {challenge.title}   [+{challenge.points} pts]")
        self.desc_lbl.setText(f"  {challenge.description}")
        self.editor.clear()

        # Charger le brouillon si disponible
        draft = self.draft_svc.load_draft(user_id, challenge.id)
        if draft is not None:
            self.editor.setPlainText(draft)
        else:
            # Charger le squelette Java boilerplate pour ce challenge spécifique
            boilerplate = JAVA_BOILERPLATES.get(challenge.title, None)
            if boilerplate is None:
                # Fallback générique
                boilerplate = (
                    "public class Solution {\n"
                    "    // Écris ton code ici\n"
                    "}"
                )
            self.editor.setPlainText(boilerplate)

        self._loading = False
        self._update_status()

    def _auto_save_draft(self):
        if self._loading:
            return
        if not self.current_challenge or not self.user_id:
            return
        code = self.editor.toPlainText()
        self.draft_svc.save_draft(self.user_id, self.current_challenge.id, code)

    def _update_status(self):
        cursor = self.editor.textCursor()
        ln = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.status_lbl.setText(f"Ln {ln}, Col {col}  |  ☕ Java")

    def _toggle_console(self):
        self.console.setVisible(not self.console.isVisible())

    def show_console_output(self, text: str, is_error: bool = False):
        self.console.setVisible(True)
        color = QColor("#FF5555") if is_error else QColor("#00FF00")
        self.console.setTextColor(color)
        self.console.append(text)
        self.console.moveCursor(QTextCursor.End)

    def _validate_code(self, code: str) -> bool:
        """Vérifie que le code contient au minimum 'class' et les accolades '{' et '}'."""
        c = code.strip()
        return "class" in c and "{" in c and "}" in c

    def _submit(self):
        code = self.editor.toPlainText().strip()
        if not code or not self.current_challenge:
            return
        # Validation du code
        if not self._validate_code(code):
            QMessageBox.warning(
                self,
                "Validation du code",
                "Ton code doit contenir au minimum la déclaration d'une classe Java "
                "et des accolades (ex: 'public class Solution { ... }')."
            )
            return
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("  Envoi en cours...  ⏳")
        self.on_submit(code, self.current_challenge)

    def _verify(self):
        code = self.editor.toPlainText().strip()
        if not code or not self.current_challenge:
            return
        # Validation du code
        if not self._validate_code(code):
            QMessageBox.warning(
                self,
                "Validation du code",
                "Ton code doit contenir au minimum la déclaration d'une classe Java "
                "et des accolades (ex: 'public class Solution { ... }')."
            )
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
