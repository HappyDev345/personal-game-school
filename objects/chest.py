"""
Chest module.

This module contains the Chest class representing interactive chests.
"""

import pygame
import random
import time
import math
from core.map import TILE_SIZE
from core.game_object import GameObject

class Chest(GameObject):
    """Represents an interactive chest that can be opened."""

    # Constants
    ANIMATION_SPEED = 0.15
    BOB_SPEED = 0.1

    # Attributes
    is_open = None
    is_opening = None
    closed_frames = None
    open_frames = None
    current_frame = None
    animation_timer = None
    animation_speed = None
    gold = None
    health_potion = None
    opened_time = None
    floating_text = None
    bobbing_offset = None
    bobbing_direction = None
    bob_speed = None
    glow_alpha = None

    # Constructor
    def __init__(self, x, y, closed_frames, open_frames):
        """
        Initialise the chest.
        
        Args:
            x (int): X coordinate of the chest.
            y (int): Y coordinate of the chest.
            closed_frames: List of animation frames for the closed chest.
            open_frames: List of animation frames for the open chest.
        """
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        
        self.is_open = False
        self.is_opening = False
        
        # Chest animation frames
        self.closed_frames = closed_frames
        self.open_frames = open_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = Chest.ANIMATION_SPEED  # Animation speed (lower is faster)
        
        # Chest contents (gold, health, etc.)
        self.gold = random.randint(10, 30)
        self.health_potion = random.choice([True, False])
        
        # Visual elements
        self.opened_time = 0
        self.floating_text = None
        self.bobbing_offset = 0
        self.bobbing_direction = 1
        self.bob_speed = Chest.BOB_SPEED
        self.glow_alpha = 0

    # Accessors
    def get_is_open(self):
        return self.is_open

    def get_gold(self):
        return self.gold

    def get_health_potion(self):
        return self.health_potion

    # Mutators
    def set_gold(self, new_gold):
        self.gold = new_gold

    def set_health_potion(self, new_health_potion):
        self.health_potion = new_health_potion

    def open(self):
        """
        Open the chest and get contents.
        
        Returns:
            dict: Chest contents, or None if already open.
        """
        if not self.is_open and not self.is_opening:
            self.is_opening = True
            self.is_open = True
            self.opened_time = time.time()
            self.current_frame = 0  # Start animation from beginning
            contents = []
            
            if self.gold > 0:
                contents.append(f"+{self.gold} gold")
            if self.health_potion:
                contents.append("+1 Health Potion")
                
            self.floating_text = ", ".join(contents)
            return {
                "gold": self.gold, 
                "health_potion": self.health_potion
            }
        return None

    # Behaviours
    def update(self):
        """Update chest state."""
        # Move hitbox with position
        super().update()
        
        # Update animation
        self.animation_timer += 1
        
        # Opening animation plays through once when first opened
        if self.is_opening:
            # Update animation frame
            if self.animation_timer >= 1 / self.animation_speed:
                self.current_frame += 1
                self.animation_timer = 0
                
                # If we've reached the end of the opening animation
                if self.current_frame >= len(self.open_frames):
                    self.is_opening = False
                    self.current_frame = len(self.open_frames) - 1
        # Idle animation for closed chests
        elif not self.is_open:
            # Add a bobbing animation to make the chest more noticeable
            self.bobbing_offset += self.bobbing_direction * self.bob_speed
            if abs(self.bobbing_offset) > 2:
                self.bobbing_direction *= -1
            
            # Update closed chest animation frame (cycles through frames)
            if self.animation_timer >= 1 / self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.closed_frames)
                self.animation_timer = 0
                
            # Pulsing glow effect for closed chests
            self.glow_alpha = 128 + 127 * math.sin(pygame.time.get_ticks() / 500)

    def draw(self, screen):
        """
        Draw the chest.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw glow effect for unopened chests
        if not self.is_open and self.glow_alpha > 0:
            # Get the dimensions of the current chest frame for proper sizing
            current_frame_idx = self.current_frame % len(self.closed_frames)
            frame = self.closed_frames[current_frame_idx]
            frame_width = frame.get_width()
            frame_height = frame.get_height()
            
            # Create a glow effect that matches the exact size of the chest with a small margin
            glow_margin = 8
            glow_surf = pygame.Surface((frame_width + glow_margin*2, frame_height + glow_margin*2), pygame.SRCALPHA)
            glow_surf.fill((255, 255, 0, int(self.glow_alpha * 0.2)))
            screen.blit(glow_surf, (self.x - glow_margin, self.y - glow_margin + self.bobbing_offset))
        
        # Draw the chest with the current animation frame
        if self.is_open or self.is_opening:
            # Use the appropriate frame from the open animation
            frame_idx = min(self.current_frame, len(self.open_frames) - 1)
            screen.blit(self.open_frames[frame_idx], (self.x, self.y))
        else:
            # Use the appropriate frame from the closed animation with bobbing effect
            frame_idx = self.current_frame % len(self.closed_frames)
            screen.blit(self.closed_frames[frame_idx], (self.x, self.y + self.bobbing_offset))
        
        # Draw floating text if chest was recently opened
        if self.floating_text and time.time() - self.opened_time < 2.0:
            font = pygame.font.Font(None, 24)
            # Calculate alpha based on time elapsed (fade out)
            alpha = 255 * (1 - (time.time() - self.opened_time) / 2.0)
            
            # Create text with shadow for better visibility
            text = font.render(self.floating_text, True, (255, 255, 0))
            shadow = font.render(self.floating_text, True, (0, 0, 0))
            
            # Draw shadow first, then text
            screen.blit(shadow, (self.x - 8, self.y - 28))
            screen.blit(text, (self.x - 10, self.y - 30))
