"""
Coin module.

This module contains the Coin class representing collectible coins.
"""

import pygame
import random
from core.game_object import GameObject

class Coin(GameObject):
    """Represents a collectible animated coin."""
    
    # Constants
    ANIMATION_SPEED = 0.15  # Animation speed (lower is faster)
    LIFETIME = 600  # 10 seconds at 60 FPS
    BOB_SPEED = 0.2

    # Attributes
    frames = None
    current_frame = None
    animation_timer = None
    lifetime = None
    bobbing_offset = None
    bobbing_direction = None
    collected = None

    # Constructor
    def __init__(self, x, y, frames):
        """
        Initialise the coin.
        
        Args:
            x (int): X coordinate of the coin.
            y (int): Y coordinate of the coin.
            frames (list): List of animation frames for the coin.
        """
        # Calculate dimensions based on first frame
        width = frames[0].get_width()
        height = frames[0].get_height()
        super().__init__(x, y, width, height)
        
        self.frames = frames
        self.current_frame = 0
        self.animation_timer = 0
        self.lifetime = Coin.LIFETIME
        self.bobbing_offset = 0
        self.bobbing_direction = 1
        self.collected = False
    
    # Accessors
    def get_collected(self):
        return self.collected

    def get_lifetime(self):
        return self.lifetime

    # Mutators
    def set_collected(self, new_collected):
        self.collected = new_collected

    def collect(self):
        """
        Mark the coin as collected and return its value.
        
        Returns:
            int: The gold value of the coin.
        """
        if not self.collected:
            self.collected = True
            return random.randint(5, 15)  # Random gold value between 5-15
        return 0

    # Behaviours
    def update(self):
        """Update the coin animation and state."""
        if self.collected:
            return
            
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.collected = True
            return
        
        # Update bobbing animation
        self.bobbing_offset += self.bobbing_direction * Coin.BOB_SPEED
        if abs(self.bobbing_offset) > 3:
            self.bobbing_direction *= -1
        
        # Update animation frame
        self.animation_timer += 1
        if self.animation_timer >= 1 / Coin.ANIMATION_SPEED:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0
            
        # Update hitbox position
        self.hitbox.x = self.x
        self.hitbox.y = self.y + self.bobbing_offset
    
    def draw(self, screen):
        """
        Draw the coin with its current animation frame.
        
        Args:
            screen: The pygame surface to draw on.
        """
        if self.collected:
            return
            
        # Draw current frame with bobbing effect
        screen.blit(self.frames[self.current_frame], (self.x, self.y + self.bobbing_offset))
