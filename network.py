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
        self.sock_id = 0

    def connect(self):
        if self.running:
            print("Stopuji starý klient...")
            self.running = False
            self.sock_id += 1   # ← stará vlákna okamžitě vypadnou
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.last_ping_time = time.time()

            print(f"Připojeno k serveru {self.host}:{self.port}")
            self.sock_id += 1
            my_id = self.sock_id
            print(f"moje id je :{my_id}")

            threading.Thread(target=self.listen,args=(my_id,), daemon=True).start()
            threading.Thread(target=self._ping_watchdog, args=(my_id,PING_TIMEOUT,), daemon=True).start()
            return True
        
        except Exception as e:
            print(f"Chyba při připojení: {e}")
            self.running = False
            return False

    def listen(self, my_id):
        if my_id != self.sock_id:
            return
        try:
            self.sock.settimeout(1.0)  # každou 1s se probudí
            buffer = ""
            while self.running and my_id == self.sock_id:
                if not self.sock:
                    break
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
            self.running = False

        active = (my_id == self.sock_id)

        self.running = False
        self.close()

        if self.on_disconnect and active:
            # jen aktivní klient má právo vyvolat disconnect událost
            print("wohoooooooo")
            if self.root:
                print("aooooo")
                self.root.after(0, lambda cb=self.on_disconnect: cb(self))
            else:
                print("bbbbbbbb")
                self.on_disconnect(self)
        
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

    def _ping_watchdog(self, my_id, timeout=15):
        print(f"[WATCHDOG START] my_id={my_id}, sock_id={self.sock_id}, client_obj={id(self)} thread={threading.get_ident()}")
        while self.running and my_id == self.sock_id:
            if time.time() - self.last_ping_time > timeout:
                print("Watchdog: dlouho nepřišel PING, beru to jako odpojení.")
                print(f"[WATCHDOG TIMEOUT] my_id={my_id}, sock_id={self.sock_id}, client_obj={id(self)} thread={threading.get_ident()}")
                # násilně ukončíme spojení
                self.running = False
                try:
                    with self.lock:
                        if self.sock:
                            self.sock.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    if self.sock and my_id == self.sock_id:
                        self.sock.close()
                except:
                    pass
                self.sock = None

                break

            time.sleep(1)
        print(f"[WATCHDOG END] my_id={my_id}, sock_id={self.sock_id}, client_obj={id(self)} thread={threading.get_ident()}")

    def stop(self):
        self.sock_id += 1
        self.running = False
        self.on_disconnect = None
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
