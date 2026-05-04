from database.db import get_connection


def get_all() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM utilisateurs ORDER BY nom").fetchall()
    return [dict(row) for row in rows]


def get_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def create(nom: str, email: str, role: str = "Autre") -> dict:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO utilisateurs (nom, email, role) VALUES (?, ?, ?)",
        (nom, email, role),
    )
    conn.commit()
    return get_by_id(cur.lastrowid)


def delete(user_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
    conn.commit()
