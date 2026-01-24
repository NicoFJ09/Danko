"""
HTTP Receiver - Laptop
Recibe datos del bot y los procesa con callback
"""

import requests
import time
import threading


class BotReceiver:
    def __init__(
        self,
        bot_ip="192.168.1.87",
        bot_port=80,
        endpoint="/data",
        poll_interval=0.15  # más rápido para movimiento
    ):
        self.bot_ip = bot_ip
        self.bot_port = bot_port
        self.endpoint = endpoint
        self.poll_interval = poll_interval
        self.url = f"http://{bot_ip}:{bot_port}{endpoint}"

        self.running = False
        self.callback = None
        self.thread = None

        self.packets_received = 0

        # 🔑 estado anterior (para filtrar duplicados)
        self.last_state = None

    def set_callback(self, callback):
        """
        Callback signature:
        callback(heading, front, left, right)
        """
        self.callback = callback

    def start(self):
        """Start receiver in background thread"""
        self.running = True
        self.thread = threading.Thread(
            target=self._poll_loop,
            daemon=True
        )
        self.thread.start()
        print(f"📡 Bot Receiver started: {self.url}")
        print(f"   Polling every {self.poll_interval}s\n")

    def _poll_loop(self):
        """Internal polling loop"""
        consecutive_errors = 0
        connected_once = False
        reset_sent = False

        while self.running:
            try:
                # ================== PING ==================
                if not connected_once:
                    try:
                        ping_response = requests.get(
                            f"http://{self.bot_ip}:{self.bot_port}/ping",
                            timeout=1
                        )
                        if ping_response.status_code == 200:
                            connected_once = True
                            print(f"✅ Bot conectado en {self.bot_ip}")

                            # Enviar RESET al simulador
                            if self.callback and not reset_sent:
                                print("📢 Enviando señal RESET al simulador...")
                                self.callback("RESET", 0, 0, 0)
                                reset_sent = True
                                self.last_state = None
                                time.sleep(0.5)
                                print("✅ Listo para recibir datos\n")
                    except:
                        time.sleep(1)
                        continue

                # No procesar datos hasta enviar RESET
                if not reset_sent:
                    time.sleep(self.poll_interval)
                    continue

                # ================== DATA ==================
                response = requests.get(self.url, timeout=2)

                if response.status_code != 200:
                    time.sleep(self.poll_interval)
                    continue

                raw = response.text.strip()

                # Ignorar RESET del endpoint (si existiera)
                if raw == "RESET":
                    time.sleep(0.5)
                    continue

                parts = raw.split()
                if len(parts) != 4:
                    print(f"⚠️  Invalid data format: {raw}")
                    time.sleep(self.poll_interval)
                    continue

                heading = parts[0]
                front = float(parts[1])
                left = float(parts[2])
                right = float(parts[3])

                # 🔑 estado discreto (redondear evita ruido)
                state = (
                    heading,
                    round(front, 1),
                    round(left, 1),
                    round(right, 1)
                )

                # ================== FILTRO ==================
                if state != self.last_state:
                    self.last_state = state
                    self.packets_received += 1
                    consecutive_errors = 0

                    if self.callback:
                        self.callback(heading, front, left, right)

            except requests.exceptions.ConnectionError:
                consecutive_errors += 1
                if connected_once:
                    if consecutive_errors == 1:
                        print("⚠️  Bot desconectado, esperando reconexión...")
                    connected_once = False
                    reset_sent = False
                    self.last_state = None
                else:
                    if consecutive_errors % 10 == 1:
                        print(f"⏳ Esperando bot en {self.bot_ip}...")

            except requests.exceptions.Timeout:
                consecutive_errors += 1
                if consecutive_errors % 10 == 1:
                    print("⏳ Timeout...")

            except Exception as e:
                print(f"❌ Error Receiver: {e}")

            time.sleep(self.poll_interval)

    def stop(self):
        """Stop receiver"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print(f"\n📊 Receiver stopped. Packets received: {self.packets_received}")


# ================== STANDALONE ==================
if __name__ == "__main__":
    BOT_IP = "192.168.101.63"  # ← CAMBIAR

    def print_data(heading, front, left, right):
        print(
            f"📨 {heading} | "
            f"Front: {front:.1f}cm | "
            f"Left: {left:.1f}cm | "
            f"Right: {right:.1f}cm"
        )

    receiver = BotReceiver(bot_ip=BOT_IP)
    receiver.set_callback(print_data)
    receiver.start()

    try:
        print("💻 HTTP Receiver - Standalone Mode")
        print("=" * 60)
        print("Press Ctrl+C to stop\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
