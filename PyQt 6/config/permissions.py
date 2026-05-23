"""
Définition des permissions et rôles de l'application Nudge.

Ce module est entièrement passif : il déclare les permissions et la matrice
rôles→permissions. Aucun effet de bord, aucune connexion à la BDD.

Usage futur (dans nudge.py) :
    from config.permissions import has_permission, SEND_REMINDERS
    if has_permission(session.role, SEND_REMINDERS):
        relance_btn.setEnabled(True)
"""
from __future__ import annotations

# ── Permissions ───────────────────────────────────────────────────────────────

# Projets
VIEW_PROJECTS   = "view_projects"
CREATE_PROJECT  = "create_project"
EDIT_PROJECT    = "edit_project"
DELETE_PROJECT  = "delete_project"

# Tâches
VIEW_TASKS          = "view_tasks"
CREATE_TASK         = "create_task"
EDIT_ALL_TASKS      = "edit_all_tasks"   # modifier les tâches de tous
EDIT_OWN_TASKS      = "edit_own_tasks"   # modifier uniquement ses propres tâches
DELETE_TASK         = "delete_task"
ASSIGN_TASK         = "assign_task"
CHANGE_TASK_STATUS  = "change_task_status"

# Relances
SEND_REMINDERS      = "send_reminders"
CONFIGURE_REMINDERS = "configure_reminders"

# Mail
CONFIGURE_SMTP = "configure_smtp"

# Assistant IA
USE_AI_ASSISTANT = "use_ai_assistant"
CLEAR_AI_HISTORY = "clear_ai_history"

# Administration
MANAGE_USERS = "manage_users"
MANAGE_ROLES = "manage_roles"

# Données
EXPORT_DATA = "export_data"
IMPORT_DATA = "import_data"

# Ensemble complet (utilisé par le rôle admin)
ALL_PERMISSIONS: frozenset[str] = frozenset({
    VIEW_PROJECTS, CREATE_PROJECT, EDIT_PROJECT, DELETE_PROJECT,
    VIEW_TASKS, CREATE_TASK, EDIT_ALL_TASKS, EDIT_OWN_TASKS,
    DELETE_TASK, ASSIGN_TASK, CHANGE_TASK_STATUS,
    SEND_REMINDERS, CONFIGURE_REMINDERS,
    CONFIGURE_SMTP,
    USE_AI_ASSISTANT, CLEAR_AI_HISTORY,
    MANAGE_USERS, MANAGE_ROLES,
    EXPORT_DATA, IMPORT_DATA,
})

# ── Rôles ─────────────────────────────────────────────────────────────────────

ROLE_ADMIN       = "admin"
ROLE_CHEF_PROJET = "chef_projet"
ROLE_UTILISATEUR = "utilisateur"
ROLE_LECTEUR     = "lecteur"

ALL_ROLES: tuple[str, ...] = (
    ROLE_ADMIN,
    ROLE_CHEF_PROJET,
    ROLE_UTILISATEUR,
    ROLE_LECTEUR,
)

# ── Matrice rôle → permissions ────────────────────────────────────────────────
#
# Règles métier :
#  - EDIT_ALL_TASKS  : modifier les tâches de n'importe qui
#  - EDIT_OWN_TASKS  : modifier uniquement ses propres tâches
#  - SEND_REMINDERS  : réservé à admin et chef de projet
#  - CONFIGURE_SMTP  : réservé à admin
#  - MANAGE_USERS    : réservé à admin
#  - CLEAR_AI_HISTORY: admin et chef de projet
#
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {

    ROLE_ADMIN: ALL_PERMISSIONS,

    ROLE_CHEF_PROJET: frozenset({
        VIEW_PROJECTS, CREATE_PROJECT, EDIT_PROJECT,
        VIEW_TASKS, CREATE_TASK, EDIT_ALL_TASKS, EDIT_OWN_TASKS,
        DELETE_TASK, ASSIGN_TASK, CHANGE_TASK_STATUS,
        SEND_REMINDERS, CONFIGURE_REMINDERS,
        USE_AI_ASSISTANT, CLEAR_AI_HISTORY,
        EXPORT_DATA,
    }),

    ROLE_UTILISATEUR: frozenset({
        VIEW_PROJECTS,
        VIEW_TASKS, CREATE_TASK, EDIT_OWN_TASKS, CHANGE_TASK_STATUS,
        USE_AI_ASSISTANT,
    }),

    ROLE_LECTEUR: frozenset({
        VIEW_PROJECTS,
        VIEW_TASKS,
    }),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def has_permission(role: str, permission: str) -> bool:
    """Retourne True si *role* possède *permission*."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def permissions_for(role: str) -> frozenset[str]:
    """Retourne l'ensemble des permissions d'un rôle."""
    return ROLE_PERMISSIONS.get(role, frozenset())
