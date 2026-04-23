# ✳ Nudge — Suivi de projet

> **Pilotez vos projets. Zéro oubli, zéro retard.**

Nudge est un logiciel de bureau permettant de centraliser le suivi de projets, piloter les tâches, identifier les échéances et envoyer des relances par mail.

---

## 📋 Prérequis

- **Windows 10/11** ou **Linux**
- **Python 3.12+** → [Télécharger Python](https://www.python.org/downloads/)
- **PyQt6** (bibliothèque d'interface graphique)

---

## 🚀 Installation et lancement

### Option 1 — Lancer depuis le code source

**1. Cloner ou télécharger le projet**
```
git clone https://github.com/votre-repo/nudge.git
cd nudge
```
Ou simplement télécharger `nudge.py` et le placer dans un dossier.

**2. Installer les dépendances**
```
pip install PyQt6
```

**3. Lancer l'application**
```
python nudge.py
```

---

### Option 2 — Générer un exécutable (.exe)

**1. Installer PyInstaller**
```
pip install pyinstaller
```

**2. Générer l'exécutable**

Dans le dossier contenant `nudge.py` :
```
pyinstaller --onefile --windowed --name Nudge nudge.py
```

**3. Récupérer l'exécutable**

Le fichier `Nudge.exe` sera généré dans le dossier `dist/`.  
Double-cliquez dessus pour lancer l'application, aucune installation Python requise.

---

## 🖥️ Utilisation

### Premier lancement
Un guide de démarrage s'affiche automatiquement à la première ouverture.  
Il peut être relu à tout moment via le bouton **"Guide"** en haut à droite.

### Créer un projet
1. Cliquez sur **"+ Ajouter un projet"** dans la barre latérale gauche
2. Renseignez le nom, une description (optionnel) et la date de fin prévisionnelle
3. Le projet apparaît dans la sidebar et sur l'écran d'accueil

### Ajouter des responsables
1. Cliquez sur **"+ Ajouter un responsable"** dans la barre latérale
2. Renseignez le nom, l'email et le rôle
3. Les responsables sont ensuite disponibles lors de la création de tâches

### Créer une tâche
1. Sélectionnez un projet
2. Cliquez sur **"+ Ajouter une tâche"**
3. Renseignez : titre, description, responsable, échéance, priorité et statut

### Gérer les tâches
| Action | Comment |
|--------|---------|
| Voir les détails | **Double-clic** sur une ligne |
| Changer le statut | Cliquer directement sur le badge statut dans la table |
| Changer le responsable | Cliquer directement sur le nom dans la table |
| Modifier tous les champs | Bouton **✏️** sur la ligne |
| Supprimer | Bouton **🗑** sur la ligne (confirmation demandée) |

### Statuts automatiques
L'application détecte automatiquement :
- **Terminée proche** — échéance dans 2 jours ou moins
- **En retard** — échéance dépassée et tâche non terminée

### Envoyer une relance par mail
1. Cliquez sur **"📧 Relancer par mail"** (cible la première tâche en retard du projet actif)
2. Ou cliquez sur le bouton **📧** directement sur une ligne en retard
3. Vérifiez/modifiez le destinataire et le message
4. Choisissez le mode **Simulation** (démo) ou **Réel** (envoi SMTP)
5. L'historique des relances est conservé dans la barre latérale

### Navigation
- Cliquez sur le logo **✳ Nudge** en haut à gauche pour revenir à l'accueil
- L'accueil affiche toutes vos cartes projets avec leur avancement

---

## 📊 Tableau de bord

Le panneau de droite affiche en temps réel :
- Nombre de projets et tâches
- Pourcentage d'avancement global (donut)
- Nombre de tâches en retard, à faire, proches de l'échéance

---

## 📁 Structure du projet

```
nudge/
├── nudge.py          # Application principale
├── README.md         # Ce fichier
└── dist/
    └── Nudge.exe     # Exécutable généré (après PyInstaller)
```

---

## ⚠️ Notes importantes

- Les données sont **stockées en mémoire** uniquement (pas de base de données encore). Elles seront perdues à la fermeture de l'application jusqu'à l'intégration de SQLite.
- Le mode **Simulation** est recommandé pour les démonstrations — aucun mail réel n'est envoyé.
- Le fichier `.nudge_config.json` est créé dans votre dossier utilisateur pour mémoriser si l'onboarding a été vu.

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Langage | Python 3.12 |
| Interface graphique | PyQt6 |
| Base de données | SQLite *(à venir)* |
| Relances automatiques | APScheduler *(à venir)* |
| Envoi mail | smtplib *(à venir)* |

---

## 👥 Équipe — Groupe 6

| Membre | Rôle |
|--------|------|
| Jason Gironcel | Responsable technique |
| Hugo Grimoult | Développeur Full Stack |
| Antoine Landry | Chef de projet |
| Lucas Mussard | Directeur artistique |
| Ného Morin | — |

---

*SAE 2.03 — IUT de Saint-Pierre, La Réunion*
