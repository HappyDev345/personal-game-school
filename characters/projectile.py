"""
Projectile module.

This module contains the Projectile class representing a magical projectile fired by the wizard.
"""

import pygame
import time
import math
import random

class Projectile:
    """Represents a magical projectile fired by the wizard."""

    # Constants

    DEFAULT_SPEED = 10
    DEFAULT_LIFETIME = 2.0

    # Attributes

    x = None
    y = None
    dx = None
    dy = None
    speed = None
    damage = None
    effect_images = None
    creation_time = None
    lifetime = None
    hit_enemies = None
    current_frame = None
    frame_time = None
    frame_duration = None
    angle = None
    rotation_speed = None
    hitbox = None

    # Constructor

    def __init__(self, x, y, target_x, target_y, damage=20, effect_images=None):
        """
        Initialise a new projectile.

        Args:
            x: Starting x position
            y: Starting y position
            target_x: Target x position
            target_y: Target y position
            damage: Amount of damage the projectile deals
            effect_images: The list of images to use for the projectile animation
                          (should be frames extracted from Wizard-Attack01_Effect.png)
        """
        self.x = x
        self.y = y

        # Calculate direction vector towards target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)

        # Normalise the direction vector
        if distance > 0:
            self.dx = dx / distance
            self.dy = dy / distance
        else:
            self.dx = 1  # Default to right if no direction
            self.dy = 0

        self.speed = Projectile.DEFAULT_SPEED
        self.damage = damage
        self.effect_images = effect_images if effect_images else []
        self.creation_time = time.time()
        self.lifetime = Projectile.DEFAULT_LIFETIME  # Seconds
        self.hit_enemies = []  # Track enemies we've already hit

        # Animation properties
        self.current_frame = 0
        self.frame_time = 0
        self.frame_duration = 0.08  # How long each frame displays (in seconds)
        self.angle = 0
        self.rotation_speed = 5  # Degrees per update

        # Create hitbox - size based on image or default
        if self.effect_images and len(self.effect_images) > 0:
            width = self.effect_images[0].get_width()
            height = self.effect_images[0].get_height()
        else:
            width = height = 30
        self.hitbox = pygame.Rect(int(self.x - width // 2), int(self.y - height // 2), width, height)

    # Accessors

    def get_damage(self):
        """Return the projectile's damage value."""
        return self.damage

    def get_speed(self):
        """Return the projectile's speed."""
        return self.speed

    def get_lifetime(self):
        """Return the projectile's lifetime in seconds."""
        return self.lifetime

    # Mutators

    def set_damage(self, damage):
        """Set the projectile's damage value."""
        self.damage = damage

    def set_speed(self, speed):
        """Set the projectile's speed."""
        self.speed = speed

    def set_lifetime(self, lifetime):
        """Set the projectile's lifetime in seconds."""
        self.lifetime = lifetime

    # Behaviours

    def update(self, enemies, game_map):
        """
        Update the projectile position and check for collisions.

        Args:
            enemies: List of enemies to check for collisions
            game_map: Map to check for wall collisions

        Returns:
            bool: True if the projectile should be removed
        """
        current_time = time.time()

        # Move the projectile along its direction vector
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # Update animation frame
        elapsed = current_time - self.frame_time
        if elapsed > self.frame_duration and self.effect_images:
            self.current_frame = (self.current_frame + 1) % len(self.effect_images)
            self.frame_time = current_time

        # Update hitbox position
        if self.effect_images and len(self.effect_images) > 0:
            width = self.effect_images[self.current_frame].get_width()
            height = self.effect_images[self.current_frame].get_height()
        else:
            width = height = 30

        self.hitbox = pygame.Rect(int(self.x - width//2), int(self.y - height//2), width, height)

        # Rotate the image for additional effect
        self.angle = (self.angle + self.rotation_speed) % 360

        # Check if lifetime exceeded
        if current_time - self.creation_time > self.lifetime:
            return True

        # Check for wall collision
        from core.map import TILE_SIZE
        if hasattr(game_map, 'is_wall'):
            tile_x = int(self.x // TILE_SIZE)
            tile_y = int(self.y // TILE_SIZE)

            if game_map.is_wall(tile_x, tile_y):
                return True

        # Check for enemy collisions
        for enemy in enemies:
            if enemy.is_alive() and enemy not in self.hit_enemies:
                if self.hitbox.colliderect(enemy.hitbox):
                    # Deal damage
                    enemy.take_damage(self.damage)

                    # Add to hit list so we don't hit it again
                    self.hit_enemies.append(enemy)

        # Don't remove the projectile after hitting enemies - it can pass through
        return False

    def draw(self, screen):
        """
        Draw the projectile.

        Args:
            screen: Surface to draw on
        """
        if self.effect_images and len(self.effect_images) > 0:
            # Get the current animation frame
            current_image = self.effect_images[self.current_frame]

            # Rotate the image for additional animation effect
            rotated_image = pygame.transform.rotate(current_image, self.angle)

            # Get the rect for the rotated image (maintains center position)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))

            # Draw the rotated image
            screen.blit(rotated_image, rect.topleft)

            # Add a pulsating glow effect around the projectile
            pulse = 0.5 + 0.5 * math.sin(time.time() * 10)  # Pulsating effect
            glow_size = max(rotated_image.get_width(), rotated_image.get_height()) + 10
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            # Outer glow - blue/cyan
            pygame.draw.circle(glow_surf, (0, 100, 255, int(40 + 20 * pulse)),
                             (glow_size//2, glow_size//2), glow_size//3 + int(3 * pulse))

            # Inner glow - brighter
            pygame.draw.circle(glow_surf, (100, 180, 255, int(70 + 30 * pulse)),
                             (glow_size//2, glow_size//2), glow_size//4)

            screen.blit(glow_surf, (int(self.x) - glow_size//2, int(self.y) - glow_size//2),
                      special_flags=pygame.BLEND_ADD)
        else:
            # Fallback rendering if no image
            pygame.draw.circle(screen, (0, 100, 255), (int(self.x), int(self.y)), 10)

            # Add a glow effect
            glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 100, 255, 100), (20, 20), 15)
            screen.blit(glow_surf, (int(self.x) - 20, int(self.y) - 20), special_flags=pygame.BLEND_ADD)
