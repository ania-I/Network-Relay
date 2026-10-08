from socket import *
from threading import *

SERVER_PORT=1234
ServerSocket=socket(AF_INET,SOCK_STREAM)
ServerSocket.bind(('',SERVER_PORT))

ServerSocket.listen(1)

def handle_client(connectionSocket):
    with connectionSocket:
        while True:
            message=connectionSocket.recv(2048)
            if not message:
                break
            connectionSocket.send('pong'.encode('utf-8'))


while True:
    connectionSocket,address=ServerSocket.connect()
    Thread(target=handle_client, args=(connectionSocket,), daemon=True).start()