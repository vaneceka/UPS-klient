import socket
import time

HOST = "192.168.2.2"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(b"HELLO NICK flooder\n")

# 50 zpráv během jedné vteřiny
for i in range(50):
    s.sendall(b"PLAY\n")

time.sleep(1)
s.close()