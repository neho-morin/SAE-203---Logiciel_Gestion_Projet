Voici les étapes pour créer l'application Nudge pour Linux :

La bonne façon pour Linux
Vous aurez besion : 
  - Du dossier SQLite
  - Du dossier PyQt6
    
La personne sur Linux doit relancer la commande complète dans le répertoire PyQt6 :
pyinstaller --onefile --windowed --name Nudge --icon=icon.ico --add-data "database:database" --add-data "services:services" --add-data "config:config" nudge.py
