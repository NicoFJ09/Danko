"""
Simple graph renderer for checkpoint visualization
Dibuja nodos (checkpoints) y sus conexiones con estilo anti-aliased
"""

import pygame
import pygame.gfxdraw
import math
from config import Config
from graph_state import MazeGraph, DirectionState, Cardinal
from graph_interaction import GraphInteraction


class GraphRenderer:
    """Renderizador simple para el grafo de checkpoints"""
    
    def __init__(self, screen, camera, graph: MazeGraph):
        self.screen = screen
        self.camera = camera
        self.graph = graph
        
        # Sistema de interacción
        self.interaction = GraphInteraction(graph, camera, Config.CHECKPOINT_RADIUS)
        
        # Fuentes
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', Config.FONT_SIZE, bold=True)
        self.font_small = pygame.font.SysFont('Arial', Config.FONT_SIZE_SMALL)
    
    def draw(self):
        """Dibuja todo el grafo"""
        # Fondo
        self.screen.fill(Config.COLOR_BG)
        
        # Dibuja conexiones primero (debajo de los nodos)
        self._draw_connections()
        
        # Dibuja flechas para crear nodos
        self._draw_arrows()
        
        # Dibuja checkpoints
        self._draw_checkpoints()
        
        # UI overlay
        self._draw_ui()
    
    def _draw_connections(self):
        """Dibuja las conexiones entre checkpoints con anti-aliasing"""
        connections = self.graph.get_connection_endpoints()
        
        for x1, y1, x2, y2 in connections:
            screen_pos1 = self.camera.world_to_screen(x1, y1)
            screen_pos2 = self.camera.world_to_screen(x2, y2)
            
            # Línea más gruesa con anti-aliasing
            width = max(2, int(4 * self.camera.zoom))
            
            # Dibujar línea suavizada
            self._draw_smooth_line(
                screen_pos1,
                screen_pos2,
                Config.COLOR_CONNECTION,
                width
            )
    
    def _draw_smooth_line(self, start, end, color, width):
        """Dibuja una línea suavizada"""
        # Para líneas más gruesas, dibujar múltiples líneas anti-aliased
        if width <= 2:
            pygame.draw.aaline(self.screen, color, start, end)
        else:
            # Línea base (sin anti-alias para grosor)
            pygame.draw.line(self.screen, color, start, end, width)
            # Borde suavizado
            lighter = tuple(min(255, c + 40) for c in color[:3])
            pygame.draw.aaline(self.screen, lighter, start, end)
    
    def _draw_checkpoints(self):
        """Dibuja todos los checkpoints con anti-aliasing"""
        for checkpoint in self.graph.get_all_checkpoints():
            screen_x, screen_y = self.camera.world_to_screen(
                checkpoint.render_x, checkpoint.render_y
            )
            
            # Determinar color del checkpoint
            if checkpoint.id == self.graph.current_checkpoint_id:
                color = Config.COLOR_CHECKPOINT_CURRENT
            elif checkpoint.is_dead_end:
                color = Config.COLOR_CHECKPOINT_DEAD_END
            else:
                color = Config.COLOR_CHECKPOINT_NORMAL
            
            # Dibujar círculo del checkpoint con anti-aliasing
            radius = max(5, int(Config.CHECKPOINT_RADIUS * self.camera.zoom))
            
            # Círculo relleno con anti-aliasing
            pygame.gfxdraw.filled_circle(self.screen, screen_x, screen_y, radius, color)
            pygame.gfxdraw.aacircle(self.screen, screen_x, screen_y, radius, color)
            
            # Borde blanco suavizado
            border_color = (255, 255, 255)
            pygame.gfxdraw.aacircle(self.screen, screen_x, screen_y, radius, border_color)
            pygame.gfxdraw.aacircle(self.screen, screen_x, screen_y, radius - 1, border_color)
            
            # Dibujar indicadores de direcciones
            self._draw_direction_indicators(checkpoint, screen_x, screen_y, radius)
            
            # ID del checkpoint (si está habilitado)
            if Config.SHOW_IDS and self.camera.zoom > 0.5:
                text = self.font_small.render(f"{checkpoint.id}", True, (0, 0, 0), color)
                text.set_alpha(200)
                text_rect = text.get_rect(center=(screen_x, screen_y))
                self.screen.blit(text, text_rect)
    
    def _draw_direction_indicators(self, checkpoint, cx, cy, radius):
        """Dibuja indicadores visuales de las direcciones del checkpoint con anti-aliasing"""
        if self.camera.zoom < 0.5:
            return  # No dibujar si el zoom es muy pequeño
        
        # Offset para los indicadores (fuera del círculo)
        indicator_offset = int(radius + 18)
        indicator_size = max(5, int(10 * self.camera.zoom))
        
        # Mapeo de direcciones a offsets
        direction_offsets = {
            Cardinal.NORTH: (0, -indicator_offset),
            Cardinal.SOUTH: (0, indicator_offset),
            Cardinal.EAST: (indicator_offset, 0),
            Cardinal.WEST: (-indicator_offset, 0)
        }
        
        for direction, state in checkpoint.directions.items():
            dx, dy = direction_offsets[direction]
            indicator_x = int(cx + dx)
            indicator_y = int(cy + dy)
            
            # Color según estado
            if state == DirectionState.UNEXPLORED:
                color = Config.COLOR_UNEXPLORED
            elif state == DirectionState.EXPLORED:
                color = Config.COLOR_EXPLORED
            else:  # BLOCKED
                color = Config.COLOR_BLOCKED
            
            # Dibujar indicador con anti-aliasing
            pygame.gfxdraw.filled_circle(self.screen, indicator_x, indicator_y, indicator_size, color)
            pygame.gfxdraw.aacircle(self.screen, indicator_x, indicator_y, indicator_size, color)
            
            # Borde oscuro para contraste
            border_color = tuple(max(0, c - 80) for c in color[:3])
            pygame.gfxdraw.aacircle(self.screen, indicator_x, indicator_y, indicator_size, border_color)
            
            # Letra de dirección (si zoom es suficiente)
            if self.camera.zoom > 0.7:
                letter = direction.value
                text = self.font_small.render(letter, True, (0, 0, 0))
                text_rect = text.get_rect(center=(indicator_x, indicator_y))
                self.screen.blit(text, text_rect)
    
    def _draw_ui(self):
        """Dibuja overlay con información mejorado"""
        # Panel semitransparente de fondo para info
        panel_height = 160
        panel = pygame.Surface((280, panel_height), pygame.SRCALPHA)
        panel.fill((15, 15, 25, 200))
        self.screen.blit(panel, (10, 10))
        
        y_offset = 20
        
        # Estadísticas del grafo
        stats = self.graph.get_stats()
        current_cp = self.graph.get_current_checkpoint()
        
        # Título
        title = self.font.render("MazeRunner", True, (100, 200, 255))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        info_lines = [
            f"Checkpoint: #{current_cp.id}",
            f"Total: {stats['total_checkpoints']}",
            f"Dead-ends: {stats['dead_ends']}",
            f"Sin explorar: {stats['unexplored_directions']}",
            f"Zoom: {self.camera.zoom:.1f}x",
        ]
        
        # Renderizar con sombra
        for line in info_lines:
            # Sombra
            shadow = self.font_small.render(line, True, (0, 0, 0))
            self.screen.blit(shadow, (21, y_offset + 1))
            # Texto
            text = self.font_small.render(line, True, Config.COLOR_TEXT)
            self.screen.blit(text, (20, y_offset))
            y_offset += 22
        
        # Indicador de completitud
        if stats['exploration_complete']:
            complete_text = self.font_small.render("✓ COMPLETO", True, Config.COLOR_EXPLORED)
            self.screen.blit(complete_text, (20, y_offset))
        
        # Panel de ayuda en la parte inferior
        help_panel = pygame.Surface((520, 100), pygame.SRCALPHA)
        help_panel.fill((15, 15, 25, 180))
        self.screen.blit(help_panel, (10, Config.WINDOW_HEIGHT - 110))
        
        help_lines_ui = [
            "🖱️ Clic en nodo = MOVE | Clic en indicador = toggle estado",
            "🖱️ Clic en flecha = crear nodo | Drag = pan | Wheel = zoom",
            "⌨️  R = RESET | D = DELETE | P = PRINT (genera código ruta)",
            "⌨️  N/S/E/W UN/BL/EX | stats | deadend | quit"
        ]
        
        y_help = Config.WINDOW_HEIGHT - 105
        for line in help_lines_ui:
            text = self.font_small.render(line, True, Config.COLOR_TEXT)
            self.screen.blit(text, (20, y_help))
            y_help += 20
    
    def _draw_arrows(self):
        """Dibuja flechas clickeables para crear nodos en direcciones libres"""
        for checkpoint in self.graph.get_all_checkpoints():
            arrows = self.interaction.get_arrows_for_checkpoint(checkpoint)
            
            for direction, (world_x, world_y) in arrows.items():
                screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
                
                # Tamaño de la flecha según zoom
                arrow_size = max(8, int(12 * self.camera.zoom))
                
                # Color de la flecha (semi-transparente)
                arrow_color = (100, 200, 100, 180)  # Verde claro
                
                # Dibujar flecha según dirección
                if direction == Cardinal.NORTH:
                    # Triángulo apuntando arriba
                    points = [
                        (screen_x, screen_y - arrow_size),
                        (screen_x - arrow_size//2, screen_y + arrow_size//2),
                        (screen_x + arrow_size//2, screen_y + arrow_size//2)
                    ]
                elif direction == Cardinal.SOUTH:
                    # Triángulo apuntando abajo
                    points = [
                        (screen_x, screen_y + arrow_size),
                        (screen_x - arrow_size//2, screen_y - arrow_size//2),
                        (screen_x + arrow_size//2, screen_y - arrow_size//2)
                    ]
                elif direction == Cardinal.EAST:
                    # Triángulo apuntando derecha
                    points = [
                        (screen_x + arrow_size, screen_y),
                        (screen_x - arrow_size//2, screen_y - arrow_size//2),
                        (screen_x - arrow_size//2, screen_y + arrow_size//2)
                    ]
                else:  # WEST
                    # Triángulo apuntando izquierda
                    points = [
                        (screen_x - arrow_size, screen_y),
                        (screen_x + arrow_size//2, screen_y - arrow_size//2),
                        (screen_x + arrow_size//2, screen_y + arrow_size//2)
                    ]
                
                # Dibujar el triángulo
                pygame.draw.polygon(self.screen, arrow_color[:3], points)
                pygame.draw.aalines(self.screen, (80, 160, 80), True, points)
