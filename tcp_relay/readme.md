Tests — Relais TCP

 tester du relai TCP 

1. Test de communication client-serveur
vérifie que le relais transmet correctement les données dans les deux sens.

Configuration
Serveur TCP : machine virtuelle Linux.
Client TCP : machine hôte Windows.
Relais TCP : machine hôte Windows.
Port d'écoute du relais : 1234.
Adresse du serveur : 192.168.112.131.
Port du serveur : 1234.
Exécution

Ouvrir trois terminaux.

Terminal 1 — Serveur (dans la VM Linux)

python3 serverTest.py

Terminal 2 — Relais (sur Windows)

Depuis la racine du projet :

python tcp_relay/relai_oo.py 192.168.112.131 1234

Terminal 3 — Client (sur Windows)

python ClientTest.py

Adapter le chemin du client à son emplacement réel dans le projet.

Résultat attendu
Le relais accepte la connexion du client.
Le serveur reçoit les requêtes envoyées par le client.
Le client reçoit les réponses du serveur via le relais.

Test réussi

2. Test entre machines différentes
vérifie le fonctionnement du relais sur le réseau.
Exécution
Lancer le serveur sur une machine.
Lancer le relais sur une autre machine, en indiquant l'adresse IP du serveur.
Lancer le client sur une troisième machine, en indiquant l'adresse IP du relais et son port 1234.
Résultat attendu
Les requêtes du client arrivent bien au serveur via le relais, et les réponses du serveur sont retransmises au client.

3. Test de plusieurs clients simultanés

Objectif : vérifier que le relais peut gérer plusieurs connexions clientes en parallèle.

Exécution
Laisser le serveur et le relais en fonctionnement.
Ouvrir trois terminaux clients.
Lancer le client dans chacun :
python ClientTest.py
Vérifier les connexions et les échanges dans le terminal du relais et dans celui du serveur.