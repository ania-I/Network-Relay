import socket
import sys
import threading

RELAY_PORT = 1234

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



def handle_client(client_socket, client_address, serverName, serverPort):
    """
    Ouvre la connexion vers le serveur et relie les deux sockets.
    """
    print(f"{client_address} connected.")

    # Connexion du relai au serveur
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        serverSocket.connect((serverName, serverPort))
        print(f"Relay connected to {serverName}:{serverPort}")

    except ConnectionError as e:
        print("Erreur de connexion au serveur")
        client_socket.close()
        serverSocket.close()

    # Création des 2 threads aller et retour
    thread_client_to_server = threading.Thread(target=relay, args=(client_socket, serverSocket))
    thread_server_to_client = threading.Thread(target=relay,args=(serverSocket, client_socket))

    thread_client_to_server.start()
    thread_server_to_client.start()

    thread_client_to_server.join()
    thread_server_to_client.join()

    client_socket.close()
    serverSocket.close()
    print(f"{client_address} deconnected.")



def main():
    # Vérification des arguments
    if len(sys.argv) != 3:
        print(f"Usage : {sys.argv[0]} <IP_SERVEUR> <PORT_SERVEUR>")
        sys.exit(1)

    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])

    relaySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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