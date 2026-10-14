# Code issu du TME1 exercice 2 (client)
from socket import *
import time

serverName = gethostname() # Adresse du relai à changer si machines différentes
serverPort = 1234 # Port du relai
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

def time_to_seconds(time_string):
    """
    Convertit une chaîne de caractères selon le format %H:%M:%S en sec
    """
    hours, minutes, seconds = map(int, time_string.split(":"))
    return hours * 3600 + minutes * 60 + seconds

try:
    while(True):
        clientSocket.sendall("Demande heure".encode('utf-8'))
        server_time = clientSocket.recv(2048).decode('utf-8') # Heure du serveur
        local_time = time.strftime("%H:%M:%S") # Heure locale

        # Conversion en sec
        server_seconds = time_to_seconds(server_time)
        local_seconds = time_to_seconds(local_time)
        difference =  server_seconds - local_seconds

        # Affichage
        print("Heure serveur : " + server_time)
        print("Heure locale : " + local_time)
        print(f"Différence de {difference} secondes")
        print("\n")
        
        time.sleep(1)

finally:
    print("Closing client socket...")
    clientSocket.close()

