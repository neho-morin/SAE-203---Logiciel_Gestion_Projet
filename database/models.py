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
"""
