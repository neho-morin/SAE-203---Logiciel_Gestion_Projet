# CLAUDE.md

## Projet
Nom du projet : Nudge

Application desktop de suivi de projet avec relance automatique par mail.

## Objectif
Développer une application lourde permettant de :
- gérer des projets
- gérer des tâches
- gérer des responsables
- suivre les échéances
- déclencher des relances automatiques par mail

## Stack technique imposée
- Python 3
- PyQt6
- SQLite
- APScheduler
- smtplib

## Contraintes importantes
- L’application doit être une vraie application desktop, pas une application web.
- Le projet doit être structuré proprement.
- Le code doit être lisible, modulaire et maintenable.
- Il faut séparer l’interface, la logique métier, la base de données et les services.
- Le projet doit rester simple et démontrable dans le cadre d’une SAE.
- Commencer par un MVP fonctionnel avant d’ajouter des options.

## Architecture souhaitée
- `main.py` : point d’entrée
- `ui/` : interface graphique PyQt6
- `database/` : connexion SQLite, schéma, accès aux données
- `services/` : logique métier, mails, scheduler
- `config/` : paramètres de l’application
- `utils/` : fonctions utilitaires

## Règles de développement
- Ne pas tout coder d’un coup.
- Travailler étape par étape.
- Toujours proposer une structure claire avant une grosse modification.
- Toujours privilégier la simplicité.
- Ajouter du code facilement testable.
- Éviter les dépendances inutiles.
- Éviter le code spaghetti.
- Faire des fonctions courtes et explicites.
- Nommer les variables et fichiers clairement.

## Ordre de priorité
1. Base SQLite fonctionnelle
2. Modèles de données
3. CRUD projets
4. CRUD tâches
5. CRUD utilisateurs
6. Interface minimale PyQt6
7. Scheduler de relance
8. Simulation des mails
9. Envoi réel SMTP si le reste fonctionne

## Règles sur les relances
Implémenter au minimum :
- rappel à J-2
- relance le jour J
- relance quotidienne après dépassement si la tâche n’est pas terminée

Au début, les relances peuvent être simulées dans la console avant de brancher un SMTP réel.

## Règles d’interface
- Interface simple
- Priorité au fonctionnel
- Pas besoin de design complexe au début
- Une fenêtre principale avec navigation claire
- Formulaires simples pour ajouter/modifier les données

## Ce qu’il faut éviter
- refaire toute l’architecture sans raison
- mélanger UI et logique métier
- rendre le projet trop ambitieux trop tôt
- ajouter des fonctionnalités hors périmètre SAE sans validation

## Méthode de travail attendue
Quand tu proposes du code :
1. explique brièvement ce que tu fais
2. donne les fichiers à créer ou modifier
3. fournis du code propre
4. garde la cohérence avec l’architecture existante
5. propose la prochaine étape sans l’implémenter automatiquement si elle est grosse