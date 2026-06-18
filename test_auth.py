"""
test_auth.py — Tests unitaires pour AuthService.
Lancer avec : pytest test_auth.py -v
Note : Nécessite une connexion MySQL configurée dans .env
"""
import pytest
import os
import sys

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))


def _get_auth():
    """Helper to create AuthService with a live DB connection."""
    from repository.mysql_repo import MySQLRepository
    from services.auth_service import AuthService
    repo = MySQLRepository()
    return AuthService(repo), repo


class TestAuthService:
    """Tests for registration and login logic."""

    TEST_USER = "test_pytest_user_xqz"
    TEST_PASS = "dojo1234"

    def setup_method(self):
        """Ensure the test user does not exist before each test."""
        try:
            auth, repo = _get_auth()
            if repo.is_connected():
                cursor = repo.connection.cursor()
                cursor.execute(
                    "DELETE FROM users WHERE username = %s", (self.TEST_USER,)
                )
                repo.connection.commit()
                cursor.close()
        except Exception:
            pass

    # ── Registration ──────────────────────────────────────────────────────────

    def test_register_success(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        ok, msg = auth.register(self.TEST_USER, self.TEST_PASS)
        assert ok is True
        assert msg == "ok"

    def test_register_duplicate_fails(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        ok, msg = auth.register(self.TEST_USER, self.TEST_PASS)
        assert ok is False
        assert self.TEST_USER in msg

    def test_register_short_username_fails(self):
        auth, _ = _get_auth()
        ok, msg = auth.register("ab", self.TEST_PASS)
        assert ok is False
        assert "3" in msg  # mentions min 3 chars

    def test_register_short_password_fails(self):
        auth, _ = _get_auth()
        ok, msg = auth.register(self.TEST_USER, "123")
        assert ok is False
        assert "4" in msg  # mentions min 4 chars

    # ── Login ─────────────────────────────────────────────────────────────────

    def test_login_success(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        user, msg = auth.login(self.TEST_USER, self.TEST_PASS)
        assert user is not None
        assert user.username == self.TEST_USER
        assert msg == "ok"

    def test_login_wrong_password_fails(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        user, msg = auth.login(self.TEST_USER, "wrongpassword")
        assert user is None
        assert "incorrect" in msg.lower()

    def test_login_unknown_user_fails(self):
        auth, _ = _get_auth()
        user, msg = auth.login("nobody_xyz_999", "pass")
        assert user is None
        assert "incorrect" in msg.lower()

    def test_login_empty_fields_fails(self):
        auth, _ = _get_auth()
        user, msg = auth.login("", "")
        assert user is None
        assert "requis" in msg.lower()

    # ── Password hashing ──────────────────────────────────────────────────────

    def test_password_is_hashed(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        stored = repo.get_user_by_username(self.TEST_USER)
        assert stored is not None
        # Hash must NOT be the plain password
        assert stored.password_hash != self.TEST_PASS
        # Hash must start with bcrypt prefix
        assert stored.password_hash.startswith("$2b$")

    def test_check_password_correct(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        user = repo.get_user_by_username(self.TEST_USER)
        assert user.check_password(self.TEST_PASS) is True

    def test_check_password_wrong(self):
        auth, repo = _get_auth()
        if not repo.is_connected():
            pytest.skip("No DB connection available")
        auth.register(self.TEST_USER, self.TEST_PASS)
        user = repo.get_user_by_username(self.TEST_USER)
        assert user.check_password("notthepassword") is False