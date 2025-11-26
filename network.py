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
        self.root = root
        self.lock = threading.Lock()  # chrání socket

    # -----------------------------
    # Pomocné funkce
    # -----------------------------
    def recv_all(self, length):
        """Přečte přesně 'length' bajtů nebo vrátí None."""
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

    def send_packet(self, msg: str):
        """Pošle length-prefixed packet."""
        if not self.running:
            return
        try:
            data = msg.encode("utf-8")
            header = struct.pack("!I", len(data))
            with self.lock:
                self.sock.sendall(header + data)
        except Exception as e:
            print("Chyba při odesílání:", e)

    # -----------------------------
    # Veřejné API
    # -----------------------------
    def connect(self):
        if self.running:
            print("Už jsem připojen → ignoruji connect()")
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

    def listen(self):
        """Čte length-prefixed zprávy od serveru."""
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

        self.close()

    def send(self, message: str):
        """Veřejné posílání zpráv (užívá nový protokol)."""
        print("[SEND] ", message)
        self.send_packet(message)

    def close(self):
        """Bezpečné zavření socketu."""
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