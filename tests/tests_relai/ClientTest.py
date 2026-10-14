from socket import *

SERVER_PORT=1234
SERVER_ADDR='127.0.0.1' 

ClientSocket=socket(AF_INET,SOCK_STREAM)
ClientSocket.bind((SERVER_ADDR,SERVER_PORT))

message="ping".encode('utf-8')
ClientSocket.send(message)
response=ClientSocket.recv(2048).decode('utf-8')
ClientSocket.close()


