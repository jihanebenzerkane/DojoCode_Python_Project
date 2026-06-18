"""
setup_db.py — Crée la base de données, les 4 tables, et insère les 15 challenges Java.
Lancer depuis la racine : python db/setup_db.py
"""
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import sys

# Charger .env depuis la racine du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def get_connection(with_db=False):
    """Connexion MySQL. Sans base = pour la créer. Avec base = pour les tables."""
    config = dict(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        charset='utf8mb4',
    )
    if with_db:
        config['database'] = os.getenv('DB_NAME', 'codedojo')
    return mysql.connector.connect(**config)


def create_tables():
    """Crée la base de données et les 4 tables."""
    print("\n[1/2] Création de la base et des tables...")
    db_name = os.getenv('DB_NAME', 'codedojo')
    conn = get_connection(with_db=False)
    cursor = conn.cursor()

    statements = [
        f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
        f"USE {db_name}",

        # ── users ─────────────────────────────────────────
        """CREATE TABLE IF NOT EXISTS users (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            username      VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            points        INT DEFAULT 0,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",

        # ── challenges ────────────────────────────────────
        """CREATE TABLE IF NOT EXISTS challenges (
            id                INT AUTO_INCREMENT PRIMARY KEY,
            title             VARCHAR(255) NOT NULL,
            description       TEXT NOT NULL,
            expected_concepts VARCHAR(500),
            points            INT DEFAULT 10,
            difficulty        VARCHAR(50) DEFAULT 'beginner'
        )""",

        # ── challenge_sessions ────────────────────────────
        """CREATE TABLE IF NOT EXISTS challenge_sessions (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            user_id       INT NOT NULL,
            challenge_id  INT NOT NULL,
            started_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            solved_at     TIMESTAMP NULL DEFAULT NULL,
            points_earned INT DEFAULT 0,
            FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
        )""",

        # ── ai_messages ───────────────────────────────────
        """CREATE TABLE IF NOT EXISTS ai_messages (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            role       VARCHAR(20)  NOT NULL,
            content    TEXT         NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES challenge_sessions(id) ON DELETE CASCADE
        )""",

        # ── user_solved_challenges (solved-once guard) ────
        """CREATE TABLE IF NOT EXISTS user_solved_challenges (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            user_id      INT NOT NULL,
            challenge_id INT NOT NULL,
            solved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_user_challenge (user_id, challenge_id),
            FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
        )""",

        # ── achievements catalogue ────────────────────────
        """CREATE TABLE IF NOT EXISTS achievements (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            code        VARCHAR(100) UNIQUE NOT NULL,
            title       VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            icon        VARCHAR(10)  NOT NULL,
            category    VARCHAR(50)  NOT NULL
        )""",

        # ── user_achievements (earned prizes) ─────────────
        """CREATE TABLE IF NOT EXISTS user_achievements (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            user_id        INT NOT NULL,
            achievement_id INT NOT NULL,
            earned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_user_achievement (user_id, achievement_id),
            FOREIGN KEY (user_id)        REFERENCES users(id)        ON DELETE CASCADE,
            FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
        )""",
    ]

    for sql in statements:
        cursor.execute(sql)
        print(f"  OK {sql.strip()[:65]}...")

    conn.commit()
    cursor.close()
    conn.close()
    print("  Tables créées avec succès.")


def seed_challenges():
    """Insère les 15 challenges Java (3 niveaux de difficulté)."""
    print("\n[2/2] Insertion des 15 challenges Java...")
    conn = get_connection(with_db=True)
    cursor = conn.cursor()

    # Vérifier si déjà insérés
    cursor.execute("SELECT COUNT(*) FROM challenges")
    count = cursor.fetchone()[0]
    if count >= 15:
        print(f"  Déjà {count} challenges en base. Rien à faire.")
        cursor.close()
        conn.close()
        return

    # Vider si partiellement rempli
    if count > 0:
        cursor.execute("DELETE FROM challenges")
        conn.commit()

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

    sql = """INSERT INTO challenges
             (title, description, expected_concepts, points, difficulty)
             VALUES (%s, %s, %s, %s, %s)"""

    cursor.executemany(sql, challenges)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM challenges")
    total = cursor.fetchone()[0]
    print(f"  OK Challenges insérés : {total} / 15 attendus.")

    cursor.close()
    conn.close()


def seed_achievements():
    """Inserts the achievement catalogue (idempotent — uses INSERT IGNORE)."""
    print("\n[3/3] Seeding achievements catalogue...")
    conn = get_connection(with_db=True)
    cursor = conn.cursor()

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

    sql = ("INSERT IGNORE INTO achievements (code, title, description, icon, category) "
           "VALUES (%s, %s, %s, %s, %s)")
    cursor.executemany(sql, achievements)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM achievements")
    total = cursor.fetchone()[0]
    print(f"  OK Achievements en base : {total}")
    cursor.close()
    conn.close()


if __name__ == '__main__':
    try:
        create_tables()
        seed_challenges()
        seed_achievements()
    except Error as e:
        print(f"\nERROR MySQL : {e}")
        print("Vérifie que MySQL est lancé et que ton .env est correct :")
        print("  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")