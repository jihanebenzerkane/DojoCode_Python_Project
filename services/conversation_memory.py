from collections import deque
from dataclasses import dataclass, field
from typing import List
import json

@dataclass
class ConversationTurn:
    role: str  # "user" ou "assistant"
    content: str
    code_snapshot: str = ""  # Code au moment de ce message
    timestamp: float = field(default_factory=lambda: __import__('time').time())

class ConversationMemory:
    """
    Mémoire contextuelle pour le Sensei IA.
    Maintient les 10 derniers échanges pour garder le contexte pédagogique.
    """
    
    def __init__(self, max_turns: int = 10):
        self.turns: deque = deque(maxlen=max_turns)
        self.error_patterns: List[str] = []  # Erreurs récurrentes de l'élève
    
    def add_turn(self, role: str, content: str, code: str = ""):
        self.turns.append(ConversationTurn(role, content, code))
        
        # Détecte les patterns d'erreur
        if "NullPointerException" in content:
            self.error_patterns.append("null_handling")
        if "ArrayIndexOutOfBounds" in content:
            self.error_patterns.append("array_bounds")
    
    def get_context_summary(self) -> str:
        """Génère un résumé pour le prompt système."""
        if not self.turns:
            return ""
        
        recent = list(self.turns)[-3:]
        summary = "Contexte récent de la conversation:\n"
        for turn in recent:
            summary += f"- {turn.role}: {turn.content[:100]}...\n"
        
        if self.error_patterns:
            summary += f"\nPatterns d'erreur détectés: {', '.join(set(self.error_patterns))}\n"
            summary += "Adapte tes explications pour cibler ces faiblesses."
        
        return summary
    
    def save_to_session(self, session_id: int, repo):
        """Sauvegarde en base pour persistance."""
        data = [{
            "role": t.role,
            "content": t.content,
            "code": t.code_snapshot,
            "ts": t.timestamp
        } for t in self.turns]
        # repo.save_conversation(session_id, json.dumps(data))
    
    @classmethod
    def load_from_session(cls, session_id: int, repo) -> "ConversationMemory":
        """Charge depuis la base."""
        memory = cls()
        # data = repo.load_conversation(session_id)
        # ... reconstruire les turns
        return memory