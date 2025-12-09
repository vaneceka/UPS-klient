import socket
import threading
import struct
import time

PING_TIMEOUT = 16

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
        if self.running:
            print("Už jsem připojen.")
            self.stop()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.last_ping_time = time.time()

            print(f"Připojeno k serveru {self.host}:{self.port}")

            threading.Thread(target=self.listen, daemon=True).start()
            threading.Thread(target=self._ping_watchdog, args=(PING_TIMEOUT,), daemon=True).start()
            return True
        except Exception as e:
            print(f"Chyba při připojení: {e}")
            self.running = False
            return False


    def listen(self):
        self.sock.settimeout(1.0)  # každou 1s se probudí

        buffer = ""

        try:
            while self.running:
                try:
                    data = self.sock.recv(4096)
                except socket.timeout:
                    # timeout není chyba, jen nic nepřišlo
                    continue

                # server ukončil spojení korektně
                if not data:
                    break  

                buffer += data.decode("utf-8")

                # zpracovat všechny kompletní řádky
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = line.strip()

                    if message != "PING":
                        print("[RECV]", message)

                    # Keepalive
                    if message == "PING":
                        self.last_ping_time = time.time()
                        self.send("PONG")
                        continue

                    # Odeslat zprávu do GUI
                    if self.on_message_callback:
                        if self.root:
                            self.root.after(0, lambda m=message: self.on_message_callback(m))
                        else:
                            self.on_message_callback(message)

        except Exception as e:
            print("Chyba při čtení:", e)

        was_running = self.running
        # konec spojení
        self.running = False
        self.close()

        if was_running and self.on_disconnect:
            cb = self.on_disconnect
            if self.root:
                self.root.after(0, lambda cb=cb: cb(self))
            else:
                cb(self)
        
    # Veřejné posílání zpráv (užívá nový protokol).
    def send(self, message: str):
        if not self.running or self.sock is None:
            return

        if not message.endswith("\n"):
            message += "\n"

        if message.strip() != "PONG":
            print("[SEND]", message.strip())

        try:
            with self.lock:
                self.sock.sendall(message.encode("utf-8"))
        except Exception as e:
            print("Chyba při odesílání:", e)
            # Bereme to jako odpojení
            self.running = False
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

            # Oznámit GUI, že jsme offline
            if hasattr(self, "on_disconnect") and self.on_disconnect:
                cb = self.on_disconnect
                if self.root:
                    self.root.after(0, lambda cb=cb: cb(self))
                else:
                    cb(self)

    def close(self):
        if self.sock is None:
            return
        self.running = False

        if self.sock:
            try:
                with self.lock:
                    self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass

            try:
                self.sock.close()
            except:
                pass

        self.sock = None
        print("Odpojeno od serveru.")

    def _ping_watchdog(self, timeout=15):
        while self.running:
            if time.time() - self.last_ping_time > timeout:
                print("Watchdog: dlouho nepřišel PING, beru to jako odpojení.")
                # násilně ukončíme spojení
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

                break

            time.sleep(1)

    def stop(self):
        self.running = False
        try:
            with self.lock:
                if self.sock:
                    try:
                        self.sock.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    try:
                        self.sock.close()
                    except:
                        pass
        except:
            pass
        self.sock = None