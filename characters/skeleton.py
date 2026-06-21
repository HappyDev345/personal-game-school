"""
Skeleton module.

This module contains the Skeleton class representing a skeleton enemy type in the game.
"""

import pygame
import math
import time
import random
from characters.enemy import Enemy

class Skeleton(Enemy):
    """Represents a Skeleton enemy type."""
    
    # Constants
    MAX_HEALTH = 40
    ATTACK_DAMAGE = 15
    SPEED = 1.5
    AGGRO_RANGE = 220
    ATTACK_RANGE = 70
    RESURRECTION_CHANCE = 0.25
    BONE_SHIELD_COOLDOWN = 10.0
    
    # Attributes
    max_health = None
    health = None
    attack_damage = None
    speed = None
    aggro_range = None
    attack_range = None
    resurrection_chance = None
    has_resurrected = None
    bone_shield_active = None
    bone_shield_cooldown = None
    last_shield_time = None
    
    # Constructor
    def __init__(self, x, y, frames):
        """
        Initialise the Skeleton.
        
        Args:
            x (int): X-coordinate of the Skeleton.
            y (int): Y-coordinate of the Skeleton.
            frames (dict): Dictionary of animation frames for different states.
        """
        super().__init__(x, y, frames)
        
        # Skeleton-specific attributes
        self.max_health = Skeleton.MAX_HEALTH  # Skeletons have less health
        self.health = Skeleton.MAX_HEALTH
        self.attack_damage = Skeleton.ATTACK_DAMAGE
        self.speed = Skeleton.SPEED  # Slightly faster than regular enemies
        self.aggro_range = Skeleton.AGGRO_RANGE  # Better sight range
        self.attack_range = Skeleton.ATTACK_RANGE

        # Special abilities
        self.resurrection_chance = Skeleton.RESURRECTION_CHANCE  # 25% chance to resurrect once
        self.has_resurrected = False
        self.bone_shield_active = False
        self.bone_shield_cooldown = Skeleton.BONE_SHIELD_COOLDOWN  # Seconds
        self.last_shield_time = 0
        self.defence = 0  # Defence bonus from bone shield

    # Accessors
    def get_resurrection_chance(self):
        return self.resurrection_chance

    def get_has_resurrected(self):
        return self.has_resurrected

    def get_bone_shield_active(self):
        return self.bone_shield_active

    def get_bone_shield_cooldown(self):
        return self.bone_shield_cooldown

    def get_last_shield_time(self):
        return self.last_shield_time

    # Mutators
    def set_resurrection_chance(self, new_resurrection_chance):
        self.resurrection_chance = new_resurrection_chance

    def set_has_resurrected(self, new_has_resurrected):
        self.has_resurrected = new_has_resurrected

    def set_bone_shield_active(self, new_bone_shield_active):
        self.bone_shield_active = new_bone_shield_active

    def take_damage(self, amount):
        """
        Take damage with potential resurrection when killed.
        
        Args:
            amount (int): The amount of damage to take.
            
        Returns:
            bool: True if the Skeleton died permanently, False otherwise.
        """
        # Reduce damage if bone shield is active
        if self.bone_shield_active:
            amount = max(1, amount // 2)
        
        # Call parent take_damage method
        died = super().take_damage(amount)
        
        # Check for resurrection chance
        if died and not self.has_resurrected and random.random() < self.resurrection_chance:
            # Resurrect with partial health
            self.health = self.max_health // 3
            self.is_dying = False
            self.state = "idle"
            self.has_resurrected = True
            return False
        
        return died
    
    # Behaviours
    def update(self, player):
        """
        Update the Skeleton based on its state and the player.
        
        Args:
            player: The player object to interact with.
        """
        current_time = time.time()
        
        # Try to activate bone shield when low on health
        if (not self.bone_shield_active and self.health < self.max_health * 0.3 and
            current_time - self.last_shield_time > self.bone_shield_cooldown):
            self.bone_shield_active = True
            self.defence += 10  # Temporarily increase defence
            # Shield will last for 5 seconds
            self.last_shield_time = current_time
        
        # Deactivate bone shield after duration
        if self.bone_shield_active and current_time - self.last_shield_time > 5.0:
            self.bone_shield_active = False
            self.defence -= 10  # Remove defence bonus
        
        # Call parent update method
        super().update(player)
    
    def draw(self, screen):
        """
        Draw the Skeleton with its current animation frame.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Call parent draw method
        super().draw(screen)

        # Draw bone shield effect when active
        if self.bone_shield_active:
            # Create a bone shield circle around the skeleton
            shield_radius = max(self.hitbox.width, self.hitbox.height) + 10
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            shield_colour = (220, 220, 220, 150)  # Bone white with transparency
            pygame.draw.circle(shield_surface, shield_colour, (shield_radius, shield_radius), shield_radius, 3)
            
            # Draw zigzag pattern to represent bones
            segments = 16
            for i in range(segments):
                angle1 = i * (2 * math.pi / segments)
                angle2 = (i + 0.5) * (2 * math.pi / segments)
                x1 = shield_radius + int(math.cos(angle1) * shield_radius)
                y1 = shield_radius + int(math.sin(angle1) * shield_radius)
                x2 = shield_radius + int(math.cos(angle2) * (shield_radius - 5))
                y2 = shield_radius + int(math.sin(angle2) * (shield_radius - 5))
                pygame.draw.line(shield_surface, shield_colour, (x1, y1), (x2, y2), 2)
            
            # Draw the shield (using Pygame's centerx/centery properties)
            screen.blit(shield_surface, 
                      (self.hitbox.centerx - shield_radius, self.hitbox.centery - shield_radius))
