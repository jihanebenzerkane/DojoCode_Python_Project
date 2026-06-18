"""
mysql_repo.py — Couche d'accès aux données MySQL.
TOUTES les requêtes sont paramétrées avec %s (protection injection SQL).
"""
import mysql.connector
from mysql.connector import Error
import sqlite3
from typing import Optional, List
from dotenv import load_dotenv
import os

from models.entities import User, Challenge, ChallengeSession, AIMessage

load_dotenv()


class SQLiteCursorWrapper:
    def __init__(self, cursor, dictionary=False):
        self.cursor = cursor
        self.dictionary = dictionary

    def execute(self, query, params=None):
        # Translate placeholders and syntax to SQLite
        query = query.replace('%s', '?')
        query = query.replace('INSERT IGNORE', 'INSERT OR IGNORE')
        query = query.replace('NOW()', 'CURRENT_TIMESTAMP')
        if "TIMESTAMPDIFF(SECOND, started_at, NOW())" in query:
            query = query.replace("TIMESTAMPDIFF(SECOND, started_at, NOW())", "(strftime('%s', 'now') - strftime('%s', started_at))")
        
        if params is not None:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        if self.dictionary:
            cols = [d[0] for d in self.cursor.description]
            return dict(zip(cols, row))
        return row

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return rows
        if self.dictionary:
            cols = [d[0] for d in self.cursor.description]
            return [dict(zip(cols, r)) for r in rows]
        return rows

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self.conn.cursor(), dictionary)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


class MySQLRepository:
    """
    Couche d'accès aux données MySQL avec basculement transparent vers SQLite.
    """

    def __init__(self):
        self.connection = None
        self.use_sqlite = False
        self.sqlite_path = None
        self._connect()

    def _connect(self):
        """Établit la connexion MySQL depuis les variables .env. Bascule sur SQLite si échec."""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'codedojo'),
                charset='utf8mb4',
                connection_timeout=5,
                autocommit=False
            )
            self.use_sqlite = False
            print("[DB] Connexion MySQL établie.")
        except Exception as e:
            print(f"[DB] ERREUR connexion MySQL : {e}")
            print("[DB] Basculement automatique sur la base SQLite locale...")
            self.use_sqlite = True
            self._connect_sqlite()

    def _connect_sqlite(self):
        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base, "db")
            os.makedirs(db_dir, exist_ok=True)
            self.sqlite_path = os.path.join(db_dir, "codedojo.db")
            self._init_sqlite_db()
            conn = sqlite3.connect(self.sqlite_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            self.connection = SQLiteConnectionWrapper(conn)
            print(f"[DB] Connexion SQLite établie : {self.sqlite_path}")
        except Exception as ex:
            print(f"[DB] ERREUR connexion SQLite : {ex}")
            self.connection = None

    def _init_sqlite_db(self):
        # Ensure db directory exists
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        cursor = conn.cursor()
        
        # Create tables using SQLite compatible syntax
        statements = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                expected_concepts TEXT,
                points INTEGER DEFAULT 10,
                difficulty TEXT DEFAULT 'beginner'
            )""",
            """CREATE TABLE IF NOT EXISTS challenge_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                solved_at TIMESTAMP NULL DEFAULT NULL,
                points_earned INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS ai_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES challenge_sessions(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS user_solved_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, challenge_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                category TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
            )"""
        ]
        
        for sql in statements:
            cursor.execute(sql)
        conn.commit()
        
        # Seed challenges if empty
        cursor.execute("SELECT COUNT(*) FROM challenges")
        count = cursor.fetchone()[0]
        if count == 0:
            challenges = [
                ("Hello Dojo",
                 "Ecris une methode sayHello() qui retourne la chaine 'Hello, Dojo!'. La methode doit etre publique et statique.",
                 "methode statique, return, String",
                 10, "beginner"),
                ("Pair ou Impair",
                 "Ecris une methode isEven(int n) qui retourne true si n est pair, false sinon. N'utilise pas de librairie externe.",
                 "modulo operator, boolean return, conditions",
                 10, "beginner"),
                ("Maximum de deux nombres",
                 "Ecris une methode max(int a, int b) qui retourne le plus grand des deux entiers sans utiliser Math.max().",
                 "if-else, comparaison, return",
                 10, "beginner"),
                ("Somme d'un tableau",
                 "Ecris une methode sumArray(int[] arr) qui retourne la somme de tous les elements d'un tableau d'entiers.",
                 "boucle for, tableau, accumulation",
                 10, "beginner"),
                ("Inverser une chaine",
                 "Ecris une methode reverseString(String s) qui retourne la chaine inversee. Exemple: 'dojo' -> 'ojod'.",
                 "String, boucle, charAt, StringBuilder",
                 10, "beginner"),
                ("Compter les voyelles",
                 "Ecris une methode countVowels(String s) qui compte le nombre de voyelles (a,e,i,o,u) dans une chaine, sans tenir compte de la casse.",
                 "String, boucle, toLowerCase, conditions multiples",
                 20, "intermediate"),
                ("Fibonacci",
                 "Ecris une methode fibonacci(int n) qui retourne le n-ieme terme de la suite de Fibonacci. fibonacci(0)=0, fibonacci(1)=1.",
                 "recursion ou iteration, cas de base, suite",
                 20, "intermediate"),
                ("Palindrome",
                 "Ecris une methode isPalindrome(String s) qui retourne true si la chaine est un palindrome (se lit pareil dans les deux sens). Ignore la casse.",
                 "String, reverse, equals, toLowerCase",
                 20, "intermediate"),
                ("Tableau trie",
                 "Ecris une methode isSorted(int[] arr) qui retourne true si le tableau est trie dans l'ordre croissant.",
                 "boucle, comparaison consecutifs, edge cases tableau vide",
                 20, "intermediate"),
                ("Occurrence d'un caractere",
                 "Ecris une methode charCount(String s, char c) qui retourne le nombre de fois que le caractere c apparait dans la chaine s.",
                 "String, boucle, charAt, compteur",
                 20, "intermediate"),
                ("FizzBuzz",
                 "Ecris une methode fizzBuzz(int n) qui retourne une liste de chaines de 1 a n. Pour les multiples de 3: 'Fizz', de 5: 'Buzz', de 15: 'FizzBuzz', sinon le nombre en chaine.",
                 "ArrayList, modulo, conditions, String.valueOf",
                 30, "advanced"),
                ("Nombre premier",
                 "Ecris une methode isPrime(int n) qui retourne true si n est un nombre premier. Gere les cas n<=1.",
                 "boucle, modulo, optimisation sqrt, edge cases",
                 30, "advanced"),
                ("Anagramme",
                 "Ecris une methode isAnagram(String s1, String s2) qui retourne true si les deux chaines sont des anagrammes (memes lettres, ordre different). Ignore la casse et les espaces.",
                 "Arrays.sort, toCharArray, toLowerCase, trim",
                 30, "advanced"),
                ("Factorielle",
                 "Ecris une methode factorial(int n) qui retourne n! (factorielle de n). Gere le cas n=0 (retourne 1). Utilise la recursion.",
                 "recursion, cas de base, multiplication",
                 30, "advanced"),
                ("Deux sommes",
                 "Etant donne un tableau d'entiers et une cible, ecris une methode twoSum(int[] nums, int target) qui retourne les indices des deux nombres dont la somme egale target. Suppose qu'il y a exactement une solution.",
                 "HashMap, indices, iteration, complexite O(n)",
                 30, "advanced"),
            ]
            cursor.executemany("INSERT INTO challenges (title, description, expected_concepts, points, difficulty) VALUES (?, ?, ?, ?, ?)", challenges)
            conn.commit()
        
        # Seed achievements if empty
        cursor.execute("SELECT COUNT(*) FROM achievements")
        count = cursor.fetchone()[0]
        if count == 0:
            achievements = [
                ('first_blood',       'Premier Sang',          'Résous ton tout premier challenge.',                             '🥋', 'milestone'),
                ('dojo_initiate',     'Initié du Dojo',         'Résous 3 challenges.',                                           '🎋', 'milestone'),
                ('apprentice_path',   "Voie de l'Apprenti",     'Résous 5 challenges.',                                           '📜', 'milestone'),
                ('halfway_there',     'À Mi-Chemin',            'Résous la moitié des challenges (8 sur 15).',                    '⛩️', 'milestone'),
                ('dojo_master',       'Maître du Dojo',         'Résous tous les 15 challenges. Félicitations, Maître !',         '🏆', 'milestone'),
                ('century',           'Le Siècle',              'Atteins 100 points.',                                            '💯', 'milestone'),
                ('triple_century',    'Triple Siècle',          'Atteins 300 points.',                                            '🔥', 'milestone'),
                ('six_hundred',       'Maître des Points',      'Atteins 600 points.',                                            '👑', 'milestone'),
                ('beginner_clear',    'Débutant Complété',      'Résous tous les challenges de niveau débutant (10 pts).',        '🟢', 'unlock'),
                ('intermediate_clear','Intermédiaire Complété', 'Résous tous les challenges de niveau intermédiaire (20 pts).',   '🟡', 'unlock'),
                ('advanced_clear',    'Avancé Complété',        'Résous tous les challenges de niveau avancé (30 pts).',          '🔴', 'unlock'),
                ('speed_demon',       'Démon de la Vitesse',    'Résous un challenge en moins de 5 minutes.',                     '⚡', 'speed'),
                ('lightning',         'Éclair',                 'Résous un challenge en moins de 2 minutes.',                     '🌩️', 'speed'),
            ]
            cursor.executemany("INSERT OR IGNORE INTO achievements (code, title, description, icon, category) VALUES (?, ?, ?, ?, ?)", achievements)
            conn.commit()
        
        cursor.close()
        conn.close()

    def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        if self.use_sqlite:
            return self.connection is not None
        return self.connection is not None and self.connection.is_connected()

    def backend_name(self) -> str:
        """Returns the active database backend name for the UI."""
        return "SQLite local" if self.use_sqlite else "MySQL"

    def health_report(self) -> dict:
        """
        Small, UI-friendly database report.
        It makes the persistence layer visible during demos and soutenances.
        """
        self._ensure_connection()
        report = {
            "backend": self.backend_name(),
            "connected": self.is_connected(),
            "database": os.getenv("DB_NAME", "codedojo") if not self.use_sqlite else self.sqlite_path,
            "users": 0,
            "challenges": 0,
            "sessions": 0,
            "messages": 0,
        }
        if not report["connected"]:
            return report

        tables = {
            "users": "users",
            "challenges": "challenges",
            "sessions": "challenge_sessions",
            "messages": "ai_messages",
        }
        try:
            cursor = self.connection.cursor()
            for key, table in tables.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row = cursor.fetchone()
                report[key] = int(row[0]) if row else 0
            cursor.close()
        except Exception as e:
            print(f"[DB] Erreur health_report : {e}")
        return report

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

    def get_top_users(self, limit: int = 10) -> List[dict]:
        """Récupère les 10 meilleurs utilisateurs classés par points."""
        self._ensure_connection()
        if not self.is_connected():
            return []
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT username, points FROM users ORDER BY points DESC, username ASC LIMIT %s",
                (limit,)
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            print(f"[DB] Erreur get_top_users : {e}")
            return []

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

    def get_total_time_spent(self, user_id: int) -> int:
        """Returns the total time spent on challenges in seconds calculated in Python."""
        self._ensure_connection()
        if not self.is_connected():
            return 0
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT started_at, solved_at FROM challenge_sessions WHERE user_id = %s",
                (user_id,)
            )
            rows = cursor.fetchall()
            cursor.close()
            
            total_seconds = 0
            from datetime import datetime
            for r in rows:
                start = r.get('started_at')
                solve = r.get('solved_at')
                
                # Convert strings to datetime objects if needed
                if isinstance(start, str):
                    try:
                        start = datetime.strptime(start.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                if isinstance(solve, str) and solve:
                    try:
                        solve = datetime.strptime(solve.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        solve = None
                
                if start:
                    if solve:
                        diff = (solve - start).total_seconds()
                    else:
                        now = datetime.now()
                        diff = min((now - start).total_seconds(), 1500)
                    
                    if diff > 0:
                        total_seconds += int(diff)
            return total_seconds
        except Exception as e:
            print(f"[DB] Erreur get_total_time_spent : {e}")
            return 0

    def close(self):
        """Ferme la connexion proprement."""
        if self.is_connected():
            self.connection.close()
            print("[DB] Connexion fermée.")
