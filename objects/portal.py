"""
Portal module.

This module contains the Portal class representing level exits.
"""

import pygame
import math
from core.map import TILE_SIZE

class Portal:
    """Represents a level exit portal."""
    
    # Constants
    ANIMATION_SPEED = 0.1

    # Attributes
    x = None
    y = None
    width = None
    height = None
    hitbox = None
    animation_timer = None
    animation_speed = None
    glow_alpha = None
    pulse_size = None
    activated = None

    # Constructor
    def __init__(self, x, y):
        """
        Initialise the portal.
        
        Args:
            x (int): X coordinate of the portal.
            y (int): Y coordinate of the portal.
        """
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.hitbox = pygame.Rect(x, y, self.width, self.height)
        
        # Visual effects
        self.animation_timer = 0
        self.animation_speed = Portal.ANIMATION_SPEED
        self.glow_alpha = 0
        self.pulse_size = 0
        self.activated = False
    
    # Accessors
    def get_activated(self):
        return self.activated

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def is_player_colliding(self, player):
        """
        Check if the player is colliding with the portal.
        Only returns true if the portal is activated.

        Args:
            player: The player object.

        Returns:
            bool: True if the player is colliding and portal is activated.
        """
        return self.hitbox.colliderect(player.hitbox) and self.activated

    # Mutators
    def set_activated(self, new_activated):
        self.activated = new_activated

    # Behaviours
    def update(self):
        """Update portal state and animations."""
        # Pulsing glow effect
        self.glow_alpha = 128 + 127 * math.sin(pygame.time.get_ticks() / 500)
        
        # Growing/shrinking effect
        self.pulse_size = 3 * math.sin(pygame.time.get_ticks() / 300)
        
        # Update hitbox position
        self.hitbox.x = self.x
        self.hitbox.y = self.y
    
    def draw(self, screen):
        """
        Draw the portal.

        Args:
            screen: The pygame surface to draw on.
        """
        # Adjust glow effect based on activation state
        if self.activated:
            # Active portal: full glow
            glow_color = (100, 200, 255)
            glow_alpha = int(self.glow_alpha * 0.3)
        else:
            # Inactive portal: dimmed red glow
            glow_color = (100, 50, 50)
            glow_alpha = int(self.glow_alpha * 0.15)

        # Draw glow effect
        glow_surf = pygame.Surface((self.width + 20 + self.pulse_size,
                                   self.height + 20 + self.pulse_size), pygame.SRCALPHA)
        glow_surf.fill((*glow_color, glow_alpha))
        screen.blit(glow_surf, (self.x - 10 - self.pulse_size/2, self.y - 10 - self.pulse_size/2))

        # Draw inner portal
        portal_surf = pygame.Surface((self.width - 10, self.height - 10), pygame.SRCALPHA)

        # Create a swirling effect with changing colours
        t = pygame.time.get_ticks() / 1000

        if self.activated:
            # Active portal: blue swirl
            r = 50 + int(50 * math.sin(t * 2))
            g = 50 + int(50 * math.sin(t * 1.5 + 2))
            b = 200 + int(55 * math.sin(t + 4))
        else:
            # Inactive portal: dark red/brown swirl, slower animation
            r = 60 + int(30 * math.sin(t * 0.5))
            g = 30 + int(20 * math.sin(t * 0.4 + 2))
            b = 40 + int(25 * math.sin(t * 0.3 + 4))

        portal_surf.fill((r, g, b, 200))

        # Draw portal on screen
        screen.blit(portal_surf, (self.x + 5, self.y + 5))

        # Draw portal border - colour changes based on activation
        if self.activated:
            border_color = (200, 200, 255)
        else:
            border_color = (150, 100, 100)

        pygame.draw.rect(screen, border_color,
                         (self.x, self.y, self.width, self.height), 3)

        # Draw some runes or symbols around the portal
        for i in range(4):
            angle = t * 2 + i * math.pi / 2
            x = self.x + self.width/2 + math.cos(angle) * (self.width/2 - 5)
            y = self.y + self.height/2 + math.sin(angle) * (self.height/2 - 5)

            # Only draw runes if portal is activated
            if self.activated:
                pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 3)
            else:
                pygame.draw.circle(screen, (100, 100, 100), (int(x), int(y)), 2)
