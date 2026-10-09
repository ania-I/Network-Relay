# Network-Relay
Implementation of TCP and HTTP relay mechanisms in Python.

## Exercice 1 : Relai TCP
* Tester `ex1_relai.py` : dans 3 terminaux différents depuis la racine du projet
    + Lancer un server HTTP quelconque
    ```bash
    python3 -m http.server 9000
    ```
    + Lancer le relai avec l'adresse et le port du serveur HTTP
    ```bash
    python3 tcp_relay/ex1_relai.py 127.0.0.1 9000
    ```
    + Exécuter une commande qui fera office de client
    ```bash
    curl http://127.0.0.1:1234/
    ```

## Exercice 2 : Relai HTTP avec cache
* Tester `ex2_httpcache.py` : dans 2 terminaux différents depuis la racine du projet
    + Lancer le serveur HTTP (issu du TM1 - ex3)
    ```bash
    python3 tests/test_http_server/http_server.py 
    ```
    + Lancer le relai avec l'adresse (en local dans cet exemple) et le port du serveur HTTP
    ```bash
    python3 http_relay/ex2_httpcache.py 127.0.0.1 8080
    ```
    + Ouvrir un navigateur à l'adresse du relai
    ```bash
    http://127.0.0.1:1234/
    http://127.0.0.1:1234/index.html
    http://127.0.0.1:1234/chiot.jpg
    http://127.0.0.1:1234/toto # Renvoie erreur 404
    ```
    On peut remarquer sur le terminal du relai et celui du serveur les requêtes effectuées et HIT/MISS sur le cache.