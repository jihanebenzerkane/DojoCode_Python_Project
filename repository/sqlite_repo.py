"""
sqlite_repo.py — Native SQLite database access layer.
"""
from __future__ import annotations

import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Set, Any
from datetime import datetime, timezone

from models.entities import User, Challenge, ChallengeSession, AIMessage
from repository.base_repo import BaseRepository

logger = logging.getLogger("codedojo.sqlite")


class SQLiteRepository(BaseRepository):
    """SQLite implementation of the repository with clean thread-safe cursor operations."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base, "db", "codedojo.db")
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Note: Do not keep a shared connection to ensure thread safety across QThreads.

    @contextmanager
    def _cursor(self):
        """Context manager that opens and closes database connections on demand."""
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"SQLite error: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def is_connected(self) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False

    def close(self) -> None:
        pass  # Connections are opened/closed dynamically per query.

    def health_report(self) -> Dict[str, Any]:
        connected = self.is_connected()
        report = {
            "backend": "SQLite local",
            "connected": connected,
            "database": self.db_path,
            "users": 0,
            "challenges": 0,
            "sessions": 0,
            "messages": 0,
        }
        if not connected:
            return report

        tables = {
            "users": "users",
            "challenges": "challenges",
            "sessions": "challenge_sessions",
            "messages": "ai_messages",
        }
        try:
            with self._cursor() as cursor:
                for key, table in tables.items():
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row = cursor.fetchone()
                    report[key] = int(row[0]) if row else 0
        except Exception as e:
            logger.error(f"Error getting SQLite health report: {e}")
        return report

    # ── USERS ────────────────────────────────────────────────────────────────

    def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash, points, streak_days, last_login, total_time_spent, attempt_count, created_at FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    # Convert created_at string to datetime if possible
                    created_at = None
                    if row['created_at']:
                        try:
                            created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                        except Exception:
                            pass
                    return User(
                        id=row['id'],
                        username=row['username'],
                        password_hash=row['password_hash'],
                        points=row['points'],
                        streak_days=row['streak_days'],
                        last_login=row['last_login'],
                        total_time_spent=row['total_time_spent'],
                        attempt_count=row['attempt_count'],
                        created_at=created_at
                    )
                return None
        except Exception as e:
            logger.error(f"Error in get_user_by_username: {e}")
            return None

    def create_user(self, username: str, password_hash: str) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in create_user: {e}")
            return False

    def update_points(self, user_id: int, points_to_add: int) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET points = MAX(0, points + ?) WHERE id = ?",
                    (points_to_add, user_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in update_points: {e}")
            return False

    def refresh_user(self, user_id: int) -> Optional[User]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash, points, streak_days, last_login, total_time_spent, attempt_count, created_at FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        username=row['username'],
                        password_hash=row['password_hash'],
                        points=row['points'],
                        streak_days=row['streak_days'],
                        last_login=row['last_login'],
                        total_time_spent=row['total_time_spent'],
                        attempt_count=row['attempt_count'],
                        created_at=row['created_at']
                    )
                return None
        except Exception as e:
            logger.error(f"Error in refresh_user: {e}")
            return None

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT username, points FROM users ORDER BY points DESC, username ASC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error in get_top_users: {e}")
            return []

    def delete_user_by_username(self, username: str) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in delete_user_by_username: {e}")
            return False

    # ── CHALLENGES ───────────────────────────────────────────────────────────

    def get_all_challenges(self) -> List[Challenge]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT id, title, description, expected_concepts, points, difficulty, topic, language, test_spec, solution_template, is_active FROM challenges WHERE is_active = 1 ORDER BY points ASC, id ASC"
                )
                return [
                    Challenge(
                        id=row['id'],
                        title=row['title'],
                        description=row['description'],
                        expected_concepts=row['expected_concepts'] or '',
                        points=row['points'],
                        difficulty=row['difficulty'],
                        topic=row['topic'] or '',
                        language=row['language'] or 'java',
                        test_spec=row['test_spec'] or '{}',
                        solution_template=row['solution_template'] or '',
                        is_active=bool(row['is_active'])
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Error in get_all_challenges: {e}")
            return []

    # ── SESSIONS ─────────────────────────────────────────────────────────────

    def create_session(self, user_id: int, challenge_id: int) -> Optional[int]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "INSERT INTO challenge_sessions (user_id, challenge_id) VALUES (?, ?)",
                    (user_id, challenge_id)
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error in create_session: {e}")
            return None

    def mark_session_solved(self, session_id: int, points_earned: int) -> bool:
        try:
            # First, fetch started_at to compute and store elapsed seconds
            elapsed = 0
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT started_at FROM challenge_sessions WHERE id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                if row and row['started_at']:
                    try:
                        start_str = row['started_at']
                        if '.' in start_str:
                            start_str = start_str.split('.')[0]
                        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                        elapsed = int((datetime.now(timezone.utc) - start_dt).total_seconds())
                    except Exception:
                        pass

                # Mark solved
                cursor.execute(
                    "UPDATE challenge_sessions SET solved_at = CURRENT_TIMESTAMP, points_earned = ?, elapsed_seconds = ? WHERE id = ?",
                    (points_earned, elapsed, session_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in mark_session_solved: {e}")
            return False

    # ── AI MESSAGES ──────────────────────────────────────────────────────────

    def save_message(self, session_id: int, role: str, content: str) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ai_messages (session_id, role, content) VALUES (?, ?, ?)",
                    (session_id, role, content)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in save_message: {e}")
            return False

    # ── SOLVED-ONCE TRACKING ─────────────────────────────────────────────────

    def has_solved(self, user_id: int, challenge_id: int) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM user_solved_challenges WHERE user_id = ? AND challenge_id = ? LIMIT 1",
                    (user_id, challenge_id)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error in has_solved: {e}")
            return False

    def mark_challenge_solved(self, user_id: int, challenge_id: int) -> bool:
        try:
            if self.has_solved(user_id, challenge_id):
                return False
            with self._cursor() as cursor:
                # Count user attempts in sessions for this challenge
                cursor.execute(
                    "SELECT COUNT(*) FROM challenge_sessions WHERE user_id = ? AND challenge_id = ?",
                    (user_id, challenge_id)
                )
                attempts = cursor.fetchone()[0] or 1
                cursor.execute(
                    "INSERT OR IGNORE INTO user_solved_challenges (user_id, challenge_id, first_attempts) VALUES (?, ?, ?)",
                    (user_id, challenge_id, attempts)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in mark_challenge_solved: {e}")
            return False

    def get_solved_challenge_ids(self, user_id: int) -> Set[int]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT challenge_id FROM user_solved_challenges WHERE user_id = ?",
                    (user_id,)
                )
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Error in get_solved_challenge_ids: {e}")
            return set()

    def count_solved(self, user_id: int) -> int:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM user_solved_challenges WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error in count_solved: {e}")
            return 0

    def count_solved_by_points(self, user_id: int, points: int) -> int:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM user_solved_challenges usc JOIN challenges c ON c.id = usc.challenge_id WHERE usc.user_id = ? AND c.points = ?",
                    (user_id, points)
                )
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error in count_solved_by_points: {e}")
            return 0

    def count_challenges_by_points(self, points: int) -> int:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM challenges WHERE points = ? AND is_active = 1",
                    (points,)
                )
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error in count_challenges_by_points: {e}")
            return 0

    # ── ACHIEVEMENTS ──────────────────────────────────────────────────────────

    def get_all_achievements(self) -> List[Dict[str, Any]]:
        try:
            with self._cursor() as cursor:
                cursor.execute("SELECT * FROM achievements ORDER BY id ASC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error in get_all_achievements: {e}")
            return []

    def get_user_achievement_ids(self, user_id: int) -> Set[int]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT achievement_id FROM user_achievements WHERE user_id = ?",
                    (user_id,)
                )
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Error in get_user_achievement_ids: {e}")
            return set()

    def award_achievement(self, user_id: int, achievement_id: int) -> bool:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                    (user_id, achievement_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error in award_achievement: {e}")
            return False

    def get_achievement_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM achievements WHERE code = ? LIMIT 1",
                    (code,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error in get_achievement_by_code: {e}")
            return None

    def get_session_elapsed_seconds(self, session_id: int) -> Optional[int]:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT started_at FROM challenge_sessions WHERE id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                if not row or not row['started_at']:
                    return None
                start_str = row['started_at']
                if '.' in start_str:
                    start_str = start_str.split('.')[0]
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                now_dt = datetime.now(timezone.utc)
                return int((now_dt - start_dt).total_seconds())
        except Exception as e:
            logger.error(f"Error in get_session_elapsed_seconds: {e}")
            return None

    def get_total_time_spent(self, user_id: int) -> int:
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    "SELECT started_at, solved_at FROM challenge_sessions WHERE user_id = ? AND solved_at IS NOT NULL",
                    (user_id,)
                )
                rows = cursor.fetchall()
            total_seconds = 0
            for r in rows:
                try:
                    start_str = r['started_at'].split('.')[0]
                    solve_str = r['solved_at'].split('.')[0]
                    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    solve_dt = datetime.strptime(solve_str, "%Y-%m-%d %H:%M:%S")
                    diff = (solve_dt - start_dt).total_seconds()
                    if diff > 0:
                        total_seconds += int(diff)
                except Exception:
                    continue
            return total_seconds
        except Exception as e:
            logger.error(f"Error in get_total_time_spent: {e}")
            return 0
