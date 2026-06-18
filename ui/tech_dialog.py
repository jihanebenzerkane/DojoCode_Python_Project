"""
tech_dialog.py - PySide dialog that exposes the project's technical stack.

This is intentionally visible in the UI because the project is academic:
it helps demonstrate PySide, database persistence and AI integration quickly.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class TechDialog(QDialog):
    def __init__(self, repo, ai_provider: str, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.ai_provider = ai_provider
        self.setWindowTitle("Stack technique CodeDojo")
        self.setMinimumSize(620, 460)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._build()
        self._style()

    def _build(self):
        report = self.repo.health_report()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(16)

        title = QLabel("Architecture vivante du projet")
        title.setObjectName("tech_title")
        root.addWidget(title)

        subtitle = QLabel(
            "PySide6 pilote l'interface, le repository isole la base de donnees, "
            "et le service IA tourne hors du thread graphique."
        )
        subtitle.setObjectName("tech_subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.addWidget(self._card("UI", "PySide6 / Qt", "Widgets, QSS, QThread, signaux/slots"), 0, 0)
        grid.addWidget(self._card("Base", report["backend"], self._db_details(report)), 0, 1)
        grid.addWidget(self._card("IA", self.ai_provider, "Prompt socratique, historique borne, timeout API"), 1, 0)
        grid.addWidget(self._card("Robustesse", "Mode degrade", "MySQL en priorite, SQLite local si MySQL est absent"), 1, 1)
        root.addLayout(grid)

        metrics = QFrame()
        metrics.setObjectName("tech_metrics")
        metrics_lay = QGridLayout(metrics)
        metrics_lay.setContentsMargins(14, 12, 14, 12)
        metrics_lay.setHorizontalSpacing(16)
        metrics_lay.setVerticalSpacing(10)

        items = [
            ("Utilisateurs", report["users"]),
            ("Challenges", report["challenges"]),
            ("Sessions", report["sessions"]),
            ("Messages IA", report["messages"]),
        ]
        for idx, (label, value) in enumerate(items):
            metrics_lay.addWidget(self._metric(label, value), idx // 2, idx % 2)
        root.addWidget(metrics)

        flow = QLabel(
            "Flux demo: Login -> Challenge -> Code Java -> Verification locale ou Sensei IA -> "
            "session et messages sauvegardes en base."
        )
        flow.setObjectName("tech_flow")
        flow.setWordWrap(True)
        root.addWidget(flow)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("tech_close_btn")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    def _card(self, label: str, title: str, body: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("tech_card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        tag = QLabel(label.upper())
        tag.setObjectName("tech_tag")
        lay.addWidget(tag)

        headline = QLabel(title)
        headline.setObjectName("tech_card_title")
        headline.setWordWrap(True)
        lay.addWidget(headline)

        desc = QLabel(body)
        desc.setObjectName("tech_card_body")
        desc.setWordWrap(True)
        lay.addWidget(desc)
        return frame

    def _metric(self, label: str, value: int) -> QFrame:
        frame = QFrame()
        frame.setObjectName("tech_metric")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)

        value_lbl = QLabel(str(value))
        value_lbl.setObjectName("tech_metric_value")
        label_lbl = QLabel(label)
        label_lbl.setObjectName("tech_metric_label")
        lay.addWidget(value_lbl)
        lay.addWidget(label_lbl)
        return frame

    def _db_details(self, report: dict) -> str:
        status = "connectee" if report["connected"] else "hors ligne"
        return f"Connexion {status}. Source: {report['database']}"

    def _style(self):
        self.setStyleSheet("""
            QDialog {
                background: #08101F;
                color: #E6F1FF;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#tech_title {
                font-size: 22px;
                font-weight: 800;
                color: #FFFFFF;
            }
            QLabel#tech_subtitle, QLabel#tech_flow {
                color: rgba(230, 241, 255, 0.72);
                font-size: 13px;
                line-height: 1.4;
            }
            QFrame#tech_card, QFrame#tech_metrics {
                background: rgba(18, 28, 48, 0.92);
                border: 1px solid rgba(77, 218, 197, 0.22);
                border-radius: 10px;
            }
            QLabel#tech_tag {
                color: #4DDAC5;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0px;
            }
            QLabel#tech_card_title {
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 750;
            }
            QLabel#tech_card_body {
                color: rgba(230, 241, 255, 0.68);
                font-size: 12px;
            }
            QFrame#tech_metric {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QLabel#tech_metric_value {
                color: #4DDAC5;
                font-size: 20px;
                font-weight: 800;
            }
            QLabel#tech_metric_label {
                color: rgba(230, 241, 255, 0.62);
                font-size: 12px;
            }
            QPushButton#tech_close_btn {
                background: #4DDAC5;
                color: #06111F;
                border: none;
                border-radius: 8px;
                padding: 8px 22px;
                font-weight: 800;
            }
            QPushButton#tech_close_btn:hover {
                background: #67E8D7;
            }
        """)
