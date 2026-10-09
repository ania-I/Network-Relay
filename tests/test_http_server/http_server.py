from socket import *
from threading import *
from pathlib import Path

# Gestion des chemins indépendant de là où est lancé le serveur
SERVER_DIR = Path(__file__).resolve().parent
WEB_ROOT = SERVER_DIR / "fichiers"

serverPort = 8080
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('Server ready')

def handle_client(connectionSocket):
    """
    Gère les requêtes HTTP
    """
    #2 Réception requête HTTP
    try:
        request = connectionSocket.recv(2048)
        if not request:
            return

        request = request.decode('utf-8')

        # Affichage de la requête sur le terminal
        print("### Requête HTTP reçue ###")
        print(request)
        print("##########################")

        #3 Analyse de la requête
        first_line = request.split("\r\n")[0] # Extraction des parties de la requête
        parts = first_line.split()
        method = parts [0] # GET
        path = parts[1] # chemin du fichier demandé

        #4 Trouver le fichier demandé
        if path == "/":
            path = "/index.html"

        relative_path = path.lstrip("/") # Retirer le "/" initial
        filepath = Path(WEB_ROOT) / relative_path # Construire le chemin vers le fichier

        if ".." in path or not filepath.is_file(): # Vérifier que le fichier existe
            send_error(connectionSocket, 404, "Not Found") # Sinon renvoyer erreur 404
            return

        content = filepath.read_bytes() # Lire le contenu du fichier

        #5 Création de la réponse HTTP

        headers = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        ).encode('utf-8')

        #6 Envoi de la réponse
        connectionSocket.sendall(headers + content)

    except Exception as e:
        print("Une erreur a été rencontrée.")

    # Fermeture de la connexion
    finally:
        print("Closing connection...")
        connectionSocket.close()

        
def send_error(connectionSocket, status_code, message):
    """
    Envoie une réponse HTTP d'erreur
    """

    content = f"""
    <html>
        <head>
            <title>{status_code} {message}</title>
        </head>
        <body>
            <h1>{status_code} {message}</h1>
        </body>
    </html>
    """.encode('utf-8')

    headers = (
        f"HTTP/1.1 {status_code} {message}\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"Connection: close\r\n"
        "\r\n"
    ).encode('utf-8')

    connectionSocket.sendall(headers + content)

#1 Création d’une socket de connection lors d’une demande par un client
try:
    while True:
        connectionSocket, address = serverSocket.accept()
        Thread(target=handle_client, args=(connectionSocket,)).start()
finally:
    print("Closing server...")
    serverSocket.close()
