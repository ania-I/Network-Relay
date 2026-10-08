# Network-Relay
Implementation of TCP and HTTP relay mechanisms in Python.

## Exercice 1 : Relai TCP
* Tester `ex1_relai.py` : dans 3 terminaux différents
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