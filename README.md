# Network-Relay
Implementation of TCP and HTTP relay mechanisms in Python.

### Anaïs Chhay & Ania Farez

## Exercice 1 : Relai TCP
* Test simple de `ex1_relai.py` : dans 3 terminaux différents depuis la racine du projet
    + Lancer un server HTTP quelconque
    ```bash
    python3 -m http.server 9000
    ```
    + Lancer le relai avec l'adresse et le port du serveur HTTP
    ```bash
    python3 tcp_relay/ex1_relai.py 127.0.0.1 9000 # adresse du serveur à changer si machines différentes
    ```
    + Exécuter une commande qui fera office de client
    ```bash
    curl http://127.0.0.1:1234/ # adresse du relai à changer si machines différentes
    ```

* Test de plusieurs clients connectés simultanément: dans 3+ terminaux différents depuis la racine du projet
    + Lancer le serveur TCP qui envoie l'heure locale (issu du TME1 - ex2)
    ```bash
    python3 tests/tests_tcp_relay/server.py
    ```
    + Lancer le relai avec l'adresse et le port du serveur
    ```bash
    python3 tcp_relay/ex1_relai.py 127.0.0.1 9000 # adresse du serveur à changer si machines différentes
    ```
    + Lancer un ou plusieurs clients dans différents terminaux (issu du TME1 - ex2)
    ```bash
    python3 tests/tests_tcp_relay/client.py # adresse du relai (par défaut gethostname()) à changer si machines différentes
    ```
    On peut voir affichés les clients connectés/deconnectés au relai.

## Exercice 2 : Relai HTTP

### Cache HTTP
* Tester `ex2_httpcache.py` (port du cache : 1234) : dans 2 terminaux différents depuis la racine du projet
    + Lancer le serveur HTTP (issu du TM1E - ex3)
    ```bash
    python3 tests/tests_http_server/http_server.py # serveur sur le port 8080
    ```
    + Lancer le relai avec l'adresse (en local dans cet exemple) et le port du serveur HTTP
    ```bash
    python3 http_relay/ex2_httpcache.py 127.0.0.1 8080 # adresse du serveur à changer si machines différentes
    ```
    + Ouvrir un navigateur à l'adresse du relai
    ```bash
    http://127.0.0.1:1234/ # adresse du relai à changer si machines différentes
    http://127.0.0.1:1234/index.html
    http://127.0.0.1:1234/chiot.jpg
    http://127.0.0.1:1234/toto # Renvoie erreur 404
    ```
    On peut remarquer sur le terminal du relai et celui du serveur les requêtes effectuées et HIT/MISS sur le cache.

### Sniffeur HTTP
* Tester `ex2_sniffeur_http.py` (port du sniffeur : 1235) : dans 2 terminaux différents depuis la racine du projet
    + Lancer le serveur HTTP
    ```bash
    python3 tests/tests_http_server/http_server.py # serveur sur le port 8080
    ```
    + Lancer le relai avec l'adresse et le port du serveur HTTP
    ```bash
    python3 http_relay/ex2_sniffeur_http.py 127.0.0.1 8080 # adresse du serveur à changer si machines différentes
    ```
    + Ouvrir un navigateur à l'adresse du relai
    ```bash
    http://127.0.0.1:1235/ # adresse du relai à changer si machines différentes
    http://127.0.0.1:1235/index.html
    http://127.0.0.1:1235/chiot.jpg
    http://127.0.0.1:1235/toto # Renvoie erreur 404
    ```
    Les requêtes faites par le client apparaissent dans `/logs/file.log`.

### Censeur HTTP

* Tester `ex2_censure_http.py` (port du censeur : 4567)
```bash
cd tests/tests_http_server/fichiers && python3 -m http.server 8000   # terminal 1
python3 http_relay/ex2_censure_http.py 127.0.0.1 8000  # terminal 2 / adresse à modifier si nécessaire
```

#### Cas à vérifier

| Commande | Attendu |
|---|---|
| `curl -i http://localhost:4567/` | 200 |
| `curl -i http://localhost:4567/public/test.txt` | 200 + contenu |
| `curl -i http://localhost:4567/prive/secret.txt` | 403 Forbidden |
| `curl -i http://localhost:4567/PRIVE/secret.txt` | 403 (insensible à la casse) |

Les IP qui sollicitent un site interdit sont stockées dans `logs/censure.log`.


## Ressources utilisées:
Relai http: https://thepythoncode.com/article/building-a-tcp-proxy-with-python