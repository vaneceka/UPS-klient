import socket
import threading

class NetworkClient:
    def __init__(self, host, port, on_message_callback=None, root=None):
        """
        :param host: IP adresa serveru (např. '127.0.0.1')
        :param port: port serveru (např. 5000)
        :param on_message_callback: funkce, která se zavolá, když přijde zpráva
        :param root: hlavní Tkinter okno (kvůli thread-safe volání)
        """
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.on_message_callback = on_message_callback
        self.root = root  # 👈 přidáno

    def connect(self):
        """Naváže spojení se serverem."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            print(f"✅ Připojeno k serveru {self.host}:{self.port}")

            # posloucháme příchozí zprávy v jiném vlákně
            threading.Thread(target=self.listen, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ Chyba při připojení: {e}")
            return False

    def listen(self):
        """Nepřetržitě poslouchá zprávy od serveru."""
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("⚠️ Server ukončil spojení.")
                    self.running = False
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = line.strip()
                    print(f"⬅️ {message}")
                    if self.on_message_callback:
                        # ✅ bezpečné volání ve vlákně Tkinteru
                        if self.root:
                            self.root.after(0, lambda msg=message: self.on_message_callback(msg))
                        else:
                            self.on_message_callback(message)

            except Exception as e:
                print(f"❌ Chyba při čtení: {e}")
                self.running = False
                break

    def send(self, message: str):
        """Odešle zprávu serveru."""
        if self.sock and self.running:
            try:
                self.sock.sendall((message + "\n").encode("utf-8"))
                print(f"{message}")
            except Exception as e:
                print(f"Chyba při odesílání: {e}")

    def close(self):
        """Ukončí spojení."""
        self.running = False
        if self.sock:
            self.sock.close()
        print("🔌 Odpojeno od serveru.")