"""
MazeRunner - Editor de Laberinto Simple
Sistema de cuadrícula simplificado con numeración de camino
"""

import pygame
import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ==================== CONFIGURACIÓN ====================

class Config:
    """Configuración del editor"""
    # Ventana
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    FPS = 60
    
    # Cuadrícula
    CELL_SIZE = 50
    WALL_WIDTH = 4
    BORDER_WIDTH = 3
    
    # Colores
    COLOR_BG = (245, 245, 250)
    COLOR_CELL_NORMAL = (255, 255, 255)
    COLOR_CELL_NUMBERED = (200, 230, 255)
    COLOR_BORDER = (128, 128, 128)  # Gris para bordes
    COLOR_WALL_BLOCKED = (0, 0, 0)  # Negro para paredes bloqueadas
    COLOR_GRID = (200, 200, 200)
    COLOR_TEXT = (40, 40, 40)
    COLOR_BUTTON = (70, 130, 180)
    COLOR_BUTTON_HOVER = (100, 149, 237)


# ==================== DIRECCIÓN CARDINAL ====================

class Cardinal(Enum):
    """Direcciones cardinales"""
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3
    
    @staticmethod
    def opposite(direction: 'Cardinal') -> 'Cardinal':
        opposites = {
            Cardinal.NORTH: Cardinal.SOUTH,
            Cardinal.SOUTH: Cardinal.NORTH,
            Cardinal.EAST: Cardinal.WEST,
            Cardinal.WEST: Cardinal.EAST
        }
        return opposites[direction]


# ==================== CELDA ====================

class Cell:
    """Celda individual de la cuadrícula"""
    
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        # Paredes: True = bloqueada, False = abierta
        self.walls = {
            Cardinal.NORTH: False,
            Cardinal.SOUTH: False,
            Cardinal.EAST: False,
            Cardinal.WEST: False
        }
        self.number = 0  # 0 = sin numerar, 1+ = parte del camino


# ==================== GRID ====================

class Grid:
    """Sistema de cuadrícula del laberinto"""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Cell]] = []
        
        # Crear cuadrícula
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(Cell(i, j))
            self.grid.append(row)
        
        # Marcar bordes como bloqueados
        self._init_borders()
    
    def _init_borders(self):
        """Marca los bordes exteriores como bloqueados"""
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.grid[i][j]
                if i == 0:
                    cell.walls[Cardinal.NORTH] = True
                if i == self.rows - 1:
                    cell.walls[Cardinal.SOUTH] = True
                if j == self.cols - 1:
                    cell.walls[Cardinal.EAST] = True
                if j == 0:
                    cell.walls[Cardinal.WEST] = True
    
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Obtiene una celda"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None
    
    def toggle_wall(self, row: int, col: int, direction: Cardinal):
        """Alterna el estado de una pared"""
        cell = self.get_cell(row, col)
        if not cell:
            return
        
        # Toggle
        cell.walls[direction] = not cell.walls[direction]
        
        # Actualizar celda adyacente
        adj_row, adj_col = self._get_adjacent(row, col, direction)
        if adj_row is not None and adj_col is not None:
            adj_cell = self.get_cell(adj_row, adj_col)
            if adj_cell:
                adj_cell.walls[Cardinal.opposite(direction)] = cell.walls[direction]
    
    def _get_adjacent(self, row: int, col: int, direction: Cardinal) -> Tuple[Optional[int], Optional[int]]:
        """Obtiene coordenadas de celda adyacente"""
        if direction == Cardinal.NORTH:
            new_row, new_col = row - 1, col
        elif direction == Cardinal.SOUTH:
            new_row, new_col = row + 1, col
        elif direction == Cardinal.EAST:
            new_row, new_col = row, col + 1
        else:  # WEST
            new_row, new_col = row, col - 1
        
        if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
            return new_row, new_col
        return None, None
    
    def set_cell_number(self, row: int, col: int, number: int):
        """Establece el número de una celda"""
        cell = self.get_cell(row, col)
        if cell:
            cell.number = number
    
    def get_next_number(self) -> int:
        """Obtiene el siguiente número para el camino"""
        max_num = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j].number > max_num:
                    max_num = self.grid[i][j].number
        return max_num + 1
    
    def clear_numbers(self):
        """Limpia todos los números del camino"""
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j].number = 0
    
    def reset(self):
        """Resetea la cuadrícula"""
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.grid[i][j]
                cell.walls = {
                    Cardinal.NORTH: False,
                    Cardinal.SOUTH: False,
                    Cardinal.EAST: False,
                    Cardinal.WEST: False
                }
                cell.number = 0
        self._init_borders()
    
    def generate_code(self, orientation=0, direction_converter=None) -> str:
        """Genera código de grafos con direcciones cardinales"""
        # Obtener camino ordenado
        path = self._get_path()
        
        if not path:
            return "# ⚠️  No hay camino definido (numera las celdas primero)"
        
        # Generar RUTA
        ruta_lines = ["RUTA = ["]
        for i in range(len(path) - 1):
            current_row, current_col = path[i]
            next_row, next_col = path[i + 1]
            
            # Determinar dirección cardinal según orientación
            if direction_converter:
                direction = direction_converter(current_row, current_col, next_row, next_col)
            else:
                # Fallback: Norte arriba por defecto
                if next_row < current_row:
                    direction = 'N'
                elif next_row > current_row:
                    direction = 'S'
                elif next_col > current_col:
                    direction = 'E'
                else:
                    direction = 'W'
            
            ruta_lines.append(f"    ({i}, '{direction}', {i + 1}),")
        
        ruta_lines.append("]")
        
        # Generar ESTADOS
        estados_lines = ["", "ESTADOS = {"]
        
        for checkpoint_idx, (row, col) in enumerate(path):
            cell = self.get_cell(row, col)
            if not cell:
                continue
            
            # Convertir paredes a formato BL/EX según orientación
            estados = {}
            
            # Mapear direcciones del grid a cardinales
            # Arriba en grid
            if direction_converter:
                # Crear mapeo de direcciones grid → cardinal
                # IMPORTANTE: Calcular TODAS las direcciones, incluso en bordes
                grid_to_cardinal = {}
                
                # Usar valores ficticios en bordes para mantener consistencia
                # Norte en grid (arriba)
                if row > 0:
                    grid_to_cardinal[Cardinal.NORTH] = direction_converter(row, col, row - 1, col)
                else:
                    # En borde superior, simular movimiento hacia arriba
                    grid_to_cardinal[Cardinal.NORTH] = direction_converter(0, 0, -1, 0)
                
                # Sur en grid (abajo)
                if row < self.rows - 1:
                    grid_to_cardinal[Cardinal.SOUTH] = direction_converter(row, col, row + 1, col)
                else:
                    grid_to_cardinal[Cardinal.SOUTH] = direction_converter(0, 0, 1, 0)
                
                # Este en grid (derecha)
                if col < self.cols - 1:
                    grid_to_cardinal[Cardinal.EAST] = direction_converter(row, col, row, col + 1)
                else:
                    grid_to_cardinal[Cardinal.EAST] = direction_converter(0, 0, 0, 1)
                
                # Oeste en grid (izquierda)
                if col > 0:
                    grid_to_cardinal[Cardinal.WEST] = direction_converter(row, col, row, col - 1)
                else:
                    grid_to_cardinal[Cardinal.WEST] = direction_converter(0, 0, 0, -1)
                
                # Asignar estados para TODAS las cardinales
                for cardinal in ['N', 'S', 'E', 'W']:
                    # Buscar qué dirección del grid corresponde a esta cardinal
                    for grid_dir, card in grid_to_cardinal.items():
                        if card == cardinal:
                            estados[cardinal] = 'BL' if cell.walls[grid_dir] else 'EX'
                            break
            else:
                # Fallback: mapeo directo
                estados['N'] = 'BL' if cell.walls[Cardinal.NORTH] else 'EX'
                estados['S'] = 'BL' if cell.walls[Cardinal.SOUTH] else 'EX'
                estados['E'] = 'BL' if cell.walls[Cardinal.EAST] else 'EX'
                estados['W'] = 'BL' if cell.walls[Cardinal.WEST] else 'EX'
            
            estados_str = ", ".join([f"'{k}': '{v}'" for k, v in sorted(estados.items())])
            line = f"    {checkpoint_idx}: {{{estados_str}}},"
            estados_lines.append(line)
        
        estados_lines.append("}")
        
        return "\n".join(ruta_lines + estados_lines)
    
    def _get_path(self) -> List[Tuple[int, int]]:
        """Obtiene el camino ordenado por números"""
        numbered_cells = []
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.grid[i][j]
                if cell.number > 0:
                    numbered_cells.append((cell.number, i, j))
        
        numbered_cells.sort(key=lambda x: x[0])
        return [(row, col) for _, row, col in numbered_cells]


# ==================== INTERACCIÓN ====================

class Interaction:
    """Manejo de interacciones del mouse"""
    
    def __init__(self, grid: Grid, margin: int):
        self.grid = grid
        self.margin = margin
    
    def get_wall_at_pos(self, mouse_pos) -> Optional[Tuple[int, int, Cardinal]]:
        """Detecta clic en pared"""
        mouse_x, mouse_y = mouse_pos
        tolerance = Config.WALL_WIDTH
        
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                x = self.margin + j * Config.CELL_SIZE
                y = self.margin + i * Config.CELL_SIZE
                
                # Norte
                if (x <= mouse_x <= x + Config.CELL_SIZE and
                    y - tolerance <= mouse_y <= y + tolerance):
                    return (i, j, Cardinal.NORTH)
                
                # Sur
                if (x <= mouse_x <= x + Config.CELL_SIZE and
                    y + Config.CELL_SIZE - tolerance <= mouse_y <= y + Config.CELL_SIZE + tolerance):
                    return (i, j, Cardinal.SOUTH)
                
                # Este
                if (x + Config.CELL_SIZE - tolerance <= mouse_x <= x + Config.CELL_SIZE + tolerance and
                    y <= mouse_y <= y + Config.CELL_SIZE):
                    return (i, j, Cardinal.EAST)
                
                # Oeste
                if (x - tolerance <= mouse_x <= x + tolerance and
                    y <= mouse_y <= y + Config.CELL_SIZE):
                    return (i, j, Cardinal.WEST)
        
        return None
    
    def get_cell_at_pos(self, mouse_pos) -> Optional[Tuple[int, int]]:
        """Obtiene celda en posición del mouse"""
        mouse_x, mouse_y = mouse_pos
        
        if (mouse_x < self.margin or mouse_y < self.margin or
            mouse_x >= self.margin + self.grid.cols * Config.CELL_SIZE or
            mouse_y >= self.margin + self.grid.rows * Config.CELL_SIZE):
            return None
        
        col = int((mouse_x - self.margin) // Config.CELL_SIZE)
        row = int((mouse_y - self.margin) // Config.CELL_SIZE)
        
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            return (row, col)
        
        return None


# ==================== RENDERER ====================

class Renderer:
    """Renderizador de la cuadrícula"""
    
    def __init__(self, screen, grid: Grid, margin: int):
        self.screen = screen
        self.grid = grid
        self.margin = margin
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 15)
        self.font_number = pygame.font.SysFont('Arial', 24, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
    
    def draw(self):
        """Dibuja todo"""
        self.screen.fill(Config.COLOR_BG)
        
        # Título
        title = self.title_font.render("MazeRunner - Editor Simple", True, Config.COLOR_TEXT)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.margin // 2))
        self.screen.blit(title, title_rect)
        
        # Borde
        border_rect = pygame.Rect(
            self.margin - Config.BORDER_WIDTH,
            self.margin - Config.BORDER_WIDTH,
            self.grid.cols * Config.CELL_SIZE + Config.BORDER_WIDTH * 2,
            self.grid.rows * Config.CELL_SIZE + Config.BORDER_WIDTH * 2
        )
        pygame.draw.rect(self.screen, Config.COLOR_BORDER, border_rect, Config.BORDER_WIDTH)
        
        # Celdas
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                cell = self.grid.grid[i][j]
                x = self.margin + j * Config.CELL_SIZE
                y = self.margin + i * Config.CELL_SIZE
                
                color = Config.COLOR_CELL_NUMBERED if cell.number > 0 else Config.COLOR_CELL_NORMAL
                pygame.draw.rect(self.screen, color, (x + 1, y + 1, Config.CELL_SIZE - 2, Config.CELL_SIZE - 2))
                
                # Número
                if cell.number > 0:
                    text = self.font_number.render(str(cell.number), True, Config.COLOR_TEXT)
                    text_rect = text.get_rect(center=(x + Config.CELL_SIZE // 2, y + Config.CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)
        
        # Grid lines
        for i in range(self.grid.rows + 1):
            y = self.margin + i * Config.CELL_SIZE
            pygame.draw.line(self.screen, Config.COLOR_GRID, 
                           (self.margin, y), 
                           (self.margin + self.grid.cols * Config.CELL_SIZE, y), 1)
        
        for j in range(self.grid.cols + 1):
            x = self.margin + j * Config.CELL_SIZE
            pygame.draw.line(self.screen, Config.COLOR_GRID, 
                           (x, self.margin), 
                           (x, self.margin + self.grid.rows * Config.CELL_SIZE), 1)
        
        # Paredes bloqueadas
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                cell = self.grid.grid[i][j]
                x = self.margin + j * Config.CELL_SIZE
                y = self.margin + i * Config.CELL_SIZE
                
                for direction, blocked in cell.walls.items():
                    if not blocked:
                        continue
                    
                    # Determinar si es borde (gris) o pared interna (negra)
                    is_border = (
                        (direction == Cardinal.NORTH and i == 0) or
                        (direction == Cardinal.SOUTH and i == self.grid.rows - 1) or
                        (direction == Cardinal.EAST and j == self.grid.cols - 1) or
                        (direction == Cardinal.WEST and j == 0)
                    )
                    
                    color = Config.COLOR_BORDER if is_border else Config.COLOR_WALL_BLOCKED
                    
                    if direction == Cardinal.NORTH:
                        start, end = (x, y), (x + Config.CELL_SIZE, y)
                    elif direction == Cardinal.SOUTH:
                        start, end = (x, y + Config.CELL_SIZE), (x + Config.CELL_SIZE, y + Config.CELL_SIZE)
                    elif direction == Cardinal.EAST:
                        start, end = (x + Config.CELL_SIZE, y), (x + Config.CELL_SIZE, y + Config.CELL_SIZE)
                    else:  # WEST
                        start, end = (x, y), (x, y + Config.CELL_SIZE)
                    
                    pygame.draw.line(self.screen, color, start, end, Config.WALL_WIDTH)
        
        # UI
        self._draw_ui()
    
    def _draw_compass(self, orientation):
        """Dibuja brújula mostrando orientación cardinal"""
        # Centrar debajo del grid
        grid_bottom = self.margin + self.grid.rows * Config.CELL_SIZE
        available_height = self.screen.get_height() - grid_bottom - 60  # 60 = espacio para botón
        
        x_compass = self.margin + 30
        y_base = grid_bottom + (available_height - 150) // 2  # Centrado verticalmente
        
        # Mapeo de orientaciones
        mapping = {
            0: {'UP': 'N', 'DOWN': 'S', 'RIGHT': 'E', 'LEFT': 'W'},
            90: {'UP': 'E', 'DOWN': 'W', 'RIGHT': 'S', 'LEFT': 'N'},
            180: {'UP': 'S', 'DOWN': 'N', 'RIGHT': 'W', 'LEFT': 'E'},
            270: {'UP': 'W', 'DOWN': 'E', 'RIGHT': 'N', 'LEFT': 'S'}
        }
        
        dirs = mapping[orientation]
        
        # Etiqueta
        label = self.font.render("ORIENTACIÓN", True, Config.COLOR_TEXT)
        self.screen.blit(label, (x_compass, y_base))
        
        # Fondo
        compass_size = 90
        y_compass = y_base + 30
        pygame.draw.rect(self.screen, (240, 240, 245), 
                        (x_compass - 5, y_compass - 5, compass_size + 10, compass_size + 10))
        pygame.draw.rect(self.screen, (150, 150, 160), 
                        (x_compass - 5, y_compass - 5, compass_size + 10, compass_size + 10), 2)
        
        # Líneas cruz
        center_x = x_compass + compass_size // 2
        center_y = y_compass + compass_size // 2
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (center_x, y_compass + 5), (center_x, y_compass + compass_size - 5), 1)
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (x_compass + 5, center_y), (x_compass + compass_size - 5, center_y), 1)
        
        # Textos
        font_compass = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Arriba
        text = font_compass.render(dirs['UP'], True, (220, 20, 60) if dirs['UP'] == 'N' else Config.COLOR_TEXT)
        text_rect = text.get_rect(center=(center_x, y_compass + 16))
        self.screen.blit(text, text_rect)
        
        # Abajo
        text = font_compass.render(dirs['DOWN'], True, (220, 20, 60) if dirs['DOWN'] == 'N' else Config.COLOR_TEXT)
        text_rect = text.get_rect(center=(center_x, y_compass + compass_size - 16))
        self.screen.blit(text, text_rect)
        
        # Derecha
        text = font_compass.render(dirs['RIGHT'], True, (220, 20, 60) if dirs['RIGHT'] == 'N' else Config.COLOR_TEXT)
        text_rect = text.get_rect(center=(x_compass + compass_size - 16, center_y))
        self.screen.blit(text, text_rect)
        
        # Izquierda
        text = font_compass.render(dirs['LEFT'], True, (220, 20, 60) if dirs['LEFT'] == 'N' else Config.COLOR_TEXT)
        text_rect = text.get_rect(center=(x_compass + 16, center_y))
        self.screen.blit(text, text_rect)
        
        # Descripción a la derecha del cuadro
        orientation_names = {
            0: "Norte ↑ Arriba",
            90: "Este → Arriba", 
            180: "Sur ↓ Arriba",
            270: "Oeste ← Arriba"
        }
        desc = self.font_small.render(orientation_names[orientation], True, Config.COLOR_TEXT)
        self.screen.blit(desc, (x_compass + compass_size + 20, y_compass + 20))
        
        # Ayuda teclas a la derecha
        help1 = self.font_small.render("(Teclas: Q/E)", True, (100, 100, 100))
        self.screen.blit(help1, (x_compass + compass_size + 20, y_compass + 45))
    
    def _draw_ui(self):
        """Dibuja instrucciones"""
        x_info = self.margin + self.grid.cols * Config.CELL_SIZE + 20
        y_info = self.margin + 20
        
        lines = [
            "CONTROLES:",
            "",
            "• Clic en pared = toggle",
            "  (bloqueada/abierta)",
            "",
            "• Clic en celda = numerar",
            "• Arrastra = múltiples",
            "",
            "• Clic derecho = quitar",
            "",
            "• Q/E = rotar orientación",
            "• P = generar código",
            "• C = limpiar números",
            "• R = reset todo",
            "• ESC = salir",
            "",
            f"Grid: {self.grid.rows}x{self.grid.cols}",
        ]
        
        for i, text in enumerate(lines):
            if text.startswith("CONTROLES"):
                surface = self.font.render(text, True, Config.COLOR_TEXT)
            else:
                surface = self.font_small.render(text, True, Config.COLOR_TEXT)
            self.screen.blit(surface, (x_info, y_info + i * 25))
    
    def draw_button(self, rect):
        """Dibuja botón"""
        mouse_pos = pygame.mouse.get_pos()
        color = Config.COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else Config.COLOR_BUTTON
        
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
        
        text = self.font.render("Generar Código", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_wall_preview(self, mouse_pos, interaction):
        """Dibuja preview de pared"""
        wall_info = interaction.get_wall_at_pos(mouse_pos)
        if not wall_info:
            return
        
        row, col, direction = wall_info
        x = self.margin + col * Config.CELL_SIZE
        y = self.margin + row * Config.CELL_SIZE
        
        if direction == Cardinal.NORTH:
            start, end = (x, y), (x + Config.CELL_SIZE, y)
        elif direction == Cardinal.SOUTH:
            start, end = (x, y + Config.CELL_SIZE), (x + Config.CELL_SIZE, y + Config.CELL_SIZE)
        elif direction == Cardinal.EAST:
            start, end = (x + Config.CELL_SIZE, y), (x + Config.CELL_SIZE, y + Config.CELL_SIZE)
        else:  # WEST
            start, end = (x, y), (x, y + Config.CELL_SIZE)
        
        pygame.draw.line(self.screen, (100, 100, 100), start, end, Config.WALL_WIDTH + 2)


# ==================== APLICACIÓN PRINCIPAL ====================

class MazeEditor:
    """Editor de laberinto principal"""
    
    def __init__(self, rows: int, cols: int):
        pygame.init()
        
        self.margin = 80
        self.button_height = 40
        self.instructions_margin = 300  # Más espacio para la brújula
        
        matrix_width = cols * Config.CELL_SIZE
        matrix_height = rows * Config.CELL_SIZE
        
        screen_width = matrix_width + self.margin * 2 + self.instructions_margin
        screen_height = max(matrix_height + self.margin * 2 + self.button_height + 20, 700)  # Mínimo 700px
        
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"MazeRunner - Editor Simple ({rows}x{cols})")
        self.clock = pygame.time.Clock()
        
        self.grid = Grid(rows, cols)
        self.renderer = Renderer(self.screen, self.grid, self.margin)
        self.interaction = Interaction(self.grid, self.margin)
        
        button_x = self.margin
        button_y = self.margin + rows * Config.CELL_SIZE + 10
        self.button_rect = pygame.Rect(button_x, button_y, 250, self.button_height)
        
        self.running = True
        self.dragging = False  # Estado de arrastre
        self.last_numbered_cell = None  # Última celda numerada para evitar duplicados
        
        # Orientación del grid (0=Norte arriba, 90=Este arriba, 180=Sur arriba, 270=Oeste arriba)
        self.orientation = 0  # Rotación en grados
        
        print("\n" + "=" * 70)
        print("🤖 MAZERUNNER - EDITOR SIMPLE")
        print("=" * 70)
        print(f"\n📐 Cuadrícula: {rows}x{cols}")
        print("\n💡 CONTROLES:")
        print("   🖱️  Clic en pared = toggle bloqueada/abierta")
        print("   🖱️  Clic en celda = numerar (camino)")
        print("   🖱️  Mantén y arrastra = numerar múltiples celdas")
        print("   🖱️  Clic derecho en celda = quitar número")
        print("   ⌨️  Q/E = rotar orientación cardinal")
        print("   ⌨️  P = generar código | C = limpiar números | R = reset")
        print("=" * 70 + "\n")
    
    def handle_events(self):
        """Maneja eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    self._handle_left_click(event.pos)
                    self.dragging = True
                elif event.button == 3:  # Clic derecho
                    self._handle_right_click(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.last_numbered_cell = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self._handle_drag(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.grid.reset()
                    print("🔄 Reset completo\n")
                elif event.key == pygame.K_c:
                    self.grid.clear_numbers()
                    print("🔄 Números limpiados\n")
                elif event.key == pygame.K_p:
                    self._print_code()
                elif event.key == pygame.K_q:
                    self.orientation = (self.orientation - 90) % 360
                    print(f"🧭 Rotación: {self._get_orientation_name()}\n")
                elif event.key == pygame.K_e:
                    self.orientation = (self.orientation + 90) % 360
                    print(f"🧭 Rotación: {self._get_orientation_name()}\n")
    
    def _handle_left_click(self, pos):
        """Maneja clic izquierdo"""
        if self.button_rect.collidepoint(pos):
            self._print_code()
            return
        
        # Primero intentar pared
        wall_info = self.interaction.get_wall_at_pos(pos)
        if wall_info:
            row, col, direction = wall_info
            self.grid.toggle_wall(row, col, direction)
            cell = self.grid.get_cell(row, col)
            if cell:
                state = "BLOQUEADA" if cell.walls[direction] else "ABIERTA"
                print(f"✅ Pared ({row},{col}) {direction.name} → {state}\n")
            return
        
        # Si no es pared, intentar numerar celda
        cell_info = self.interaction.get_cell_at_pos(pos)
        if cell_info:
            row, col = cell_info
            cell = self.grid.get_cell(row, col)
            if cell:
                if cell.number == 0:
                    next_num = self.grid.get_next_number()
                    self.grid.set_cell_number(row, col, next_num)
                    print(f"🔢 Celda ({row},{col}) → Número {next_num}\n")
    
    def _handle_right_click(self, pos):
        """Maneja clic derecho"""
        cell_info = self.interaction.get_cell_at_pos(pos)
        if cell_info:
            row, col = cell_info
            self.grid.set_cell_number(row, col, 0)
            print(f"❌ Número eliminado de ({row},{col})\n")
    
    def _handle_drag(self, pos):
        """Maneja arrastre del mouse para numerar celdas"""
        # Solo numerar celdas, no paredes
        cell_info = self.interaction.get_cell_at_pos(pos)
        if cell_info:
            row, col = cell_info
            
            # Evitar numerar la misma celda múltiples veces en un solo arrastre
            if self.last_numbered_cell == (row, col):
                return
            
            cell = self.grid.get_cell(row, col)
            if cell and cell.number == 0:
                next_num = self.grid.get_next_number()
                self.grid.set_cell_number(row, col, next_num)
                self.last_numbered_cell = (row, col)
                print(f"🔢 Celda ({row},{col}) → Número {next_num}")
    
    def _get_orientation_name(self):
        """Retorna el nombre de la orientación actual"""
        names = {
            0: "Norte ↑ Arriba",
            90: "Este → Arriba", 
            180: "Sur ↓ Arriba",
            270: "Oeste ← Arriba"
        }
        return names.get(self.orientation, "Desconocido")
    
    def _grid_direction_to_cardinal(self, from_row, from_col, to_row, to_col):
        """Convierte movimiento del grid a dirección cardinal según orientación"""
        # Determinar dirección en el grid
        if to_row < from_row:  # Arriba
            grid_dir = 'UP'
        elif to_row > from_row:  # Abajo
            grid_dir = 'DOWN'
        elif to_col > from_col:  # Derecha
            grid_dir = 'RIGHT'
        else:  # Izquierda
            grid_dir = 'LEFT'
        
        # Mapeo según orientación
        # 0° = Norte arriba (por defecto)
        # 90° = Este arriba (grid rotado 90° CCW, este está arriba)
        # 180° = Sur arriba (grid rotado 180°)
        # 270° = Oeste arriba (grid rotado 270° CCW = 90° CW)
        
        mapping = {
            0: {'UP': 'N', 'DOWN': 'S', 'RIGHT': 'E', 'LEFT': 'W'},
            90: {'UP': 'E', 'DOWN': 'W', 'RIGHT': 'S', 'LEFT': 'N'},
            180: {'UP': 'S', 'DOWN': 'N', 'RIGHT': 'W', 'LEFT': 'E'},
            270: {'UP': 'W', 'DOWN': 'E', 'RIGHT': 'N', 'LEFT': 'S'}
        }
        
        return mapping[self.orientation][grid_dir]
    
    def _print_code(self):
        """Genera e imprime código"""
        code = self.grid.generate_code(self.orientation, self._grid_direction_to_cardinal)
        print("\n" + "=" * 70)
        print("CÓDIGO GENERADO:")
        print("=" * 70)
        print(f"# Orientación: {self._get_orientation_name()}")
        print(code)
        print("=" * 70 + "\n")
    
    def run(self):
        """Loop principal"""
        while self.running:
            self.handle_events()
            
            self.renderer.draw()
            self.renderer._draw_compass(self.orientation)
            self.renderer.draw_button(self.button_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            if not self.button_rect.collidepoint(mouse_pos):
                self.renderer.draw_wall_preview(mouse_pos, self.interaction)
            
            pygame.display.flip()
            self.clock.tick(Config.FPS)
        
        pygame.quit()


# ==================== MAIN ====================

def get_grid_size():
    """Solicita tamaño de cuadrícula"""
    print("\n" + "=" * 70)
    print("🎯 CONFIGURACIÓN DE CUADRÍCULA")
    print("=" * 70)
    
    while True:
        try:
            print("\n📐 Ingresa el tamaño:")
            rows = int(input("   Filas (3-20): "))
            cols = int(input("   Columnas (3-20): "))
            
            if rows < 3 or cols < 3:
                print("❌ Mínimo 3x3")
                continue
            
            if rows > 20 or cols > 20:
                print("⚠️  Máximo recomendado: 20x20")
                if input("¿Continuar? (s/n): ").lower() != 's':
                    continue
            
            return rows, cols
        
        except ValueError:
            print("❌ Números válidos por favor")
        except KeyboardInterrupt:
            print("\n👋 Cancelado")
            sys.exit(0)


def main():
    rows, cols = get_grid_size()
    editor = MazeEditor(rows, cols)
    editor.run()


if __name__ == "__main__":
    main()
