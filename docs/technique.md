# ⚙️ Documentation technique

## 🏗️ Architecture

Architecture en couches :
[ Interface PyQt ]
↓
[ Logique métier ]
↓
[ Base SQLite ]
↓
[ Services (SMTP / Scheduler) ]


---

## 🔁 Flux de fonctionnement

1. Création projet
2. Ajout tâches
3. Enregistrement en base
4. Analyse des échéances
5. Déclenchement relance
6. Envoi ou simulation mail
7. Historisation

---

## 🛠️ Choix techniques

| Élément | Choix |
|--------|------|
| Langage | Python 3 |
| Interface | PyQt6 |
| Base de données | SQLite |
| Mail | smtplib |
| Scheduler | APScheduler |

---

## 🗄️ Modélisation des données

### Projet
- id
- nom
- description
- date_debut
- date_fin
- statut

### Tâche
- id
- nom
- description
- date_echeance
- priorité
- statut
- id_projet
- id_responsable

### Utilisateur
- id
- nom
- email

### Relance
- id
- date
- type
- contenu
- id_tache

### Relations
- 1 projet → N tâches
- 1 utilisateur → N tâches
- 1 tâche → N relances

---

## 📬 Système de relance

### Règles

| Situation | Action |
|----------|------|
| J-2 | rappel |
| Jour J | relance |
| J+1 | relance quotidienne |
| long retard | relance hebdomadaire |

### Contenu mail
- projet
- tâche
- échéance
- statut
- message

---

## 🧠 Bonus (optionnel)

- IA pour reformuler les mails
- simulation d’envoi mail

