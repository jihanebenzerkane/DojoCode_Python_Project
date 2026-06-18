"""
base_repo.py — Abstract base repository defining the database interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Set, Any
from models.entities import User, Challenge, ChallengeSession, AIMessage


class BaseRepository(ABC):
    """Abstract base class for all database repositories (MySQL, SQLite)."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Checks if connection is active."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes connection/pool resources."""
        pass

    @abstractmethod
    def health_report(self) -> Dict[str, Any]:
        """Returns DB metadata and metrics (table counts, connection details)."""
        pass

    # ── USERS ────────────────────────────────────────────────────────────────

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Gets user by username."""
        pass

    @abstractmethod
    def create_user(self, username: str, password_hash: str) -> bool:
        """Creates a new user."""
        pass

    @abstractmethod
    def update_points(self, user_id: int, points_to_add: int) -> bool:
        """Modifies user's accumulated score."""
        pass

    @abstractmethod
    def refresh_user(self, user_id: int) -> Optional[User]:
        """Refreshes and returns updated user data."""
        pass

    @abstractmethod
    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns leaderboard statistics."""
        pass

    @abstractmethod
    def delete_user_by_username(self, username: str) -> bool:
        """Deletes user by username (mainly for tests)."""
        pass

    # ── CHALLENGES ───────────────────────────────────────────────────────────

    @abstractmethod
    def get_all_challenges(self) -> List[Challenge]:
        """Returns all challenges."""
        pass

    # ── SESSIONS ─────────────────────────────────────────────────────────────

    @abstractmethod
    def create_session(self, user_id: int, challenge_id: int) -> Optional[int]:
        """Initializes a coding session."""
        pass

    @abstractmethod
    def mark_session_solved(self, session_id: int, points_earned: int) -> bool:
        """Marks the session as solved and timestamps it."""
        pass

    # ── AI MESSAGES ──────────────────────────────────────────────────────────

    @abstractmethod
    def save_message(self, session_id: int, role: str, content: str) -> bool:
        """Appends a new user/assistant message to the AI conversation log."""
        pass

    # ── SOLVED-ONCE TRACKING ─────────────────────────────────────────────────

    @abstractmethod
    def has_solved(self, user_id: int, challenge_id: int) -> bool:
        """Checks if user has solved the challenge before."""
        pass

    @abstractmethod
    def mark_challenge_solved(self, user_id: int, challenge_id: int) -> bool:
        """Locks the challenge as solved. Returns True if first solve, False if repeat."""
        pass

    @abstractmethod
    def get_solved_challenge_ids(self, user_id: int) -> Set[int]:
        """Returns a set of IDs for challenges completed by the user."""
        pass

    @abstractmethod
    def count_solved(self, user_id: int) -> int:
        """Returns total solved count for user."""
        pass

    @abstractmethod
    def count_solved_by_points(self, user_id: int, points: int) -> int:
        """Returns how many challenges of a specific point-value were solved."""
        pass

    @abstractmethod
    def count_challenges_by_points(self, points: int) -> int:
        """Returns the total number of challenges of a specific point-value."""
        pass
