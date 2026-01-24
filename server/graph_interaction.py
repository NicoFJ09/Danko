"""
Manejo de interacciones del mouse con el grafo
"""

import math
from graph_state import DirectionState, Cardinal, Checkpoint


class GraphInteraction:
    """Maneja clics y interacciones del usuario con el grafo"""
    
    def __init__(self, graph, camera, checkpoint_radius):
        self.graph = graph
        self.camera = camera
        self.checkpoint_radius = checkpoint_radius
    
    def handle_click(self, screen_pos):
        """
        Maneja clic del mouse.
        Retorna: (tipo, data) donde tipo puede ser:
          - 'checkpoint': clic en centro de nodo, data = checkpoint_id
          - 'direction': clic en indicador de dirección, data = (checkpoint_id, direction)
          - 'arrow': clic en flecha para crear nodo, data = (checkpoint_id, direction)
          - None: clic en vacío
        """
        # Convertir a coordenadas del mundo
        world_pos = self.camera.screen_to_world(*screen_pos)
        
        # Verificar clic en cada checkpoint
        for checkpoint in self.graph.get_all_checkpoints():
            cp_x, cp_y = checkpoint.render_x, checkpoint.render_y
            distance = math.sqrt((world_pos[0] - cp_x)**2 + (world_pos[1] - cp_y)**2)
            
            # Ajustar radius por zoom
            radius = self.checkpoint_radius
            
            # Clic en centro del checkpoint (MOVE)
            if distance < radius * 0.5:
                return ('checkpoint', checkpoint.id)
            
            # Clic en indicador de dirección (TOGGLE estado)
            direction_result = self._check_direction_click(
                checkpoint, world_pos, cp_x, cp_y, radius
            )
            if direction_result:
                return ('direction', (checkpoint.id, direction_result))
            
            # Clic en flecha para crear nodo (solo si no hay conexión)
            arrow_result = self._check_arrow_click(
                checkpoint, world_pos, cp_x, cp_y, radius
            )
            if arrow_result:
                return ('arrow', (checkpoint.id, arrow_result))
        
        return (None, None)
    
    def _check_direction_click(self, checkpoint, world_pos, cp_x, cp_y, radius):
        """Verifica si se hizo clic en un indicador de dirección"""
        # Distancia desde el centro hasta los indicadores
        indicator_distance = radius + 15
        
        # Posiciones de los indicadores
        indicators = {
            Cardinal.NORTH: (cp_x, cp_y - indicator_distance),
            Cardinal.SOUTH: (cp_x, cp_y + indicator_distance),
            Cardinal.EAST: (cp_x + indicator_distance, cp_y),
            Cardinal.WEST: (cp_x - indicator_distance, cp_y)
        }
        
        # Radio del indicador (pequeño)
        indicator_radius = 8
        
        for direction, (ind_x, ind_y) in indicators.items():
            dist = math.sqrt((world_pos[0] - ind_x)**2 + (world_pos[1] - ind_y)**2)
            if dist < indicator_radius:
                return direction
        
        return None
    
    def _check_arrow_click(self, checkpoint, world_pos, cp_x, cp_y, radius):
        """Verifica si se hizo clic en una flecha para crear nodo"""
        # Flechas están más alejadas que los indicadores
        arrow_distance = radius + 40
        
        # Solo mostrar flechas en direcciones SIN conexión existente
        arrows = {}
        for direction in [Cardinal.NORTH, Cardinal.SOUTH, Cardinal.EAST, Cardinal.WEST]:
            # Verificar directamente si esta dirección tiene conexión
            if direction not in checkpoint.connections:
                # No hay conexión, agregar flecha
                if direction == Cardinal.NORTH:
                    arrows[direction] = (cp_x, cp_y - arrow_distance)
                elif direction == Cardinal.SOUTH:
                    arrows[direction] = (cp_x, cp_y + arrow_distance)
                elif direction == Cardinal.EAST:
                    arrows[direction] = (cp_x + arrow_distance, cp_y)
                elif direction == Cardinal.WEST:
                    arrows[direction] = (cp_x - arrow_distance, cp_y)
        
        # Verificar clic en alguna flecha
        arrow_click_radius = 12
        for direction, (arrow_x, arrow_y) in arrows.items():
            dist = math.sqrt((world_pos[0] - arrow_x)**2 + (world_pos[1] - arrow_y)**2)
            if dist < arrow_click_radius:
                return direction
        
        return None
    
    def get_arrows_for_checkpoint(self, checkpoint):
        """
        Retorna las posiciones de las flechas para crear nodos.
        Solo en direcciones SIN conexión existente.
        Retorna: dict {Cardinal: (x, y)}
        """
        arrows = {}
        cp_x, cp_y = checkpoint.render_x, checkpoint.render_y
        arrow_distance = self.checkpoint_radius + 40
        
        for direction in [Cardinal.NORTH, Cardinal.SOUTH, Cardinal.EAST, Cardinal.WEST]:
            # Solo agregar flecha si NO hay conexión en esta dirección
            if direction not in checkpoint.connections:
                if direction == Cardinal.NORTH:
                    arrows[direction] = (cp_x, cp_y - arrow_distance)
                elif direction == Cardinal.SOUTH:
                    arrows[direction] = (cp_x, cp_y + arrow_distance)
                elif direction == Cardinal.EAST:
                    arrows[direction] = (cp_x + arrow_distance, cp_y)
                elif direction == Cardinal.WEST:
                    arrows[direction] = (cp_x - arrow_distance, cp_y)
        
        return arrows
