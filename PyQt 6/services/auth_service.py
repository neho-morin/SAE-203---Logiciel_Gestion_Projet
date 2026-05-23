"""
Service d'authentification Nudge.

═══════════════════════════════════════════════════════════════════════════════
PHASE ACTUELLE  →  stub passif
═══════════════════════════════════════════════════════════════════════════════
L'application fonctionne sans fenêtre de connexion.
La session active est toujours un admin fictif tant que
NUDGE_AUTH_ENABLED=false (valeur par défaut).

Pour activer l'authentification réelle :
  1. Mettre NUDGE_AUTH_ENABLED=true dans le .env
  2. Ajouter un LoginDialog dans nudge.py
  3. Appeler auth_service.login_with_db(username, password) au démarrage
  4. Passer la session à MainWindow et conditionner les boutons avec .can()

═══════════════════════════════════════════════════════════════════════════════
GUIDE D'INTÉGRATION FUTURE (nudge.py)
═══════════════════════════════════════════════════════════════════════════════

    # Au démarrage, avant d'afficher MainWindow :
    import services.auth_service as auth_service
    if auth_service.AUTH_ENABLED:
        session = show_login_dialog()          # à implémenter
        if session is None:
            sys.exit(0)
    else:
        session = auth_service.current_session()

    # Dans MainWindow, conditionner les boutons :
    from config.permissions import SEND_REMINDERS, CONFIGURE_SMTP
    self.relance_btn.setVisible(session.can(SEND_REMINDERS))
    config_btn.setVisible(session.can(CONFIGURE_SMTP))

    # Dans on_relance_global() :
    if not auth_service.can(SEND_REMINDERS):
        QMessageBox.warning(self, "Accès refusé", "Vous n'avez pas la permission d'envoyer des relances.")
        return
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Optional

from config.permissions import ROLE_ADMIN, ROLE_PERMISSIONS, has_permission


# ── Session utilisateur ───────────────────────────────────────────────────────

@dataclass
class UserSession:
    user_id:     int
    username:    str
    role:        str
    permissions: frozenset[str] = field(default_factory=frozenset)

    def can(self, permission: str) -> bool:
        """Raccourci : vérifie si cette session possède une permission."""
        return permission in self.permissions

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


# ── État global ───────────────────────────────────────────────────────────────

# Contrôlé par NUDGE_AUTH_ENABLED dans le .env
AUTH_ENABLED: bool = os.getenv("NUDGE_AUTH_ENABLED", "false").lower() == "true"

# Session stub (admin fictif) utilisée quand AUTH_ENABLED=false
_STUB_SESSION = UserSession(
    user_id=0,
    username="admin_stub",
    role=ROLE_ADMIN,
    permissions=ROLE_PERMISSIONS[ROLE_ADMIN],
)

_current_session: Optional[UserSession] = _STUB_SESSION


# ── API publique ──────────────────────────────────────────────────────────────

def current_session() -> Optional[UserSession]:
    """Retourne la session active. Toujours admin_stub si AUTH_ENABLED=false."""
    if not AUTH_ENABLED:
        return _STUB_SESSION
    return _current_session


def is_authenticated() -> bool:
    """Retourne True si une session est active."""
    return current_session() is not None


def can(permission: str) -> bool:
    """
    Raccourci global : la session active possède-t-elle cette permission ?
    Utilisable sans référence à la session :
        if auth_service.can(SEND_REMINDERS): ...
    """
    session = current_session()
    return session.can(permission) if session else False


def logout() -> None:
    """Invalide la session active."""
    global _current_session
    _current_session = None


# ── Mots de passe ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Retourne un hash PBKDF2-SHA256 avec sel aléatoire (format 'salt_hex:dk_hex')."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """Vérifie un mot de passe contre un hash stocké par hash_password()."""
    try:
        salt_hex, dk_hex = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
        return dk.hex() == dk_hex
    except Exception:
        return False


# ── Authentification BDD ──────────────────────────────────────────────────────

def login_with_db(username: str, password: str) -> Optional[UserSession]:
    """
    Tente de connecter un utilisateur depuis auth_users.
    Retourne une UserSession si succès, None sinon.
    Met à jour _current_session en cas de succès.

    À appeler depuis LoginDialog (à implémenter dans nudge.py).
    """
    global _current_session
    from database.db import get_connection

    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, role FROM auth_users "
        "WHERE username = ? AND is_active = 1",
        (username,),
    ).fetchone()

    if row is None:
        return None
    if not verify_password(password, row["password_hash"]):
        return None

    role = row["role"]
    session = UserSession(
        user_id=row["id"],
        username=row["username"],
        role=role,
        permissions=ROLE_PERMISSIONS.get(role, frozenset()),
    )
    _current_session = session
    return session


# ── Premier lancement ─────────────────────────────────────────────────────────

def needs_first_admin() -> bool:
    """Retourne True si aucun compte n'existe encore dans auth_users."""
    try:
        from database.db import get_connection
        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) FROM auth_users").fetchone()[0]
        return count == 0
    except Exception:
        return False


def create_first_admin(username: str, password: str) -> bool:
    """
    Crée le compte admin initial si aucun utilisateur n'existe.
    Retourne True si créé, False si un compte existe déjà.
    """
    if not needs_first_admin():
        return False
    from database.db import get_connection
    conn = get_connection()
    conn.execute(
        "INSERT INTO auth_users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), ROLE_ADMIN),
    )
    conn.commit()
    return True


# ── CRUD utilisateurs ─────────────────────────────────────────────────────────

def get_all_users() -> list[dict]:
    """Retourne tous les comptes auth_users."""
    from database.db import get_connection
    rows = get_connection().execute(
        "SELECT id, username, role, is_active, created_at FROM auth_users ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


def create_user(username: str, password: str, role: str) -> tuple[bool, str]:
    """
    Crée un nouveau compte.
    Retourne (True, '') si succès, (False, message_erreur) sinon.
    """
    if not username.strip():
        return False, "L'identifiant est obligatoire."
    if len(password) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."
    try:
        from database.db import get_connection
        conn = get_connection()
        conn.execute(
            "INSERT INTO auth_users (username, password_hash, role) VALUES (?, ?, ?)",
            (username.strip(), hash_password(password), role),
        )
        conn.commit()
        return True, ""
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return False, f"L'identifiant « {username} » est déjà utilisé."
        return False, str(exc)


def update_user_role(user_id: int, role: str) -> None:
    """Change le rôle d'un compte."""
    from database.db import get_connection
    conn = get_connection()
    conn.execute("UPDATE auth_users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()


def set_user_active(user_id: int, is_active: bool) -> None:
    """Active ou désactive un compte."""
    from database.db import get_connection
    conn = get_connection()
    conn.execute("UPDATE auth_users SET is_active = ? WHERE id = ?", (1 if is_active else 0, user_id))
    conn.commit()


def delete_user(user_id: int) -> None:
    """Supprime définitivement un compte."""
    from database.db import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM auth_users WHERE id = ?", (user_id,))
    conn.commit()
