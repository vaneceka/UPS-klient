import socket
import time

HOST = "192.168.2.2"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))

# Rozkousaná zpráva HELLO a PLAY
chunks = [b"H", b"E", b"LLO", b" NICK te", b"st\n", b"P", b"L", b"AY\n"]

for c in chunks:
    s.sendall(c)
    time.sleep(0.1)

s.close()