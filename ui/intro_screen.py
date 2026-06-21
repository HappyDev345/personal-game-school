"""
Intro Screen module.

This module contains the IntroScreen class for handling the game's intro/menu screen.
"""

import pygame
import sys
import os
import math
# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Colours
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class IntroScreen:
    """Manages the game's intro/menu screen."""
    
    def __init__(self, screen):
        """
        Initialise the intro screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Load background image
        self.background = self._load_background()
        
        # Initialise button attributes
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, 200, 50)
        self.quit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 50)
        self.button_highlighted = None
        
        # Animation effects
        self.animation_timer = 0
        self.animation_speed = 0.05
    
    def _load_background(self):
        """Load the background image from multiple possible locations."""
        # Get the current directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Define multiple possible paths for the background image
        possible_paths = [
            # Direct path
            os.path.join(current_dir, "assets", "main_menu_background.png"),
            # UI folder
            os.path.join(current_dir, "assets", "images", "ui", "main_menu_background.png"),
            # src version
            os.path.join(current_dir, "src", "assets", "images", "ui", "main_menu_background.png"),
            # Try using demonstration.png as a fallback
            os.path.join(current_dir, "assets", "character and tileset", "demonstration.png"),
        ]
        
        # Try each path until we find a valid image
        for bg_path in possible_paths:
            try:
                if os.path.exists(bg_path):
                    background = pygame.image.load(bg_path).convert()
                    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    return background
            except Exception:
                continue
        
        # If no image was found, create a fallback
        return self._create_fallback_background()
    
    def _create_fallback_background(self):
        """Create a more advanced fallback background for the main menu."""
        import random
        
        # Create a gradient background
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw a gradient from dark blue to deep purple (dungeon-like)
        for y in range(SCREEN_HEIGHT):
            # Calculate the colour for this row
            ratio = y / SCREEN_HEIGHT
            r = int(30 + 10 * (1 - ratio))
            g = int(10 + 10 * (1 - ratio))
            b = int(60 + 20 * (1 - ratio))
            color = (r, g, b)
            
            # Draw a horizontal line with this colour
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
        
        # Create a "dungeon wall" texture effect
        cell_size = 60
        for x in range(0, SCREEN_WIDTH, cell_size):
            for y in range(0, SCREEN_HEIGHT, cell_size):
                # Random variation in the size and position of each "stone"
                stone_width = random.randint(cell_size-10, cell_size-2)
                stone_height = random.randint(cell_size-10, cell_size-2)
                stone_x = x + random.randint(1, 5)
                stone_y = y + random.randint(1, 5)
                
                # Random shade for each stone
                shade = random.randint(-15, 15)
                stone_color = (
                    max(20, min(50, 35 + shade)),
                    max(20, min(40, 25 + shade)),
                    max(40, min(80, 60 + shade))
                )
                
                # Draw the stone
                pygame.draw.rect(background, stone_color, 
                                (stone_x, stone_y, stone_width, stone_height),
                                border_radius=4)
                
                # Add a subtle edge highlight to each stone
                pygame.draw.rect(background, (stone_color[0]+10, stone_color[1]+10, stone_color[2]+10),
                                (stone_x, stone_y, stone_width, stone_height), 
                                1, border_radius=4)
        
        # Add some torches/light sources with a subtle glow effect
        torch_positions = [
            (100, 150), 
            (SCREEN_WIDTH-100, 150),
            (100, SCREEN_HEIGHT-150),
            (SCREEN_WIDTH-100, SCREEN_HEIGHT-150),
        ]
        
        for tx, ty in torch_positions:
            # Create a soft glow effect
            for radius in range(70, 0, -1):
                intensity = (70 - radius) / 70.0
                glow_color = (
                    int(255 * intensity * 0.7),
                    int(200 * intensity * 0.5),
                    int(100 * intensity * 0.3),
                    int(150 * intensity)
                )
                
                # Create a surface with per-pixel alpha for the glow
                glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (radius, radius), radius)
                background.blit(glow_surface, (tx-radius, ty-radius))
            
            # Draw the actual torch
            pygame.draw.rect(background, (120, 80, 40), (tx-5, ty-15, 10, 20))
            pygame.draw.circle(background, (255, 200, 100), (tx, ty-18), 8)
            
        # Add some subtle hints of "runes" on the walls
        for _ in range(10):
            rune_x = random.randint(100, SCREEN_WIDTH-100)
            rune_y = random.randint(100, SCREEN_HEIGHT-100)
            rune_size = random.randint(20, 40)
            rune_color = (100, 100, 180, 100)  # Semi-transparent bluish glow
            
            # Create a surface for the rune with per-pixel alpha
            rune_surface = pygame.Surface((rune_size, rune_size), pygame.SRCALPHA)
            
            # Draw a random rune-like shape
            if random.choice([True, False]):
                # Circle rune
                pygame.draw.circle(rune_surface, rune_color, (rune_size//2, rune_size//2), rune_size//2, 2)
                pygame.draw.line(rune_surface, rune_color, 
                                (rune_size//4, rune_size//2), 
                                (rune_size*3//4, rune_size//2), 2)
            else:
                # Angular rune
                points = []
                for i in range(random.randint(3, 5)):
                    angle = 2 * math.pi * i / random.randint(3, 5)
                    x = rune_size//2 + int(rune_size//2 * 0.8 * math.cos(angle))
                    y = rune_size//2 + int(rune_size//2 * 0.8 * math.sin(angle))
                    points.append((x, y))
                pygame.draw.polygon(rune_surface, rune_color, points, 2)
            
            background.blit(rune_surface, (rune_x, rune_y))
        
        return background
    
    def handle_events(self):
        """
        Handle pygame events for the intro screen.
        
        Returns:
            str: Action to take ('start', 'quit', or None).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return 'start'
            
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over the buttons
                mouse_pos = pygame.mouse.get_pos()
                if self.start_button_rect.collidepoint(mouse_pos):
                    self.button_highlighted = 'start'
                elif self.quit_button_rect.collidepoint(mouse_pos):
                    self.button_highlighted = 'quit'
                else:
                    self.button_highlighted = None
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                if self.start_button_rect.collidepoint(mouse_pos):
                    return 'start'
                elif self.quit_button_rect.collidepoint(mouse_pos):
                    return 'quit'
        
        return None
    
    def update(self, dt):
        """
        Update intro screen animations.
        
        Args:
            dt: Delta time since last frame.
        """
        # Update animation timer
        self.animation_timer += dt * self.animation_speed
        if self.animation_timer > 1.0:
            self.animation_timer = 0.0
    
    def draw(self):
        """Draw the intro screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw Start button
        start_color = (0, 200, 0) if self.button_highlighted == 'start' else (0, 150, 0)
        pygame.draw.rect(self.screen, start_color, self.start_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.start_button_rect, 2, border_radius=10)
        
        start_text = self.font_small.render("Start Game", True, WHITE)
        start_text_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Draw Quit button
        quit_color = (200, 0, 0) if self.button_highlighted == 'quit' else (150, 0, 0)
        pygame.draw.rect(self.screen, quit_color, self.quit_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.quit_button_rect, 2, border_radius=10)
        
        quit_text = self.font_small.render("Quit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Draw help text
        help_text = self.font_small.render("Press ENTER or SPACE to start", True, WHITE)
        help_text_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        self.screen.blit(help_text, help_text_rect)
    
    def run(self):
        """
        Run the intro screen loop.
        
        Returns:
            str: 'start' to begin the game or 'quit' to exit.
        """
        clock = pygame.time.Clock()
        
        while True:
            # Handle events
            action = self.handle_events()
            if action in ('start', 'quit'):
                return action
            
            # Update and draw
            dt = clock.tick(60) / 1000.0
            self.update(dt)
            self.draw()
            
            # Update display
            pygame.display.flip()