"""
Simple graph renderer for checkpoint visualization
Dibuja nodos (checkpoints) y sus conexiones
"""

import pygame
import math
from config import Config
from graph_state import MazeGraph, DirectionState, Cardinal


class GraphRenderer:
    """Renderizador simple para el grafo de checkpoints"""
    
    def __init__(self, screen, camera, graph: MazeGraph):
        self.screen = screen
        self.camera = camera
        self.graph = graph
        
        # Fuentes
        self.font = pygame.font.Font(None, Config.FONT_SIZE)
        self.font_small = pygame.font.Font(None, Config.FONT_SIZE_SMALL)
    
    def draw(self):
        """Dibuja todo el grafo"""
        # Fondo
        self.screen.fill(Config.COLOR_BG)
        
        # Dibuja conexiones primero (debajo de los nodos)
        self._draw_connections()
        
        # Dibuja checkpoints
        self._draw_checkpoints()
        
        # UI overlay
        self._draw_ui()
    
    def _draw_connections(self):
        """Dibuja las conexiones entre checkpoints"""
        connections = self.graph.get_connection_endpoints()
        
        for x1, y1, x2, y2 in connections:
            screen_pos1 = self.camera.world_to_screen(x1, y1)
            screen_pos2 = self.camera.world_to_screen(x2, y2)
            
            pygame.draw.line(
                self.screen,
                Config.COLOR_CONNECTION,
                screen_pos1,
                screen_pos2,
                max(1, int(3 * self.camera.zoom))
            )
    
    def _draw_checkpoints(self):
        """Dibuja todos los checkpoints"""
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
            
            # Dibujar círculo del checkpoint
            radius = max(5, int(Config.CHECKPOINT_RADIUS * self.camera.zoom))
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            
            # Borde
            pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), radius, 2)
            
            # Dibujar indicadores de direcciones
            self._draw_direction_indicators(checkpoint, screen_x, screen_y, radius)
            
            # ID del checkpoint (si está habilitado)
            if Config.SHOW_IDS and self.camera.zoom > 0.5:
                text = self.font_small.render(f"#{checkpoint.id}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x, screen_y))
                self.screen.blit(text, text_rect)
    
    def _draw_direction_indicators(self, checkpoint, cx, cy, radius):
        """Dibuja indicadores visuales de las direcciones del checkpoint"""
        if self.camera.zoom < 0.6:
            return  # No dibujar si el zoom es muy pequeño
        
        # Offset para los indicadores (fuera del círculo)
        indicator_offset = radius + 15
        indicator_size = max(4, int(8 * self.camera.zoom))
        
        # Mapeo de direcciones a offsets
        direction_offsets = {
            Cardinal.NORTH: (0, -indicator_offset),
            Cardinal.SOUTH: (0, indicator_offset),
            Cardinal.EAST: (indicator_offset, 0),
            Cardinal.WEST: (-indicator_offset, 0)
        }
        
        for direction, state in checkpoint.directions.items():
            dx, dy = direction_offsets[direction]
            indicator_x = cx + dx
            indicator_y = cy + dy
            
            # Color según estado
            if state == DirectionState.UNEXPLORED:
                color = Config.COLOR_UNEXPLORED
            elif state == DirectionState.EXPLORED:
                color = Config.COLOR_EXPLORED
            else:  # BLOCKED
                color = Config.COLOR_BLOCKED
            
            # Dibujar indicador
            pygame.draw.circle(
                self.screen,
                color,
                (int(indicator_x), int(indicator_y)),
                indicator_size
            )
            
            # Letra de dirección (si zoom es suficiente)
            if self.camera.zoom > 0.8:
                letter = direction.value
                text = self.font_small.render(letter, True, (0, 0, 0))
                text_rect = text.get_rect(center=(int(indicator_x), int(indicator_y)))
                self.screen.blit(text, text_rect)
    
    def _draw_ui(self):
        """Dibuja overlay con información"""
        y_offset = 15
        
        # Estadísticas del grafo
        stats = self.graph.get_stats()
        current_cp = self.graph.get_current_checkpoint()
        
        info_lines = [
            f"Checkpoint Actual: #{current_cp.id}",
            f"Total Checkpoints: {stats['total_checkpoints']}",
            f"Dead-ends: {stats['dead_ends']}",
            f"Direcciones sin explorar: {stats['unexplored_directions']}",
            f"Zoom: {self.camera.zoom:.2f}x",
        ]
        
        if stats['exploration_complete']:
            info_lines.append("✅ EXPLORACIÓN COMPLETA")
        
        # Renderizar
        for line in info_lines:
            text = self.font_small.render(line, True, Config.COLOR_TEXT)
            self.screen.blit(text, (15, y_offset))
            y_offset += 22
        
        # Instrucciones en la parte inferior
        instructions = [
            "━━━ CONTROLES ━━━",
            "Drag: Pan | Scroll: Zoom | Space: Centrar en checkpoint actual",
            "",
            "━━━ COMANDOS ━━━",
            "N/S/E/W: Crear checkpoint en dirección (ej: 'N BLOCKED UNEXPLORED UNEXPLORED')",
            "U: Marcar dirección como UNEXPLORED | B: Marcar como BLOCKED",
            "D: Marcar checkpoint actual como dead-end",
            "R: Reset completo | ESC: Salir"
        ]
        
        y_offset = Config.WINDOW_HEIGHT - (len(instructions) * 20) - 10
        for line in instructions:
            text = self.font_small.render(line, True, Config.COLOR_TEXT_DIM)
            self.screen.blit(text, (15, y_offset))
            y_offset += 20
