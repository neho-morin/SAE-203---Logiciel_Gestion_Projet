SCHEMA = """
CREATE TABLE IF NOT EXISTS utilisateurs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    role        TEXT NOT NULL DEFAULT 'Autre',
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS projets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL,
    description TEXT,
    statut      TEXT NOT NULL DEFAULT 'en cours',
    date_fin    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS taches (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
    responsable_id  INTEGER REFERENCES utilisateurs(id) ON DELETE SET NULL,
    titre           TEXT NOT NULL,
    description     TEXT,
    statut          TEXT NOT NULL DEFAULT 'À faire',
    echeance        TEXT,
    priorite        TEXT NOT NULL DEFAULT 'Moyenne',
    created_at      TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS relances (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tache_id    INTEGER NOT NULL REFERENCES taches(id) ON DELETE CASCADE,
    tache_titre TEXT NOT NULL,
    email       TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'manuel',
    mode        TEXT NOT NULL DEFAULT 'Simulation',
    envoyee_le  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS chat_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    role            TEXT    NOT NULL,
    content         TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    conversation_id TEXT    NOT NULL DEFAULT 'default'
);

CREATE TABLE IF NOT EXISTS auth_users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'utilisateur',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    is_active     INTEGER NOT NULL DEFAULT 1
);
"""
