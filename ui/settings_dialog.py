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
        # Mettre à jour l'environnement pour les appels en cours
        os.environ["GEMINI_API_KEY"] = data["api_key"]
        os.environ["GROQ_API_KEY"] = data["api_key"]
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

        # ── Section 1 : Configuration de la Clé API (Retirée) ──
        # L'utilisateur ne doit plus configurer l'API Key ici.

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

    def _save(self):
        # Récupérer la difficulté
        
        difficulty = "beginner"
        if self.radio_int.isChecked():
            difficulty = "intermediate"
        elif self.radio_adv.isChecked():
            difficulty = "advanced"

        # Sauvegarder
        # L'API key reste inchangée
        self._settings["ai_difficulty"] = difficulty
        save_settings(self._settings)

        self.accept()

    def _style(self):
        # Stylesheet spécifique pour s'intégrer au thème clair et zen de l'app
        self.setStyleSheet("""
            QDialog {
                background: #F9F6F0;
                color: #2A3B3C;
                font-family: 'Segoe UI', 'Yu Gothic UI', sans-serif;
            }
            QLabel#settings_title {
                font-size: 18px;
                font-weight: bold;
                color: #2A3B3C;
                border-bottom: 2px solid rgba(94, 123, 125, 0.2);
                padding-bottom: 6px;
            }
            QLabel#settings_section_hdr {
                font-size: 13px;
                font-weight: bold;
                color: #5D7F81;
                margin-top: 4px;
            }
            QLineEdit#settings_input {
                background: #FFFFFF;
                border: 1px solid rgba(94, 123, 125, 0.4);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                color: #2A3B3C;
            }
            QLineEdit#settings_input:focus {
                border: 1.5px solid #D97A3E;
            }
            QFrame#settings_radio_card {
                background: rgba(255, 255, 255, 0.5);
                border: 1px solid rgba(94, 123, 125, 0.2);
                border-radius: 8px;
            }
            QRadioButton {
                font-weight: bold;
                font-size: 13px;
                color: #2A3B3C;
                min-height: 24px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QLabel#settings_desc_lbl {
                font-size: 11px;
                color: #5E7B7D;
                margin-left: 24px;
                margin-bottom: 10px;
            }
            QPushButton#settings_btn_pri {
                background: #D97A3E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#settings_btn_pri:hover {
                background: #E89F3E;
            }
            QPushButton#settings_btn_pri:pressed {
                background: #B65E2A;
            }
            QPushButton#settings_btn_sec {
                background: transparent;
                color: #5E7B7D;
                border: 1px solid rgba(94, 123, 125, 0.4);
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
            }
            QPushButton#settings_btn_sec:hover {
                background: rgba(94, 123, 125, 0.1);
                color: #2A3B3C;
            }
        """)
