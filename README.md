# ⛩️ CodeDojo

> **Discipline · Code · Excellence**
> 
> Une plateforme d'apprentissage Java desktop propulsée par l'IA — conçue pour les étudiants ENSAH en IA & Transformation Digitale.

---

## 📋 Description

**CodeDojo** est une application desktop Python (PySide6) qui propose :

- 📜 **15 challenges Java** de 3 niveaux de difficulté (Débutant, Intermédiaire, Avancé)
- 🧘 **Sensei IA** — un tuteur pédagogique propulsé par **Groq API (LLaMA 3)** qui utilise la méthode socratique
- ⭐ **Système de points & niveaux** (Étudiant → Apprenti → Pratiquant → Maître)
- ⏱️ **Timer Pomodoro** intégré dans l'interface
- 🍂 **Animation de feuilles tombantes** pour une atmosphère Dojo zen
- ✏️ **Éditeur de code Java** avec **coloration syntaxique** intégrée

---

## 🗂️ Structure du projet

```
codedojo/
├── main.py                    # Point d'entrée
├── .env                       # Variables d'environnement (DB + API)
├── requirements.txt           # Dépendances Python
├── run.bat                    # Lancer avec le venv Windows
│
├── assets/
│   └── style.qss              # Feuille de styles centralisée (UI)
│
├── db/
│   ├── setup_db.py            # Créer le schéma + insérer les 15 challenges
│   ├── init_db.sql            # Script SQL brut (alternatif)
│   └── seed_challenges.sql    # Données de seed SQL
│
├── models/
│   └── entities.py            # Dataclasses : User, Challenge, ChallengeSession, AIMessage
│
├── repository/
│   └── mysql_repo.py          # Couche DAO MySQL (requêtes paramétrées)
│
├── services/
│   ├── auth_service.py        # Inscription / Connexion (bcrypt)
│   ├── groq_service.py        # Client API Groq (LLaMA 3)
│   ├── groq_worker.py         # QThread pour appels Groq asynchrones
│   └── sensei_prompt.py       # Construction du prompt Sensei (méthode socratique)
│
└── ui/
    ├── login_window.py        # Fenêtre de connexion / inscription
    ├── main_window.py         # Fenêtre principale (3 panneaux)
    ├── java_highlighter.py    # Colorisation syntaxique Java (QSyntaxHighlighter)
    └── leaf_overlay.py        # Animation de feuilles tombantes (QPainter)
```

---

## ⚙️ Configuration

### 1. Prérequis

- Python **3.11+** (testé avec 3.14.3)
- MySQL **8.x** en cours d'exécution (XAMPP recommandé)
- Une clé API **Groq** gratuite : https://console.groq.com

### 2. Environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration `.env`

Modifie le fichier `.env` à la racine du projet :

```env
# ── Base de données MySQL ──────────────────────────
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=           # ton mot de passe MySQL (vide si XAMPP par défaut)
DB_NAME=codedojo

# ── Groq API ───────────────────────────────────────
GROQ_API_KEY=gsk_...   # ta clé API Groq
```

### 4. Initialisation de la base de données

```bash
python db/setup_db.py
```

Cela crée automatiquement :
- La base de données `codedojo`
- Les 4 tables (`users`, `challenges`, `challenge_sessions`, `ai_messages`)
- Les **15 challenges Java** pré-chargés

---

## 🚀 Lancer l'application

### Option A — Script batch (recommandé sur Windows)

```bat
run.bat
```

### Option B — Avec le venv activé

```bash
.\venv\Scripts\activate
python main.py
```

---

## 🎮 Utilisation

1. **Inscription** — Crée un compte avec un nom d'utilisateur + mot de passe (min. 4 caractères)
2. **Connexion** — Accède à l'interface principale CodeDojo
3. **Choisir un challenge** — Sélectionne un challenge dans le panneau gauche (🟢=10pts, 🟡=20pts, 🔴=30pts)
4. **Écrire du code Java** — L'éditeur central avec coloration syntaxique s'ouvre
5. **Soumettre au Sensei** — Le Sensei analyse ton code et te guide par des questions socratiques
6. **Gagner des points** — Si le Sensei détecte que ta solution est correcte, tes points sont mis à jour

---

## 🏆 Niveaux

| Points | Niveau |
|--------|--------|
| 0–99 | 🎋 Étudiant |
| 100–299 | 🥷 Apprenti |
| 300–599 | ⚔️ Pratiquant |
| 600+ | 🧘 Maître |

---

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | PySide6 (Qt 6.x) |
| Base de données | MySQL + mysql-connector-python |
| IA Tuteur | Groq API (LLaMA 3 - 8B) |
| Sécurité | bcrypt (hachage de mots de passe) |
| Config | python-dotenv |
| Tests | pytest |

---

## 👩‍💻 Auteur

Développé dans le cadre du module **IA & Transformation Digitale** — ENSAH 2025–2026
