# ⛩️ CodeDojo - Diagrammes UML du Projet

Ce document présente l'ensemble de la conception technique du projet **CodeDojo** sous forme de diagrammes **UML** dynamiques générés avec **Mermaid**.

---

## 1. Diagramme des Cas d'Utilisation (Use Case Diagram)

Ce diagramme illustre les interactions des différents acteurs (l'Utilisateur/Élève et l'API externe Groq) avec les fonctionnalités du système.

```mermaid
flowchart TB
    %% Nodes styling & classes definition
    classDef actorStyle fill:#C1392B,stroke:#2C2416,stroke-width:2px,color:#FFFFFF;
    classDef ucStyle fill:#F5EDD6,stroke:#6B5D3F,stroke-width:1.5px,color:#2C2416;
    classDef systemStyle fill:#E8E0D5,stroke:#2C2416,stroke-width:2px,color:#2C2416;

    %% Acteurs
    U(("Utilisateur<br>🧑‍💻")):::actorStyle
    AI(("Groq API<br>🤖")):::actorStyle

    subgraph CodeDojo ["⛩️ Système CodeDojo"]
        direction TB
        UC1("S'inscrire<br><i>(Register)</i>"):::ucStyle
        UC2("Se connecter<br><i>(Login)</i>"):::ucStyle
        UC3("Choisir un challenge<br><i>(Choose Challenge)</i>"):::ucStyle
        UC4("Écrire du code Java<br><i>(Write Java Code)</i>"):::ucStyle
        UC5("Voir ses points<br><i>(View Points)</i>"):::ucStyle
        UC6("Valider & soumettre à l'IA<br><i>(Submit Code)</i>"):::ucStyle
        UC7("Recevoir un hint socratique<br><i>(Get Socratic Hint)</i>"):::ucStyle
    end

    %% Links
    U --> UC1
    U --> UC2
    U --> UC3
    U --> UC4
    U --> UC5
    
    UC6 --> AI
    
    %% Use case relationships
    UC6 -.->|include| UC7
    UC6 -.->|include| UC3
    UC6 -.->|include| UC4
```

---

## 2. Diagramme de Classes (Class Diagram)

Ce diagramme présente l'architecture logicielle du projet. Il illustre le découpage propre en couches respectant les principes de l'architecture d'entreprise :
- **Models/Entities** (Dataclasses métier)
- **Repository** (Accès aux données MySQL paramétré)
- **Services** (Logique d'authentification et appels asynchrones Groq)
- **UI (PySide6)** (Interface utilisateur avec design Dojo)

```mermaid
classDiagram
    direction TB

    %% Class Definitions
    class User {
        +int id
        +str username
        +str password_hash
        +int points
        +check_password(str plain_password) bool
        +get_level_name() str
    }

    class Challenge {
        +int id
        +str title
        +str description
        +str expected_concepts
        +int points
        +str difficulty
        +get_prompt_context() str
    }

    class ChallengeSession {
        +int id
        +int user_id
        +int challenge_id
        +int points_earned
        +datetime started_at
        +datetime solved_at
    }

    class AIMessage {
        +int id
        +int session_id
        +str role
        +str content
        +datetime created_at
    }

    class AuthService {
        +MySQLRepository repo
        +register(str username, str password) tuple[bool, str]
        +login(str username, str password) tuple[User, str]
        -_hash_password(str password) str
    }

    class GroqService {
        +Groq client
        +ask_sensei(str user_msg, str title, str code, list history) str
    }

    class GroqWorker {
        +Signal response_ready
        +Signal error_occurred
        +GroqService groq_service
        +run()
    }

    class MySQLRepository {
        +Connection connection
        +is_connected() bool
        +get_user_by_username(str username) User
        +create_user(str username, str password_hash) bool
        +update_points(int user_id, int points) bool
        +refresh_user(int user_id) User
        +get_all_challenges() list[Challenge]
        +create_session(int user_id, int challenge_id) int
        +mark_session_solved(int session_id, int points) bool
        +save_message(int session_id, str role, str content) bool
        +close()
    }

    class LoginWindow {
        +AuthService auth
        +MySQLRepository repo
        +QLineEdit username
        +QLineEdit password
        -_login()
        -_signup()
        -_open(User user)
    }

    class MainWindow {
        +User user
        +MySQLRepository repo
        +GroqService groq_service
        +ChallengePanel challenge_panel
        +EditorPanel editor_panel
        +AIPanel ai_panel
        -_submit_code()
        -_refresh_display()
    }

    %% Relationships
    ChallengeSession "N" --> "1" User : associates
    ChallengeSession "N" --> "1" Challenge : associates
    AIMessage "N" --> "1" ChallengeSession : contains
    
    AuthService --> MySQLRepository : queries
    LoginWindow --> AuthService : authenticates
    LoginWindow --> MySQLRepository : connects
    
    MainWindow --> MySQLRepository : updates
    MainWindow --> GroqService : requests
    GroqWorker --> GroqService : delegates
    MainWindow ..> GroqWorker : runs
```

---

## 3. Diagramme de Séquence - Authentification (Sequence Diagram - Auth)

Ce diagramme montre le flux d'opérations lors de la connexion d'un utilisateur, en mettant en évidence la vérification sécurisée avec **bcrypt**.

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant LW as LoginWindow
    participant AS as AuthService
    participant DB as MySQLRepository
    participant MySQL as Base MySQL

    U->>LW: Saisit credentials & clique sur Login
    LW->>AS: login(username, password)
    AS->>DB: get_user_by_username(username)
    DB->>MySQL: SELECT * FROM users WHERE username = %s
    MySQL-->>DB: Enregistrement utilisateur
    alt Utilisateur non trouvé
        DB-->>AS: None
        AS-->>LW: (None, "Nom d'utilisateur ou mot de passe incorrect")
        LW->>U: Affiche message d'erreur
    else Utilisateur trouvé
        DB-->>AS: Instance User
        AS->>AS: user.check_password(password)
        note over AS: Vérification via bcrypt.checkpw
        alt Mot de passe incorrect
            AS-->>LW: (None, "Nom d'utilisateur ou mot de passe incorrect")
            LW->>U: Affiche message d'erreur
        else Mot de passe correct
            AS-->>LW: (User, "ok")
            LW->>LW: _open(user)
            LW->>U: Ouvre la MainWindow et ferme LoginWindow
        end
    end
```

---

## 4. Diagramme de Séquence - Soumission de Code (Sequence Diagram - Code Submission)

Ce diagramme montre le traitement complet lors de la soumission de code Java, du thread asynchrone (QThread) pour l'API Groq (llama-3-8b-8192) jusqu'à la mise à jour des points de l'étudiant.

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant MW as MainWindow
    participant GW as GroqWorker (QThread)
    participant GS as GroqService
    participant API as Groq API (LLaMA 3)
    participant DB as MySQLRepository

    U->>MW: Saisit le code Java & clique sur Envoyer / Submit
    MW->>MW: Valide la saisie (code non vide)
    alt Code vide
        MW->>U: Affiche un avertissement "Code vide"
    else Code valide
        MW->>MW: Affiche un indicateur de chargement (désactive l'envoi)
        MW->>GW: Instantie et démarre GroqWorker.start()
        activate GW
        GW->>GS: ask_sensei(submitted_code, challenge_title, ...)
        GS->>API: POST /v1/chat/completions (llama3-8b-8192)
        note over API: Application du prompt Sensei (Méthode Socratique)
        API-->>GS: JSON response avec le message du Sensei
        GS-->>GW: Réponse textuelle (hint)
        GW-->>MW: Signal response_ready(hint)
        deactivate GW
        MW->>MW: Affiche le hint dans AIPanel
        MW->>DB: save_message(session_id, 'assistant', hint)
        MW->>MW: Réactive l'interface
        alt Si le Sensei détecte que la solution est correcte
            MW->>DB: mark_session_solved(session_id, points_earned)
            MW->>DB: update_points(user_id, points_earned)
            MW->>DB: save_message(session_id, 'system', 'Challenge résolu')
            MW->>MW: Affiche un message de félicitations
            MW->>MW: _refresh_display() (mise à jour des points et niveau)
            MW->>U: Actualise le score de l'étudiant
        end
    end
```
