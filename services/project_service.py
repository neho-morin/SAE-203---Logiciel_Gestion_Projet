from database.db import get_connection


def get_all() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projets ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


def get_by_id(project_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM projets WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None


def create(nom: str, description: str = "", date_fin: str = "") -> dict:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO projets (nom, description, date_fin) VALUES (?, ?, ?)",
        (nom, description, date_fin),
    )
    conn.commit()
    return get_by_id(cur.lastrowid)


def update(project_id: int, nom: str, description: str = "", date_fin: str = "") -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE projets SET nom = ?, description = ?, date_fin = ? WHERE id = ?",
        (nom, description, date_fin, project_id),
    )
    conn.commit()


def delete(project_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM projets WHERE id = ?", (project_id,))
    conn.commit()
