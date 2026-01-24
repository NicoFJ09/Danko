"""
Camera system for infinite scrollable canvas in pygame
Handles pan, zoom, and world-to-screen coordinate conversion
"""

import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MapConfig

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Camera position in world coordinates (center of view)
        self.x = 0
        self.y = 0
        
        # Zoom level
        self.zoom = MapConfig.INITIAL_ZOOM
        
        # Dragging state
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_offset = (0, 0)
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen pixels"""
        # Translate relative to camera
        rel_x = world_x - self.x
        rel_y = world_y - self.y
        
        # Apply zoom
        screen_x = rel_x * self.zoom + self.width / 2
        screen_y = rel_y * self.zoom + self.height / 2
        
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen pixels to world coordinates"""
        # Reverse the transformation
        rel_x = (screen_x - self.width / 2) / self.zoom
        rel_y = (screen_y - self.height / 2) / self.zoom
        
        world_x = rel_x + self.x
        world_y = rel_y + self.y
        
        return world_x, world_y
    
    def handle_mouse_down(self, pos, button):
        """Handle mouse button press"""
        if button == 1:  # Left click
            self.dragging = True
            self.drag_start = pos
            self.drag_offset = (self.x, self.y)
    
    def handle_mouse_up(self, pos, button):
        """Handle mouse button release"""
        if button == 1:  # Left click
            self.dragging = False
    
    def handle_mouse_motion(self, pos, rel):
        """Handle mouse movement"""
        if self.dragging:
            # Calculate drag delta in world coordinates
            dx = (self.drag_start[0] - pos[0]) / self.zoom
            dy = (self.drag_start[1] - pos[1]) / self.zoom
            
            self.x = self.drag_offset[0] + dx
            self.y = self.drag_offset[1] + dy
    
    def handle_mouse_wheel(self, y):
        """Handle mouse wheel for zooming"""
        # Get mouse position before zoom
        mouse_pos = pygame.mouse.get_pos()
        world_pos_before = self.screen_to_world(*mouse_pos)
        
        # Update zoom
        if y > 0:  # Scroll up (zoom in)
            self.zoom = min(self.zoom + MapConfig.ZOOM_SPEED, MapConfig.MAX_ZOOM)
        elif y < 0:  # Scroll down (zoom out)
            self.zoom = max(self.zoom - MapConfig.ZOOM_SPEED, MapConfig.MIN_ZOOM)
        
        # Adjust camera position to keep mouse point stable
        world_pos_after = self.screen_to_world(*mouse_pos)
        self.x += world_pos_before[0] - world_pos_after[0]
        self.y += world_pos_before[1] - world_pos_after[1]
    
    def center_on(self, world_x, world_y):
        """Center camera on specific world coordinates"""
        self.x = world_x
        self.y = world_y
    
    def get_visible_bounds(self):
        """Get the world coordinates of the visible area"""
        # Top-left corner
        left, top = self.screen_to_world(0, 0)
        # Bottom-right corner
        right, bottom = self.screen_to_world(self.width, self.height)
        
        return left, top, right, bottom