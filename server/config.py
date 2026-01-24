"""
Configuration file for MazeRunner - Graph-based visualization
"""

class Config:
    # ============ Ventana ============
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FPS = 60
    
    # ============ Grafo ============
    CHECKPOINT_SPACING = 100    # pixels - distancia entre checkpoints
    CHECKPOINT_RADIUS = 22      # pixels - radio del checkpoint
    
    # ============ Colores ============
    COLOR_BG = (20, 22, 30)                     # Fondo oscuro profesional
    COLOR_CHECKPOINT_NORMAL = (80, 140, 200)    # Checkpoint normal (azul suave)
    COLOR_CHECKPOINT_CURRENT = (80, 220, 120)   # Checkpoint actual (verde esmeralda)
    COLOR_CHECKPOINT_DEAD_END = (220, 70, 70)   # Dead-end (rojo)
    COLOR_CONNECTION = (120, 140, 160)          # Conexión explorada (gris azulado)
    
    # Estados de dirección
    COLOR_UNEXPLORED = (255, 230, 80)   # Amarillo brillante
    COLOR_EXPLORED = (80, 220, 120)     # Verde esmeralda
    COLOR_BLOCKED = (240, 80, 80)       # Rojo coral
    
    # UI
    COLOR_TEXT = (235, 235, 240)
    COLOR_TEXT_DIM = (140, 145, 155)
    FONT_SIZE = 20
    FONT_SIZE_SMALL = 15
    
    # ============ Cámara ============
    INITIAL_ZOOM = 1.0
    ZOOM_SPEED = 0.15
    MIN_ZOOM = 0.3
    MAX_ZOOM = 3.0
    
    # ============ Debug ============
    DEBUG_MODE = True
    SHOW_IDS = True