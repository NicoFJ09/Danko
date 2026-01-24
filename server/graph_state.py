"""
Graph-based checkpoint system for MazeRunner
Nodos representan checkpoints, aristas representan conexiones exploradas
"""

from enum import Enum
from typing import Dict, Optional, List, Set


class DirectionState(Enum):
    """Estados posibles de una dirección en un checkpoint"""
    UNEXPLORED = "unexplored"  # No explorada aún
    EXPLORED = "explored"      # Ya explorada (hay conexión)
    BLOCKED = "blocked"        # Pared/bloqueada


class Cardinal(Enum):
    """Direcciones cardinales"""
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    
    @staticmethod
    def opposite(direction: 'Cardinal') -> 'Cardinal':
        """Retorna dirección opuesta"""
        opposites = {
            Cardinal.NORTH: Cardinal.SOUTH,
            Cardinal.SOUTH: Cardinal.NORTH,
            Cardinal.EAST: Cardinal.WEST,
            Cardinal.WEST: Cardinal.EAST
        }
        return opposites[direction]
    
    @staticmethod
    def from_string(s: str) -> Optional['Cardinal']:
        """Convierte string a Cardinal"""
        mapping = {'N': Cardinal.NORTH, 'S': Cardinal.SOUTH, 
                   'E': Cardinal.EAST, 'W': Cardinal.WEST}
        return mapping.get(s.upper())


class Checkpoint:
    """Representa un nodo/checkpoint en el laberinto"""
    
    def __init__(self, checkpoint_id: int, parent_id: Optional[int] = None):
        self.id = checkpoint_id
        self.parent_id = parent_id
        
        # Estados de cada dirección cardinal
        self.directions: Dict[Cardinal, DirectionState] = {
            Cardinal.NORTH: DirectionState.UNEXPLORED,
            Cardinal.SOUTH: DirectionState.UNEXPLORED,
            Cardinal.EAST: DirectionState.UNEXPLORED,
            Cardinal.WEST: DirectionState.UNEXPLORED
        }
        
        # Conexiones: mapea dirección -> ID del checkpoint conectado
        self.connections: Dict[Cardinal, int] = {}
        
        # Metadata
        self.is_dead_end = False
        self.visited_count = 0  # Cuántas veces se ha visitado
        
        # Posición para renderizado (se calcula automáticamente)
        self.render_x = 0
        self.render_y = 0
    
    def set_direction(self, direction: Cardinal, state: DirectionState):
        """Establece el estado de una dirección"""
        self.directions[direction] = state
    
    def connect_to(self, direction: Cardinal, checkpoint_id: int):
        """Establece conexión hacia otro checkpoint"""
        self.connections[direction] = checkpoint_id
        self.directions[direction] = DirectionState.EXPLORED
    
    def get_unexplored_directions(self, exclude_arrival: Optional[Cardinal] = None) -> List[Cardinal]:
        """Retorna lista de direcciones sin explorar (excluyendo dirección de llegada)"""
        unexplored = [
            direction for direction, state in self.directions.items()
            if state == DirectionState.UNEXPLORED
        ]
        
        if exclude_arrival and exclude_arrival in unexplored:
            unexplored.remove(exclude_arrival)
        
        return unexplored
    
    def get_explored_directions(self, exclude_arrival: Optional[Cardinal] = None) -> List[Cardinal]:
        """Retorna lista de direcciones exploradas (excluyendo dirección de llegada)"""
        explored = [
            direction for direction, state in self.directions.items()
            if state == DirectionState.EXPLORED
        ]
        
        if exclude_arrival and exclude_arrival in explored:
            explored.remove(exclude_arrival)
        
        return explored
    
    def has_unexplored(self) -> bool:
        """Verifica si tiene alguna dirección sin explorar"""
        return any(state == DirectionState.UNEXPLORED 
                   for state in self.directions.values())
    
    def __repr__(self):
        return f"Checkpoint(id={self.id}, parent={self.parent_id}, unexplored={self.has_unexplored()})"


class MazeGraph:
    """Grafo del laberinto - gestiona todos los checkpoints y sus conexiones"""
    
    def __init__(self):
        self.checkpoints: Dict[int, Checkpoint] = {}
        self.current_checkpoint_id = 0
        self.next_id = 1
        
        # Crear checkpoint inicial (#0)
        self._create_initial_checkpoint()
    
    def _create_initial_checkpoint(self):
        """Crea el checkpoint inicial en el origen"""
        checkpoint = Checkpoint(checkpoint_id=0, parent_id=None)
        checkpoint.render_x = 0
        checkpoint.render_y = 0
        self.checkpoints[0] = checkpoint
        print(f"✅ Checkpoint #0 creado (inicio)")
    
    def create_checkpoint(
        self, 
        parent_id: int,
        arrival_direction: Cardinal,
        front_state: DirectionState,
        left_state: DirectionState,
        right_state: DirectionState,
        current_heading: Cardinal
    ) -> Checkpoint:
        """
        Crea un nuevo checkpoint basado en lecturas de sensores
        
        Args:
            parent_id: ID del checkpoint desde el que se llegó
            arrival_direction: Dirección por la que se llegó (relativo al PARENT)
            front_state: Estado del sensor frontal (BLOCKED si ≤5cm, UNEXPLORED si >5cm)
            left_state: Estado del sensor izquierdo (BLOCKED si <20cm, UNEXPLORED si ≥20cm)
            right_state: Estado del sensor derecho (BLOCKED si <20cm, UNEXPLORED si ≥20cm)
            current_heading: Heading actual del bot (dirección absoluta)
        """
        checkpoint = Checkpoint(checkpoint_id=self.next_id, parent_id=parent_id)
        
        # Calcular direcciones absolutas según heading actual
        left_direction = self._rotate_direction(current_heading, -90)  # Izquierda
        right_direction = self._rotate_direction(current_heading, 90)  # Derecha
        back_direction = Cardinal.opposite(current_heading)  # Atrás
        
        # Asignar estados
        checkpoint.set_direction(current_heading, front_state)  # Frente
        checkpoint.set_direction(left_direction, left_state)    # Izquierda
        checkpoint.set_direction(right_direction, right_state)  # Derecha
        checkpoint.set_direction(back_direction, DirectionState.EXPLORED)  # Atrás (por donde llegó)
        
        # Conectar bidireccionalmente con parent
        checkpoint.connect_to(back_direction, parent_id)
        
        parent = self.checkpoints[parent_id]
        parent.connect_to(arrival_direction, checkpoint.id)
        
        # Calcular posición de renderizado basada en parent
        self._calculate_render_position(checkpoint, parent, arrival_direction)
        
        # Agregar al grafo
        self.checkpoints[self.next_id] = checkpoint
        print(f"✅ Checkpoint #{self.next_id} creado (parent: #{parent_id})")
        
        self.next_id += 1
        return checkpoint
    
    def _rotate_direction(self, direction: Cardinal, degrees: int) -> Cardinal:
        """Rota una dirección cardinal por grados (90, -90, 180)"""
        order = [Cardinal.NORTH, Cardinal.EAST, Cardinal.SOUTH, Cardinal.WEST]
        idx = order.index(direction)
        rotation_steps = degrees // 90
        new_idx = (idx + rotation_steps) % 4
        return order[new_idx]
    
    def _calculate_render_position(self, checkpoint: Checkpoint, parent: Checkpoint, direction: Cardinal):
        """Calcula posición de renderizado del checkpoint basado en su parent"""
        # Espaciado entre checkpoints (en píxeles)
        spacing = 100
        
        offset_map = {
            Cardinal.NORTH: (0, -spacing),
            Cardinal.SOUTH: (0, spacing),
            Cardinal.EAST: (spacing, 0),
            Cardinal.WEST: (-spacing, 0)
        }
        
        dx, dy = offset_map[direction]
        checkpoint.render_x = parent.render_x + dx
        checkpoint.render_y = parent.render_y + dy
    
    def update_checkpoint_direction(self, checkpoint_id: int, direction: Cardinal, state: DirectionState):
        """Actualiza el estado de una dirección en un checkpoint"""
        if checkpoint_id in self.checkpoints:
            self.checkpoints[checkpoint_id].set_direction(direction, state)
            print(f"🔄 Checkpoint #{checkpoint_id}: {direction.value} → {state.value}")
    
    def mark_as_dead_end(self, checkpoint_id: int):
        """Marca un checkpoint como dead-end"""
        if checkpoint_id in self.checkpoints:
            self.checkpoints[checkpoint_id].is_dead_end = True
            print(f"🚫 Checkpoint #{checkpoint_id} marcado como dead-end")
    
    def get_checkpoint(self, checkpoint_id: int) -> Optional[Checkpoint]:
        """Retorna un checkpoint por su ID"""
        return self.checkpoints.get(checkpoint_id)
    
    def set_current_checkpoint(self, checkpoint_id: int):
        """Establece el checkpoint actual"""
        if checkpoint_id in self.checkpoints:
            self.current_checkpoint_id = checkpoint_id
            self.checkpoints[checkpoint_id].visited_count += 1
    
    def get_current_checkpoint(self) -> Checkpoint:
        """Retorna el checkpoint actual"""
        return self.checkpoints[self.current_checkpoint_id]
    
    def find_next_unexplored_checkpoint(self) -> Optional[Checkpoint]:
        """Busca el siguiente checkpoint con direcciones UNEXPLORED siguiendo la cadena de parents"""
        current = self.get_current_checkpoint()
        
        # Primero verificar si el actual tiene unexplored
        if current.has_unexplored():
            return current
        
        # Buscar en la cadena de parents
        checkpoint = current
        while checkpoint.parent_id is not None:
            parent = self.get_checkpoint(checkpoint.parent_id)
            if parent is None:
                break
            if parent.has_unexplored():
                return parent
            checkpoint = parent
        
        return None  # No hay más checkpoints con unexplored
    
    def get_all_checkpoints(self) -> List[Checkpoint]:
        """Retorna lista de todos los checkpoints"""
        return list(self.checkpoints.values())
    
    def get_connection_endpoints(self) -> List[tuple]:
        """
        Retorna lista de conexiones para renderizar
        Formato: [(x1, y1, x2, y2), ...]
        """
        connections = []
        seen = set()
        
        for checkpoint in self.checkpoints.values():
            for direction, connected_id in checkpoint.connections.items():
                # Evitar duplicados (ambas direcciones de la conexión)
                connection_key = tuple(sorted([checkpoint.id, connected_id]))
                if connection_key not in seen:
                    seen.add(connection_key)
                    connected = self.checkpoints[connected_id]
                    connections.append((
                        checkpoint.render_x, checkpoint.render_y,
                        connected.render_x, connected.render_y
                    ))
        
        return connections
    
    def delete_checkpoint(self, checkpoint_id: int) -> bool:
        """
        Borra un checkpoint y todos sus DESCENDIENTES (hijos en el árbol).
        No se puede borrar el checkpoint #0 (raíz).
        Si se borra el checkpoint actual, se mueve al parent.
        
        Returns:
            True si se borró exitosamente, False si no se pudo borrar
        """
        # No permitir borrar el checkpoint inicial
        if checkpoint_id == 0:
            print("❌ No se puede borrar el checkpoint #0 (raíz)")
            return False
        
        # Verificar que existe
        if checkpoint_id not in self.checkpoints:
            print(f"❌ Checkpoint #{checkpoint_id} no existe")
            return False
        
        # Recolectar todos los descendientes (búsqueda recursiva)
        to_delete = self._collect_descendants(checkpoint_id)
        to_delete.add(checkpoint_id)  # Incluir el nodo mismo
        
        # Si el checkpoint actual está en la lista de borrado, mover al parent
        checkpoint = self.checkpoints[checkpoint_id]
        if self.current_checkpoint_id in to_delete:
            if checkpoint.parent_id is not None:
                self.current_checkpoint_id = checkpoint.parent_id
                print(f"📍 Checkpoint actual movido a #{checkpoint.parent_id} (parent)")
            else:
                self.current_checkpoint_id = 0
                print(f"📍 Checkpoint actual movido a #0 (raíz)")
        
        # Desconectar del parent
        if checkpoint.parent_id is not None:
            parent = self.checkpoints.get(checkpoint.parent_id)
            if parent:
                # Encontrar y eliminar la conexión desde el parent
                for direction, connected_id in list(parent.connections.items()):
                    if connected_id == checkpoint_id:
                        del parent.connections[direction]
                        parent.set_direction(direction, DirectionState.UNEXPLORED)
                        break
        
        # Borrar todos los checkpoints marcados
        deleted_count = 0
        for cp_id in sorted(to_delete):
            if cp_id in self.checkpoints:
                del self.checkpoints[cp_id]
                deleted_count += 1
        
        print(f"🗑️  Borrados {deleted_count} checkpoint(s): {sorted(to_delete)}")
        return True
    
    def _collect_descendants(self, checkpoint_id: int) -> Set[int]:
        """
        Recolecta recursivamente todos los descendientes de un checkpoint.
        Un descendiente es cualquier nodo cuyo parent_id apunta hacia arriba en el árbol.
        """
        descendants = set()
        
        # Buscar todos los checkpoints que tienen este como parent
        for cp_id, checkpoint in self.checkpoints.items():
            if checkpoint.parent_id == checkpoint_id:
                descendants.add(cp_id)
                # Recursivamente agregar los descendientes de este hijo
                descendants.update(self._collect_descendants(cp_id))
        
        return descendants
    
    def reset(self):
        """Resetea el grafo completamente"""
        self.checkpoints.clear()
        self.current_checkpoint_id = 0
        self.next_id = 1
        self._create_initial_checkpoint()
        print("🔄 Grafo reseteado")
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del grafo"""
        total_checkpoints = len(self.checkpoints)
        dead_ends = sum(1 for cp in self.checkpoints.values() if cp.is_dead_end)
        total_unexplored = sum(
            len(cp.get_unexplored_directions()) 
            for cp in self.checkpoints.values()
        )
        
        return {
            'total_checkpoints': total_checkpoints,
            'dead_ends': dead_ends,
            'unexplored_directions': total_unexplored,
            'exploration_complete': total_unexplored == 0
        }
    
    def generate_route_code(self) -> str:
        """
        Genera código Python para el bot con la ruta a seguir.
        Retorna string con código copiable.
        """
        # Ordenar checkpoints por ID
        sorted_checkpoints = sorted(self.checkpoints.values(), key=lambda cp: cp.id)
        
        # Generar RUTA: recorrer en orden de IDs siguiendo las conexiones
        ruta_steps = []
        for checkpoint in sorted_checkpoints:
            # Para cada conexión de este checkpoint
            for direction, destination_id in sorted(checkpoint.connections.items(), key=lambda x: x[1]):
                # Solo incluir si el destino tiene ID mayor (evitar duplicados)
                if destination_id > checkpoint.id:
                    ruta_steps.append((checkpoint.id, direction.value, destination_id))
        
        # Generar ESTADOS: mapear cada checkpoint a sus estados
        estados = {}
        for checkpoint in sorted_checkpoints:
            estados[checkpoint.id] = {
                'N': self._state_to_str(checkpoint.directions.get(Cardinal.NORTH, DirectionState.UNEXPLORED)),
                'S': self._state_to_str(checkpoint.directions.get(Cardinal.SOUTH, DirectionState.UNEXPLORED)),
                'E': self._state_to_str(checkpoint.directions.get(Cardinal.EAST, DirectionState.UNEXPLORED)),
                'W': self._state_to_str(checkpoint.directions.get(Cardinal.WEST, DirectionState.UNEXPLORED)),
            }
        
        # Formatear código Python
        output = "# === RUTA GENERADA DESDE SERVIDOR ===\n"
        output += "# Copiar y pegar en el código del bot\n\n"
        
        # RUTA
        output += "# Lista de pasos: (checkpoint_actual, dirección, checkpoint_destino)\n"
        output += "RUTA = [\n"
        for actual, dir_str, destino in ruta_steps:
            output += f"    ({actual}, '{dir_str}', {destino}),  # Paso: {actual} → {dir_str} → {destino}\n"
        output += "]\n\n"
        
        # ESTADOS
        output += "# Estados esperados en cada checkpoint (para validación sensores)\n"
        output += "# BL=Blocked, EX=Explored, UN=Unexplored\n"
        output += "ESTADOS = {\n"
        for cp_id, states in estados.items():
            output += f"    {cp_id}: {states},\n"
        output += "}\n\n"
        
        # Instrucciones de uso
        output += "# === USO EN EL BOT ===\n"
        output += "# for paso, (actual, direccion, destino) in enumerate(RUTA):\n"
        output += "#     validar_sensores(ESTADOS[actual])\n"
        output += "#     moverse_en_direccion(direccion)\n"
        output += "#     esperar_llegada_a_checkpoint(destino)\n"
        
        return output
    
    def _state_to_str(self, state: DirectionState) -> str:
        """Convierte DirectionState a string corto"""
        mapping = {
            DirectionState.BLOCKED: 'BL',
            DirectionState.EXPLORED: 'EX',
            DirectionState.UNEXPLORED: 'UN'
        }
        return mapping.get(state, 'UN')
