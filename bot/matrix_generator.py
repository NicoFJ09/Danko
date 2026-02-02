import pygame
import sys

# --------------------------
# Mapas predeterminados
# --------------------------
MAPAS_PREDETERMINADOS = [
    # Mapa 0: Laberinto simple
    [
        [[1,0,0,1], [1,0,1,0], [1,0,1,1], [1,0,1,1], [1,0,1,1]],
        [[0,0,0,1], [0,1,1,0], [0,0,1,1], [0,0,1,1], [0,0,1,1]],
        [[0,0,0,1], [1,0,1,0], [0,1,1,1], [0,0,1,1], [0,0,1,1]],
        [[0,0,0,1], [0,1,1,0], [1,0,1,1], [0,0,1,1], [0,1,1,1]],
        [[0,1,0,1], [1,1,1,0], [0,1,1,1], [0,1,1,1], [1,1,1,1]]
    ],
    # Mapa 1: Pasillos cruzados
    [
        [[1,0,0,1], [1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,1,0]],
        [[0,0,0,1], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,1,0]],
        [[0,0,0,1], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,1,0]],
        [[0,0,0,1], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,1,0]],
        [[0,1,0,1], [0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,1,0]]
    ],
    # Mapa 2: Espiral
    [
        [[1,0,0,1], [1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,1,0]],
        [[0,0,1,1], [0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]],
        [[0,0,1,1], [1,0,0,1], [1,0,0,0], [1,0,0,0], [0,0,1,0]],
        [[0,0,1,1], [0,1,1,0], [0,1,1,0], [0,1,1,0], [0,0,1,0]],
        [[0,1,0,1], [1,1,0,0], [1,1,0,0], [1,1,0,0], [0,1,1,0]]
    ],
    [
    [[1,0,0,1],[1,0,0,0],[1,0,1,0],["S",0,0,1],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,1,0]],
    [[0,0,0,1],[0,0,0,0],[0,0,1,0],[0,0,0,1],[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,0,0,0],[0,0,1,0]],
    [[0,0,0,1],[0,0,0,0],[0,0,1,0],[0,0,0,1],[0,0,1,0],[1,0,0,1],[1,0,0,0],[0,0,0,0],[0,0,1,0]],
    [[0,1,0,1],[0,1,0,0],[0,1,1,0],[0,0,0,1],[0,0,1,0],[0,0,0,1],[0,0,0,0],[0,0,0,0],[0,0,1,0]],
    [[1,0,0,1],[1,0,0,0],[1,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,0,1],[0,0,1,0],[0,0,0,1],[0,0,1,0]],
    [[0,1,0,1],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,0,1],[0,0,1,0],[0,0,0,1],[0,0,1,0]],
    [[1,0,0,1],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[0,0,0,0],[0,0,1,0],[0,1,0,1],[0,1,1,0]],
    [[0,0,0,1],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,0,0,0],[1,0,1,0]],
    [[0,1,0,1],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,"E",0]]
]
]

# --------------------------
# Configuración del editor de laberinto
# --------------------------
FILAS = 9
COLS = 9

def cargar_mapa(indice=None):
    """
    Carga un mapa predeterminado o inicializa uno vacío con bordes
    Args:
        indice: Índice del mapa a cargar, si es None carga mapa vacío con bordes
    """
    global MATRIZ, camino_actual
    
    # Reiniciar el camino actual
    camino_actual = None
    
    # Inicializar matriz vacía
    MATRIZ = [[Celda() for _ in range(COLS)] for _ in range(FILAS)]
    
    if indice is not None and 0 <= indice < len(MAPAS_PREDETERMINADOS):
        # Copiar el mapa predeterminado y expandirlo a 9x9
        mapa_base = MAPAS_PREDETERMINADOS[indice]
        filas_base = len(mapa_base)
        cols_base = len(mapa_base[0])
        
        # Copiar el patrón base en el centro
        offset_y = (FILAS - filas_base) // 2
        offset_x = (COLS - cols_base) // 2
        
        for i in range(filas_base):
            for j in range(cols_base):
                for k in range(4):
                    MATRIZ[i + offset_y][j + offset_x][k] = mapa_base[i][j][k]
    else:
        # Marcar bordes exteriores
        for i in range(FILAS):
            for j in range(COLS):
                if i == 0:  # Primera fila - muro norte
                    MATRIZ[i][j][0] = 1
                if i == FILAS-1:  # Última fila - muro sur
                    MATRIZ[i][j][1] = 1
                if j == COLS-1:  # Última columna - muro este
                    MATRIZ[i][j][2] = 1
                if j == 0:  # Primera columna - muro oeste
                    MATRIZ[i][j][3] = 1

# Definir clase para celdas de la matriz
class Celda:
    def __init__(self):
        self.valores = [0, 0, 0, 0]
    
    def __getitem__(self, idx):
        return self.valores[idx]
    
    def __setitem__(self, idx, valor):
        self.valores[idx] = valor
    
    def __str__(self):
        return str(self.valores)
    
    def __len__(self):
        return len(self.valores)
    
    def __iter__(self):
        return iter(self.valores)
    
    def copy(self):
        nueva_celda = Celda()
        nueva_celda.valores = self.valores[:]
        return nueva_celda
    
    def limpiar_marcador(self, marcador):
        self.valores = [0 if v == marcador else v for v in self.valores]

# Inicializar matriz cargando el mapa predeterminado 3 (9x9)
cargar_mapa(3)  # Cargar el mapa 9x9 por defecto

CELDA_SIZE = 35  # Tamaño de cada celda en píxeles
MURO_WIDTH = 4   # Grosor del muro
MARGEN = 80     # Espacio extra alrededor de la matriz
BUTTON_HEIGHT = 40  # Altura del botón
BORDE_WIDTH = 3  # Grosor del borde exterior
INSTRUCCIONES_MARGEN = 200  # Espacio para instrucciones

# --------------------------
# Inicialización de Pygame
# --------------------------
pygame.init()

# Calcular dimensiones de la pantalla
matrix_width = COLS * CELDA_SIZE  # Ancho de la matriz
matrix_height = FILAS * CELDA_SIZE  # Alto de la matriz
screen_width = matrix_width + MARGEN*2 + INSTRUCCIONES_MARGEN + 100  # Ancho total con espacio extra para instrucciones
screen_height = matrix_height + MARGEN*2 + BUTTON_HEIGHT + 80  # Alto total con espacio extra para botón

# Configurar fuentes más grandes
font = pygame.font.Font(None, 32)  # Fuente más grande para mejor legibilidad
title_font = pygame.font.Font(None, 42)  # Fuente aún más grande para el título

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Editor de Laberinto - Haz clic en las líneas para crear muros")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)  # Fuente más grande
title_font = pygame.font.Font(None, 36)  # Fuente para título

# Importar solver
import matrix_solver

# Colores
BG_COLOR = (245, 245, 250)
GRID_COLOR = (180, 180, 180)
MURO_COLOR = (0, 0, 0)
MURO_HOVER_COLOR = (100, 100, 100)
CELDA_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
TEXT_COLOR = (255, 255, 255)
BORDE_COLOR = (60, 60, 60)
TITLE_COLOR = (40, 40, 40)
CAMINO_COLOR = (50, 205, 50)  # Verde claro para el camino
ENTRADA_COLOR = (0, 191, 255)  # Azul para entrada
SALIDA_COLOR = (255, 69, 0)   # Rojo-naranja para salida

# --------------------------
# Variables globales
# --------------------------
mouse_pos = (0, 0)
button_rect = None
camino_actual = None  # Almacena el camino encontrado
entrada_pos = None   # Posición de la entrada
salida_pos = None    # Posición de la salida
modo_entrada = False  # Modo de colocación de entrada
modo_salida = False   # Modo de colocación de salida

# Constantes para modos
MODO_NORMAL = "normal"
MODO_ENTRADA = "entrada"
MODO_SALIDA = "salida"
modo_actual = MODO_NORMAL

# Constantes para direcciones
NORTE = 0
SUR = 1
ESTE = 2
OESTE = 3

# --------------------------
# Funciones auxiliares
# --------------------------
def detectar_muro_click(mouse_x, mouse_y):
    """Detecta en qué muro se hizo clic y devuelve (fila, col, direccion)"""
    for i in range(FILAS):
        for j in range(COLS):
            x = MARGEN + j * CELDA_SIZE
            y = MARGEN + i * CELDA_SIZE
            
            # Detectar clic en muro Norte (horizontal arriba)
            if (x <= mouse_x <= x + CELDA_SIZE and 
                y - MURO_WIDTH//2 <= mouse_y <= y + MURO_WIDTH//2):
                return (i, j, 0)  # Norte
            
            # Detectar clic en muro Sur (horizontal abajo)
            if (x <= mouse_x <= x + CELDA_SIZE and 
                y + CELDA_SIZE - MURO_WIDTH//2 <= mouse_y <= y + CELDA_SIZE + MURO_WIDTH//2):
                return (i, j, 1)  # Sur
            
            # Detectar clic en muro Este (vertical derecha)
            if (x + CELDA_SIZE - MURO_WIDTH//2 <= mouse_x <= x + CELDA_SIZE + MURO_WIDTH//2 and 
                y <= mouse_y <= y + CELDA_SIZE):
                return (i, j, 2)  # Este
            
            # Detectar clic en muro Oeste (vertical izquierda)
            if (x - MURO_WIDTH//2 <= mouse_x <= x + MURO_WIDTH//2 and 
                y <= mouse_y <= y + CELDA_SIZE):
                return (i, j, 3)  # Oeste
    
    return None

def alternar_muro(fila, col, direccion):
    """
    Alterna el estado de un muro específico entre presente (1) y ausente (0)
    """
    # Verificar si hay un marcador especial (E o S)
    valor_actual = MATRIZ[fila][col][direccion]
    if isinstance(valor_actual, str):
        return  # No alterar si es una entrada o salida
    
    # Alternar el estado del muro
    nuevo_estado = 1 - valor_actual
    MATRIZ[fila][col][direccion] = nuevo_estado
    
    # Si es un muro interior, actualizar también la celda adyacente
    # pero solo si no hay marcador especial en la celda adyacente
    if direccion == NORTE and fila > 0:  # Muro norte
        if not isinstance(MATRIZ[fila-1][col][SUR], str):
            MATRIZ[fila-1][col][SUR] = nuevo_estado
    elif direccion == SUR and fila < FILAS-1:  # Muro sur
        if not isinstance(MATRIZ[fila+1][col][NORTE], str):
            MATRIZ[fila+1][col][NORTE] = nuevo_estado
    elif direccion == ESTE and col < COLS-1:  # Muro este
        if not isinstance(MATRIZ[fila][col+1][OESTE], str):
            MATRIZ[fila][col+1][OESTE] = nuevo_estado
    elif direccion == OESTE and col > 0:  # Muro oeste
        if not isinstance(MATRIZ[fila][col-1][ESTE], str):
            MATRIZ[fila][col-1][ESTE] = nuevo_estado

def generar_codigo_matriz():
    """Genera el código de la matriz, lo imprime en consola y actualiza el camino"""
    global camino_actual, entrada_pos, salida_pos
    
    print("\n" + "="*50)
    print("CÓDIGO GENERADO:")
    print("="*50)
    print("MATRIZ = [")
    for i, fila in enumerate(MATRIZ):
        linea = "    ["
        for j, celda in enumerate(fila):
            linea += str(celda).replace(" ", "")
            if j < len(fila) - 1:
                linea += ","
        linea += "]"
        if i < len(MATRIZ) - 1:
            linea += ","
        print(linea)
    print("]")
    print("="*50)
    
    # Intentar encontrar un camino
    try:
        camino_actual = matrix_solver.encontrar_camino(MATRIZ)
        if camino_actual:
            entrada_pos = camino_actual[0]
            salida_pos = camino_actual[-1]
            print("\n✅ ¡Camino encontrado!")
            print(f"Longitud del camino: {len(camino_actual)} celdas")
            print(f"Distancia total: {len(camino_actual) * matrix_solver.CM_POR_CELDA} cm")
        else:
            print("\n❌ No se encontró un camino válido")
            entrada_pos = None
            salida_pos = None
    except Exception as e:
        print(f"\n❌ Error al buscar camino: {str(e)}")
        camino_actual = None
        entrada_pos = None
        salida_pos = None

def dibujar_laberinto():
    """Dibuja el laberinto con grid y muros"""
    screen.fill(BG_COLOR)
    
    # Dibujar borde exterior del área de juego
    border_rect = pygame.Rect(MARGEN - BORDE_WIDTH, MARGEN - BORDE_WIDTH, 
                             COLS * CELDA_SIZE + BORDE_WIDTH*2, 
                             FILAS * CELDA_SIZE + BORDE_WIDTH*2)
    pygame.draw.rect(screen, BORDE_COLOR, border_rect, BORDE_WIDTH)
    
    # Dibujar grid base
    for i in range(FILAS + 1):
        y = MARGEN + i * CELDA_SIZE
        pygame.draw.line(screen, GRID_COLOR, (MARGEN, y), (MARGEN + COLS * CELDA_SIZE, y), 1)
    
    for j in range(COLS + 1):
        x = MARGEN + j * CELDA_SIZE
        pygame.draw.line(screen, GRID_COLOR, (x, MARGEN), (x, MARGEN + FILAS * CELDA_SIZE), 1)
    
    # Dibujar celdas y camino
    for i in range(FILAS):
        for j in range(COLS):
            x = MARGEN + j * CELDA_SIZE
            y = MARGEN + i * CELDA_SIZE
            
            # Color base de la celda
            color = CELDA_COLOR
            
            # Colorear entrada y salida siempre (independiente del camino)
            celda = MATRIZ[i][j]
            if any(v == 'E' for v in celda):
                color = ENTRADA_COLOR
            elif any(v == 'S' for v in celda):
                color = SALIDA_COLOR
            # Si hay camino y no es entrada/salida, colorear como parte del camino
            elif camino_actual and (i, j) in camino_actual:
                color = CAMINO_COLOR
            
            # Resaltar celda si estamos en modo entrada/salida y el mouse está sobre ella
            if (modo_actual != MODO_NORMAL and
                MARGEN <= mouse_pos[0] <= MARGEN + COLS * CELDA_SIZE and
                MARGEN <= mouse_pos[1] <= MARGEN + FILAS * CELDA_SIZE):
                mouse_celda_x = (mouse_pos[0] - MARGEN) // CELDA_SIZE
                mouse_celda_y = (mouse_pos[1] - MARGEN) // CELDA_SIZE
                if i == mouse_celda_y and j == mouse_celda_x:
                    if modo_actual == MODO_ENTRADA:
                        color = tuple(map(lambda x: min(255, x + 50), ENTRADA_COLOR))
                    elif modo_actual == MODO_SALIDA:
                        color = tuple(map(lambda x: min(255, x + 50), SALIDA_COLOR))
            
            pygame.draw.rect(screen, color, (x+1, y+1, CELDA_SIZE-2, CELDA_SIZE-2))
    
    # Dibujar muros activos
    for i in range(FILAS):
        for j in range(COLS):
            x = MARGEN + j * CELDA_SIZE
            y = MARGEN + i * CELDA_SIZE
            celda = MATRIZ[i][j]
            
            # Norte (horizontal arriba)
            if celda[0]:
                pygame.draw.line(screen, MURO_COLOR, (x, y), (x + CELDA_SIZE, y), MURO_WIDTH)
            
            # Sur (horizontal abajo) 
            if celda[1]:
                pygame.draw.line(screen, MURO_COLOR, (x, y + CELDA_SIZE), (x + CELDA_SIZE, y + CELDA_SIZE), MURO_WIDTH)
            
            # Este (vertical derecha)
            if celda[2]:
                pygame.draw.line(screen, MURO_COLOR, (x + CELDA_SIZE, y), (x + CELDA_SIZE, y + CELDA_SIZE), MURO_WIDTH)
            
            # Oeste (vertical izquierda)
            if celda[3]:
                pygame.draw.line(screen, MURO_COLOR, (x, y), (x, y + CELDA_SIZE), MURO_WIDTH)

def dibujar_preview_muro(mouse_x, mouse_y):
    """Muestra preview del muro donde se haría clic"""
    muro_info = detectar_muro_click(mouse_x, mouse_y)
    if muro_info:
        i, j, direccion = muro_info
        x = MARGEN + j * CELDA_SIZE
        y = MARGEN + i * CELDA_SIZE
        
        # Dibujar preview del muro en gris
        if direccion == 0:  # Norte
            pygame.draw.line(screen, MURO_HOVER_COLOR, (x, y), (x + CELDA_SIZE, y), MURO_WIDTH)
        elif direccion == 1:  # Sur
            pygame.draw.line(screen, MURO_HOVER_COLOR, (x, y + CELDA_SIZE), (x + CELDA_SIZE, y + CELDA_SIZE), MURO_WIDTH)
        elif direccion == 2:  # Este
            pygame.draw.line(screen, MURO_HOVER_COLOR, (x + CELDA_SIZE, y), (x + CELDA_SIZE, y + CELDA_SIZE), MURO_WIDTH)
        elif direccion == 3:  # Oeste
            pygame.draw.line(screen, MURO_HOVER_COLOR, (x, y), (x, y + CELDA_SIZE), MURO_WIDTH)

def dibujar_boton():
    """Dibuja el botón para generar código"""
    global button_rect
    button_x = MARGEN
    button_y = MARGEN + FILAS * CELDA_SIZE + 20
    button_width = 250  # Botón más ancho
    
    button_rect = pygame.Rect(button_x, button_y, button_width, BUTTON_HEIGHT)
    
    # Color del botón (cambia si el mouse está encima)
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
    
    # Texto del botón
    text = font.render("Generar Código", True, TEXT_COLOR)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

def dibujar_titulo_e_instrucciones():
    """Dibuja el título y las instrucciones en pantalla"""
    # Título centrado en toda la pantalla
    titulo = title_font.render("Editor de Laberinto 9x9", True, TITLE_COLOR)
    titulo_rect = titulo.get_rect(center=(screen_width // 2, MARGEN // 2))
    screen.blit(titulo, titulo_rect)
    
    # Instrucciones en el lado derecho
    instrucciones = [
        "• Haz clic en las líneas para crear/quitar muros",
        "• Presiona 'E' para colocar entrada (azul)",
        "• Presiona 'S' para colocar salida (naranja)",
        "• Presiona 'G' o el botón para generar código",
        "   y buscar camino (verde)",
        "• Presiona 'C' para limpiar todo",
        "• Presiona 0-" + str(len(MAPAS_PREDETERMINADOS)-1) + " para cargar",
        "   mapas predeterminados",
        "• ESC cancela la selección de entrada/salida"
    ]
    
    # Posicionar instrucciones a la derecha de la matriz
    x_instrucciones = MARGEN + matrix_width + 40
    y_instrucciones = MARGEN + 60
    
    for i, texto in enumerate(instrucciones):
        text_surface = font.render(texto, True, (60, 60, 60))
        screen.blit(text_surface, (x_instrucciones, y_instrucciones + i * 30))

# --------------------------
# Bucle principal
# --------------------------
running = True
while running:
    clock.tick(60)  # 60 FPS para mejor respuesta
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                # Verificar si se hizo clic en el botón
                if button_rect and button_rect.collidepoint(mouse_pos):
                    generar_codigo_matriz()
                else:
                    # Si estamos en modo entrada/salida
                    if modo_actual != MODO_NORMAL:
                        # Convertir posición del mouse a coordenadas de celda
                        if (MARGEN <= mouse_pos[0] <= MARGEN + COLS * CELDA_SIZE and
                            MARGEN <= mouse_pos[1] <= MARGEN + FILAS * CELDA_SIZE):
                            cel_x = int((mouse_pos[0] - MARGEN) // CELDA_SIZE)
                            cel_y = int((mouse_pos[1] - MARGEN) // CELDA_SIZE)
                            
                            marcador = 'E' if modo_actual == MODO_ENTRADA else 'S'
                            
                            # Limpiar marcadores anteriores
                            for i in range(FILAS):
                                for j in range(COLS):
                                    MATRIZ[i][j].limpiar_marcador(marcador)
                            
                            # Solo permitir colocar en bordes exteriores
                            es_borde = cel_x == 0 or cel_x == COLS-1 or cel_y == 0 or cel_y == FILAS-1
                            
                            if es_borde:
                                # Determinar el borde más cercano
                                x_rel = (mouse_pos[0] - (MARGEN + cel_x * CELDA_SIZE)) / CELDA_SIZE
                                y_rel = (mouse_pos[1] - (MARGEN + cel_y * CELDA_SIZE)) / CELDA_SIZE
                                
                                # Encontrar el borde exterior más cercano
                                if cel_y == 0:  # Borde superior
                                    MATRIZ[cel_y][cel_x][0] = marcador
                                elif cel_y == FILAS-1:  # Borde inferior
                                    MATRIZ[cel_y][cel_x][1] = marcador
                                elif cel_x == COLS-1:  # Borde derecho
                                    MATRIZ[cel_y][cel_x][2] = marcador
                                elif cel_x == 0:  # Borde izquierdo
                                    MATRIZ[cel_y][cel_x][3] = marcador
                            
                            modo_actual = MODO_NORMAL  # Volver al modo normal
                    else:
                        # Verificar si se hizo clic en un muro
                        muro_info = detectar_muro_click(mouse_pos[0], mouse_pos[1])
                        if muro_info:
                            fila, col, direccion = muro_info
                            alternar_muro(fila, col, direccion)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if modo_actual != MODO_NORMAL:
                    modo_actual = MODO_NORMAL  # Cancelar modo especial
                else:
                    running = False
            elif event.key == pygame.K_c:  # Presionar 'C' para limpiar
                cargar_mapa()
            # Teclas numéricas para cargar mapas predeterminados
            elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, 
                             pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                mapa_num = int(event.unicode)
                cargar_mapa(mapa_num if mapa_num < len(MAPAS_PREDETERMINADOS) else None)
            elif event.key == pygame.K_g:  # Presionar 'G' para generar código
                generar_codigo_matriz()
            elif event.key == pygame.K_e:  # Presionar 'E' para modo entrada
                modo_actual = MODO_ENTRADA if modo_actual != MODO_ENTRADA else MODO_NORMAL
            elif event.key == pygame.K_s:  # Presionar 'S' para modo salida
                modo_actual = MODO_SALIDA if modo_actual != MODO_SALIDA else MODO_NORMAL
    
    # Dibujar todo
    dibujar_laberinto()
    
    # Dibujar preview del muro si el mouse está sobre uno
    if not (button_rect and button_rect.collidepoint(mouse_pos)):
        dibujar_preview_muro(mouse_pos[0], mouse_pos[1])
    
    dibujar_boton()
    dibujar_titulo_e_instrucciones()
    
    pygame.display.flip()

print("¡Editor de laberinto cerrado!")
pygame.quit()
sys.exit()
