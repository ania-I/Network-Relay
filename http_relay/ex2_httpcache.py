import socket
import sys
import threading

RELAY_PORT = 1234

# Cache en mémoire : {chemin:réponse HTTP en bytes} + verrou
cache = {}
cache_lock = threading.Lock()


def relay(src, dst):
    """
    Retransmet les données de source vers destination.
    """
    try:
        while True:
            received = src.recv(2048)

            if not received:
                break
            else:
                dst.sendall(received)
    finally:
        dst.shutdown(socket.SHUT_WR)


def fetch_from_server(request_bytes, serverName, serverPort):
    """
    Envoie la requête au serveur et lit toute la réponse du serveur.
    """
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serverSocket.connect((serverName, serverPort))
        serverSocket.sendall(request_bytes)

        parts = []
        while True:
            data = serverSocket.recv(4096)
            if not data:
                break
            parts.append(data)
        return b"".join(parts)
    finally:
        serverSocket.close()


def is_status_200(response):
    """
    Vrai si la ligne de statut de la réponse est "HTTP/1.x 200 ...".
    """
    status_line = response.split(b"\r\n", 1)[0].split(b" ")
    return len(status_line) >= 2 and status_line[1] == b"200"


def handle_client(client_socket, client_address, serverName, serverPort):
    """
    Traite la requête d'un client : utilise le cache, sinon le serveur.
    """
    print(f"{client_address} connected.")

    # Réception requête HTTP
    try:
        request = client_socket.recv(2048)
        if not request:
            return

        request = request.decode('utf-8')

        # Analyse de la requête
        head, _, body = request.partition("\r\n\r\n")
        lines = head.split("\r\n")
 
        try:
            method, path, version = lines[0].split(" ", 2)
        except ValueError:
            print("Requête invalide")
            return


        if method == "GET":
            with cache_lock:
                cached = cache.get(path.encode('utf-8'))

            # Envoie depuis le cache si présent
            if cached is not None:
                print(f"[CACHE HIT]  GET {path}")
                client_socket.sendall(cached)
                return
            
            # Serveur sinon
            print(f"[CACHE MISS] GET {path}")
            try:
                response = fetch_from_server(request.encode('utf-8'),serverName, serverPort)
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except OSError:
                print("Erreur de connexion au serveur")
                return

            if not response:
                return

            # On ne met en cache que les réponses 200 OK
            if is_status_200(response):
                with cache_lock:
                    cache[path.encode('utf-8')] = response

            client_socket.sendall(response)

        else:
            # Autres méthodes : pas de cache/simple relai
            print(f"[RELAIS] {method} {path}")
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                serverSocket.connect((serverName, serverPort))
            except OSError:
                print("Erreur de connexion au serveur")
                serverSocket.close()
                return

            serverSocket.sendall(request.encode('utf-8'))

            thread_client_to_server  = threading.Thread(target=relay, args=(client_socket, serverSocket))
            thread_server_to_client = threading.Thread(target=relay, args=(serverSocket, client_socket))
            thread_client_to_server .start()
            thread_server_to_client.start()
            thread_client_to_server .join()
            thread_server_to_client.join()

    except OSError as e:
        print(f"Erreur avec {client_address} : {e}")
        

    finally:
        client_socket.close()
        print(f"{client_address} disconnected.")


def main():
    # Vérification des arguments
    if len(sys.argv) != 3:
        print(f"Usage : {sys.argv[0]} <IP_SERVEUR> <PORT_SERVEUR>")
        sys.exit(1)

    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])

    relaySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    relaySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    relaySocket.bind(('', RELAY_PORT))
    relaySocket.listen()
    print("Relay ready")

    # Créer une socket de connexion pour chaque client
    try:
        while True:
            client_socket, client_address = relaySocket.accept()
            threading.Thread(target=handle_client,
                             args=(client_socket, client_address, serverName, serverPort)).start()
    finally:
        print("\nClosing Relay...")
        relaySocket.close()

if __name__ == "__main__":
    main()