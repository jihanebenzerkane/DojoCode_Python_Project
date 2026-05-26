"""
entities.py — Dataclasses métier de CodeDojo.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import bcrypt


@dataclass
class User:
    """Utilisateur de la plateforme."""
    username: str
    password_hash: str
    points: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def check_password(self, plain_password: str) -> bool:
        """Vérifie le mot de passe avec bcrypt."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def get_level_name(self) -> str:
        """
        Retourne le nom du niveau selon les points :
          0-99 pts    → Étudiant
          100-299 pts → Apprenti
          300-599 pts → Pratiquant
          600+ pts    → Maître
        """
        if self.points < 100:
            return "Étudiant"
        elif self.points < 300:
            return "Apprenti"
        elif self.points < 600:
            return "Pratiquant"
        else:
            return "Maître"


@dataclass
class Challenge:
    """Challenge Java proposé à l'élève."""
    title: str
    description: str
    expected_concepts: str = ''
    points: int = 10
    difficulty: str = 'beginner'
    id: Optional[int] = None

    def get_prompt_context(self) -> str:
        """Retourne le contexte du challenge pour le prompt IA."""
        return (
            f"Challenge: {self.title}\n"
            f"Description: {self.description}\n"
            f"Expected concepts: {self.expected_concepts}\n"
            f"Points: {self.points}"
        )


@dataclass
class ChallengeSession:
    """Session d'un utilisateur sur un challenge."""
    user_id: int
    challenge_id: int
    points_earned: int = 0
    id: Optional[int] = None
    started_at: Optional[datetime] = None
    solved_at: Optional[datetime] = None


@dataclass
class AIMessage:
    """Message dans la conversation IA."""
    session_id: int
    role: str        # 'user' ou 'assistant'
    content: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None