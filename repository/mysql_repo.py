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

    def close(self):
        """Ferme la connexion proprement."""
        if self.is_connected():
            self.connection.close()
            print("[DB] Connexion fermée.")