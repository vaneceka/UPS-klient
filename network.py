import socket
import threading
import time

PING_TIMEOUT = 8

class NetworkClient:
    def __init__(self, host, port, on_message_callback=None, root=None):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False

        self.on_message_callback = on_message_callback
        self.on_disconnect = None
        self.root = root

        self.lock = threading.Lock()
        self.last_ping_time = time.time()

    def connect(self):
        # zastavení starého socketu
        self.stop()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.last_ping_time = time.time()

            print(f"Připojeno k serveru {self.host}:{self.port}")

            # Spustíme vlákna
            threading.Thread(target=self.listen, daemon=True).start()
            threading.Thread(target=self._ping_watchdog, daemon=True).start()

            return True

        except Exception as e:
            print("Chyba při připojení:", e)
            self.running = False
            return False

    def listen(self):
        try:
            self.sock.settimeout(1.0)
            buffer = ""

            while self.running:
                try:
                    data = self.sock.recv(4096)
                except socket.timeout:
                    continue
                
                # server zavřel spojení
                if not data:
                    break  

                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    msg = line.strip()

                    if msg == "PING":
                        self.last_ping_time = time.time()
                        self.send("PONG")
                        continue

                    if self.on_message_callback:
                        if self.root:
                            self.root.after(0, lambda m=msg: self.on_message_callback(m))
                        else:
                            self.on_message_callback(msg)

        except Exception as e:
            print("Chyba při čtení:", e)

        self._handle_disconnect()

    def send(self, message: str):
        if not self.running:
            return
        if not message.endswith("\n"):
            message += "\n"

        try:
            with self.lock:
                self.sock.sendall(message.encode("utf-8"))
        except:
            self._handle_disconnect()

    def _ping_watchdog(self):
        while self.running:
            if time.time() - self.last_ping_time > PING_TIMEOUT:
                print("PING timeout – odpojuji klienta.")
                self._handle_disconnect()
                return
            time.sleep(1)

    def _handle_disconnect(self):
        if not self.running:
            return

        self.running = False
        try:
            with self.lock:
                if self.sock:
                    self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass

        try:
            if self.sock:
                self.sock.close()
        except:
            pass

        self.sock = None
        print("Odpojeno od serveru.")

        if self.on_disconnect:
            if self.root:
                self.root.after(0, lambda: self.on_disconnect(self))
            else:
                self.on_disconnect(self)


    def stop(self):
        self.running = False
        try:
            with self.lock:
                if self.sock:
                    try: self.sock.shutdown(socket.SHUT_RDWR)
                    except: pass
                    try: self.sock.close()
                    except: pass
        except:
            pass
        self.sock = None