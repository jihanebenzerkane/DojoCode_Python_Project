# ⛩️ CodeDojo

> **Discipline · Code · Excellence**
> 
> Une plateforme d'apprentissage Java desktop propulsée par l'IA — conçue pour les étudiants ENSAH en IA & Transformation Digitale.

---

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt6-8A2BE2?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge)](https://github.com/)

---

## 📋 Description

**CodeDojo** est une application desktop Python (PySide6) moderne et immersive qui transforme l'apprentissage du langage Java en une véritable aventure interactive. En combinant l'esthétique zen d'un temple de code japonais et l'intelligence de modèles de langage avancés (Gemini / Groq), CodeDojo propose un entraînement intensif rythmé par la méthode socratique.

---

## 🌟 Fonctionnalités Clés & Expérience Utilisateur

### 🔴 Fonctionnalités Professionnelles Récemment Ajoutées
1. **🚀 Boilerplate Java Intelligent :** L'éditeur de code est automatiquement pré-rempli à chaque sélection de challenge avec le squelette et les signatures de méthodes exactes requises. Plus besoin d'écrire la structure répétitive !
2. **⌨️ Raccourcis Clavier Avancés (Power-User) :**
   - `Ctrl + Enter` : Soumettre instantanément le code au Sensei IA
   - `Ctrl + Shift + V` : Vérifier et compiler via le terminal JDK local
   - `Ctrl + /` : Commenter / Décommenter les lignes sélectionnées
3. **📁 Sauvegarde Automatique des Brouillons :** Les modifications de code sont stockées en temps réel (`~/.codedojo_drafts.json`) par utilisateur et par challenge. Ton travail n'est jamais perdu !
4. **🔍 Filtre & Recherche Dynamique :** Recherche tes défis par texte et filtre-les par statut (*Tous*, *À faire*, *Résolus*).
5. **🥋 Dashboard Profil Utilisateur :** Suivi graphique complet de ta progression avec barre de progression de niveau, indicateurs par palier, temps total de codage et grille de badges.
6. **🏆 Classement du Dojo (Leaderboard) :** Suis la compétition en direct avec le Top 10 des meilleurs utilisateurs de la base de données.
7. **⏱️ Alarme & Alertes Pomodoro :** Le timer de 25 minutes clignote en rouge vif durant les 5 dernières minutes et affiche une notification lorsque la session s'achève.

### 🍃 Autres Fonctionnalités
- 📜 **15 challenges Java** structurés en 3 catégories de progression déblocables (Débutant, Intermédiaire, Avancé)
- 🧘 **Sensei IA** — un tuteur pédagogique socratique qui te guide par des questions sans jamais dévoiler directement la solution.
- 🧪 **Terminal de Compilation JDK 25 :** Compilation et exécution de tests unitaires locales avec feedback rétro interactif.
- 🍂 **Ambiance Zen :** Feuilles tombantes animées, sélecteur de fonds d'écran relaxants et lecteur de musique Lofi intégré.

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
│   ├── style.qss              # Feuille de styles centralisée (UI Dojo Zen)
│   └── app_bg.png             # Fonds d'écran immersifs
│
├── db/
│   ├── setup_db.py            # Créer le schéma + insérer les 15 challenges
│   ├── init_db.sql            # Script SQL brut de structure
│   └── seed_challenges.sql    # Données d'insertion initiales
│
├── models/
│   └── entities.py            # Dataclasses : User, Challenge, ChallengeSession, AIMessage
│
├── repository/
│   └── mysql_repo.py          # Couche d'accès DB avec fallback SQLite automatique
│
├── services/
│   ├── auth_service.py        # Inscription / Connexion avec hachage bcrypt
│   ├── draft_service.py       # Persistance locale des brouillons JSON
│   ├── achievement_service.py # Évaluation et attribution des récompenses
│   ├── groq_service.py        # Connecteur API Groq / Gemini
│   ├── groq_worker.py         # Thread d'appel asynchrone IA
│   └── verification_service.py# Compilateur et runner Java local
│
└── ui/
    ├── login_window.py        # Écran de connexion au Dojo
    ├── main_window.py         # Assemblage principal de l'IDE
    ├── challenge_panel.py     # Liste filtrable et progressive des défis
    ├── editor_panel.py        # Éditeur Java avec coloration syntaxique et raccourcis
    ├── profile_dialog.py      # Modal statistiques, temps de code et badges
    ├── leaderboard_dialog.py  # Modal du classement des 10 meilleurs
    ├── settings_dialog.py     # Configuration API et niveau du Sensei
    ├── java_highlighter.py    # Colorisation syntaxique QSyntaxHighlighter
    ├── background_picker.py   # Galerie des décors zen
    ├── music_player.py        # Lecteur de flux audio lofi
    └── leaf_overlay.py        # Animation interactive de chute des feuilles
```

---

## ⚙️ Configuration

### 1. Prérequis

- Python **3.11+**
- Java **JDK 8+** (recommandé JDK 25 configuré sur votre `PATH` pour utiliser le terminal vérificateur local)
- MySQL **8.x** (ex: via XAMPP) ou utilise le **mode dégradé SQLite automatique sans config !**
- Une clé API gratuite : **Gemini** (https://aistudio.google.com) ou **Groq** (https://console.groq.com)

### 2. Initialisation Rapide

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Fichier `.env` de Configuration

Créez ou modifiez un fichier `.env` à la racine :

```env
# ── Configuration de la Base de Données ──
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=           # Laisser vide si XAMPP par défaut
DB_NAME=codedojo

# ── Clé API d'IA ──
GEMINI_API_KEY=AIzaSy... # Fortement recommandé pour l'intégration Gemini
# OU
GROQ_API_KEY=gsk_...
```

*Note : Si MySQL n'est pas démarré, l'application basculera de manière invisible sur une base locale SQLite de secours (`db/codedojo.db`). Aucun paramétrage MySQL obligatoire !*

### 4. Seed de la Base

```bash
python db/setup_db.py
```

---

## 🚀 Lancement

Exécutez simplement le lanceur automatique sous Windows :
```bat
run.bat
```
Ou manuellement :
```bash
python main.py
```

---

## 🏆 Voie de la Progression

| Rangs et Niveaux | Points requis | Badge |
| :--- | :---: | :---: |
| **🎋 Étudiant** | 0 – 99 | Débutant |
| **🥷 Apprenti** | 100 – 299 | Intermédiaire |
| **⚔️ Pratiquant** | 300 – 599 | Expérimenté |
| **🧘 Maître** | 600+ | Légende |

---

## 🛠️ Stack Technique

- **Moteur UI :** PySide6 (Qt6)
- **Base de Données :** MySQL Connector / SQLite3
- **Chiffrement :** bcrypt
- **IA Tuteur :** Google Gemini API / Groq API (LLaMA 3.3)
- **Compilateur :** Local `javac` / `java` subprocess execution

---

## 👩‍💻 Auteur

Développé dans le cadre du module **IA & Transformation Digitale** — ENSAH 2025–2026.
Une approche moderne d'apprentissage ludique des compétences d'ingénierie logicielle.
