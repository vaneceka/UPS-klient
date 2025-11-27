import socket
import threading
import struct


class NetworkClient:
    def __init__(self, host, port, on_message_callback=None, root=None):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.on_message_callback = on_message_callback
        self.on_disconnect = None
        self.root = root
        self.lock = threading.Lock()  # chrání socket


    # Přečte přesně 'length' bajtů nebo vrátí None.
    def recv_all(self, length):
        data = b""
        while len(data) < length:
            try:
                chunk = self.sock.recv(length - len(data))
            except OSError:
                return None
            if not chunk:
                return None
            data += chunk
        return data

    # Pošle length-prefixed packet.
    def send_packet(self, msg: str):
        if not self.running:
            return
        try:
            data = msg.encode("utf-8")
            header = struct.pack("!I", len(data))
            with self.lock:
                self.sock.sendall(header + data)
        except Exception as e:
            print("Chyba při odesílání:", e)

    def connect(self):
        if self.running:
            print("Už jsem připojen.")
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True

            print(f"Připojeno k serveru {self.host}:{self.port}")

            threading.Thread(target=self.listen, daemon=True).start()
            return True
        except Exception as e:
            print(f"Chyba při připojení: {e}")
            self.running = False
            return False

    # Čte length-prefixed zprávy od serveru.
    def listen(self):
        while self.running:
            try:
                header = self.recv_all(4)
                if not header:
                    print("Spojení ukončeno (header).")
                    break
                
                (length,) = struct.unpack("!I", header)

                if length == 0 or length > 65536:
                    print("Neplatná délka:", length)
                    break

                payload = self.recv_all(length)
                if not payload:
                    print("Spojení ukončeno (payload).")
                    break

                message = payload.decode("utf-8")
                print("[RECV] ", message)

                if self.on_message_callback:
                    if self.root:
                        self.root.after(0, lambda m=message: self.on_message_callback(m))
                    else:
                        self.on_message_callback(message)

            except Exception as e:
                print("Chyba při čtení:", e)
                break

        self.running = False
        self.close()

        if hasattr(self, 'on_disconnect') and self.on_disconnect:
            if self.root:
                self.root.after(0, self.on_disconnect)
            else:
                self.on_disconnect()
    
    # Veřejné posílání zpráv (užívá nový protokol).
    def send(self, message: str):
        print("[SEND] ", message)
        self.send_packet(message)

    # Bezpečné zavření socketu.
    def close(self):
        if not self.running:
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