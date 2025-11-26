import socket
import threading
import time

HOST = "192.168.2.2"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(b"HELLO NICK testmove\n")
s.sendall(b"PLAY\n")

def spam_moves():
    for _ in range(10):
        s.sendall(b"MOVE 2 3 3 4\n")

# dva thread-y posílají MOVE zároveň
t1 = threading.Thread(target=spam_moves)
t2 = threading.Thread(target=spam_moves)
t1.start()
t2.start()
t1.join()
t2.join()

time.sleep(1)
s.close()