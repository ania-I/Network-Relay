from socket import *

SERVER_PORT=1234
SERVER_ADDR='127.0.0.1' //test sur la meme machine

ClientSocket=socket(AF_INET,SOCK_CSTREAM)
ClientScoket.bind((SERVER_ADDR,SERVER_PORT))

message="ping".encode('utf-8')
clientSocket.send(message)
response=clientSocket.recv(2048).decode('utf-8')
clientSocket.close()


