import socket

HOST = "192.168.2.2"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(b"HELLO NICK binar\n")

# Pošli zakázané znaky
s.sendall(b"\x00\xFF\x10\x99hello\n")

s.close()