-- ============================================================
-- CodeDojo -- init_db.sql
-- Executer en premier, une seule fois
-- ============================================================

CREATE DATABASE IF NOT EXISTS codedojo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE codedojo;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    points        INT DEFAULT 0,
    level         INT DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenges (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    description       TEXT NOT NULL,
    difficulty        VARCHAR(50) DEFAULT 'junior',
    points            INT DEFAULT 10,
    language          VARCHAR(50) DEFAULT 'java',
    expected_concepts VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS challenge_sessions (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    challenge_id  INT NOT NULL,
    started_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    solved        BOOLEAN DEFAULT FALSE,
    points_earned INT DEFAULT 0,
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_messages (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    role       VARCHAR(20)  NOT NULL,
    content    TEXT         NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES challenge_sessions(id) ON DELETE CASCADE
);

SELECT 'Tables creees avec succes.' AS status;