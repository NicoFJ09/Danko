"""
Configuration file for MazeRunner map simulator
All tunable parameters in one place
"""

class MapConfig:
    # ============ Detección de cambios ============
    CONSISTENCY_THRESHOLD = 2  # cm - variación aceptable entre medidas consecutivas
    CHANGE_THRESHOLD = 5       # cm - cambio mínimo para considerarlo significativo
    CONFIRMATION_COUNT = 1     # cantidad de medidas consecutivas necesarias para confirmar cambio
    
    # ============ Límites físicos del laberinto ============
    MAX_VALID_DISTANCE = 100   # cm - cualquier lectura mayor es descartada como alucinación
    WALL_THRESHOLD = 5         # cm - si distancia < 5cm es pared continua
    
    # ============ Grid y movimiento ============
    CELL_SIZE = 20             # cm - tamaño nominal de una celda del grid
    MOVEMENT_THRESHOLD = 10    # cm - movimiento acumulado necesario para cambiar de celda
    
    # ============ Visualización ============
    WINDOW_WIDTH = 1200        # pixels
    WINDOW_HEIGHT = 800        # pixels
    CELL_PIXEL_SIZE = 40       # pixels - tamaño de cada celda en pantalla
    
    # Colores (RGB)
    COLOR_BG = (20, 20, 30)              # Fondo oscuro
    COLOR_GRID = (50, 50, 60)            # Líneas del grid
    COLOR_WALL = (255, 255, 255)         # Paredes blancas
    COLOR_EXPLORED = (80, 120, 80)       # Celdas exploradas (verde oscuro)
    COLOR_CURRENT = (100, 200, 255)      # Celda actual del bot (azul)
    COLOR_PATH = (150, 150, 200)         # Trail del camino recorrido
    
    # Cámara
    INITIAL_ZOOM = 5.0         # Zoom inicial
    ZOOM_SPEED = 0.1           # Velocidad de zoom con scroll
    MIN_ZOOM = 0.2             # Zoom mínimo
    MAX_ZOOM = 5.0             # Zoom máximo
    PAN_SPEED = 1.0            # Velocidad de pan con drag
    
    # ============ Debugging ============
    DEBUG_MODE = True          # Mostrar info de debug en consola
    SHOW_SENSOR_RAYS = True    # Dibujar rayos de sensores en el mapa