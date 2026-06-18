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
    streak_days: int = 0
    last_login: Optional[datetime] = None
    total_time_spent: int = 0
    attempt_count: int = 0
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
    """Challenge proposé à l'élève (dynamique et multi-langage)."""
    title: str
    description: str
    expected_concepts: str = ''
    points: int = 10
    difficulty: str = 'beginner'
    topic: str = ''
    language: str = 'java'
    test_spec: str = '{}'  # JSON string
    solution_template: str = ''
    is_active: bool = True
    success_rate: float = 0.0
    average_time: int = 0
    created_by: str = 'ai'
    id: Optional[int] = None
    created_at: Optional[datetime] = None

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
    elapsed_seconds: int = 0
    id: Optional[int] = None
    started_at: Optional[datetime] = None
    solved_at: Optional[datetime] = None


@dataclass
class AIMessage:
    """Message dans la conversation IA."""
    session_id: int
    role: str        # 'user' ou 'assistant'
    content: str
    prompt_version: str = '1.0'
    id: Optional[int] = None
    created_at: Optional[datetime] = None