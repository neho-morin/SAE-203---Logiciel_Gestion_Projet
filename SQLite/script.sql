
CREATE TABLE Utilisateur (
    id_utilisateur TEXT PRIMARY KEY,
    nom_utilisateur VARCHAR(50) NOT NULL,
    prenom_utilisateur VARCHAR(50),
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


CREATE TABLE Tache (
    id_tache TEXT PRIMARY KEY,
    description_tache TEXT,
    date_creation DATETIME,
    date_echeance DATETIME,
    priorite TEXT CHECK(priorite IN ('basse', 'moyenne', 'haute')),
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
    id_tache TEXT NOT NULL,
    id_utilisateur TEXT NOT NULL,
    FOREIGN KEY (id_tache) REFERENCES Tache(id_tache),
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
);