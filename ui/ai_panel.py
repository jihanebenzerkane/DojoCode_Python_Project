"""
ai_panel.py — Panneau de droite contenant le chat de conversation socratique avec le Sensei.
"""
from html import escape
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QTimer

class AIPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("right_panel")
        self.setMinimumWidth(200)
        self.setMaximumWidth(500)
        self._thinking_lbl = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QLabel("  🧘  Sensei IA", objectName="panel_header")
        hdr.setFixedHeight(40)
        lay.addWidget(hdr)

        self.sub_lbl = QLabel("  IA · Méthode socratique",
                     objectName="panel_sub")
        self.sub_lbl.setFixedHeight(26)
        lay.addWidget(self.sub_lbl)

        self.scroll = QScrollArea(objectName="chat_scroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget(objectName="chat_container")
        self.chat_lay = QVBoxLayout(self.container)
        self.chat_lay.setContentsMargins(10, 10, 10, 10)
        self.chat_lay.setSpacing(10)
        self.chat_lay.addStretch()

        self.scroll.setWidget(self.container)
        lay.addWidget(self.scroll)

        # ── Welcome message ───────────────────────────────────────────────
        self._add("sensei",
                  "Konnichiwa 🎋\n\n"
                  "Je suis le Sensei, ton guide sur la voie du Java.\n\n"
                  "Choisis un challenge à gauche, écris ton code,\n"
                  "et soumets-le — je te guiderai par des indices\n"
                  "et des questions, sans jamais te donner\n"
                  "la réponse directement.\n\n"
                  "一歩一歩 — Un pas à la fois. 🥋")

    def set_provider_label(self, label: str):
        """Update the subtitle to reflect the active AI provider."""
        self.sub_lbl.setText(f"  {label}")

    def _add(self, role: str, text: str):
        prefix = "🧘 Sensei" if role == "sensei" else "🥋 Toi"
        obj = "bubble_sensei" if role == "sensei" else "bubble_user"
        safe_text = escape(text).replace(chr(10), '<br>')
        lbl = QLabel(
            f"<b>{prefix}</b><br><br>{safe_text}",
            objectName=obj
        )
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_lay.insertWidget(self.chat_lay.count() - 1, lbl)
        self._scroll_bottom()

    def _scroll_bottom(self):
        QTimer.singleShot(60, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))

    def add_user(self, code: str):
        preview = code[:120] + "..." if len(code) > 120 else code
        self._add("user", preview)

    def add_sensei(self, text: str):
        self._add("sensei", text)

    def show_thinking(self):
        self._thinking_lbl = QLabel(
            "🧘 Sensei réfléchit...",
            objectName="bubble_thinking"
        )
        self._thinking_lbl.setWordWrap(True)
        self.chat_lay.insertWidget(self.chat_lay.count() - 1, self._thinking_lbl)
        self._scroll_bottom()

    def hide_thinking(self):
        if self._thinking_lbl:
            self._thinking_lbl.deleteLater()
            self._thinking_lbl = None

    def show_success(self, points: int):
        lbl = QLabel(f"✅  +{points} pts gagnés !  🏆",
                     objectName="success_banner")
        lbl.setAlignment(Qt.AlignCenter)
        self.chat_lay.insertWidget(self.chat_lay.count() - 1, lbl)
        self._scroll_bottom()

    def show_already_solved(self):
        """Shown when the user re-solves a challenge they already completed."""
        lbl = QLabel(
            "🔄  Déjà résolu — bonne pratique !  (pas de points supplémentaires)",
            objectName="already_solved_banner"
        )
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        self.chat_lay.insertWidget(self.chat_lay.count() - 1, lbl)
        self._scroll_bottom()

    def add_verification_result(self, result: dict):
        obj = "verification_bubble"
        
        status = ""
        details = ""
        
        if not result.get("compiled", True):
            status = "<span style='color: #FF5555; font-weight: bold;'>ERREUR DE COMPILATION</span>"
            details = f"<br><span style='color: #FF9999;'><b>Détails :</b></span><br><pre style='white-space: pre-wrap; font-size: 11px; color: #FF9999;'>{result.get('compilation_error', '')}</pre>"
        elif result.get("runtime_error"):
            status = "<span style='color: #FF5555; font-weight: bold;'>ERREUR D'EXÉCUTION</span>"
            details = f"<br><span style='color: #FF9999;'><b>Détails :</b></span><br><pre style='white-space: pre-wrap; font-size: 11px; color: #FF9999;'>{result.get('runtime_error', '')}</pre>"
        else:
            test_results = result.get("test_results", [])
            all_passed = result.get("success", False)
            if all_passed:
                status = "<span style='color: #55FF55; font-weight: bold;'>SUCCÈS</span>"
            else:
                status = "<span style='color: #FF9955; font-weight: bold;'>ÉCHEC</span>"
            
            lines = []
            for t in test_results:
                tag = "<span style='color: #55FF55; font-weight: bold;'>[ OK ]</span>" if t["passed"] else "<span style='color: #FF5555; font-weight: bold;'>[ ERR ]</span>"
                line = f"{tag} <span style='font-weight: bold;'>{t['name']}</span>"
                if not t["passed"] and t.get("details"):
                    line += f"<br>      <span style='color: #FFAAAA; font-size: 11px;'>⤷ {t['details']}</span>"
                lines.append(line)
            
            # Si tout est réussi, on affiche le fameux message rétro "Hello Dojo : )" en grand !
            if all_passed:
                lines.append("<br><div style='text-align: center; color: #55FF55; font-size: 18px; font-weight: bold; font-family: \"Consolas\", monospace; margin: 10px 0;'><br>Hello Dojo : )<br></div>")
            
            details = "<br>" + "<br>".join(lines)
            
        html = f"""
        <div style="font-family: 'Consolas', monospace; font-size: 12px; line-height: 1.4;">
            <span style="color: #8888FF; font-weight: bold;">💻 TERMINAL VERIFICATEUR v1.0</span><br>
            <span style="color: #888888;">------------------------------------------</span><br>
            <b>Environnement :</b> JDK 25 (OpenJDK)<br>
            <b>Résultat :</b> {status}<br>
            <span style="color: #888888;">------------------------------------------</span>
            {details}
        </div>
        """
        
        lbl = QLabel(html, objectName=obj)
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_lay.insertWidget(self.chat_lay.count() - 1, lbl)
        self._scroll_bottom()

    def show_error(self, error: str):
        """Display connection/API error with actionable guidance."""
        # Detect 401 / invalid key errors
        is_auth_error = "401" in error or "invalid_api_key" in error or "Invalid API Key" in error

        if is_auth_error:
            html = (
                "<div style='font-family: Segoe UI, sans-serif;'>"
                "<span style='font-size:15px;'>🔑</span> "
                "<b style='color:#E07A5F;'>Clé API invalide</b><br><br>"
                "Ta clé Groq ou Gemini est expirée, incorrecte ou absente.<br><br>"
                "<b>Comment corriger :</b><br>"
                "&nbsp;1. Clique sur <b>⚙️ Paramètres</b> dans la barre du haut<br>"
                "&nbsp;2. Colle une nouvelle clé API valide<br>"
                "&nbsp;3. Clique <b>Enregistrer</b> et soumets à nouveau<br><br>"
                "<span style='color:#9E9B82; font-size:11px;'>"
                "🟣 Groq gratuit → console.groq.com<br>"
                "🔵 Gemini gratuit → aistudio.google.com"
                "</span></div>"
            )
            lbl = QLabel(html, objectName="error_banner")
            lbl.setWordWrap(True)
            lbl.setTextFormat(Qt.RichText)
            self.chat_lay.insertWidget(self.chat_lay.count() - 1, lbl)
            self._scroll_bottom()
        else:
            self._add("sensei", f"⚠️ Erreur de connexion :\n{error}")
