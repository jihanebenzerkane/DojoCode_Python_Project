"""
draft_service.py — Service de sauvegarde automatique des brouillons de code de l'élève.
"""
import os
import json

class DraftService:
    def __init__(self):
        self.filepath = os.path.expanduser("~/.codedojo_drafts.json")

    def _load_all_drafts(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[DraftService] Erreur lors de la lecture des brouillons : {e}")
            return {}

    def _save_all_drafts(self, drafts: dict):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(drafts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[DraftService] Erreur lors de l'écriture des brouillons : {e}")

    def save_draft(self, user_id: int, challenge_id: int, code: str):
        """Enregistre le brouillon pour un utilisateur et un challenge donnés."""
        if not user_id or not challenge_id:
            return
        drafts = self._load_all_drafts()
        key = f"{user_id}_{challenge_id}"
        drafts[key] = code
        self._save_all_drafts(drafts)

    def load_draft(self, user_id: int, challenge_id: int) -> str:
        """Charge le brouillon d'un utilisateur pour un challenge. Retourne None si inexistant."""
        if not user_id or not challenge_id:
            return None
        drafts = self._load_all_drafts()
        key = f"{user_id}_{challenge_id}"
        return drafts.get(key, None)
