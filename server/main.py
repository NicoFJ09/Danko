"""
MazeRunner Graph Visualizer - Manual Input Mode
Visualización de grafo de checkpoints con entrada manual por consola
"""

import pygame
from config import Config
from graph_state import MazeGraph, DirectionState, Cardinal
from simple_camera import SimpleCamera
from graph_renderer import GraphRenderer


class MazeVisualizer:
    """Visualizador del grafo con input manual"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("MazeRunner - Graph Visualizer (Manual Input)")
        self.clock = pygame.time.Clock()
        
        # Sistema de grafo
        self.graph = MazeGraph()
        
        # Cámara y renderer
        self.camera = SimpleCamera(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.renderer = GraphRenderer(self.screen, self.camera, self.graph)
        
        # Centrar en checkpoint inicial
        self.camera.center_on(0, 0)
        
        self.running = True
        
        # Estado para comandos
        self.current_heading = Cardinal.NORTH
        
        print("\n" + "=" * 70)
        print("🤖 MAZERUNNER - VISUALIZADOR DE GRAFO")
        print("=" * 70)
        print("\n📍 Sistema iniciado con Checkpoint #0")
        print(f"🧭 Heading inicial: {self.current_heading.value}")
        print("\n💡 COMANDOS DISPONIBLES:")
        print("   - Para crear checkpoint: <dirección> <front> <left> <right>")
        print("     Ejemplo: N BLOCKED UNEXPLORED UNEXPLORED")
        print("   - Direcciones: N, S, E, W")
        print("   - Estados: UNEXPLORED, EXPLORED, BLOCKED")
        print("   - 'update <checkpoint_id> <direccion> <estado>' - Actualizar dirección")
        print("   - 'move <checkpoint_id>' - Mover a checkpoint")
        print("   - 'deadend' - Marcar checkpoint actual como dead-end")
        print("   - 'stats' - Ver estadísticas")
        print("   - 'reset' - Resetear grafo")
        print("   - 'quit' - Salir")
        print("\n⌨️  Esperando comandos...\n")
    
    def handle_events(self):
        """Maneja eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.camera.handle_mouse_down(event.pos, event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.camera.handle_mouse_up(event.pos, event.button)
            
            elif event.type == pygame.MOUSEMOTION:
                self.camera.handle_mouse_motion(event.pos)
            
            elif event.type == pygame.MOUSEWHEEL:
                self.camera.handle_mouse_wheel(event.y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Centrar en checkpoint actual
                    current = self.graph.get_current_checkpoint()
                    self.camera.center_on(current.render_x, current.render_y)
                    print(f"📍 Centrado en Checkpoint #{current.id}")
    
    def process_command(self, command: str):
        """Procesa comando de entrada del usuario"""
        parts = command.strip().upper().split()
        
        if not parts:
            return
        
        cmd = parts[0]
        
        # Quit
        if cmd in ['QUIT', 'EXIT', 'Q']:
            self.running = False
            return
        
        # Reset
        if cmd in ['RESET', 'R']:
            self.graph.reset()
            self.current_heading = Cardinal.NORTH
            self.camera.center_on(0, 0)
            print("🔄 Grafo reseteado\n")
            return
        
        # Stats
        if cmd in ['STATS', 'S']:
            stats = self.graph.get_stats()
            print("\n📊 ESTADÍSTICAS:")
            print(f"   Total checkpoints: {stats['total_checkpoints']}")
            print(f"   Dead-ends: {stats['dead_ends']}")
            print(f"   Direcciones sin explorar: {stats['unexplored_directions']}")
            print(f"   Exploración completa: {'✅ SÍ' if stats['exploration_complete'] else '❌ NO'}\n")
            return
        
        # Dead-end
        if cmd in ['DEADEND', 'D']:
            current = self.graph.get_current_checkpoint()
            self.graph.mark_as_dead_end(current.id)
            return
        
        # Move to checkpoint
        if cmd == 'MOVE' and len(parts) >= 2:
            try:
                checkpoint_id = int(parts[1])
                if checkpoint_id in self.graph.checkpoints:
                    self.graph.set_current_checkpoint(checkpoint_id)
                    current = self.graph.get_current_checkpoint()
                    self.camera.center_on(current.render_x, current.render_y)
                    print(f"🤖 Movido a Checkpoint #{checkpoint_id}\n")
                else:
                    print(f"❌ Checkpoint #{checkpoint_id} no existe\n")
            except ValueError:
                print("❌ ID inválido\n")
            return
        
        # Update direction of existing checkpoint
        if cmd == 'UPDATE' and len(parts) >= 4:
            try:
                checkpoint_id = int(parts[1])
                direction = Cardinal.from_string(parts[2])
                state_str = parts[3]
                
                state_map = {
                    'UNEXPLORED': DirectionState.UNEXPLORED,
                    'EXPLORED': DirectionState.EXPLORED,
                    'BLOCKED': DirectionState.BLOCKED
                }
                
                if state_str not in state_map:
                    print(f"❌ Estado inválido: {state_str}\n")
                    return
                
                state = state_map[state_str]
                self.graph.update_checkpoint_direction(checkpoint_id, direction, state)
                print()
            except (ValueError, AttributeError) as e:
                print(f"❌ Comando inválido: {e}\n")
            return
        
        # Crear nuevo checkpoint: <DIRECCION> <FRONT> <LEFT> <RIGHT>
        # Ejemplo: N BLOCKED UNEXPLORED UNEXPLORED
        if cmd in ['N', 'S', 'E', 'W'] and len(parts) >= 4:
            try:
                direction = Cardinal.from_string(cmd)
                front_str = parts[1]
                left_str = parts[2]
                right_str = parts[3]
                
                # Mapear strings a estados
                state_map = {
                    'UNEXPLORED': DirectionState.UNEXPLORED,
                    'EXPLORED': DirectionState.EXPLORED,
                    'BLOCKED': DirectionState.BLOCKED,
                    'U': DirectionState.UNEXPLORED,
                    'E': DirectionState.EXPLORED,
                    'B': DirectionState.BLOCKED
                }
                
                front_state = state_map.get(front_str, DirectionState.UNEXPLORED)
                left_state = state_map.get(left_str, DirectionState.UNEXPLORED)
                right_state = state_map.get(right_str, DirectionState.UNEXPLORED)
                
                # Crear checkpoint
                current = self.graph.get_current_checkpoint()
                new_checkpoint = self.graph.create_checkpoint(
                    parent_id=current.id,
                    arrival_direction=direction,
                    front_state=front_state,
                    left_state=left_state,
                    right_state=right_state,
                    current_heading=direction
                )
                
                # Mover a nuevo checkpoint
                self.graph.set_current_checkpoint(new_checkpoint.id)
                self.current_heading = direction
                
                # Centrar cámara
                self.camera.center_on(new_checkpoint.render_x, new_checkpoint.render_y)
                
                print(f"🧭 Heading actualizado: {direction.value}")
                print(f"🤖 Ahora en Checkpoint #{new_checkpoint.id}\n")
                
            except Exception as e:
                print(f"❌ Error al crear checkpoint: {e}")
                print("Formato: <DIRECCION> <FRONT> <LEFT> <RIGHT>")
                print("Ejemplo: N BLOCKED UNEXPLORED UNEXPLORED\n")
            return
        
        # Comando no reconocido
        print(f"❌ Comando no reconocido: {command}")
        print("Escribe 'quit' para salir o usa los comandos mostrados arriba\n")
    
    def update(self):
        """Actualización del estado"""
        pass
    
    def render(self):
        """Renderiza el grafo"""
        self.renderer.draw()
        pygame.display.flip()
    
    def run(self):
        """Loop principal"""
        import threading
        
        def input_thread():
            """Thread para recibir input sin bloquear pygame"""
            while self.running:
                try:
                    command = input("> ")
                    if command:
                        self.process_command(command)
                except EOFError:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}\n")
        
        # Iniciar thread de input
        input_handler = threading.Thread(target=input_thread, daemon=True)
        input_handler.start()
        
        # Loop principal de pygame
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(Config.FPS)
        
        pygame.quit()
        print("\n👋 Visualizador cerrado")


def main():
    visualizer = MazeVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()

