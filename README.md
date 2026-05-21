# Nudge — Logiciel de Gestion de Projet

Application desktop de suivi de projet avec relance automatique par mail.

Développée avec Python 3, PyQt6 et SQLite dans le cadre d'une SAE.

---

## Fonctionnalités

- Gestion de projets, tâches et responsables
- Suivi des échéances avec détection automatique des retards
- Relances par mail (mode simulation ou envoi SMTP réel)
- Scheduler automatique : rappel à J-2, relance le jour J, relance quotidienne après dépassement
- Interface desktop complète avec tableau de bord

---

## Structure du projet

```
SAE-203---Logiciel_Gestion_Projet/
├── PyQt 6/
│   ├── nudge.py          # Point d'entrée de l'application
│   ├── icon.ico          # Icône de l'application
│   ├── config/           # Paramètres (SMTP, chemin BDD)
│   ├── database/         # Connexion SQLite et schéma
│   └── services/         # Logique métier, mails, scheduler
├── Cr. .exe for Windows/
│   └── Nudge.spec        # Fichier de build PyInstaller
└── SQLite/               # Outils SQLite (Windows)
```

La base de données est créée automatiquement dans le dossier personnel de l'utilisateur (`~/nudge.db`).

---

## Version Windows

### Option 1 — Télécharger l'exécutable (recommandé)

Un exécutable `.exe` prêt à l'emploi est disponible au lien suivant :

**[Télécharger Nudge.exe (Google Drive)](https://drive.google.com/file/d/1nLW7ekrIV66FOQ9B3nsrvqkBwCamNcdV/view?usp=sharing)**

1. Téléchargez `Nudge.exe`
2. Double-cliquez sur le fichier pour lancer l'application
3. Aucune installation requise

> Windows peut afficher un avertissement SmartScreen au premier lancement. Cliquez sur **"Informations complémentaires"** puis **"Exécuter quand même"**.

---

### Option 2 — Lancer depuis les sources (Windows)

**Prérequis :**

- Python 3.11 ou supérieur — [python.org](https://www.python.org/downloads/)
- Cocher **"Add Python to PATH"** lors de l'installation

**Installation et lancement :**

Ouvrez un terminal dans le dossier `PyQt 6/` et exécutez :

```bat
pip install PyQt6 python-dotenv apscheduler
python nudge.py
```

---

### Option 3 — Compiler l'exécutable soi-même (Windows)

Pour générer un nouveau `.exe` depuis les sources :

```bat
pip install pyinstaller PyQt6 python-dotenv apscheduler
pyinstaller --onefile --windowed --name Nudge --icon=icon.ico --add-data "database;database" --add-data "services;services" --add-data "config;config" nudge.py
```

> Sur Windows, le séparateur dans `--add-data` est un point-virgule `;`.

L'exécutable généré se trouve dans le dossier `dist/`.

---

## Version Linux

### Option 1 — Lancer depuis les sources (recommandé)

**Prérequis :**

- Python 3.11 ou supérieur
- pip

**Installation des dépendances :**

```bash
pip install PyQt6 python-dotenv apscheduler
```

Sur certaines distributions, il peut être nécessaire d'installer des dépendances système pour PyQt6 :

```bash
# Ubuntu / Debian
sudo apt install python3-pyqt6 libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install python3-qt6

# Arch Linux
sudo pacman -S python-pyqt6
```

**Lancement :**

```bash
cd "PyQt 6"
python nudge.py
```

---

### Option 2 — Compiler un exécutable Linux

Pour générer un binaire autonome exécutable sur Linux :

```bash
pip install pyinstaller PyQt6 python-dotenv apscheduler
cd "PyQt 6"
pyinstaller --onefile --windowed --name Nudge --icon=icon.ico --add-data "database:database" --add-data "services:services" --add-data "config:config" nudge.py
```

> Sur Linux, le séparateur dans `--add-data` est un deux-points `:`.

L'exécutable généré se trouve dans le dossier `dist/`. Pour le lancer :

```bash
./dist/Nudge
```

> L'exécutable généré sur Linux ne fonctionnera que sur Linux. Il n'est pas compatible Windows, et inversement.

---

## Configuration de l'envoi de mail

Par défaut, l'application fonctionne en **mode simulation** : les mails sont affichés dans la console mais ne sont pas réellement envoyés.

Pour activer l'envoi réel, deux méthodes sont disponibles :

### Méthode 1 — Via l'interface graphique

Cliquez sur le bouton **"Config. mail"** dans la barre supérieure de l'application et renseignez :

- Serveur SMTP (ex : `smtp.gmail.com`)
- Port (ex : `587`)
- Email expéditeur
- Mot de passe d'application

### Méthode 2 — Via le fichier `.env`

Créez un fichier `.env` dans le dossier `PyQt 6/` avec le contenu suivant :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
MAIL_SIMULATE=false
```

> **Pour Gmail :** utilisez un mot de passe d'application à 16 caractères (pas votre mot de passe habituel).  
> Générez-le sur : [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)  
> La validation en deux étapes doit être activée sur le compte.

---

## Scheduler automatique

Le scheduler démarre automatiquement avec l'application et vérifie chaque jour à **08h00** les tâches à relancer :

| Déclencheur | Action |
|---|---|
| J-2 avant l'échéance | Rappel envoyé au responsable |
| Jour J | Relance le jour de l'échéance |
| Après dépassement | Relance quotidienne tant que la tâche n'est pas terminée |

---

## Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python 3 | Langage principal |
| PyQt6 | Interface graphique desktop |
| SQLite | Base de données locale |
| APScheduler | Scheduler de relances automatiques |
| smtplib | Envoi de mails SMTP |
| python-dotenv | Lecture du fichier `.env` |
