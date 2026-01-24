"""
Simple camera system for pan and zoom
"""

import pygame
from config import Config


class SimpleCamera:
    """Cámara simple para pan/zoom del canvas"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Posición de la cámara (centro del viewport en coordenadas del mundo)
        self.x = 0
        self.y = 0
        
        # Zoom
        self.zoom = Config.INITIAL_ZOOM
        
        # Estado de drag
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_offset = (0, 0)
    
    def world_to_screen(self, world_x, world_y):
        """Convierte coordenadas del mundo a píxeles de pantalla"""
        rel_x = world_x - self.x
        rel_y = world_y - self.y
        
        screen_x = rel_x * self.zoom + self.width / 2
        screen_y = rel_y * self.zoom + self.height / 2
        
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convierte píxeles de pantalla a coordenadas del mundo"""
        rel_x = (screen_x - self.width / 2) / self.zoom
        rel_y = (screen_y - self.height / 2) / self.zoom
        
        world_x = rel_x + self.x
        world_y = rel_y + self.y
        
        return world_x, world_y
    
    def handle_mouse_down(self, pos, button):
        """Mouse button press"""
        if button == 1:  # Left click
            self.dragging = True
            self.drag_start = pos
            self.drag_offset = (self.x, self.y)
    
    def handle_mouse_up(self, pos, button):
        """Mouse button release"""
        if button == 1:
            self.dragging = False
    
    def handle_mouse_motion(self, pos):
        """Mouse movement"""
        if self.dragging:
            dx = (self.drag_start[0] - pos[0]) / self.zoom
            dy = (self.drag_start[1] - pos[1]) / self.zoom
            
            self.x = self.drag_offset[0] + dx
            self.y = self.drag_offset[1] + dy
    
    def handle_mouse_wheel(self, y):
        """Mouse wheel zoom"""
        mouse_pos = pygame.mouse.get_pos()
        world_pos_before = self.screen_to_world(*mouse_pos)
        
        # Zoom
        if y > 0:  # Scroll up
            self.zoom = min(self.zoom + Config.ZOOM_SPEED, Config.MAX_ZOOM)
        elif y < 0:  # Scroll down
            self.zoom = max(self.zoom - Config.ZOOM_SPEED, Config.MIN_ZOOM)
        
        # Mantener punto bajo el mouse fijo
        world_pos_after = self.screen_to_world(*mouse_pos)
        self.x += world_pos_before[0] - world_pos_after[0]
        self.y += world_pos_before[1] - world_pos_after[1]
    
    def center_on(self, world_x, world_y):
        """Centrar cámara en coordenadas del mundo"""
        self.x = world_x
        self.y = world_y
