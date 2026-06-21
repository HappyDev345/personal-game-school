"""
Enemy module.

This module contains the Enemy class representing enemies in the game.
"""

import pygame
import math
import time
from abc import abstractmethod
from core.map import TILE_SIZE
from core.game_object import GameObject

FPS = 60

class Enemy(GameObject):
    """Represents an enemy character."""
    
    # Constants
    MAX_HEALTH = 50
    WIDTH = 90
    HEIGHT = 115
    ANIMATION_SPEED = 0.2
    HITBOX_OFFSET_X = 33
    HITBOX_OFFSET_Y = 37
    SPEED = 1
    AGGRO_RANGE = 200
    ATTACK_RANGE = 80
    ATTACK_DAMAGE = 10
    ATTACK_COOLDOWN = 2.0
    
    # Attributes
    width = None
    height = None
    frames = None
    current_frame = None
    animation_timer = None
    animation_speed = None
    state = None
    direction = None
    animation_start_time = None
    max_health = None
    health = None
    hitbox_offset_x = None
    hitbox_offset_y = None
    hitbox = None
    speed = None
    aggro_range = None
    attack_range = None
    facing_left = None
    attack_damage = None
    attack_cooldown = None
    last_attack_time = None
    is_dying = None
    death_timer = None
    
    # Constructor
    def __init__(self, x, y, frames):
        """
        Initialise the enemy.
        
        Args:
            x (int): X-coordinate of the enemy.
            y (int): Y-coordinate of the enemy.
            frames (dict): Dictionary of animation frames for different states.
        """
        # Smaller hitbox to match player's and allow movement through narrow passages
        hitbox_width = 25  # Reduced from 30
        hitbox_height = 35  # Reduced from 40
        super().__init__(x, y, hitbox_width, hitbox_height)
        
        # Set full sprite dimensions
        self.width = Enemy.WIDTH
        self.height = Enemy.HEIGHT

        self.frames = frames
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = Enemy.ANIMATION_SPEED
        self.state = "idle"  # Can be "idle", "attack", "hurt", or "death"
        self.direction = "left"  # Can be "left" or "right"
        self.animation_start_time = 0

        # Health
        self.max_health = Enemy.MAX_HEALTH
        self.health = Enemy.MAX_HEALTH

        # Hitbox with offset from sprite position
        # The skeleton sprite has empty space around it - like the player sprite
        # Sprite size is 90x115, but the character's body is positioned more in the middle
        self.hitbox_offset_x = Enemy.HITBOX_OFFSET_X  # Adjusted to centre the narrower hitbox
        self.hitbox_offset_y = Enemy.HITBOX_OFFSET_Y  # Raised slightly higher for the shorter hitbox
        self.hitbox = pygame.Rect(x + self.hitbox_offset_x, y + self.hitbox_offset_y, hitbox_width, hitbox_height)

        # Movement and AI
        self.speed = Enemy.SPEED
        self.aggro_range = Enemy.AGGRO_RANGE
        self.attack_range = Enemy.ATTACK_RANGE
        self.facing_left = True

        # Combat
        self.attack_damage = Enemy.ATTACK_DAMAGE
        self.attack_cooldown = Enemy.ATTACK_COOLDOWN
        self.last_attack_time = 0

        # Death animation
        self.is_dying = False
        self.death_timer = 0
    
    # Accessors
    def get_health(self):
        return self.health

    def get_max_health(self):
        return self.max_health

    def get_speed(self):
        return self.speed

    def get_attack_damage(self):
        return self.attack_damage

    def get_attack_range(self):
        return self.attack_range

    def get_aggro_range(self):
        return self.aggro_range

    def get_state(self):
        return self.state

    def get_facing_left(self):
        return self.facing_left

    def get_is_dying(self):
        return self.is_dying

    def is_alive(self):
        """
        Check if enemy is alive.
        
        Returns:
            bool: True if the enemy is alive, False otherwise.
        """
        return self.health > 0 and not self.is_dying
    
    def _distance_to_player(self, player):
        """
        Calculate distance to the player.
        
        Args:
            player: The player object.
            
        Returns:
            float: Distance to the player in pixels.
        """
        return math.sqrt((self.hitbox.centerx - player.hitbox.centerx)**2 + 
                         (self.hitbox.centery - player.hitbox.centery)**2)
    
    def _is_valid_position(self, game_map):
        """
        Check if the current position is valid (not inside a wall).
        
        Args:
            game_map: The game map data.
            
        Returns:
            bool: True if the position is valid, False if inside a wall.
        """
        if game_map is None:
            return True  # No map provided, assume valid position
            
        # Check corners for collision
        points = [
            # Corners
            (self.hitbox.left, self.hitbox.top),
            (self.hitbox.right, self.hitbox.top),
            (self.hitbox.left, self.hitbox.bottom),
            (self.hitbox.right, self.hitbox.bottom),
            # Centre
            (self.hitbox.centerx, self.hitbox.centery)
        ]
        
        for px, py in points:
            # Convert to tile coordinates
            tile_x = px // TILE_SIZE
            tile_y = py // TILE_SIZE
            
            # Check if tile is a wall
            if hasattr(game_map, 'is_wall'):
                if game_map.is_wall(tile_x, tile_y):
                    return False
        
        return True
    
    # Mutators
    def set_health(self, new_health):
        self.health = new_health

    def set_speed(self, new_speed):
        self.speed = new_speed

    def set_attack_damage(self, new_attack_damage):
        self.attack_damage = new_attack_damage

    def set_attack_range(self, new_attack_range):
        self.attack_range = new_attack_range

    def set_aggro_range(self, new_aggro_range):
        self.aggro_range = new_aggro_range

    def set_state(self, new_state):
        self.state = new_state

    def set_facing_left(self, new_facing_left):
        self.facing_left = new_facing_left

    @abstractmethod
    def take_damage(self, amount):
        """
        Take damage from the player.

        This method must be implemented by subclasses to define enemy-specific
        damage response (e.g. berserker rage for Orc, bone shield for Skeleton).

        Args:
            amount (int): The amount of damage to take.

        Returns:
            bool: True if the enemy died, False otherwise.
        """
        self.health -= amount
        
        # Ensure health doesn't go below 0
        if self.health < 0:
            self.health = 0
        
        # If enemy dies from this damage
        if self.health <= 0:
            self.state = "death"
            self.animation_start_time = time.time()
            self.is_dying = True
            self.death_timer = 0
            return True
        
        # Otherwise, enter hurt state
        self.state = "hurt"
        self.animation_start_time = time.time()
        self.current_frame = 0
        return False
    
    # Behaviours
    def update(self, player):
        """
        Update the enemy based on its state and the player.
        
        Args:
            player: The player object to interact with.
        """
        current_time = time.time()
        
        # Update hitbox position
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y
        
        # If enemy is dead or dying, just update death animation
        if self.state == "death" or self.is_dying:
            self.is_dying = True
            self.state = "death"
            
            # Death animation timing
            frames_per_second = 8
            self.death_timer += 1 / FPS
            self.current_frame = min(int(self.death_timer * frames_per_second), len(self.frames["death"]) - 1)
            
            # If reached the end of death animation, keep the last frame
            if self.current_frame >= len(self.frames["death"]) - 1:
                self.current_frame = len(self.frames["death"]) - 1
            
            return
        
        # Handle state transitions based on player proximity
        player_distance = self._distance_to_player(player)
        
        # Update direction based on player position
        if player.hitbox.centerx < self.hitbox.centerx:
            self.facing_left = True
            self.direction = "left"
        else:
            self.facing_left = False
            self.direction = "right"
        
        # State machine
        if self.state == "hurt":
            # Stay in hurt state until animation completes
            frames_per_second = 10
            elapsed = current_time - self.animation_start_time
            self.current_frame = min(int(elapsed * frames_per_second), len(self.frames["hurt"]) - 1)
            
            if self.current_frame >= len(self.frames["hurt"]) - 1:
                self.state = "idle"
                self.current_frame = 0
                
        elif self.state == "attack":
            # Stay in attack state until animation completes
            frames_per_second = 10
            elapsed = current_time - self.animation_start_time
            self.current_frame = min(int(elapsed * frames_per_second), len(self.frames["attack"]) - 1)
            
            if self.current_frame >= len(self.frames["attack"]) - 1:
                self.state = "idle"
                self.current_frame = 0
                
                # Deal damage to player at the end of attack animation
                if player_distance <= self.attack_range:
                    player.take_damage(self.attack_damage)
        
        elif player_distance <= self.attack_range:
            # Player in attack range - attack if cooldown elapsed
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.state = "attack"
                self.animation_start_time = current_time
                self.last_attack_time = current_time
                self.current_frame = 0
        
        elif player_distance <= self.aggro_range:
            # Player in aggro range but not attack range - move toward player
            self.state = "idle"  # We'll use idle animation for movement
            
            # Store previous position for collision rollback
            old_x, old_y = self.x, self.y
            
            # Get direction to player
            dx = player.hitbox.centerx - self.hitbox.centerx
            dy = player.hitbox.centery - self.hitbox.centery
            
            # Normalise direction
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx /= length
                dy /= length
            
            # Move toward player (try horizontal and vertical movement separately)
            # Try horizontal movement
            self.x += dx * self.speed
            self.hitbox.x = self.x + self.hitbox_offset_x
            
            # Use self.game_map if available, otherwise try player.game_map
            game_map = getattr(self, 'game_map', None) or getattr(player, 'game_map', None)
            
            if game_map and not self._is_valid_position(game_map):
                # Horizontal movement caused collision, revert it
                self.x = old_x
                self.hitbox.x = old_x + self.hitbox_offset_x
            
            # Try vertical movement
            self.y += dy * self.speed
            self.hitbox.y = self.y + self.hitbox_offset_y
            if game_map and not self._is_valid_position(game_map):
                # Vertical movement caused collision, revert it
                self.y = old_y
                self.hitbox.y = old_y + self.hitbox_offset_y
        
        else:
            # Player not in range - idle
            self.state = "idle"
        
        # Update idle animation if in idle state
        if self.state == "idle":
            self.animation_timer += 1
            if self.animation_timer >= 1 / self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames["idle"])
                self.animation_timer = 0
    
    def draw(self, screen):
        """
        Draw the enemy with the current animation frame.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Get the current frame based on state
        frame = self.frames[self.state][min(self.current_frame, len(self.frames[self.state]) - 1)]
        
        # Flip the frame if facing right (assuming frames face left by default)
        if not self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        
        # Draw the frame
        screen.blit(frame, (self.x, self.y))
        
        # Draw health bar only if alive
        if self.health > 0:
            health_bar_width = 25  # Match hitbox width
            health_bar_height = 4
            health_ratio = self.health / self.max_health
            
            # Position health bar above the hitbox
            health_bar_x = self.hitbox.x
            health_bar_y = self.hitbox.y - 8
            
            # Background
            pygame.draw.rect(screen, (100, 0, 0), 
                           (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            
            # Health
            pygame.draw.rect(screen, (200, 0, 0), 
                           (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
        
        # Debug: Draw hitbox and sprite boundaries when F1 is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_F1]:
            # Draw sprite boundaries
            sprite_rect = pygame.Rect(self.x, self.y, 90, 115)  # Actual sprite dimensions
            pygame.draw.rect(screen, (0, 0, 255), sprite_rect, 1)  # Blue rectangle
            
            # Draw a vertical centre line for the sprite
            pygame.draw.line(screen, (0, 0, 255), 
                           (self.x + 90//2, self.y), 
                           (self.x + 90//2, self.y + 115), 1)
            
            # Draw hitbox
            pygame.draw.rect(screen, (0, 255, 0), self.hitbox, 1)  # Green rectangle
