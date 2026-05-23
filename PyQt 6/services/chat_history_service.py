from database.db import get_connection


def get_all(conversation_id: str = "default") -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_history "
        "WHERE conversation_id = ? ORDER BY id",
        (conversation_id,),
    ).fetchall()
    return [{"role": r["role"], "content": r["content"], "created_at": r["created_at"]} for r in rows]


def add(role: str, content: str, conversation_id: str = "default") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (role, content, conversation_id) VALUES (?, ?, ?)",
        (role, content, conversation_id),
    )
    conn.commit()


def clear(conversation_id: str = "default") -> None:
    conn = get_connection()
    conn.execute("DELETE FROM chat_history WHERE conversation_id = ?", (conversation_id,))
    conn.commit()
