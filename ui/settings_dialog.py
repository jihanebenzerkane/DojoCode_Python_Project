"""
settings_dialog.py — Boîte de dialogue pour configurer l'IA et l'API Key.
Sauvegarde persistante dans settings.json à la racine.
"""
import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt


SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "settings.json"
)


def load_settings() -> dict:
    """Charge les paramètres depuis settings.json. Retourne les valeurs par défaut si inexistant."""
    defaults = {
        "ai_difficulty": "beginner",  # "beginner", "intermediate", "advanced"
        "api_key": ""
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # S'assurer que les clés par défaut sont présentes
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception as e:
            print(f"[Settings] Erreur lors de la lecture : {e}")
    
    # Si settings.json n'existe pas, essayer de lire les clés API dans .env pour rétrocompatibilité
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
    defaults["api_key"] = api_key
    return defaults


def save_settings(data: dict):
    """Sauvegarde les paramètres dans settings.json."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # Route the key to the correct provider env var based on its prefix
        api_key = data.get("api_key", "").strip()
        if api_key.startswith("AIzaSy"):
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ.pop("GROQ_API_KEY", None)
        elif api_key:
            os.environ["GROQ_API_KEY"] = api_key
            os.environ.pop("GEMINI_API_KEY", None)
    except Exception as e:
        print(f"[Settings] Erreur lors de l'écriture : {e}")


class SettingsDialog(QDialog):
    """Fenêtre modale des paramètres."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Dojo & Sensei IA ⚙️")
        self.setFixedSize(520, 480)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._settings = load_settings()
        self._build()
        self._style()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        # ── Titre principal ──
        title = QLabel("Paramètres de l'application")
        title.setObjectName("settings_title")
        lay.addWidget(title)

        # ── Section 1 : Configuration de la Clé API ──
        sec1_title = QLabel("🔑 Clé API (Groq ou Gemini)")
        sec1_title.setObjectName("settings_section_hdr")
        lay.addWidget(sec1_title)

        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("settings_input")
        self.api_key_input.setPlaceholderText("gsk_... (Groq) ou AIzaSy... (Gemini)")
        self.api_key_input.setFixedHeight(38)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self._settings.get("api_key", ""))

        self._show_key = False
        self._eye_btn = QPushButton("👁️")
        self._eye_btn.setObjectName("settings_eye_btn")
        self._eye_btn.setFixedSize(38, 38)
        self._eye_btn.setCursor(Qt.PointingHandCursor)
        self._eye_btn.setToolTip("Afficher / masquer la clé")
        self._eye_btn.clicked.connect(self._toggle_key_visibility)

        key_row = QHBoxLayout()
        key_row.setSpacing(6)
        key_row.addWidget(self.api_key_input)
        key_row.addWidget(self._eye_btn)
        lay.addLayout(key_row)

        key_hint = QLabel("   💡 Groq gratuit (gsk_...) → <a href='https://console.groq.com'>console.groq.com</a>"
                          " &nbsp;·&nbsp; Gemini → <a href='https://aistudio.google.com'>aistudio.google.com</a>")
        key_hint.setObjectName("settings_desc_lbl")
        key_hint.setWordWrap(True)
        key_hint.setOpenExternalLinks(True)
        lay.addWidget(key_hint)

        # ── Section 2 : Configuration du Sensei (Difficulté) ──
        sec2_title = QLabel("🧘 Comportement du Sensei IA")
        sec2_title.setObjectName("settings_section_hdr")
        lay.addWidget(sec2_title)

        # Container pour les options radio
        radio_frame = QFrame()
        radio_frame.setObjectName("settings_radio_card")
        radio_lay = QVBoxLayout(radio_frame)
        radio_lay.setContentsMargins(14, 12, 14, 12)
        radio_lay.setSpacing(12)

        self.btn_grp = QButtonGroup(self)

        # Option Débutant
        self.radio_beg = QRadioButton("Sensei Patient (Débutant)")
        self.radio_beg.setDescription = "Le Sensei te guide pas à pas avec des analogies simples et t'encourage à chaque étape."
        self.btn_grp.addButton(self.radio_beg)
        radio_lay.addWidget(self.radio_beg)
        
        desc_beg = QLabel("   💡 Guide pas à pas avec analogies simples.")
        desc_beg.setObjectName("settings_desc_lbl")
        radio_lay.addWidget(desc_beg)

        # Option Intermédiaire
        self.radio_int = QRadioButton("Ronin Exigeant (Intermédiaire)")
        self.radio_int.setDescription = "Le Sensei repère tes erreurs de logique et pointe directement vers la ligne ou le concept défectueux."
        self.btn_grp.addButton(self.radio_int)
        radio_lay.addWidget(self.radio_int)

        desc_int = QLabel("   💡 Indices ciblés sur les erreurs de logique.")
        desc_int.setObjectName("settings_desc_lbl")
        radio_lay.addWidget(desc_int)

        # Option Avancé
        self.radio_adv = QRadioButton("Maître Zen (Avancé)")
        self.radio_adv.setDescription = "Le Sensei répond par des questions socratiques minimalistes et profondes pour te forcer à chercher par toi-même."
        self.btn_grp.addButton(self.radio_adv)
        radio_lay.addWidget(self.radio_adv)

        desc_adv = QLabel("   💡 Questions philosophiques et indices cryptiques.")
        desc_adv.setObjectName("settings_desc_lbl")
        radio_lay.addWidget(desc_adv)

        lay.addWidget(radio_frame)

        # Sélectionner la valeur actuelle
        mode = self._settings.get("ai_difficulty", "beginner")
        if mode == "intermediate":
            self.radio_int.setChecked(True)
        elif mode == "advanced":
            self.radio_adv.setChecked(True)
        else:
            self.radio_beg.setChecked(True)

        # ── Boutons de bas de page (Sauver / Annuler) ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setObjectName("settings_btn_sec")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setObjectName("settings_btn_pri")
        self.save_btn.clicked.connect(self._save)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        lay.addLayout(btn_row)

    def _toggle_key_visibility(self):
        """Toggle API key field between hidden and visible."""
        self._show_key = not self._show_key
        if self._show_key:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self._eye_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self._eye_btn.setText("👁️")

    def _save(self):
        # Récupérer la clé API
        api_key = self.api_key_input.text().strip()

        # Récupérer la difficulté
        difficulty = "beginner"
        if self.radio_int.isChecked():
            difficulty = "intermediate"
        elif self.radio_adv.isChecked():
            difficulty = "advanced"

        # Sauvegarder
        self._settings["ai_difficulty"] = difficulty
        self._settings["api_key"] = api_key
        save_settings(self._settings)

        self.accept()

    def _style(self):
        # Stylesheet spécifique pour s'intégrer au thème clair et zen de l'app
        self.setStyleSheet("""
            QDialog {
                background: #F5F7EC;
                color: #4E533C;
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
            }
            QLabel#settings_title {
                font-size: 18px;
                font-weight: bold;
                color: #4E533C;
                border-bottom: 2px solid rgba(78, 83, 60, 0.2);
                padding-bottom: 6px;
            }
            QLabel#settings_section_hdr {
                font-size: 13px;
                font-weight: bold;
                color: #8D9078;
                margin-top: 4px;
            }
            QLineEdit#settings_input {
                background: #FFFFFF;
                border: 1px solid rgba(78, 83, 60, 0.4);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                color: #4E533C;
            }
            QLineEdit#settings_input:focus {
                border: 1.5px solid #8D9078;
            }
            QFrame#settings_radio_card {
                background: #FFFFFF;
                border: 1px solid rgba(78, 83, 60, 0.2);
                border-radius: 8px;
            }
            QRadioButton {
                font-weight: bold;
                font-size: 13px;
                color: #4E533C;
                min-height: 24px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QLabel#settings_desc_lbl {
                font-size: 11px;
                color: #8D9078;
                margin-left: 24px;
                margin-bottom: 10px;
            }
            QPushButton#settings_btn_pri {
                background: #8D9078;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#settings_btn_pri:hover {
                background: #9FA28A;
            }
            QPushButton#settings_btn_pri:pressed {
                background: #4E533C;
            }
            QPushButton#settings_btn_sec {
                background: transparent;
                color: #8D9078;
                border: 1px solid rgba(141, 144, 120, 0.4);
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
            }
            QPushButton#settings_btn_sec:hover {
                background: rgba(141, 144, 120, 0.1);
                color: #4E533C;
            }
        """)