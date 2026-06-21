"""
Wizard module.

This module contains the Wizard class representing a player character with ranged attacks.
"""

import pygame
import time
import math
import random
from characters.character import Character
from characters.projectile import Projectile


class Wizard(Character):
    """Represents a Wizard character with ranged magic attacks."""

    # Constants

    MAX_HEALTH = 80
    SPEED = 3
    ATTACK_DAMAGE = 20
    ATTACK_RANGE = 300
    ATTACK_COOLDOWN = 0.8

    # Attributes

    max_health = None
    health = None
    attack_damage = None
    speed = None
    attack_range = None
    attack_cooldown = None
    projectiles = None
    effect_images = None
    loaded_effect = None
    magic_particles = None

    # Constructor

    def __init__(self, x, y, idle_frames, attack_frames):
        """
        Initialise the wizard.
        
        Args:
            x (int): X-coordinate of the wizard.
            y (int): Y-coordinate of the wizard.
            idle_frames (list): List of idle animation frames.
            attack_frames (list): List of attack animation frames.
        """
        # Call parent constructor first
        super().__init__(x, y, idle_frames, attack_frames)
        
        # Override player attributes for wizard
        self.max_health = Wizard.MAX_HEALTH
        self.health = Wizard.MAX_HEALTH
        self.speed = Wizard.SPEED  # Slightly slower movement speed
        self.attack_damage = Wizard.ATTACK_DAMAGE  # Magic does more damage
        self.attack_range = Wizard.ATTACK_RANGE  # Much larger attack range for projectiles
        self.attack_cooldown = Wizard.ATTACK_COOLDOWN  # Slightly longer cooldown between attacks

        # Projectile management
        self.projectiles = []
        self.effect_images = None  # Will hold the effect images for projectiles
        self.loaded_effect = False  # Flag to track if we've tried to load the effect
        
        # Visual effects
        self.magic_particles = []
        
    # Accessors

    def get_projectiles(self):
        """Return the list of active projectiles."""
        return self.projectiles

    def get_effect_images(self):
        """Return the effect images used for projectiles."""
        return self.effect_images

    def get_magic_particles(self):
        """Return the list of active magic particles."""
        return self.magic_particles

    def _is_in_attack_range(self, enemy):
        """
        Check if an enemy is within attack range.
        Overridden to only check distance, not direction (as projectiles can be aimed).

        Args:
            enemy: The enemy object to check.

        Returns:
            bool: True if the enemy is in attack range, False otherwise.
        """
        # Calculate distance from player centre to enemy centre
        player_center_x = self.hitbox.centerx
        player_center_y = self.hitbox.centery
        enemy_center_x = enemy.hitbox.centerx
        enemy_center_y = enemy.hitbox.centery

        # Calculate distance
        dist = math.sqrt((player_center_x - enemy_center_x) ** 2 +
                       (player_center_y - enemy_center_y) ** 2)

        # For wizard, we only check distance, not direction
        # since we'll launch a projectile in the direction we're facing
        return dist <= self.attack_range

    # Mutators

    def set_projectiles(self, projectiles):
        """Set the list of active projectiles."""
        self.projectiles = projectiles

    def set_effect_images(self, new_effect_images):
        """Set the effect images used for projectiles."""
        self.effect_images = new_effect_images

    # Behaviours

    def update(self, game_map, enemies=None):
        """
        Update the wizard and its projectiles.
        
        Args:
            game_map: The game map data.
            enemies: List of enemy objects to check for projectile collisions.
        """
        # Store reference to game map for collision detection
        self.game_map = game_map
        
        # Store current state before update
        previous_state = self.state
        previous_frame = self.current_frame
        
        # Store position before update for hitbox correction
        old_x, old_y = self.x, self.y
        
        # Regular player update (movement, animation)
        super().update(game_map, None)
        
        # Check if position changed, if so we need to properly update hitbox
        # This is necessary because the parent class might not be accounting for our custom offsets
        if old_x != self.x or old_y != self.y:
            # Calculate new hitbox position based on our custom offsets
            self.hitbox.x = self.x + self.hitbox_offset_x
            self.hitbox.y = self.y + self.hitbox_offset_y
        
        # Special handling for attack animation - override animation timing for smoother spell casting
        if self.state == "attack":
            current_time = time.time()
            elapsed = current_time - self.attack_start_time
            
            # Customise animation speed for the wizard's attack
            # We want the wind-up to be slower, the release to be faster
            if previous_frame != self.current_frame:
                if self.current_frame == 3:  # Middle of the attack (spell release)
                    # Create projectile at the moment of spell release if we haven't already
                    if not hasattr(self, '_spell_released') and enemies:
                        # Mark that we've released the spell
                        self._spell_released = True
                        # Actually create the projectile
                        self.attack(enemies)
        
        # When attack animation ends, clean up any special attributes
        if previous_state == "attack" and self.state == "idle":
            if hasattr(self, '_spell_released'):
                delattr(self, '_spell_released')
        
        # Update projectiles if we have enemies
        if enemies is not None:
            for projectile in self.projectiles[:]:
                if projectile.update(enemies, game_map):
                    self.projectiles.remove(projectile)
        
        # Try to load the effect image if we haven't already
        if not self.loaded_effect:
            self._load_effect_image()
        
        # Generate idle magic particles for visual effect - more for wizard
        # Higher chance when idle, less during attack
        particle_chance = 0.08 if self.state == "idle" else 0.03
        if random.random() < particle_chance:
            # Determine colour based on state
            if self.state == "idle":
                # Blue/cyan particles during idle
                color = (0, 191, 255)
            else:
                # More magical purple/blue particles during attack
                color = (100 + random.randint(0, 100), 50 + random.randint(0, 100), 255)
            
            # Position particles around wizard based on state
            if self.state == "idle":
                # Particles hover around the wizard
                x_offset = random.uniform(-15, 15)
                y_offset = random.uniform(-25, 0)  # Mostly above the wizard
            else:
                # During attack, particles move toward casting position
                direction = -1 if self.facing_left else 1
                x_offset = random.uniform(0, 25) * direction  # In front of wizard
                y_offset = random.uniform(-30, -10)  # Above hands level
            
            # Create the particle
            self.magic_particles.append({
                'x': self.hitbox.centerx + x_offset,
                'y': self.hitbox.centery + y_offset,
                'size': random.uniform(1, 4),  # Slightly larger particles
                'lifetime': random.uniform(0.5, 2.0),  # Longer lifetimes
                'creation_time': time.time(),
                'color': color,
                'speed': random.uniform(0.5, 2.0),  # Variable speed
                'direction': random.uniform(0, 2 * math.pi)
            })
        
        # Update existing particles with more dynamic movement
        for particle in self.magic_particles[:]:
            # Base movement
            base_speed = particle['speed']
            
            # Add some wobble to the particles
            wobble = math.sin(time.time() * 5 + hash(str(particle)) % 100) * 0.3
            
            # If attacking, make particles flow toward spell direction
            if self.state == "attack" and self.current_frame >= 2:
                # Pull particles toward casting direction
                direction_pull = 0
                if self.facing_left:
                    direction_pull = -0.5
                else:
                    direction_pull = 0.5
                
                # Apply the pull
                particle['x'] += direction_pull
                
                # Increase speed during key casting frames
                if self.current_frame in [2, 3, 4]:
                    base_speed *= 1.5
            
            # Move particle with wobble
            particle['x'] += (math.cos(particle['direction']) + wobble) * base_speed
            particle['y'] += (math.sin(particle['direction']) - 0.1) * base_speed  # Slight upward drift
            
            # Remove if lifetime exceeded
            if time.time() - particle['creation_time'] > particle['lifetime']:
                self.magic_particles.remove(particle)
    
    def _load_effect_image(self):
        """Try to load the wizard effect images for projectiles."""
        try:
            # First try to get the image from the game's asset loader
            try:
                from core.game import asset_loader_instance
                if asset_loader_instance:
                    effect_image = asset_loader_instance.get_wizard_projectile_effect()
                    if effect_image:
                        # Create animation frames from the effect image
                        self.effect_images = self._create_effect_animation_frames(effect_image)
                        if self.effect_images:
                            return
            except (ImportError, AttributeError) as e:
                pass
                
            # If that fails, try direct loading
            import os
            
            # List of possible paths to try
            try_paths = [
                # Direct paths to where we know the files exist
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "assets", "Wizard", "Wizard", "Wizard-Attack01_Effect.png"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "assets", "Wizard", "Wizard", "Wizard-Attack02_Effect.png"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "assets", "Wizard", "Wizard with shadows", "Wizard-Attack01_Effect.png"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "assets", "Wizard", "Wizard with shadows", "Wizard-Attack02_Effect.png"),
            ]
            
            # Try each path
            for path in try_paths:
                if os.path.exists(path):
                    try:
                        effect_image = pygame.image.load(path).convert_alpha()
                        # Create animation frames from this image
                        self.effect_images = self._create_effect_animation_frames(effect_image)
                        if self.effect_images:
                            return
                    except Exception:
                        pass
            
            # If we still don't have effect images, create fallback frames
            if not self.effect_images:
                self.effect_images = self._create_fallback_effect_frames()
                
        except Exception:
            self.effect_images = self._create_fallback_effect_frames()
        finally:
            self.loaded_effect = True  # Mark that we've tried loading
    
    def _create_effect_animation_frames(self, effect_image):
        """Create animation frames from a projectile effect image."""
        try:
            frames = []
            
            # Get dimensions of the original image
            original_width = effect_image.get_width()
            original_height = effect_image.get_height()
            
            # If the image is large enough, it likely contains animation frames
            # Try to extract 4 frames by dividing horizontally
            if original_width >= 100:  # Arbitrary threshold to detect spritesheet
                num_frames = 4
                frame_width = original_width // num_frames
                frame_height = original_height
                
                for i in range(num_frames):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(effect_image, (0, 0), frame_rect)
                    
                    # Scale to an appropriate size for projectile (50x50 pixels)
                    frame = pygame.transform.scale(frame, (50, 50))
                    frames.append(frame)
            else:
                # If it's a single image, create 4 frames with rotation for animation
                # First scale the image to appropriate size
                effect_image = pygame.transform.scale(effect_image, (50, 50))
                
                # Create 4 frames with different rotations
                for i in range(4):
                    angle = i * 90
                    frame = pygame.transform.rotate(effect_image, angle)
                    frames.append(frame)
            
            return frames
            
        except Exception as e:
            print(f"Error creating effect animation frames: {e}")
            return None
    
    def _create_fallback_effect_frames(self):
        """Create fallback effect animation frames if we can't load the real ones."""
        frames = []
        
        # Create 4 different frames for animation
        for i in range(4):
            # Create a simple surface with a magic-looking effect
            surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Vary the size slightly for animation
            size_variation = 2 * math.sin(i * math.pi / 2)
            
            # Draw a blue magical-looking circle
            pygame.draw.circle(surface, (0, 50, 200, 200), (25, 25), 20 + size_variation)
            pygame.draw.circle(surface, (50, 100, 255, 200), (25, 25), 15 + size_variation)
            pygame.draw.circle(surface, (100, 150, 255, 200), (25, 25), 10 + size_variation)
            pygame.draw.circle(surface, (200, 220, 255, 200), (25, 25), 5 + size_variation)
            
            # Add some "sparkles" - different for each frame
            for _ in range(5):
                angle = random.random() * 2 * math.pi
                distance = random.randint(8, 18)
                x = int(25 + math.cos(angle) * distance)
                y = int(25 + math.sin(angle) * distance)
                size = random.randint(1, 3)
                pygame.draw.circle(surface, (255, 255, 255, 255), (x, y), size)
            
            frames.append(surface)
            
        return frames
    
    def attack(self, enemies=None):
        """
        Create a magic projectile when attacking.
        
        Args:
            enemies: Optional list of enemies to target the closest one.
        """
        # Find closest enemy to target
        target_x, target_y = None, None
        if enemies and len(enemies) > 0:
            # Find closest living enemy
            closest_enemy = None
            min_distance = float('inf')
            
            for enemy in enemies:
                if enemy.is_alive():
                    # Calculate distance
                    dx = enemy.hitbox.centerx - self.hitbox.centerx
                    dy = enemy.hitbox.centery - self.hitbox.centery
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
            
            # If we found a target, set the target position
            if closest_enemy:
                target_x = closest_enemy.hitbox.centerx
                target_y = closest_enemy.hitbox.centery
                
                # Update facing direction based on target
                self.facing_left = target_x < self.hitbox.centerx
        
        # If no target found, shoot in the direction we're facing
        if target_x is None or target_y is None:
            # Default to shooting straight ahead in the direction we're facing
            if self.facing_left:
                target_x = self.hitbox.centerx - 500  # Far to the left
            else:
                target_x = self.hitbox.centerx + 500  # Far to the right
                
            target_y = self.hitbox.centery  # Level with wizard
        
        # Calculate projectile spawn position (hands of wizard)
        # For better visual effect, spawn position depends on animation frame
        hand_offset_x = 0
        hand_offset_y = 0
        
        # If we're in the middle of an attack animation, use the frame to position projectile better
        if self.state == "attack" and self.current_frame in [2, 3, 4]:
            # Hands extend further in these frames
            hand_offset_x = 10 + (self.current_frame * 2)
            hand_offset_y = -15 - (self.current_frame * 2)  # Higher for spell release
        
        # Calculate spawn position based on facing direction
        if self.facing_left:
            spawn_x = self.hitbox.left - hand_offset_x  # Left of wizard
        else:
            spawn_x = self.hitbox.right + hand_offset_x  # Right of wizard
            
        spawn_y = self.hitbox.centery + hand_offset_y  # Above centre
        
        # Ensure the effect images are loaded
        if not self.loaded_effect:
            self._load_effect_image()
        
        # Create the projectile with the animation frames
        projectile = Projectile(
            spawn_x, spawn_y, 
            target_x, target_y, 
            damage=self.attack_damage,
            effect_images=self.effect_images
        )
        
        # Add to projectile list
        self.projectiles.append(projectile)
        
        # Add "casting burst" effect particles
        for _ in range(10):  # Create a burst of particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 4.0)
            size = random.uniform(2.0, 5.0)
            lifetime = random.uniform(0.3, 1.0)
            
            # Random colour in blue/purple magical palette
            r = random.randint(50, 150)
            g = random.randint(50, 200)
            b = 255  # Keep blue at maximum
            
            self.magic_particles.append({
                'x': spawn_x,
                'y': spawn_y,
                'size': size,
                'lifetime': lifetime,
                'creation_time': time.time(),
                'color': (r, g, b),
                'speed': speed,
                'direction': angle
            })
    
    def draw(self, screen):
        """
        Draw the wizard with the current animation frame and projectiles.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw magic particles first (behind wizard)
        for particle in self.magic_particles:
            # Calculate fade based on lifetime
            age = time.time() - particle['creation_time']
            fade_ratio = 1 - (age / particle['lifetime'])
            
            # Adjust colour and size based on fade
            color = particle['color']
            alpha = int(150 * fade_ratio)
            size = particle['size'] * fade_ratio
            
            # Create surface for particle with alpha
            # Ensure size is at least 1 pixel
            safe_size = max(1, int(size * 2))
            particle_surf = pygame.Surface((safe_size, safe_size), pygame.SRCALPHA)
            
            # Handle colour for pygame with alpha
            try:
                # Make sure all colour values are integers
                r = int(color[0]) if isinstance(color, tuple) and len(color) >= 1 else 0
                g = int(color[1]) if isinstance(color, tuple) and len(color) >= 2 else 100
                b = int(color[2]) if isinstance(color, tuple) and len(color) >= 3 else 255
                a = int(alpha)
                # Ensure alpha is within valid range
                a = max(0, min(255, a))
                # Create a proper RGBA colour
                rgba_color = (r, g, b, a)
                # Draw the circle with the RGBA colour
                pygame.draw.circle(particle_surf, rgba_color, (safe_size // 2, safe_size // 2), max(1, int(size)))
            except (TypeError, ValueError, IndexError):
                # Fallback to a safe colour if any issues
                safe_alpha = max(0, min(255, int(alpha) if isinstance(alpha, (int, float)) else 150))
                pygame.draw.circle(particle_surf, (0, 100, 255, safe_alpha), 
                                 (safe_size // 2, safe_size // 2), max(1, int(size)))
            
            # Draw with additive blending for glow effect
            screen.blit(particle_surf, 
                       (int(particle['x'] - size), int(particle['y'] - size)), 
                       special_flags=pygame.BLEND_ADD)
        
        # Draw the wizard using the parent method
        super().draw(screen)
        
        # Draw projectiles on top
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # When attacking, add dynamic magic effects based on attack animation stage
        if self.attacking and self.state == "attack":
            # Get hand position based on animation frame and direction
            # Adjust hand position more dynamically based on the frame
            frame_offset_x = 0
            frame_offset_y = 0
            
            # More dramatic hand movement during casting animation
            if self.current_frame >= 1:
                # Forward movement increases with frame number for dramatic effect
                frame_offset_x = 7 * self.current_frame  
                
                # Vertical movement: up for charge, down for release, back up for follow-through
                if self.current_frame <= 2:
                    # Raising hands to gather energy
                    frame_offset_y = -5 * self.current_frame  # Move hands up
                elif self.current_frame == 3:
                    # Release point
                    frame_offset_y = -12 # Highest point
                else:
                    # Follow-through
                    frame_offset_y = -12 + (self.current_frame - 3) * 3  # Move back down
            
            # Calculate final hand positions
            direction_mult = 1 if not self.facing_left else -1
            hand_x = self.hitbox.centerx + (frame_offset_x * direction_mult)
            hand_y = self.hitbox.centery + frame_offset_y - 10  # Slightly above centre
            
            # Determine stage of spell casting for appropriate effects
            if self.current_frame <= 1:
                # BEGINNING STAGE: Spell is gathering energy
                pulse = 0.5 + 0.5 * math.sin(time.time() * 12)
                
                # Create a subtle gathering energy effect
                glow_size = 40
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                # Starting with blue energy
                glow_color = (0, 150, 220, int(80 + 40 * pulse))
                pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//3)
                screen.blit(glow_surf, (hand_x - glow_size//2, hand_y - glow_size//2), 
                          special_flags=pygame.BLEND_ADD)
                
                # Add subtle trails of energy flowing into hands
                for _ in range(2):
                    # Energy particles flowing toward hand
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(20, 40)
                    particle_x = hand_x + math.cos(angle) * distance
                    particle_y = hand_y + math.sin(angle) * distance
                    
                    # Draw energy trail from particle to hand
                    trail_surf = pygame.Surface((int(distance*2), int(distance*2)), pygame.SRCALPHA)
                    start_pos = (int(distance), int(distance))
                    end_pos = (int(distance + math.cos(angle) * -distance), 
                              int(distance + math.sin(angle) * -distance))
                    
                    # Gradient trail
                    for i in range(5):
                        # Calculate point along the trail
                        factor = i / 5
                        pos_x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * factor)
                        pos_y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * factor)
                        
                        # Draw decreasing circles along the trail
                        size = 3 - (2 * factor)
                        alpha = int(150 - 100 * factor)
                        pygame.draw.circle(trail_surf, (100, 200, 255, alpha), (pos_x, pos_y), size)
                    
                    # Draw the trail
                    screen.blit(trail_surf, (particle_x - distance, particle_y - distance),
                               special_flags=pygame.BLEND_ADD)
                
            elif self.current_frame in [2, 3]:
                # MIDDLE STAGE: Spell is being cast/released
                pulse = 0.5 + 0.5 * math.sin(time.time() * 15)
                
                # Maximum energy at frame 3 (release point)
                intensity = 1.0 if self.current_frame == 3 else 0.7
                glow_size = int(70 * intensity)
                core_size = int(40 * intensity)
                
                # Main energy glow (outer)
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                # Colour shifts from blue to purple during cast
                if self.current_frame == 2:
                    glow_color = (80, 150, 255, int(150 * intensity * pulse))
                else:
                    glow_color = (120, 100, 255, int(180 * intensity * pulse))
                
                pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                screen.blit(glow_surf, (hand_x - glow_size//2, hand_y - glow_size//2), 
                          special_flags=pygame.BLEND_ADD)
                
                # Inner core (brighter)
                core_surf = pygame.Surface((core_size, core_size), pygame.SRCALPHA)
                core_color = (180, 220, 255, int(220 * intensity))
                pygame.draw.circle(core_surf, core_color, (core_size//2, core_size//2), core_size//2 - 5)
                screen.blit(core_surf, (hand_x - core_size//2, hand_y - core_size//2), 
                          special_flags=pygame.BLEND_ADD)
                
                # Add magical particles radiating from the hand during casting
                particle_count = 5 if self.current_frame == 3 else 3
                for _ in range(particle_count):
                    # Particles emanate outward
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(5, 15 * intensity)
                    particle_x = hand_x + math.cos(angle) * distance
                    particle_y = hand_y + math.sin(angle) * distance
                    size = random.uniform(2, 5 * intensity)
                    
                    # Create a small particle with glow
                    particle_surf = pygame.Surface((int(size*3), int(size*3)), pygame.SRCALPHA)
                    
                    # Inner bright core
                    pygame.draw.circle(particle_surf, (255, 255, 255, 200), 
                                     (int(size*1.5), int(size*1.5)), size)
                    # Outer glow
                    pygame.draw.circle(particle_surf, (200, 220, 255, 100), 
                                     (int(size*1.5), int(size*1.5)), size*1.5)
                    
                    screen.blit(particle_surf, (particle_x - size*1.5, particle_y - size*1.5),
                               special_flags=pygame.BLEND_ADD)
                
                # Add magical runes/symbols for frame 3 (release point)
                if self.current_frame == 3:
                    # Create a magical rune/circle effect
                    rune_size = 80
                    rune_surf = pygame.Surface((rune_size, rune_size), pygame.SRCALPHA)
                    
                    # Outer circle
                    pygame.draw.circle(rune_surf, (120, 150, 255, 120), (rune_size//2, rune_size//2), 
                                     rune_size//2 - 2, 2)
                    
                    # Inner geometric pattern - spinning star
                    angle_offset = time.time() * 2  # Rotation
                    for i in range(5):  # 5-point star
                        angle1 = angle_offset + (i * 2 * math.pi / 5)
                        angle2 = angle_offset + ((i+2) % 5 * 2 * math.pi / 5)
                        
                        # Calculate points on circle
                        r = rune_size//3
                        x1 = rune_size//2 + int(r * math.cos(angle1))
                        y1 = rune_size//2 + int(r * math.sin(angle1))
                        x2 = rune_size//2 + int(r * math.cos(angle2))
                        y2 = rune_size//2 + int(r * math.sin(angle2))
                        
                        # Draw line segment
                        pygame.draw.line(rune_surf, (180, 200, 255, 150), (x1, y1), (x2, y2), 2)
                    
                    # Draw the rune behind the hand
                    screen.blit(rune_surf, (hand_x - rune_size//2, hand_y - rune_size//2),
                              special_flags=pygame.BLEND_ADD)
            else:
                # END STAGE: Spell has been cast, energy dissipating
                # Fading effect based on frame
                fade_factor = max(0, 1.0 - (self.current_frame - 3) * 0.3)
                
                # Residual energy glow
                glow_size = int(40 * fade_factor)
                if glow_size > 0:
                    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                    glow_color = (100, 100, 220, int(100 * fade_factor))
                    pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                    screen.blit(glow_surf, (hand_x - glow_size//2, hand_y - glow_size//2), 
                              special_flags=pygame.BLEND_ADD)
                
                # Trailing particles showing spell aftereffect
                if random.random() < 0.5 * fade_factor:
                    for _ in range(2):
                        # Particles drift away from hand
                        angle = random.uniform(0, 2 * math.pi)
                        distance = random.uniform(5, 15)
                        particle_x = hand_x + math.cos(angle) * distance
                        particle_y = hand_y + math.sin(angle) * distance
                        size = random.uniform(1, 3) * fade_factor
                        
                        # Small fading particles
                        particle_surf = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
                        pygame.draw.circle(particle_surf, (150, 150, 255, int(100 * fade_factor)), 
                                         (int(size), int(size)), size)
                        screen.blit(particle_surf, (particle_x - size, particle_y - size),
                                  special_flags=pygame.BLEND_ADD)
    
