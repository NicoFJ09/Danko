"""
MazeRunner Map Simulator - Main Script
Terminal input loop + real-time pygame visualization
"""

import pygame
import sys
import threading
from config import MapConfig
from map.map_state import MapState
from map.camera import Camera
from map.renderer import MapRenderer

class MapSimulator:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((MapConfig.WINDOW_WIDTH, MapConfig.WINDOW_HEIGHT))
        pygame.display.set_caption("MazeRunner - Map Simulator")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.map_state = MapState()
        self.camera = Camera(MapConfig.WINDOW_WIDTH, MapConfig.WINDOW_HEIGHT)
        self.renderer = MapRenderer(self.screen, self.camera, self.map_state)
        
        # Center camera on starting position
        start_x, start_y = self.renderer.cell_to_world(0, 0)
        self.camera.center_on(start_x, start_y)
        
        self.running = True
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.camera.handle_mouse_down(event.pos, event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.camera.handle_mouse_up(event.pos, event.button)
            
            elif event.type == pygame.MOUSEMOTION:
                self.camera.handle_mouse_motion(event.pos, event.rel)
            
            elif event.type == pygame.MOUSEWHEEL:
                self.camera.handle_mouse_wheel(event.y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Center on bot
                    bot_x, bot_y = self.renderer.cell_to_world(*self.map_state.bot_cell)
                    self.camera.center_on(bot_x, bot_y)
    
    def update(self):
        """Update game state"""
        pass  # Map updates happen when new sensor data comes in
    
    def render(self):
        """Render the map"""
        self.renderer.draw()
        pygame.display.flip()
    
    def run_visualization(self):
        """Main visualization loop (runs in main thread)"""
        print("\n🎮 Pygame window opened")
        print("💡 Use mouse to pan/zoom, SPACE to center on bot, ESC to quit\n")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        print("\n👋 Visualization closed")
    
    def input_loop(self):
        """Terminal input loop (runs in separate thread)"""
        print("\n" + "="*60)
        print("🤖 MazeRunner Map Simulator - Terminal Input")
        print("="*60)
        print("\nEnter sensor data to update the map.")
        print("Format: <heading> <front_cm> <left_cm> <right_cm>")
        print("Example: N 15 5 25")
        print("Valid headings: N, S, E, W")
        print("Type 'quit' to exit\n")
        
        while self.running:
            try:
                # Get input
                user_input = input("📡 Enter sensor data: ").strip()
                
                if user_input.lower() == 'quit':
                    self.running = False
                    break
                
                # Parse input
                parts = user_input.split()
                if len(parts) != 4:
                    print("❌ Invalid format. Use: <heading> <front> <left> <right>")
                    print("   Example: N 15 5 25\n")
                    continue
                
                heading = parts[0].upper()
                if heading not in ['N', 'S', 'E', 'W']:
                    print("❌ Invalid heading. Use: N, S, E, or W\n")
                    continue
                
                try:
                    front = float(parts[1])
                    left = float(parts[2])
                    right = float(parts[3])
                except ValueError:
                    print("❌ Distances must be numbers\n")
                    continue
                
                # Update map with new sensor data
                print(f"\n📊 Processing: heading={heading}, front={front}cm, left={left}cm, right={right}cm")
                events = self.map_state.update_sensors(front, left, right, heading)
                
                # Report events
                if events['new_walls']:
                    print(f"   🧱 New walls detected: {len(events['new_walls'])}")
                if events['new_paths']:
                    print(f"   🚪 New paths detected: {len(events['new_paths'])}")
                if events['movement']:
                    print(f"   🤖 Bot moved to {self.map_state.bot_cell}")
                
                print(f"   ✅ Map updated\n")
                
            except EOFError:
                # Handle Ctrl+D
                self.running = False
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                print("\n\n⚠️  Interrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    def run(self):
        """Start both visualization and input loops"""
        # Start input loop in separate thread
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()
        
        # Run visualization in main thread
        self.run_visualization()
        
        print("\n✅ Simulator stopped")

def main():
    simulator = MapSimulator()
    simulator.run()

if __name__ == "__main__":
    main()