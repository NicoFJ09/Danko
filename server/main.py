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
        print("   🖱️  MOUSE:")
        print("      - Clic en nodo = mover a ese checkpoint")
        print("      - Clic en círculo N/S/E/W = toggle estado (UN→EX→BL)")
        print("      - Clic en flecha = crear nuevo nodo en esa dirección")
        print("      - Drag = pan | Wheel = zoom")
        print("\n   ⌨️  TECLADO:")
        print("      - R = RESET | D = DELETE | P = PRINT (genera código ruta)")
        print("      - ESC = salir | ESPACIO = centrar")
        print("\n   ⌨️  COMANDOS:")
        print("      - Crear checkpoint: N/S/E/W <front> <left> <right>")
        print("        Estados: UN/EX/BL (unexplored/explored/blocked)")
        print("        Ejemplo: N BL UN UN")
        print("      - UPDATE <id> <dir> <estado>  |  MOVE <id>")
        print("      - DELETE [id] | PRINT | stats | deadend <id> | reset | quit")
        print("\n⌨️  Esperando comandos...\n")
    
    def handle_events(self):
        """Maneja eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Clic izquierdo para interacciones
                if event.button == 1:
                    click_type, click_data = self.renderer.interaction.handle_click(event.pos)
                    
                    if click_type == 'checkpoint':
                        # Mover a checkpoint
                        checkpoint_id = click_data
                        if checkpoint_id in self.graph.checkpoints:
                            self.graph.set_current_checkpoint(checkpoint_id)
                            current = self.graph.get_current_checkpoint()
                            self.camera.center_on(current.render_x, current.render_y)
                            print(f"🤖 Movido a Checkpoint #{checkpoint_id}\n")
                    
                    elif click_type == 'direction':
                        # Toggle estado de dirección
                        if click_data and isinstance(click_data, tuple) and len(click_data) == 2:
                            cp_id: int = click_data[0]
                            direction: Cardinal = click_data[1]
                            checkpoint = self.graph.checkpoints.get(cp_id)
                            if checkpoint:
                                # Ciclar estados: UNEXPLORED → EXPLORED → BLOCKED → UNEXPLORED
                                current_state = checkpoint.directions[direction]
                                if current_state == DirectionState.UNEXPLORED:
                                    new_state = DirectionState.EXPLORED
                                elif current_state == DirectionState.EXPLORED:
                                    new_state = DirectionState.BLOCKED
                                else:  # BLOCKED
                                    new_state = DirectionState.UNEXPLORED
                                
                                self.graph.update_checkpoint_direction(cp_id, direction, new_state)
                                
                                state_names = {
                                    DirectionState.UNEXPLORED: 'UNEXPLORED',
                                    DirectionState.EXPLORED: 'EXPLORED',
                                    DirectionState.BLOCKED: 'BLOCKED'
                                }
                                print(f"✅ CP#{cp_id}: {direction.value} → {state_names[new_state]}\n")
                    
                    elif click_type == 'arrow':
                        # Crear nuevo checkpoint en esa dirección
                        if click_data:
                            checkpoint_id, direction = click_data
                            self._create_node_in_direction(checkpoint_id, direction)
                    
                    else:
                        # No hay elemento interactivo, permitir pan
                        self.camera.handle_mouse_down(event.pos, event.button)
                
                # Pan con otros botones del mouse
                else:
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
                elif event.key == pygame.K_r:
                    # Reset con tecla R
                    self.graph.reset()
                    self.current_heading = Cardinal.NORTH
                    self.camera.center_on(0, 0)
                    print("🔄 Grafo reseteado (tecla R)\n")
                elif event.key == pygame.K_d:
                    # Delete checkpoint actual con tecla D
                    current = self.graph.get_current_checkpoint()
                    if self.graph.delete_checkpoint(current.id):
                        # Centrar en nuevo checkpoint actual
                        new_current = self.graph.get_current_checkpoint()
                        self.camera.center_on(new_current.render_x, new_current.render_y)
                        print(f"📍 Ahora en Checkpoint #{new_current.id}\n")
                elif event.key == pygame.K_p:
                    # Print route code con tecla P
                    route_code = self.graph.generate_route_code()
                    print("\n" + "="*70)
                    print(route_code)
                    print("="*70 + "\n")
                elif event.key == pygame.K_SPACE:
                    # Centrar en checkpoint actual
                    current = self.graph.get_current_checkpoint()
                    self.camera.center_on(current.render_x, current.render_y)
                    print(f"📍 Centrado en Checkpoint #{current.id}")
    
    def _create_node_in_direction(self, parent_checkpoint_id, direction):
        """Crea un nuevo checkpoint en la dirección especificada y mueve el bot ahí"""
        # Verificar que no haya ya una conexión en esa dirección
        parent = self.graph.checkpoints.get(parent_checkpoint_id)
        if parent and direction in parent.connections:
            print(f"❌ Ya existe un checkpoint en {direction.value} del checkpoint #{parent_checkpoint_id}\n")
            return
        
        # Por defecto, crear con front=UNEXPLORED, laterales=BLOCKED
        front_state = DirectionState.UNEXPLORED
        left_state = DirectionState.BLOCKED
        right_state = DirectionState.BLOCKED
        
        # Crear el checkpoint
        # - parent_id: checkpoint desde el que sale
        # - arrival_direction: dirección en la que se mueve (vista desde parent)
        # - current_heading: la misma dirección (el bot se mueve en esa dirección)
        new_id = self.graph.create_checkpoint(
            parent_checkpoint_id,  # parent_id
            direction,             # arrival_direction (desde parent)
            front_state,
            left_state,
            right_state,
            direction              # current_heading (bot mirando en esa dirección)
        )
        
        opposite = Cardinal.opposite(direction)
        print(f"✅ Checkpoint #{new_id} creado ({direction.value})")
        print(f"🔗 Conectado a Checkpoint #{parent_checkpoint_id} desde {opposite.value}")
        print(f"🤖 Ahora en Checkpoint #{new_id}\n")
        
        # Centrar cámara en el nuevo checkpoint
        current = self.graph.get_current_checkpoint()
        self.camera.center_on(current.render_x, current.render_y)
        current = self.graph.get_current_checkpoint()
        self.camera.center_on(current.render_x, current.render_y)
    
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
        
        # Print route code
        if cmd in ['PRINT', 'P']:
            route_code = self.graph.generate_route_code()
            print("\n" + "="*70)
            print(route_code)
            print("="*70 + "\n")
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
        
        # Dead-end (requiere ID)
        if cmd == 'DEADEND' and len(parts) >= 2:
            try:
                checkpoint_id = int(parts[1])
                self.graph.mark_as_dead_end(checkpoint_id)
            except ValueError:
                print("❌ ID inválido\n")
            return
        
        # Delete checkpoint (usa actual si no se especifica ID)
        if cmd in ['DELETE', 'DEL']:
            if len(parts) >= 2:
                try:
                    checkpoint_id = int(parts[1])
                    if self.graph.delete_checkpoint(checkpoint_id):
                        current = self.graph.get_current_checkpoint()
                        self.camera.center_on(current.render_x, current.render_y)
                except ValueError:
                    print("❌ ID inválido\n")
            else:
                # Borrar checkpoint actual
                current = self.graph.get_current_checkpoint()
                if self.graph.delete_checkpoint(current.id):
                    new_current = self.graph.get_current_checkpoint()
                    self.camera.center_on(new_current.render_x, new_current.render_y)
                    print(f"📍 Ahora en Checkpoint #{new_current.id}\n")
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
                
                if direction is None:
                    print(f"❌ Dirección inválida: {parts[2]}\n")
                    return
                
                state_str = parts[3].upper()
                
                # Mapear strings a estados (acepta múltiples variantes)
                state_map = {
                    'UNEXPLORED': DirectionState.UNEXPLORED,
                    'EXPLORED': DirectionState.EXPLORED,
                    'BLOCKED': DirectionState.BLOCKED,
                    'UN': DirectionState.UNEXPLORED,
                    'EX': DirectionState.EXPLORED,
                    'BL': DirectionState.BLOCKED,
                    'U': DirectionState.UNEXPLORED,
                    'E': DirectionState.EXPLORED,
                    'B': DirectionState.BLOCKED
                }
                
                if state_str not in state_map:
                    print(f"❌ Estado inválido: {state_str}\n")
                    print(f"   Usa: UNEXPLORED/UN/U, EXPLORED/EX/E, BLOCKED/BL/B\n")
                    return
                
                state = state_map[state_str]
                self.graph.update_checkpoint_direction(checkpoint_id, direction, state)
                
                # Mostrar confirmación con nombre completo
                state_names = {
                    DirectionState.UNEXPLORED: 'UNEXPLORED',
                    DirectionState.EXPLORED: 'EXPLORED',
                    DirectionState.BLOCKED: 'BLOCKED'
                }
                print(f"✅ Checkpoint #{checkpoint_id}: {direction.value} → {state_names[state]}\n")
            except (ValueError, AttributeError) as e:
                print(f"❌ Comando inválido: {e}\n")
            return
        
        # Crear nuevo checkpoint: <HEADING> <FRONT> <LEFT> <RIGHT>
        # HEADING = Dirección ACTUAL del bot (hacia dónde está mirando)
        # Ejemplo: N BLOCKED UNEXPLORED UNEXPLORED
        if cmd in ['N', 'S', 'E', 'W'] and len(parts) >= 4:
            try:
                # IMPORTANTE: El bot reporta su HEADING ACTUAL, no la dirección de llegada
                current_heading = Cardinal.from_string(cmd)
                if current_heading is None:
                    print(f"❌ Heading inválido: {cmd}\n")
                    return
                
                front_str = parts[1].upper()
                left_str = parts[2].upper()
                right_str = parts[3].upper()
                
                # Mapear strings a estados (acepta múltiples variantes)
                state_map = {
                    'UNEXPLORED': DirectionState.UNEXPLORED,
                    'EXPLORED': DirectionState.EXPLORED,
                    'BLOCKED': DirectionState.BLOCKED,
                    'UN': DirectionState.UNEXPLORED,
                    'EX': DirectionState.EXPLORED,
                    'BL': DirectionState.BLOCKED,
                    'U': DirectionState.UNEXPLORED,
                    'E': DirectionState.EXPLORED,
                    'B': DirectionState.BLOCKED
                }
                
                if front_str not in state_map or left_str not in state_map or right_str not in state_map:
                    invalid = [s for s in [front_str, left_str, right_str] if s not in state_map]
                    print(f"❌ Estado inválido: {', '.join(invalid)}\n")
                    print(f"   Usa: UNEXPLORED/UN/U, EXPLORED/EX/E, BLOCKED/BL/B\n")
                    return
                
                front_state = state_map[front_str]
                left_state = state_map[left_str]
                right_state = state_map[right_str]
                
                # Calcular dirección de llegada basándose en el heading anterior y el actual
                # Si el bot gira, la dirección de llegada es opuesta al nuevo heading
                # Si el bot avanza recto, la dirección de llegada es opuesta al heading actual
                current_cp = self.graph.get_current_checkpoint()
                
                # Determinar dirección desde parent hacia este nuevo checkpoint
                # El bot avanzó en la dirección de su heading ANTERIOR
                arrival_direction = self.current_heading
                
                # Verificar que no haya ya una conexión en esa dirección
                if arrival_direction in current_cp.connections:
                    print(f"❌ Ya existe un checkpoint en {arrival_direction.value} del checkpoint #{current_cp.id}")
                    print(f"   No se puede crear otro checkpoint en la misma dirección\n")
                    return
                
                # Crear checkpoint
                new_checkpoint = self.graph.create_checkpoint(
                    parent_id=current_cp.id,
                    arrival_direction=arrival_direction,
                    front_state=front_state,
                    left_state=left_state,
                    right_state=right_state,
                    current_heading=current_heading
                )
                
                # Mover a nuevo checkpoint
                self.graph.set_current_checkpoint(new_checkpoint.id)
                
                # Actualizar heading actual
                self.current_heading = current_heading
                
                # Centrar cámara
                self.camera.center_on(new_checkpoint.render_x, new_checkpoint.render_y)
                
                print(f"🧭 Bot mirando: {current_heading.value}")
                print(f"🤖 Ahora en Checkpoint #{new_checkpoint.id}\n")
                
            except Exception as e:
                print(f"❌ Error al crear checkpoint: {e}")
                print("Formato: <HEADING> <FRONT> <LEFT> <RIGHT>")
                print("HEADING = Dirección actual del bot (N/S/E/W)")
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

