
CREATE TABLE Utilisateur (
    id_utilisateur TEXT PRIMARY KEY,
    nom_utilisateur VARCHAR(50) NOT NULL,
    prénom_utilisateur VARCHAR(50),
    email VARCHAR(255),
    rôle VARCHAR(30)
);


CREATE TABLE Projet (
    id_projet TEXT PRIMARY KEY,
    nom_projet VARCHAR(100) NOT NULL,
    description_projet TEXT,
    date_debut DATE,
    date_fin DATE,
    status_projet VARCHAR(20),
    id_utilisateur TEXT NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);


CREATE TABLE Tâche (
    id_tâche TEXT PRIMARY KEY,
    description_tâche TEXT,
    date_creation DATETIME,
    date_échéance DATETIME,
    priorité TEXT CHECK(priorité IN ('basse', 'moyenne', 'haute')),
    status VARCHAR(20),
    id_projet TEXT NOT NULL,
    id_utilisateur TEXT NOT NULL,
    FOREIGN KEY (id_projet) REFERENCES Projet(id_projet),
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);


CREATE TABLE Relance (
    id_relance TEXT PRIMARY KEY,
    date_envor DATETIME,
    type_relance VARCHAR(20),
    contenu TEXT,
    id_tâche TEXT NOT NULL,
    id_utilisateur TEXT NOT NULL,
    FOREIGN KEY (id_tâche) REFERENCES Tache(id_tâche),
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);
