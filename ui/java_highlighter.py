"""
java_highlighter.py — Colorisation syntaxique Java pour le QPlainTextEdit.
Utilise QSyntaxHighlighter de PySide6.
"""
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class JavaHighlighter(QSyntaxHighlighter):
    """Colorisation syntaxique Java basique (mots-clés, chaînes, commentaires, chiffres)."""

    KEYWORDS = [
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
        "class", "const", "continue", "default", "do", "double", "else", "enum",
        "extends", "final", "finally", "float", "for", "goto", "if", "implements",
        "import", "instanceof", "int", "interface", "long", "native", "new", "null",
        "package", "private", "protected", "public", "return", "short", "static",
        "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
        "transient", "try", "void", "volatile", "while", "true", "false",
        "String", "ArrayList", "HashMap", "List", "Map", "System", "Math",
    ]

    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # ── Keywords ──────────────────────────────────────────────────────
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor("#8EC07C"))  # Sage green (warm lofi)
        kw_fmt.setFontWeight(QFont.Bold)
        for word in self.KEYWORDS:
            pattern = QRegularExpression(rf"\b{word}\b")
            self.rules.append((pattern, kw_fmt))

        # ── Strings: double-quoted ────────────────────────────────────────
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#E6B86A"))  # Warm amber (lofi)
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), str_fmt))

        # ── Strings: single-quoted chars ──────────────────────────────────
        char_fmt = QTextCharFormat()
        char_fmt.setForeground(QColor("#E6B86A"))  # Warm amber
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), char_fmt))

        # ── Numeric literals ─────────────────────────────────────────────
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#D3956A"))  # Warm terracotta
        self.rules.append((QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"), num_fmt))

        # ── Annotations ──────────────────────────────────────────────────
        ann_fmt = QTextCharFormat()
        ann_fmt.setForeground(QColor("#B8BB8E"))  # Olive cream (lofi)
        self.rules.append((QRegularExpression(r"@\w+"), ann_fmt))

        # ── Single-line comments // ───────────────────────────────────────
        self._comment_fmt = QTextCharFormat()
        self._comment_fmt.setForeground(QColor("#928374"))  # Warm gray (lofi)
        self._comment_fmt.setFontItalic(True)
        self.rules.append((QRegularExpression(r"//[^\n]*"), self._comment_fmt))

        # ── Block comments /* */ ──────────────────────────────────────────
        self._block_start = QRegularExpression(r"/\*")
        self._block_end = QRegularExpression(r"\*/")

    def highlightBlock(self, text: str):
        # Apply single-line rules
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # Handle /* ... */ multiline block comments
        self.setCurrentBlockState(0)
        start = 0
        if self.previousBlockState() != 1:
            m = self._block_start.match(text)
            if m.hasMatch():
                start = m.capturedStart()
            else:
                return  # no block comment

        while start >= 0:
            m_end = self._block_end.match(text, start)
            if m_end.hasMatch():
                length = m_end.capturedEnd() - start
                self.setFormat(start, length, self._comment_fmt)
                m_next = self._block_start.match(text, m_end.capturedEnd())
                start = m_next.capturedStart() if m_next.hasMatch() else -1
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start, len(text) - start, self._comment_fmt)
                break
