from database.db import get_connection

_SELECT = """
    SELECT
        t.id,
        t.project_id,
        t.responsable_id,
        t.titre,
        t.description,
        t.statut,
        t.echeance,
        t.priorite,
        t.created_at,
        u.nom   AS responsable,
        u.email AS responsable_email
    FROM taches t
    LEFT JOIN utilisateurs u ON t.responsable_id = u.id
"""


def _to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


def get_all() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(_SELECT + "ORDER BY t.echeance ASC").fetchall()
    return [_to_dict(r) for r in rows]


def get_by_project(project_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        _SELECT + "WHERE t.project_id = ? ORDER BY t.echeance ASC",
        (project_id,),
    ).fetchall()
    return [_to_dict(r) for r in rows]


def get_by_id(task_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(_SELECT + "WHERE t.id = ?", (task_id,)).fetchone()
    return _to_dict(row) if row else None


def create(project_id: int, titre: str, description: str = "", responsable_id=None,
           echeance: str = "", priorite: str = "Moyenne", statut: str = "À faire") -> dict:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO taches
               (project_id, titre, description, responsable_id, echeance, priorite, statut)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (project_id, titre, description, responsable_id, echeance, priorite, statut),
    )
    conn.commit()
    return get_by_id(cur.lastrowid)


def update(task_id: int, titre: str, description: str = "", responsable_id=None,
           echeance: str = "", priorite: str = "Moyenne", statut: str = "À faire") -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE taches
           SET titre=?, description=?, responsable_id=?, echeance=?, priorite=?, statut=?
           WHERE id=?""",
        (titre, description, responsable_id, echeance, priorite, statut, task_id),
    )
    conn.commit()


def update_statut(task_id: int, statut: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE taches SET statut = ? WHERE id = ?", (statut, task_id))
    conn.commit()


def update_responsable(task_id: int, responsable_id) -> None:
    conn = get_connection()
    conn.execute("UPDATE taches SET responsable_id = ? WHERE id = ?", (responsable_id, task_id))
    conn.commit()


def delete(task_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM taches WHERE id = ?", (task_id,))
    conn.commit()
