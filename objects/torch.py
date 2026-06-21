"""
Torch module.

This module contains the Torch class representing decorative torches in the game.
"""

import pygame
import time
import math
import random
from core.game_object import GameObject

class Torch(GameObject):
    """Represents a decorative torch with animation."""
    
    # Constants
    ANIMATION_SPEED = 0.15
    PARTICLE_INTERVAL = 0.2  # Seconds between particle spawns

    # Attributes
    frames = None
    current_frame = None
    animation_timer = None
    light_radius = None
    base_light_radius = None
    flicker_timer = None
    particles = None
    particle_timer = None

    # Constructor
    def __init__(self, x, y, frames):
        """
        Initialise the torch.
        
        Args:
            x (int): X coordinate of the torch.
            y (int): Y coordinate of the torch.
            frames (list): List of animation frames.
        """
        # No hitbox for decorative torches - they are just visual
        super().__init__(x, y, 0, 0)
        
        # Store frames and animation state
        self.frames = frames
        self.current_frame = 0
        self.animation_timer = 0
        
        # Light flicker effect
        self.light_radius = random.randint(30, 40)
        self.base_light_radius = self.light_radius
        self.flicker_timer = random.random() * math.pi  # Random starting phase
        
        # Particle effects
        self.particles = []
        self.particle_timer = 0
    
    # Accessors
    def get_light_radius(self):
        return self.light_radius

    def get_particles(self):
        return self.particles

    # Mutators

    # Behaviours
    def update(self):
        """Update torch animation and effects."""
        # Update animation frame
        self.animation_timer += 1
        if self.animation_timer >= 1 / Torch.ANIMATION_SPEED:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0
            
        # Update flicker effect
        self.flicker_timer += 0.1
        self.light_radius = self.base_light_radius + math.sin(self.flicker_timer) * 5
            
        # Update particle effects
        self.particle_timer += 1/60  # Assuming 60 FPS
        if self.particle_timer >= Torch.PARTICLE_INTERVAL:
            self.particle_timer = 0
            # Add a new particle 
            self.particles.append({
                "x": self.x + self.frames[0].get_width() // 2,
                "y": self.y + self.frames[0].get_height() // 3,
                "dx": random.uniform(-0.2, 0.2),
                "dy": random.uniform(-0.8, -0.5),
                "size": random.uniform(1, 3),
                "lifetime": 1.0,
                "color": (255, 200, random.randint(0, 100), 150)  # RGBA
            })
            
        # Update existing particles
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["lifetime"] -= 0.02
            if particle["lifetime"] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        """
        Draw the torch with lighting and particle effects.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw light effect first (under the torch)
        light_surf = pygame.Surface((int(self.light_radius * 2), int(self.light_radius * 2)), pygame.SRCALPHA)
        # Radial gradient for light
        for radius in range(int(self.light_radius), 0, -1):
            alpha = int(100 * (radius / self.light_radius))
            if alpha < 0:
                alpha = 0
            pygame.draw.circle(light_surf, (255, 200, 100, alpha), 
                              (int(self.light_radius), int(self.light_radius)), radius)
        
        # Position light under the torch
        light_pos = (
            self.x + self.frames[0].get_width() // 2 - self.light_radius,
            self.y + self.frames[0].get_height() // 3 - self.light_radius
        )
        screen.blit(light_surf, light_pos, special_flags=pygame.BLEND_ADD)
        
        # Draw the torch
        current_frame = self.frames[self.current_frame]
        screen.blit(current_frame, (self.x, self.y))
        
        # Draw particles (embers)
        for particle in self.particles:
            # Fade out as lifetime decreases
            alpha = int(255 * particle["lifetime"])
            color = (particle["color"][0], particle["color"][1], particle["color"][2], alpha)
            
            # Create a small surface for the particle
            particle_surf = pygame.Surface((int(particle["size"] * 2), int(particle["size"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, 
                             (int(particle["size"]), int(particle["size"])), int(particle["size"]))
            
            # Draw with additive blending for glow effect
            screen.blit(particle_surf, (int(particle["x"] - particle["size"]), int(particle["y"] - particle["size"])), 
                       special_flags=pygame.BLEND_ADD)
