"""
Construction du contexte Nudge à envoyer à OpenClaw.
Partagé entre l'API (api/app.py) et l'interface desktop (nudge.py).
"""
from datetime import date

import services.task_service    as task_service
import services.project_service as project_service

_DAY = {0: "aujourd'hui", 1: "demain", 2: "après-demain"}


def build_nudge_context() -> str:
    today        = date.today()
    all_tasks    = task_service.get_all()
    all_projects = project_service.get_all()

    active = [t for t in all_tasks if t["statut"] != "Terminée"]

    late, upcoming, late_ids, upcoming_ids = [], [], set(), set()
    for t in active:
        try:
            diff = (date.fromisoformat(t["echeance"]) - today).days
        except (ValueError, TypeError):
            continue
        if diff < 0:
            late.append((t, abs(diff)))
            late_ids.add(t["id"])
        elif diff <= 2:
            upcoming.append((t, diff))
            upcoming_ids.add(t["id"])

    priority_only = [
        t for t in active
        if t.get("priorite") in ("Haute", "Critique")
        and t["id"] not in late_ids
        and t["id"] not in upcoming_ids
    ]

    total = len(all_tasks)
    done  = sum(1 for t in all_tasks if t["statut"] == "Terminée")

    def _line(t: dict, extra: str = "") -> str:
        resp = t.get("responsable") or "Non attribué"
        ech  = t.get("echeance") or "—"
        prio = t.get("priorite") or "—"
        stat = t.get("statut") or "—"
        note = f" ({extra})" if extra else ""
        return f"  • {t['titre']} | {resp} | Échéance : {ech}{note} | {prio} | {stat}"

    lines = [f"=== CONTEXTE NUDGE — {today.isoformat()} ===", ""]

    lines.append(f"PROJETS ({len(all_projects)})")
    for p in all_projects[:15]:
        lines.append(f"  • {p['nom']} | Échéance : {p.get('date_fin') or '—'}")

    lines += ["", f"TÂCHES EN RETARD ({len(late)})"]
    lines += [_line(t, f"{d}j de retard") for t, d in late[:15]] or ["  Aucune."]

    lines += ["", f"TÂCHES PROCHES ≤ 2 jours ({len(upcoming)})"]
    lines += [_line(t, _DAY.get(d, f"dans {d}j")) for t, d in upcoming[:15]] or ["  Aucune."]

    lines += ["", f"TÂCHES PRIORITAIRES EN COURS ({len(priority_only)})"]
    lines += [_line(t) for t in priority_only[:15]] or ["  Aucune."]

    lines += [
        "",
        "RÉSUMÉ",
        f"  Total : {total}  |  Terminées : {done}  |  En retard : {len(late)}"
        f"  |  Proches : {len(upcoming)}  |  Prioritaires actives : {len(priority_only)}",
    ]

    return "\n".join(lines)
