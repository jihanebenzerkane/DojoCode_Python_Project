-- ============================================================
-- CodeDojo v2 — Migration: add solved-once tracking + achievements
-- Run ONCE after your existing database is set up:
--   mysql -u root -p codedojo < db/migrate_v2.sql
-- ============================================================

USE codedojo;

-- 1. Per-user solved challenges (one row per user+challenge, permanent record)
CREATE TABLE IF NOT EXISTS user_solved_challenges (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    challenge_id INT NOT NULL,
    solved_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_challenge (user_id, challenge_id),
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
);

-- 2. Achievement definitions (static catalogue)
CREATE TABLE IF NOT EXISTS achievements (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(100) UNIQUE NOT NULL,  -- machine key, e.g. 'first_blood'
    title       VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    icon        VARCHAR(10)  NOT NULL,          -- emoji
    category    VARCHAR(50)  NOT NULL           -- 'milestone', 'streak', 'unlock', 'speed'
);

-- 3. User-earned achievements (one row per user+achievement)
CREATE TABLE IF NOT EXISTS user_achievements (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    achievement_id INT NOT NULL,
    earned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_achievement (user_id, achievement_id),
    FOREIGN KEY (user_id)        REFERENCES users(id)        ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
);

-- 4. Seed achievement catalogue
INSERT IGNORE INTO achievements (code, title, description, icon, category) VALUES
-- First steps
('first_blood',      'Premier Sang',       'Résous ton tout premier challenge.',                          '🥋', 'milestone'),
('dojo_initiate',    'Initié du Dojo',     'Résous 3 challenges.',                                        '🎋', 'milestone'),
('apprentice_path',  'Voie de l\'Apprenti','Résous 5 challenges.',                                        '📜', 'milestone'),
('halfway_there',    'À Mi-Chemin',        'Résous la moitié des challenges (8 sur 15).',                 '⛩️', 'milestone'),
('dojo_master',      'Maître du Dojo',     'Résous tous les 15 challenges. Félicitations, Maître !',      '🏆', 'milestone'),
-- Points milestones
('century',          'Le Siècle',          'Atteins 100 points.',                                         '💯', 'milestone'),
('triple_century',   'Triple Siècle',      'Atteins 300 points.',                                         '🔥', 'milestone'),
('six_hundred',      'Maître des Points',  'Atteins 600 points.',                                         '👑', 'milestone'),
-- Difficulty unlocks
('beginner_clear',   'Débutant Complété',  'Résous tous les challenges de niveau débutant (10 pts).',     '🟢', 'unlock'),
('intermediate_clear','Intermédiaire Complété','Résous tous les challenges de niveau intermédiaire (20 pts).','🟡','unlock'),
('advanced_clear',   'Avancé Complété',    'Résous tous les challenges de niveau avancé (30 pts).',       '🔴', 'unlock'),
-- Speed
('speed_demon',      'Démon de la Vitesse','Résous un challenge en moins de 5 minutes.',                  '⚡', 'speed'),
('lightning',        'Éclair',             'Résous un challenge en moins de 2 minutes.',                  '🌩️', 'speed');

SELECT CONCAT('Achievements seeded: ', COUNT(*), ' entries') AS status FROM achievements;