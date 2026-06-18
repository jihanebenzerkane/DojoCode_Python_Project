"""
achievement_service.py — Evaluates and awards achievements after each solve.

Called by MainWindow after a successful solve (AI path or verify path).
Returns a list of newly-earned achievement dicts so the UI can display them.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repository.mysql_repo import MySQLRepository
    from models.entities import User, Challenge


# ── Achievement evaluation rules ─────────────────────────────────────────────
# Each rule is: (code, check_fn(repo, user, challenge, session_id) -> bool)
# The check_fn receives the CURRENT state AFTER the solve has been committed.

def _check_first_blood(repo, user, challenge, session_id):
    return repo.count_solved(user.id) == 1

def _check_dojo_initiate(repo, user, challenge, session_id):
    return repo.count_solved(user.id) >= 3

def _check_apprentice_path(repo, user, challenge, session_id):
    return repo.count_solved(user.id) >= 5

def _check_halfway_there(repo, user, challenge, session_id):
    total = sum(
        repo.count_challenges_by_points(pts) for pts in [10, 20, 30]
    )
    return repo.count_solved(user.id) >= total // 2

def _check_dojo_master(repo, user, challenge, session_id):
    total = sum(
        repo.count_challenges_by_points(pts) for pts in [10, 20, 30]
    )
    return repo.count_solved(user.id) >= total

def _check_century(repo, user, challenge, session_id):
    return user.points >= 100

def _check_triple_century(repo, user, challenge, session_id):
    return user.points >= 300

def _check_six_hundred(repo, user, challenge, session_id):
    return user.points >= 600

def _check_beginner_clear(repo, user, challenge, session_id):
    total = repo.count_challenges_by_points(10)
    return total > 0 and repo.count_solved_by_points(user.id, 10) >= total

def _check_intermediate_clear(repo, user, challenge, session_id):
    total = repo.count_challenges_by_points(20)
    return total > 0 and repo.count_solved_by_points(user.id, 20) >= total

def _check_advanced_clear(repo, user, challenge, session_id):
    total = repo.count_challenges_by_points(30)
    return total > 0 and repo.count_solved_by_points(user.id, 30) >= total

def _check_speed_demon(repo, user, challenge, session_id):
    if session_id is None:
        return False
    elapsed = repo.get_session_elapsed_seconds(session_id)
    return elapsed is not None and elapsed <= 300  # 5 minutes

def _check_lightning(repo, user, challenge, session_id):
    if session_id is None:
        return False
    elapsed = repo.get_session_elapsed_seconds(session_id)
    return elapsed is not None and elapsed <= 120  # 2 minutes


RULES = [
    ("first_blood",       _check_first_blood),
    ("dojo_initiate",     _check_dojo_initiate),
    ("apprentice_path",   _check_apprentice_path),
    ("halfway_there",     _check_halfway_there),
    ("dojo_master",       _check_dojo_master),
    ("century",           _check_century),
    ("triple_century",    _check_triple_century),
    ("six_hundred",       _check_six_hundred),
    ("beginner_clear",    _check_beginner_clear),
    ("intermediate_clear",_check_intermediate_clear),
    ("advanced_clear",    _check_advanced_clear),
    ("lightning",         _check_lightning),      # check lightning first (stricter)
    ("speed_demon",       _check_speed_demon),
]


class AchievementService:
    """
    Evaluates which achievements a user just unlocked after a solve,
    awards them in the DB, and returns the list of newly-earned achievements.
    """

    def __init__(self, repo: "MySQLRepository"):
        self.repo = repo

    def evaluate_after_solve(
        self,
        user,
        challenge,
        session_id: int | None
    ) -> list[dict]:
        """
        Call this right after:
          1. mark_challenge_solved() returned True (first solve)
          2. repo.refresh_user() updated user.points

        Returns a list of newly-earned achievement dicts (may be empty).
        """
        already_earned = self.repo.get_user_achievement_ids(user.id)
        newly_earned = []

        for code, check_fn in RULES:
            ach = self.repo.get_achievement_by_code(code)
            if ach is None:
                continue  # achievement not seeded yet — skip gracefully
            if ach["id"] in already_earned:
                continue  # user already has it
            try:
                if check_fn(self.repo, user, challenge, session_id):
                    awarded = self.repo.award_achievement(user.id, ach["id"])
                    if awarded:
                        newly_earned.append(ach)
                        already_earned.add(ach["id"])  # prevent double-fire in same pass
            except Exception as e:
                print(f"[Achievement] Error checking '{code}': {e}")

        return newly_earned