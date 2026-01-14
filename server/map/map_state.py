"""
Map state manager - handles the grid, bot position, walls, and exploration
"""

from statistics import median
from config import MapConfig

class MapState:
    def __init__(self):
        # Bot state
        self.bot_cell = (0, 0)  # (row, col) - posición discreta en el grid
        self.bot_heading = 'N'  # N, S, E, W
        self.accumulated_movement = 0  # cm acumulados sin cambiar de celda
        
        # Grid: dict de celdas exploradas
        # Cada celda: {
        #   'explored': bool,
        #   'walls': {'N': bool, 'S': bool, 'E': bool, 'W': bool}
        # }
        self.grid = {}
        self._init_cell(self.bot_cell)
        
        # Sensor history para filtrado (guardamos últimas N medidas)
        self.history_size = MapConfig.CONFIRMATION_COUNT + 2
        self.sensor_history = {
            'front': [],
            'left': [],
            'right': []
        }
        
        # Valores estables actuales (después de filtrado)
        self.stable_values = {
            'front': None,
            'left': None,
            'right': None
        }
        
        # Path trail para visualización
        self.path_trail: list[tuple[int, int]] = [self.bot_cell]
        
    def _init_cell(self, cell):
        """Inicializar una celda nueva en el grid"""
        if cell not in self.grid:
            self.grid[cell] = {
                'explored': False,
                'walls': {'N': False, 'S': False, 'E': False, 'W': False}
            }
    
    def is_valid_reading(self, distance):
        """Verificar si una lectura es físicamente válida"""
        if distance < 0:
            return False
        if distance > MapConfig.MAX_VALID_DISTANCE:
            return False
        return True
    
    def add_sensor_reading(self, sensor_name, distance):
        """Agregar lectura de sensor al historial (si es válida)"""
        if not self.is_valid_reading(distance):
            if MapConfig.DEBUG_MODE:
                print(f"⚠️  Lectura inválida descartada: {sensor_name}={distance}cm")
            return False
        
        # Agregar a historial
        self.sensor_history[sensor_name].append(distance)
        
        # Mantener solo últimas N lecturas
        if len(self.sensor_history[sensor_name]) > self.history_size:
            self.sensor_history[sensor_name].pop(0)
        
        return True
    
    def get_stable_value(self, sensor_name):
        """Calcular valor estable usando mediana"""
        history = self.sensor_history[sensor_name]
        if len(history) < MapConfig.CONFIRMATION_COUNT:
            return None  # No hay suficientes datos todavía
        
        return median(history)
    
    def is_consistent(self, sensor_name):
        """Verificar si las últimas N lecturas son consistentes entre sí"""
        history = self.sensor_history[sensor_name]
        if len(history) < MapConfig.CONFIRMATION_COUNT:
            return False
        
        recent = history[-MapConfig.CONFIRMATION_COUNT:]
        max_diff = max(recent) - min(recent)
        
        return max_diff <= MapConfig.CONSISTENCY_THRESHOLD
    
    def has_significant_change(self, sensor_name, new_stable):
        """Verificar si hay cambio significativo vs valor estable anterior"""
        if self.stable_values[sensor_name] is None:
            return False
        
        old_stable = self.stable_values[sensor_name]
        change = abs(new_stable - old_stable)
        
        return change > MapConfig.CHANGE_THRESHOLD
    
    def update_sensors(self, front, left, right, heading):
        """
        Actualizar sensores y detectar cambios
        Retorna dict con eventos detectados
        """
        # Guardar heading anterior para detectar si hubo rotación
        previous_heading = self.bot_heading
        self.bot_heading = heading
        
        events = {
            'new_walls': [],
            'new_paths': [],
            'movement': None,
            'rotation': previous_heading != heading
        }
        
        # Si hubo rotación, limpiar historial de sensores (apuntan a nuevas direcciones)
        if events['rotation']:
            if MapConfig.DEBUG_MODE:
                print(f"🔄 Rotación detectada: {previous_heading} → {heading}")
            # Resetear historial porque los sensores apuntan a direcciones diferentes
            for sensor_name in ['front', 'left', 'right']:
                self.sensor_history[sensor_name] = []
                self.stable_values[sensor_name] = None
            self.accumulated_movement = 0  # Reset accumulated movement on rotation
        
        # Agregar lecturas al historial
        self.add_sensor_reading('front', front)
        self.add_sensor_reading('left', left)
        self.add_sensor_reading('right', right)
        
        # Procesar cada sensor
        for sensor_name in ['front', 'left', 'right']:
            if not self.is_consistent(sensor_name):
                continue  # No hay consistencia todavía
            
            new_stable = self.get_stable_value(sensor_name)
            if new_stable is None:
                continue
            
            # Detectar paredes
            if new_stable < MapConfig.WALL_THRESHOLD:
                direction = self._sensor_to_direction(sensor_name, heading)
                if not self.grid[self.bot_cell]['walls'][direction]:
                    self.grid[self.bot_cell]['walls'][direction] = True
                    events['new_walls'].append((self.bot_cell, direction))
                    if MapConfig.DEBUG_MODE:
                        print(f"🧱 Pared detectada: celda {self.bot_cell}, dirección {direction}")
            
            # Detectar cambios significativos (nuevo camino)
            if self.has_significant_change(sensor_name, new_stable):
                if new_stable >= MapConfig.WALL_THRESHOLD:
                    direction = self._sensor_to_direction(sensor_name, heading)
                    events['new_paths'].append((self.bot_cell, direction, new_stable))
                    if MapConfig.DEBUG_MODE:
                        print(f"🚪 Nuevo camino detectado: celda {self.bot_cell}, dirección {direction}, distancia {new_stable}cm")
            
            # Actualizar valor estable
            self.stable_values[sensor_name] = new_stable
        
        # Detectar movimiento SOLO si NO hubo rotación
        if self.stable_values['front'] is not None and not events['rotation']:
            events['movement'] = self._detect_movement()
        
        # Marcar celda actual como explorada
        self.grid[self.bot_cell]['explored'] = True
        
        return events
    
    def _sensor_to_direction(self, sensor_name, heading):
        """Convertir sensor (front/left/right) a dirección absoluta (N/S/E/W)"""
        direction_map = {
            'N': {'front': 'N', 'left': 'W', 'right': 'E'},
            'S': {'front': 'S', 'left': 'E', 'right': 'W'},
            'E': {'front': 'E', 'left': 'N', 'right': 'S'},
            'W': {'front': 'W', 'left': 'S', 'right': 'N'}
        }
        return direction_map[heading][sensor_name]
    
    def _detect_movement(self):
        """Detectar si el bot se movió basándose en cambios en sensores"""
        # Si sensor frontal disminuye, el bot avanzó
        if len(self.sensor_history['front']) < 2:
            return None
        
        prev_front = self.sensor_history['front'][-2]
        curr_front = self.sensor_history['front'][-1]
        
        movement = prev_front - curr_front  # Positivo = avanzó
        
        if abs(movement) > 2:  # Movimiento significativo
            self.accumulated_movement += abs(movement)
            
            # Si acumulamos suficiente, mover a siguiente celda
            if self.accumulated_movement >= MapConfig.MOVEMENT_THRESHOLD:
                self._move_to_next_cell()
                self.accumulated_movement = 0
                return True
        
        return None
    
    def _move_to_next_cell(self):
        """Mover bot a la siguiente celda según heading"""
        row, col = self.bot_cell
        
        if self.bot_heading == 'N':
            new_cell = (row - 1, col)
        elif self.bot_heading == 'S':
            new_cell = (row + 1, col)
        elif self.bot_heading == 'E':
            new_cell = (row, col + 1)
        elif self.bot_heading == 'W':
            new_cell = (row, col - 1)
        else:
            return
        
        self.bot_cell = new_cell
        self._init_cell(new_cell)
        self.path_trail.append(new_cell)
        
        if MapConfig.DEBUG_MODE:
            print(f"🤖 Bot movido a celda {new_cell}")
    
    def get_all_cells(self):
        """Retornar todas las celdas en el grid"""
        return list(self.grid.keys())
    
    def get_explored_cells(self):
        """Retornar solo celdas exploradas"""
        return [cell for cell, data in self.grid.items() if data['explored']]
    
    def get_walls_in_cell(self, cell):
        """Retornar direcciones con paredes en una celda"""
        if cell not in self.grid:
            return []
        return [direction for direction, has_wall in self.grid[cell]['walls'].items() if has_wall]