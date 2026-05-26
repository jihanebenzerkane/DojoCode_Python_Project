"""
mysql_repo.py — Couche d'accès aux données MySQL.
TOUTES les requêtes sont paramétrées avec %s (protection injection SQL).
"""
import mysql.connector
from mysql.connector import Error
from typing import Optional, List
from dotenv import load_dotenv
import os

from models.entities import User, Challenge, ChallengeSession, AIMessage

load_dotenv()


class MySQLRepository:
    """
    Couche d'accès aux données MySQL.
    TOUTES les requêtes sont paramétrées (protection injection SQL).
    """

    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self):
        """Établit la connexion MySQL depuis les variables .env"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'codedojo'),
                charset='utf8mb4',
                autocommit=False
            )
            print("[DB] Connexion MySQL établie.")
        except Error as e:
            print(f"[DB] ERREUR connexion : {e}")
            self.connection = None

    def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        return self.connection is not None and self.connection.is_connected()

    def _ensure_connection(self):
        """Reconnecte si nécessaire (MySQL idle timeout)."""
        if not self.is_connected():
            self._connect()

    # ── USERS ────────────────────────────────────────────────────────────────

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son username. Requête paramétrée."""
        self._ensure_connection()
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()
            cursor.close()
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    points=row['points'],
                    created_at=row['created_at']
                )
            return None
        except Error as e:
            print(f"[DB] Erreur get_user : {e}")
            return None

    def create_user(self, username: str, password_hash: str) -> bool:
        """Crée un nouvel utilisateur. Retourne True si succès."""
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[DB] Erreur create_user : {e}")
            self.connection.rollback()
            return False

    def update_points(self, user_id: int, points_to_add: int) -> bool:
        """Ajoute des points à un utilisateur."""
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE users SET points = points + %s WHERE id = %s",
                (points_to_add, user_id)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[DB] Erreur update_points : {e}")
            self.connection.rollback()
            return False

    def refresh_user(self, user_id: int) -> Optional[User]:
        """Recharge un utilisateur depuis la DB (points frais)."""
        self._ensure_connection()
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    points=row['points'],
                    created_at=row['created_at']
                )
            return None
        except Error as e:
            print(f"[DB] Erreur refresh_user : {e}")
            return None

    # ── CHALLENGES ───────────────────────────────────────────────────────────

    def get_all_challenges(self) -> List[Challenge]:
        """Récupère tous les challenges depuis la DB."""
        self._ensure_connection()
        if not self.is_connected():
            return []
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM challenges ORDER BY points ASC, id ASC"
            )
            rows = cursor.fetchall()
            cursor.close()
            return [
                Challenge(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    expected_concepts=row['expected_concepts'] or '',
                    points=row['points'],
                    difficulty=row['difficulty'],
                )
                for row in rows
            ]
        except Error as e:
            print(f"[DB] Erreur get_all_challenges : {e}")
            return []

    # ── SESSIONS ─────────────────────────────────────────────────────────────

    def create_session(self, user_id: int, challenge_id: int) -> Optional[int]:
        """Crée une session de challenge. Retourne l'ID de la session."""
        self._ensure_connection()
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO challenge_sessions (user_id, challenge_id) VALUES (%s, %s)",
                (user_id, challenge_id)
            )
            self.connection.commit()
            session_id = cursor.lastrowid
            cursor.close()
            return session_id
        except Error as e:
            print(f"[DB] Erreur create_session : {e}")
            self.connection.rollback()
            return None

    def mark_session_solved(self, session_id: int, points_earned: int) -> bool:
        """Marque une session comme résolue avec solved_at = NOW()."""
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE challenge_sessions SET solved_at = NOW(), points_earned = %s WHERE id = %s",
                (points_earned, session_id)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[DB] Erreur mark_session_solved : {e}")
            self.connection.rollback()
            return False

    # ── AI MESSAGES ──────────────────────────────────────────────────────────

    def save_message(self, session_id: int, role: str, content: str) -> bool:
        """Sauvegarde un message IA dans l'historique."""
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO ai_messages (session_id, role, content) VALUES (%s, %s, %s)",
                (session_id, role, content)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[DB] Erreur save_message : {e}")
            self.connection.rollback()
            return False

    # ── SOLVED-ONCE TRACKING ─────────────────────────────────────────────────

    def has_solved(self, user_id: int, challenge_id: int) -> bool:
        """Returns True if this user has already solved this challenge before."""
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT 1 FROM user_solved_challenges "
                "WHERE user_id = %s AND challenge_id = %s LIMIT 1",
                (user_id, challenge_id)
            )
            found = cursor.fetchone() is not None
            cursor.close()
            return found
        except Error as e:
            print(f"[DB] Erreur has_solved : {e}")
            return False

    def mark_challenge_solved(self, user_id: int, challenge_id: int) -> bool:
        """
        Permanently records that this user solved this challenge.
        Uses INSERT IGNORE so re-solves are safely no-ops.
        Returns True if it was a NEW solve (first time), False if already solved.
        """
        self._ensure_connection()
        if not self.is_connected():
            return False
        if self.has_solved(user_id, challenge_id):
            return False  # already solved — caller must NOT award points again
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT IGNORE INTO user_solved_challenges (user_id, challenge_id) "
                "VALUES (%s, %s)",
                (user_id, challenge_id)
            )
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        except Error as e:
            print(f"[DB] Erreur mark_challenge_solved : {e}")
            self.connection.rollback()
            return False

    def get_solved_challenge_ids(self, user_id: int) -> set:
        """Returns the set of challenge IDs already solved by this user."""
        self._ensure_connection()
        if not self.is_connected():
            return set()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT challenge_id FROM user_solved_challenges WHERE user_id = %s",
                (user_id,)
            )
            ids = {row[0] for row in cursor.fetchall()}
            cursor.close()
            return ids
        except Error as e:
            print(f"[DB] Erreur get_solved_challenge_ids : {e}")
            return set()

    def count_solved(self, user_id: int) -> int:
        """Returns the total number of challenges this user has solved."""
        self._ensure_connection()
        if not self.is_connected():
            return 0
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM user_solved_challenges WHERE user_id = %s",
                (user_id,)
            )
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            print(f"[DB] Erreur count_solved : {e}")
            return 0

    def count_solved_by_points(self, user_id: int, points: int) -> int:
        """Returns how many challenges of a given point-value the user has solved."""
        self._ensure_connection()
        if not self.is_connected():
            return 0
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM user_solved_challenges usc "
                "JOIN challenges c ON c.id = usc.challenge_id "
                "WHERE usc.user_id = %s AND c.points = %s",
                (user_id, points)
            )
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            print(f"[DB] Erreur count_solved_by_points : {e}")
            return 0

    def count_challenges_by_points(self, points: int) -> int:
        """Returns total number of challenges with the given point value."""
        self._ensure_connection()
        if not self.is_connected():
            return 0
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM challenges WHERE points = %s", (points,)
            )
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            print(f"[DB] Erreur count_challenges_by_points : {e}")
            return 0

    # ── ACHIEVEMENTS ──────────────────────────────────────────────────────────

    def get_all_achievements(self) -> List[dict]:
        """Returns the full achievement catalogue."""
        self._ensure_connection()
        if not self.is_connected():
            return []
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM achievements ORDER BY id ASC")
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            print(f"[DB] Erreur get_all_achievements : {e}")
            return []

    def get_user_achievement_ids(self, user_id: int) -> set:
        """Returns the set of achievement IDs already earned by this user."""
        self._ensure_connection()
        if not self.is_connected():
            return set()
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT achievement_id FROM user_achievements WHERE user_id = %s",
                (user_id,)
            )
            ids = {row[0] for row in cursor.fetchall()}
            cursor.close()
            return ids
        except Error as e:
            print(f"[DB] Erreur get_user_achievement_ids : {e}")
            return set()

    def award_achievement(self, user_id: int, achievement_id: int) -> bool:
        """
        Awards an achievement to a user.
        INSERT IGNORE means it's safe to call multiple times — only fires once.
        Returns True if it was newly awarded, False if already had it.
        """
        self._ensure_connection()
        if not self.is_connected():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT IGNORE INTO user_achievements (user_id, achievement_id) VALUES (%s, %s)",
                (user_id, achievement_id)
            )
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        except Error as e:
            print(f"[DB] Erreur award_achievement : {e}")
            self.connection.rollback()
            return False

    def get_achievement_by_code(self, code: str) -> Optional[dict]:
        """Fetches a single achievement row by its code."""
        self._ensure_connection()
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM achievements WHERE code = %s LIMIT 1", (code,)
            )
            row = cursor.fetchone()
            cursor.close()
            return row
        except Error as e:
            print(f"[DB] Erreur get_achievement_by_code : {e}")
            return None

    def get_session_elapsed_seconds(self, session_id: int) -> Optional[int]:
        """Returns seconds elapsed since session started (for speed achievements)."""
        self._ensure_connection()
        if not self.is_connected():
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT TIMESTAMPDIFF(SECOND, started_at, NOW()) "
                "FROM challenge_sessions WHERE id = %s",
                (session_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else None
        except Error as e:
            print(f"[DB] Erreur get_session_elapsed_seconds : {e}")
            return None

    def close(self):
        """Ferme la connexion proprement."""
        if self.is_connected():
            self.connection.close()
            print("[DB] Connexion fermée.")