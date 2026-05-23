"""
Résolution des chemins — compatible développement et exécutable PyInstaller.

Usage :
    from config.paths import get_env_path, get_db_path, get_user_data_dir
"""
import sys
from pathlib import Path

IS_FROZEN: bool = getattr(sys, "frozen", False)

# En mode frozen, sys._MEIPASS contient les fichiers du bundle.
# En dev, on remonte depuis ce fichier : config/paths.py → config/ → PyQt 6/
if IS_FROZEN:
    _BUNDLE_ROOT: Path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
else:
    _BUNDLE_ROOT: Path = Path(__file__).resolve().parent.parent  # PyQt 6/


def get_user_data_dir() -> Path:
    """~/.nudge/ — dossier utilisateur persistant, toujours accessible en écriture."""
    d = Path.home() / ".nudge"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_env_path() -> Path:
    """
    .env utilisateur.
    - Dev    : racine du projet (parent de PyQt 6/) si elle existe, sinon ~/.nudge/.env
    - Frozen : ~/.nudge/.env  (hors du bundle, modifiable par l'utilisateur)
    """
    if IS_FROZEN:
        return get_user_data_dir() / ".env"
    project_root = _BUNDLE_ROOT.parent
    dev_env = project_root / ".env"
    if dev_env.exists():
        return dev_env
    return get_user_data_dir() / ".env"


def get_db_path() -> Path:
    """
    nudge.db — base SQLite.
    - Dev    : ~/nudge.db  (rétrocompatibilité)
    - Frozen : ~/.nudge/nudge.db
    """
    if IS_FROZEN:
        return get_user_data_dir() / "nudge.db"
    return Path.home() / "nudge.db"


def get_relance_config_path() -> Path:
    """Config JSON des relances."""
    if IS_FROZEN:
        return get_user_data_dir() / "relance_config.json"
    return Path.home() / ".nudge_relance_config.json"


def get_nudge_config_path() -> Path:
    """Config JSON onboarding / préférences UI."""
    if IS_FROZEN:
        return get_user_data_dir() / "nudge_config.json"
    return Path.home() / ".nudge_config.json"
