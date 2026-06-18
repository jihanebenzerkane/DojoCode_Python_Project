import json
import os
import urllib.error
import urllib.request

from services.sensei_prompt import SenseiPrompt


MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS = 6000
REQUEST_TIMEOUT_SECONDS = 20


class GroqService:
    """
    AI gateway for CodeDojo.

    It supports two providers behind the same interface:
    - Gemini when the key starts with AIzaSy
    - Groq for the other configured keys
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        if not self.api_key:
            raise ValueError("Aucune cle API IA n'est configuree.")

        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.client = None

        if self.api_key.startswith("AIzaSy"):
            self.provider = "gemini"
            print("[Dojo AI] Fournisseur detecte : Google Gemini")
        else:
            self.provider = "groq"
            print("[Dojo AI] Fournisseur detecte : Groq")
            self._init_groq_client()

    def _init_groq_client(self):
        try:
            from groq import Groq
            import httpx

            self.client = Groq(
                api_key=self.api_key,
                http_client=httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS),
            )
        except ImportError:
            self.client = None
            print("[Dojo AI] Package 'groq' non installe. Requis pour le mode Groq.")
        except Exception as e:
            self.client = None
            print(f"[Dojo AI] Non disponible : {e}")

    def ask_sensei(
        self,
        user_message: str,
        challenge,
        submitted_code: str = "",
        conversation_history: list | None = None,
        difficulty: str = "beginner",
    ) -> str:
        """
        Builds the pedagogical prompt and sends it to the selected provider.
        The history is compacted to keep latency and token cost predictable.
        """
        history = self._compact_history(conversation_history or [])
        prompt = SenseiPrompt(challenge, difficulty)
        system_prompt = prompt.build_system()
        user_code_msg = prompt.build_user(submitted_code)
        full_user_message = f"{user_code_msg}\n\nQuestion de l'eleve: {user_message}"

        if self.provider == "gemini":
            return self._call_gemini(system_prompt, history, full_user_message)
        return self._call_groq(system_prompt, history, full_user_message)

    def provider_label(self) -> str:
        """Human-readable AI status for PySide labels."""
        if self.provider == "gemini":
            return f"Google Gemini - {self.gemini_model} - Methode socratique"
        return f"Groq - {self.model_name} - Methode socratique"

    def _compact_history(self, history: list) -> list:
        clean = []
        budget = MAX_HISTORY_CHARS
        for msg in reversed(history[-MAX_HISTORY_MESSAGES:]):
            role = msg.get("role")
            content = (msg.get("content") or "").strip()
            if role not in {"user", "assistant"} or not content:
                continue

            content = content[:budget]
            if not content:
                break

            clean.append({"role": role, "content": content})
            budget -= len(content)
            if budget <= 0:
                break
        return list(reversed(clean))

    def _call_gemini(self, system_prompt: str, history: list, user_msg: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={self.api_key}"
        )

        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_msg}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                res_body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8", errors="replace")
            print(f"[Gemini Error] HTTP {e.code}: {err_content}")
            raise RuntimeError(f"Gemini API Error (HTTP {e.code}) : {e.reason}") from e
        except Exception as e:
            print(f"[Gemini Error] Connection failed: {e}")
            raise RuntimeError(f"Impossible de joindre l'API Gemini : {e}") from e

        candidates = res_body.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return "Desole, je n'ai pas pu generer de reponse."

    def _call_groq(self, system_prompt: str, history: list, user_msg: str) -> str:
        if not self.client:
            raise RuntimeError("Le client Groq n'est pas installe ou initialise.")

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_msg})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=400,
                temperature=0.7,
            )
        except Exception as e:
            raise RuntimeError(f"Erreur Groq API : {e}") from e

        return response.choices[0].message.content
