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
        # ── 10 pts (beginner) : Hello World, variables, if/else, for loop, while loop ──
        ("Hello World",
         "Écris un programme Java qui affiche 'Hello, World!' dans la console en utilisant System.out.println().",
         "System.out.println, méthode main, classe publique",
         10, "beginner"),

        ("Variables et types",
         "Déclare une variable entière 'age' = 25, une variable String 'nom' = 'Dojo', et affiche : 'Je suis Dojo et j'ai 25 ans'.",
         "int, String, déclaration de variables, concaténation",
         10, "beginner"),

        ("If / Else",
         "Écris une méthode estMajeur(int age) qui retourne true si age >= 18, false sinon. Affiche un message approprié.",
         "if, else, boolean, comparaison, return",
         10, "beginner"),

        ("Boucle For",
         "Écris une méthode afficherTable(int n) qui affiche la table de multiplication de n de 1 à 10.",
         "boucle for, System.out.println, multiplication",
         10, "beginner"),

        ("Boucle While",
         "Écris une méthode compterJusqua(int n) qui affiche les nombres de 1 à n en utilisant une boucle while.",
         "boucle while, incrémentation, condition d'arrêt",
         10, "beginner"),

        # ── 20 pts (intermediate) : arrays, methods, String, ArrayList, HashMap ──
        ("Tableaux (Arrays)",
         "Écris une méthode trouverMax(int[] tableau) qui retourne le plus grand élément d'un tableau d'entiers.",
         "tableau int[], boucle, comparaison, variable max",
         20, "intermediate"),

        ("Méthodes",
         "Écris deux méthodes : carre(int n) qui retourne n², et perimetre(int longueur, int largeur) qui retourne le périmètre d'un rectangle.",
         "méthodes avec paramètres, return, int, calcul",
         20, "intermediate"),

        ("Manipulation de String",
         "Écris une méthode compterMots(String phrase) qui retourne le nombre de mots dans une phrase (séparés par des espaces).",
         "String.split(), length, trim, gestion chaîne vide",
         20, "intermediate"),

        ("ArrayList",
         "Écris une méthode filtrerPairs(ArrayList<Integer> nombres) qui retourne une nouvelle ArrayList contenant uniquement les nombres pairs.",
         "ArrayList, add, boucle for-each, modulo, générics",
         20, "intermediate"),

        ("HashMap",
         "Écris une méthode compterLettres(String mot) qui retourne un HashMap<Character, Integer> comptant l'occurrence de chaque lettre.",
         "HashMap, put, getOrDefault, charAt, boucle",
         20, "intermediate"),

        # ── 30 pts (advanced) : OOP/classes, inheritance, interfaces, exceptions, File I/O ──
        ("OOP — Classes",
         "Crée une classe Étudiant avec les attributs nom (String), age (int), note (double). Ajoute un constructeur, des getters, et une méthode estRecu() qui retourne true si note >= 10.",
         "class, constructeur, attributs privés, getters, méthode boolean",
         30, "advanced"),

        ("Héritage",
         "Crée une classe Animal avec un attribut nom et une méthode parler(). Crée Chien et Chat qui héritent d'Animal et redéfinissent parler() ('Woof!' et 'Miaou!').",
         "extends, super, @Override, polymorphisme",
         30, "advanced"),

        ("Interfaces",
         "Crée une interface Calculable avec une méthode double calculer(). Implémente-la dans Cercle (aire = π*r²) et Rectangle (aire = l*L).",
         "interface, implements, Math.PI, méthode abstraite",
         30, "advanced"),

        ("Exceptions",
         "Écris une méthode diviser(int a, int b) qui retourne a/b mais lance une ArithmeticException personnalisée si b == 0, avec try-catch dans le main.",
         "try, catch, throw, ArithmeticException, message personnalisé",
         30, "advanced"),

        ("File I/O",
         "Écris un programme qui crée un fichier 'notes.txt', y écrit 3 lignes de texte avec BufferedWriter, puis lit et affiche le contenu avec BufferedReader.",
         "BufferedWriter, BufferedReader, FileWriter, FileReader, try-with-resources",
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