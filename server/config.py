"""
Configuration file for MazeRunner - Graph-based visualization
Simplified settings for checkpoint-based maze representation
"""

class Config:
    # ============ Ventana ============
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FPS = 60
    
    # ============ Visualización de grafo ============
    CHECKPOINT_SPACING = 100    # pixels - distancia entre checkpoints conectados
    CHECKPOINT_RADIUS = 20      # pixels - radio del círculo del checkpoint
    
    # Colores (RGB)
    COLOR_BG = (25, 25, 35)                    # Fondo oscuro
    COLOR_CHECKPOINT_NORMAL = (100, 150, 200)  # Checkpoint normal (azul)
    COLOR_CHECKPOINT_CURRENT = (255, 200, 50)  # Checkpoint actual (amarillo)
    COLOR_CHECKPOINT_DEAD_END = (200, 80, 80)  # Dead-end (rojo)
    COLOR_CONNECTION = (150, 150, 180)         # Conexión explorada (gris azulado)
    
    # Estados de dirección (para indicadores visuales)
    COLOR_UNEXPLORED = (255, 255, 100)  # Amarillo - no explorado
    COLOR_EXPLORED = (100, 255, 100)    # Verde - explorado
    COLOR_BLOCKED = (255, 100, 100)     # Rojo - bloqueado
    
    # Texto
    COLOR_TEXT = (220, 220, 220)
    COLOR_TEXT_DIM = (150, 150, 150)
    FONT_SIZE = 18
    FONT_SIZE_SMALL = 14
    
    # ============ Cámara ============
    INITIAL_ZOOM = 1.0
    ZOOM_SPEED = 0.15
    MIN_ZOOM = 0.3
    MAX_ZOOM = 3.0
    
    # ============ Debug ============
    DEBUG_MODE = True           # Mostrar info de debug
    SHOW_GRID = False           # Mostrar grid de fondo (opcional)
    SHOW_IDS = True             # Mostrar IDs de checkpoints