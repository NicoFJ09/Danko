"""
Renderer for drawing the maze map in pygame
Handles grid, walls, bot, and sensor visualization
"""

import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MapConfig

class MapRenderer:
    def __init__(self, screen, camera, map_state):
        self.screen = screen
        self.camera = camera
        self.map_state = map_state
        
        # Load bot sprites
        self.sprites = self._load_sprites()
        
        # Font for debug info
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
    
    def _load_sprites(self):
        """Load bot direction sprites"""
        sprites = {}
        sprite_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        
        for direction in ['up', 'down', 'left', 'right']:
            sprite_path = os.path.join(sprite_dir, f'{direction}.png')
            
            if os.path.exists(sprite_path):
                # Load and scale sprite
                original = pygame.image.load(sprite_path)
                size = int(MapConfig.CELL_PIXEL_SIZE * 0.4)  # 40% of cell size
                scaled = pygame.transform.scale(original, (size, size))
                sprites[direction] = scaled
            else:
                # Create placeholder if sprite not found
                size = int(MapConfig.CELL_PIXEL_SIZE * 0.4)
                placeholder = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # Draw arrow shape based on direction
                if direction == 'up':
                    pygame.draw.polygon(placeholder, (255, 100, 100), 
                                      [(size//2, 0), (size, size), (0, size)])
                elif direction == 'down':
                    pygame.draw.polygon(placeholder, (255, 100, 100),
                                      [(0, 0), (size, 0), (size//2, size)])
                elif direction == 'left':
                    pygame.draw.polygon(placeholder, (255, 100, 100),
                                      [(size, 0), (size, size), (0, size//2)])
                elif direction == 'right':
                    pygame.draw.polygon(placeholder, (255, 100, 100),
                                      [(0, 0), (size, size//2), (0, size)])
                
                sprites[direction] = placeholder
        
        return sprites
    
    def cell_to_world(self, row, col):
        """Convert grid cell to world coordinates (center of cell)"""
        x = col * MapConfig.CELL_SIZE
        y = row * MapConfig.CELL_SIZE
        return x, y
    
    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(MapConfig.COLOR_BG)
        
        # Draw grid and cells
        self._draw_grid()
        
        # Draw path trail
        self._draw_path_trail()
        
        # Draw bot
        self._draw_bot()
        
        # Draw sensor rays (if enabled)
        if MapConfig.SHOW_SENSOR_RAYS:
            self._draw_sensor_rays()
        
        # Draw UI overlay
        self._draw_ui()
    
    def _draw_grid(self):
        """Draw the grid and walls"""
        # Get visible bounds to only draw what's on screen
        left, top, right, bottom = self.camera.get_visible_bounds()
        
        # Calculate which cells are visible
        min_col = int(left / MapConfig.CELL_SIZE) - 1
        max_col = int(right / MapConfig.CELL_SIZE) + 1
        min_row = int(top / MapConfig.CELL_SIZE) - 1
        max_row = int(bottom / MapConfig.CELL_SIZE) + 1
        
        # Draw cells
        for cell in self.map_state.get_all_cells():
            row, col = cell
            
            # Skip if not visible
            if not (min_col <= col <= max_col and min_row <= row <= max_row):
                continue
            
            # Get cell corners in world coordinates
            x, y = self.cell_to_world(row, col)
            cell_size = MapConfig.CELL_SIZE
            
            # Convert to screen coordinates
            top_left = self.camera.world_to_screen(x - cell_size/2, y - cell_size/2)
            top_right = self.camera.world_to_screen(x + cell_size/2, y - cell_size/2)
            bottom_left = self.camera.world_to_screen(x - cell_size/2, y + cell_size/2)
            bottom_right = self.camera.world_to_screen(x + cell_size/2, y + cell_size/2)
            
            # Draw cell background if explored
            if self.map_state.grid[cell]['explored']:
                # Highlight current cell differently
                if cell == self.map_state.bot_cell:
                    color = MapConfig.COLOR_CURRENT
                else:
                    color = MapConfig.COLOR_EXPLORED
                
                pygame.draw.polygon(self.screen, color, 
                                  [top_left, top_right, bottom_right, bottom_left])
            
            # Draw cell border
            pygame.draw.polygon(self.screen, MapConfig.COLOR_GRID,
                              [top_left, top_right, bottom_right, bottom_left], 1)
            
            # Draw walls
            walls = self.map_state.get_walls_in_cell(cell)
            for direction in walls:
                if direction == 'N':
                    pygame.draw.line(self.screen, MapConfig.COLOR_WALL,
                                   top_left, top_right, 3)
                elif direction == 'S':
                    pygame.draw.line(self.screen, MapConfig.COLOR_WALL,
                                   bottom_left, bottom_right, 3)
                elif direction == 'W':
                    pygame.draw.line(self.screen, MapConfig.COLOR_WALL,
                                   top_left, bottom_left, 3)
                elif direction == 'E':
                    pygame.draw.line(self.screen, MapConfig.COLOR_WALL,
                                   top_right, bottom_right, 3)
    
    def _draw_path_trail(self):
        """Draw the path the bot has traveled"""
        if len(self.map_state.path_trail) < 2:
            return
        
        points = []
        for cell in self.map_state.path_trail:
            world_x, world_y = self.cell_to_world(*cell)
            screen_pos = self.camera.world_to_screen(world_x, world_y)
            points.append(screen_pos)
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, MapConfig.COLOR_PATH, False, points, 2)
    
    def _draw_bot(self):
        """Draw the bot sprite at current position"""
        # Get bot position in world coordinates
        world_x, world_y = self.cell_to_world(*self.map_state.bot_cell)
        screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
        
        # Select sprite based on heading
        heading_to_sprite = {'N': 'up', 'S': 'down', 'E': 'right', 'W': 'left'}
        sprite_key = heading_to_sprite.get(self.map_state.bot_heading, 'up')
        sprite = self.sprites[sprite_key]
        
        # Scale sprite based on zoom
        scaled_size = int(MapConfig.CELL_PIXEL_SIZE * 0.4 * self.camera.zoom)
        if scaled_size > 5:  # Only draw if visible
            scaled_sprite = pygame.transform.scale(sprite, (scaled_size, scaled_size))
            
            # Center sprite on bot position
            rect = scaled_sprite.get_rect(center=(screen_x, screen_y))
            self.screen.blit(scaled_sprite, rect)
    
    def _draw_sensor_rays(self):
        """Draw sensor distance rays"""
        if not all(v is not None for v in self.map_state.stable_values.values()):
            return
        
        # Bot position
        world_x, world_y = self.cell_to_world(*self.map_state.bot_cell)
        screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
        
        heading = self.map_state.bot_heading
        
        # Define sensor directions relative to bot
        sensor_angles = {
            'N': {'front': (0, -1), 'left': (-1, 0), 'right': (1, 0)},
            'S': {'front': (0, 1), 'left': (1, 0), 'right': (-1, 0)},
            'E': {'front': (1, 0), 'left': (0, -1), 'right': (0, 1)},
            'W': {'front': (-1, 0), 'left': (0, 1), 'right': (0, -1)}
        }
        
        if heading not in sensor_angles:
            return
        
        # Draw each sensor ray
        for sensor_name, (dx, dy) in sensor_angles[heading].items():
            distance = self.map_state.stable_values[sensor_name]
            if distance is None:
                continue
            
            # Calculate end point of ray in world coordinates
            end_world_x = world_x + dx * distance
            end_world_y = world_y + dy * distance
            end_screen = self.camera.world_to_screen(end_world_x, end_world_y)
            
            # Color based on distance (red = close, green = far)
            if distance < MapConfig.WALL_THRESHOLD:
                color = (255, 100, 100)  # Red - wall detected
            else:
                color = (100, 200, 255)  # Blue - open path
            
            # Draw ray
            pygame.draw.line(self.screen, color, (screen_x, screen_y), end_screen, 2)
            
            # Draw dot at end
            pygame.draw.circle(self.screen, color, end_screen, 4)
    
    def _draw_ui(self):
        """Draw UI overlay with info"""
        y_offset = 10
        
        # Bot info
        info_lines = [
            f"Bot Position: {self.map_state.bot_cell}",
            f"Heading: {self.map_state.bot_heading}",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Cells Explored: {len(self.map_state.get_explored_cells())}",
        ]
        
        # Sensor values
        if all(v is not None for v in self.map_state.stable_values.values()):
            info_lines.append(f"Front: {self.map_state.stable_values['front']:.1f}cm")
            info_lines.append(f"Left: {self.map_state.stable_values['left']:.1f}cm")
            info_lines.append(f"Right: {self.map_state.stable_values['right']:.1f}cm")
        
        # Render text
        for line in info_lines:
            text_surface = self.font_small.render(line, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
        
        # Instructions at bottom
        instructions = [
            "Hold & Drag: Pan view",
            "Scroll: Zoom in/out",
            "Terminal: Enter sensor data"
        ]
        
        y_offset = MapConfig.WINDOW_HEIGHT - 70
        for line in instructions:
            text_surface = self.font_small.render(line, True, (150, 150, 150))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20