"""
Dummy telemetry sender for testing bot→laptop communication
Simulates the bot sending UDP packets with sensor and position data
"""

import socket
import json
import time
import random

class DummyBot:
    def __init__(self, laptop_ip="127.0.0.1", laptop_port=5000):
        self.laptop_ip = laptop_ip
        self.laptop_port = laptop_port
        
        # Bot state
        self.x = 10.0  # cm
        self.y = 10.0  # cm
        self.heading = 0.0  # degrees (0=North, 90=East, 180=South, 270=West)
        self.sequence = 0
        
        # Setup UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def read_sensors(self):
        """Simulate ultrasonic sensor readings (in cm)"""
        return {
            "front": round(random.uniform(5, 30), 2),
            "left": round(random.uniform(5, 30), 2),
            "right": round(random.uniform(5, 30), 2)
        }
    
    def simulate_movement(self):
        """Simulate bot moving around"""
        # Random walk for testing
        self.x += random.uniform(-2, 2)
        self.y += random.uniform(-2, 2)
        self.heading = (self.heading + random.uniform(-5, 5)) % 360
        
        # Keep within bounds (200x100 cm maze)
        self.x = max(0, min(200, self.x))
        self.y = max(0, min(100, self.y))
    
    def create_packet(self):
        """Create telemetry packet"""
        sensors = self.read_sensors()
        
        packet = {
            "seq": self.sequence,
            "timestamp": time.time(),
            "position": {
                "x": round(self.x, 2),
                "y": round(self.y, 2),
                "heading": round(self.heading, 2)
            },
            "sensors": sensors,
            "action": "MOVING"
        }
        
        self.sequence += 1
        return packet
    
    def send_telemetry(self):
        """Send telemetry packet to laptop"""
        packet = self.create_packet()
        try:
            self.sock.sendto(
                json.dumps(packet).encode(), 
                (self.laptop_ip, self.laptop_port)
            )
            print(f"📤 Sent packet #{packet['seq']} to {self.laptop_ip}:{self.laptop_port}")
            return True
        except Exception as e:
            print(f"❌ Error sending packet: {e}")
            return False
    
    def run(self, frequency_hz=20):
        """Main loop - send telemetry at specified frequency"""
        interval = 1.0 / frequency_hz
        print(f"🤖 Dummy Bot starting...")
        print(f"📡 Sending to {self.laptop_ip}:{self.laptop_port} at {frequency_hz}Hz")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.simulate_movement()
                self.send_telemetry()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped")
            self.sock.close()

if __name__ == "__main__":
    # For testing: run this script to simulate the bot
    bot = DummyBot(laptop_ip="127.0.0.1", laptop_port=5000)
    bot.run(frequency_hz=20)  # 20Hz = every 50ms