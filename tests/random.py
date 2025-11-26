import socket
import os
import time

SERVER_IP = "192.168.2.2"
SERVER_PORT = 5001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

def send(msg):
    print("SEND:", msg.strip())
    s.sendall(msg.encode())

def recv_line():
    data = b""
    while b"\n" not in data:
        part = s.recv(1)
        if not part:
            return ""
        data += part
    line = data.decode()
    print("RECV:", line.strip())
    return line

# HELLO NICK
send("HELLO NICK binar\n")
recv_line()

print("=== SPAM RANDOM BINARIES ===")

try:
    for i in range(100):
        chunk = os.urandom(128)  # náhodných 128 bajtů
        s.sendall(chunk)
        time.sleep(0.01)
except:
    pass

print("Hotovo, spojení pravděpodobně uzavřeno serverem.")
s.close()