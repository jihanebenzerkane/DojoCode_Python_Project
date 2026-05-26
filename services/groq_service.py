import os
import json
import urllib.request
import urllib.error
from services.sensei_prompt import SenseiPrompt


class GroqService:
    """
    Service d'appel à l'IA gérant automatiquement deux fournisseurs :
    1. Gemini (Google, gratuit via clé API AI Studio)
    2. Groq (Llama 3, si clé gsk_ configurée)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        # Détection du fournisseur
        if self.api_key.startswith("AIzaSy"):
            self.provider = "gemini"
            print("[Dojo AI] Fournisseur détecté : Google Gemini (Gratuit)")
        else:
            self.provider = "groq"
            print("[Dojo AI] Fournisseur détecté : Groq (Llama 3)")
            # Initialisation paresseuse du client Groq pour éviter des erreurs d'import si non utilisé
            try:
                from groq import Groq
                import httpx
                self.client = Groq(
                    api_key=self.api_key,
                    http_client=httpx.Client()
                )
            except ImportError:
                self.client = None
                print("[Dojo AI] ⚠ Package 'groq' non installé. Requis uniquement pour le mode Groq.")
            except Exception as e:
                self.client = None
                print(f"[Dojo AI] Non disponible : {e}")

    def ask_sensei(
        self,
        user_message: str,
        challenge,
        submitted_code: str = "",
        conversation_history: list = None,
        difficulty: str = "beginner"
    ) -> str:
        """
        Envoie les prompts au Sensei et retourne sa réponse.
        Gère Groq ou Gemini de manière transparente.
        """
        if conversation_history is None:
            conversation_history = []

        # Construction des invites Dojo (SenseiPrompt)
        prompt = SenseiPrompt(challenge, difficulty)
        system_prompt = prompt.build_system()
        user_code_msg = prompt.build_user(submitted_code)
        full_user_message = f"{user_code_msg}\n\nQuestion de l'élève: {user_message}"

        if self.provider == "gemini":
            return self._call_gemini(system_prompt, conversation_history, full_user_message)
        else:
            return self._call_groq(system_prompt, conversation_history, full_user_message)

    def _call_gemini(self, system_prompt: str, history: list, user_msg: str) -> str:
        """Appel direct à l'API REST de Gemini (sans dépendance externe)."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

        # Construction de l'historique au format Gemini (roles: 'user' ou 'model')
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # Ajout du message actuel
        contents.append({
            "role": "user",
            "parts": [{"text": user_msg}]
        })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                # Extraction du texte de la réponse
                candidates = res_body.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return "Désolé, je n'ai pas pu générer de réponse."
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            print(f"[Gemini Error] HTTP {e.code}: {err_content}")
            raise Exception(f"Gemini API Error (HTTP {e.code}) : {e.reason}")
        except Exception as e:
            print(f"[Gemini Error] Connection failed: {e}")
            raise Exception(f"Impossible de joindre l'API Gemini : {e}")

    def _call_groq(self, system_prompt: str, history: list, user_msg: str) -> str:
        """Appel via la bibliothèque officielle Groq."""
        if not self.client:
            raise Exception("Le client Groq n'est pas installé ou initialisé.")

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_msg})

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message.content