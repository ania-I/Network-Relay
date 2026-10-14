# Code issu du TME1 exercice 2 (serveur)
from socket import *
from threading import *
import time

serverPort = 9000 # Port du serveur à connecter au relai
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('Server ready')

def handle_client(clientSocket):
    """
    Envoie l'heure du serveur à chaque client
    """
    try:
        while True:
            received = clientSocket.recv(2048)
            if not received:
                break
            else:
                server_time = time.strftime("%H:%M:%S") # Heure à envoyer
                clientSocket.sendall(server_time.encode('utf-8'))
    finally:
        print("Closing connexion...")
        clientSocket.close()

# Créer une socket de connexion pour chaque client
try:
    while True:
        connectionSocket, address = serverSocket.accept()
        Thread(target=handle_client,
        args=(connectionSocket,)).start()
finally:
    print("Closing server...")
    serverSocket.close()
