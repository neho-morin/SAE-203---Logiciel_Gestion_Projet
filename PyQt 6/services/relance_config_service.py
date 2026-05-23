import json
import os
from datetime import date

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".nudge_relance_config.json")

_DEFAULTS: dict = {
    "scope": "late",
    "days_ahead": 3,
    "statuts": [],
    "project_id": None,
    "priorites": [],
}


def _parse_days(value) -> int:
    """Convertit days_ahead en int — rétrocompatibilité avec les anciennes valeurs texte."""
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, (float,)):
        return max(0, int(value))
    if isinstance(value, str):
        import re
        m = re.search(r'\d+', value)
        return int(m.group()) if m else _DEFAULTS["days_ahead"]
    return _DEFAULTS["days_ahead"]


def load() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "days_ahead" in data:
                data["days_ahead"] = _parse_days(data["days_ahead"])
            return {**_DEFAULTS, **data}
        except Exception:
            pass
    return dict(_DEFAULTS)


def save(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_tasks_for_relance(config: dict) -> list[dict]:
    import services.task_service as task_service

    all_tasks  = task_service.get_all()
    today      = date.today()
    scope      = config.get("scope", "late")
    days_ahead = config.get("days_ahead", 3)
    statuts    = config.get("statuts") or []
    project_id = config.get("project_id")
    priorites  = config.get("priorites") or []

    result = []
    for t in all_tasks:
        if t["statut"] == "Terminée":
            continue
        if project_id is not None and t.get("project_id") != project_id:
            continue
        if priorites and t.get("priorite") not in priorites:
            continue
        if statuts and t.get("statut") not in statuts:
            continue

        try:
            diff = (date.fromisoformat(t["echeance"]) - today).days
        except (ValueError, TypeError):
            diff = None

        if scope == "late":
            if diff is None or diff >= 0:
                continue
        elif scope == "today":
            if diff is None or diff != 0:
                continue
        elif scope == "days":
            if diff is None or diff < 0 or diff > days_ahead:
                continue
        # scope == "all": aucun filtre de date supplémentaire

        result.append(t)

    return result
