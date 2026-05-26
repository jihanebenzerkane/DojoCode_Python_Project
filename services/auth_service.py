"""
auth_service.py — Authentification (inscription / connexion).
Les mots de passe sont toujours hachés avec bcrypt.
Jamais de mot de passe en clair en base.
"""
import bcrypt
from typing import Optional
from models.entities import User
from repository.mysql_repo import MySQLRepository


class AuthService:
    """
    Gère l'authentification : inscription et connexion.
    Les mots de passe sont toujours hachés avec bcrypt.
    """

    def __init__(self, repo: MySQLRepository):
        self.repo = repo

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Inscrit un nouvel utilisateur.
        Retourne (True, 'ok') ou (False, 'message erreur').
        """
        # Validations
        username = username.strip()
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit faire au moins 3 caractères."
        if len(username) > 50:
            return False, "Le nom d'utilisateur est trop long (max 50)."
        if len(password) < 4:
            return False, "Le mot de passe doit faire au moins 4 caractères."

        # Vérifier si username déjà pris
        existing = self.repo.get_user_by_username(username)
        if existing:
            return False, f"Le nom '{username}' est déjà utilisé."

        # Hacher le mot de passe avec bcrypt
        password_hash = self._hash_password(password)

        # Créer l'utilisateur
        success = self.repo.create_user(username, password_hash)
        if success:
            return True, "ok"
        else:
            return False, "Erreur base de données. Réessaie."

    def login(self, username: str, password: str) -> tuple[Optional[User], str]:
        """
        Connecte un utilisateur.
        Retourne (User, 'ok') ou (None, 'message erreur').
        """
        username = username.strip()
        if not username or not password:
            return None, "Nom d'utilisateur et mot de passe requis."

        # Récupérer l'utilisateur
        user = self.repo.get_user_by_username(username)
        if not user:
            return None, "Nom d'utilisateur ou mot de passe incorrect."

        # Vérifier le mot de passe avec bcrypt
        if not user.check_password(password):
            return None, "Nom d'utilisateur ou mot de passe incorrect."

        return user, "ok"

    def _hash_password(self, password: str) -> str:
        """Hache un mot de passe avec bcrypt. Retourne le hash en string."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')