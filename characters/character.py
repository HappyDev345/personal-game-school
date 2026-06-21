"""
Character module.

This module contains the base Character class that all playable characters
inherit from. It provides common functionality for player-controlled characters
including movement, combat, and animation."""

import pygame
import math
import time
from abc import abstractmethod
from core.map import TILE_SIZE
from core.game_object import GameObject


class Character(GameObject):
    """Base class for all player-controlled characters (Warrior, Wizard, etc.)."""

    # Constants

    MAX_HEALTH = 100
    SPEED = 2
    ATTACK_DAMAGE = 10
    DEFENCE = 0
    ATTACK_RANGE = 50
    ATTACK_COOLDOWN = 1.0
    ANIMATION_SPEED = 0.15

    # Attributes

    frames = None
    current_frame = None
    animation_timer = None
    animation_speed = None
    state = None
    attacking = None
    attack_start_time = None
    facing_left = None
    hitbox_offset_x = None
    hitbox_offset_y = None
    speed = None
    max_health = None
    health = None
    attack_damage = None
    defence = None
    attack_range = None
    attack_cooldown = None
    last_attack_time = None

    # Constructor

    def __init__(self, x, y, idle_frames, attack_frames):
        """
        Initialise a character.

        Args:
            x (int): X-coordinate of the character.
            y (int): Y-coordinate of the character.
            idle_frames (list): List of idle animation frames.
            attack_frames (list): List of attack animation frames.
        """
        # Compute content bounding rect from idle frames to size the hitbox
        content_rect = None
        for frame in idle_frames:
            bbox = frame.get_bounding_rect()
            if bbox.width > 0 and bbox.height > 0:
                if content_rect is None:
                    content_rect = bbox.copy()
                else:
                    content_rect.union_ip(bbox)

        # Fallback for transparent/empty frames (e.g. unit tests with dummy surfaces)
        if content_rect is None or content_rect.width == 0 or content_rect.height == 0:
            content_rect = pygame.Rect(0, 0, idle_frames[0].get_width(), idle_frames[0].get_height())
        else:
            # Add small margin for gameplay feel
            margin = 2
            content_rect.inflate_ip(margin * 2, margin * 2)
            content_rect.clamp_ip(pygame.Rect(0, 0, idle_frames[0].get_width(), idle_frames[0].get_height()))

        self.content_rect = content_rect

        # Hitbox dimensions match the visible content area
        hitbox_width = content_rect.width
        hitbox_height = content_rect.height
        super().__init__(x, y, hitbox_width, hitbox_height)

        # Animation frames stored by state
        self.frames = {
            "idle": idle_frames,
            "attack": attack_frames
        }
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = Character.ANIMATION_SPEED  # Lower is faster
        self.state = "idle"  # Can be "idle" or "attack"
        self.attacking = False
        self.attack_start_time = 0
        self.facing_left = False

        # Hitbox offset derived from content bounding rect
        self.hitbox_offset_x = content_rect.x
        self.hitbox_offset_y = content_rect.y
        self.hitbox = pygame.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y,
            hitbox_width,
            hitbox_height
        )

        # Movement properties
        self.speed = Character.SPEED

        # Health
        self.max_health = Character.MAX_HEALTH
        self.health = Character.MAX_HEALTH

        # Combat properties
        self.attack_damage = Character.ATTACK_DAMAGE
        self.defence = Character.DEFENCE  # Australian spelling: defence
        self.attack_range = Character.ATTACK_RANGE
        self.attack_cooldown = Character.ATTACK_COOLDOWN
        self.last_attack_time = 0

    # Accessors

    def get_health(self):
        return self.health

    def get_max_health(self):
        return self.max_health

    def get_speed(self):
        return self.speed

    def get_attack_damage(self):
        return self.attack_damage

    def get_defence(self):
        return self.defence

    def get_attack_range(self):
        return self.attack_range

    def get_attack_cooldown(self):
        return self.attack_cooldown

    def get_facing_left(self):
        return self.facing_left

    def get_state(self):
        return self.state

    def is_alive(self):
        """
        Check if the character is alive.

        Returns:
            bool: True if alive, False if dead.
        """
        return self.health > 0

    def _is_valid_position(self, game_map):
        """
        Check if the current position is valid (not colliding with walls).

        Args:
            game_map: The game map for collision detection.

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        # Check corners and centre of hitbox for collision
        points = [
            (self.hitbox.left, self.hitbox.top),
            (self.hitbox.right, self.hitbox.top),
            (self.hitbox.left, self.hitbox.bottom),
            (self.hitbox.right, self.hitbox.bottom),
            (self.hitbox.centerx, self.hitbox.centery)
        ]

        for px, py in points:
            # Convert to tile coordinates
            tile_x = px // TILE_SIZE
            tile_y = py // TILE_SIZE

            # Check if tile is a wall
            if hasattr(game_map, 'is_wall') and game_map.is_wall(tile_x, tile_y):
                return False

        return True

    def _is_in_attack_range(self, target):
        """
        Check if target is within attack range.

        Args:
            target: The target character.

        Returns:
            bool: True if in range, False otherwise.
        """
        # Calculate distance from character centre to target centre
        char_centre_x = self.hitbox.centerx
        char_centre_y = self.hitbox.centery
        target_centre_x = target.hitbox.centerx
        target_centre_y = target.hitbox.centery

        # Calculate distance
        dist = math.sqrt((char_centre_x - target_centre_x) ** 2 +
                         (char_centre_y - target_centre_y) ** 2)

        # Check direction for melee attacks (facing matters)
        if self.attack_range < 100:  # Assume melee attack
            if self.facing_left and target_centre_x > char_centre_x:
                return False
            if not self.facing_left and target_centre_x < char_centre_x:
                return False

        return dist <= self.attack_range

    # Mutators

    def set_health(self, new_health):
        self.health = new_health

    def set_speed(self, new_speed):
        self.speed = new_speed

    def set_attack_damage(self, new_attack_damage):
        self.attack_damage = new_attack_damage

    def set_defence(self, new_defence):
        self.defence = new_defence

    def set_attack_range(self, new_attack_range):
        self.attack_range = new_attack_range

    def set_attack_cooldown(self, new_attack_cooldown):
        self.attack_cooldown = new_attack_cooldown

    def set_facing_left(self, new_facing_left):
        self.facing_left = new_facing_left

    def take_damage(self, amount):
        """
        Take damage from an attack.

        Args:
            amount (int): The amount of damage to take.

        Returns:
            bool: True if the character died, False otherwise.
        """
        self.health -= amount
        if self.health < 0:
            self.health = 0
        return self.health <= 0

    def heal(self, amount):
        """
        Heal the character.

        Args:
            amount (int): Amount of health to restore.

        Returns:
            int: Amount of health actually restored.
        """
        if self.health >= self.max_health:
            return 0

        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health

    def teleport(self, x, y):
        """
        Teleport the character to a new position.

        Args:
            x (int): The new x coordinate.
            y (int): The new y coordinate.
        """
        self.x = x
        self.y = y
        self.hitbox.x = x + self.hitbox_offset_x
        self.hitbox.y = y + self.hitbox_offset_y

    # Behaviours

    def update(self, game_map, enemies=None):
        """
        Update the character's position, input, and animation.

        Handles keyboard input for movement (WASD/arrows) and attacking (space).
        Manages animation state transitions between idle and attack.

        Args:
            game_map: The game map for collision detection.
            enemies: Optional list of enemies (used by subclasses like Wizard).
        """
        # Store reference to game map for other objects to use
        self.game_map = game_map

        keys = pygame.key.get_pressed()
        current_time = time.time()

        # Only process movement if not attacking
        if not self.attacking:
            # Store previous position
            old_x, old_y = self.x, self.y

            # Handle movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= self.speed
                self.facing_left = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += self.speed
                self.facing_left = False
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += self.speed

            # Update hitbox position with offset
            self.hitbox.x = self.x + self.hitbox_offset_x
            self.hitbox.y = self.y + self.hitbox_offset_y

            # Check collision and revert if needed
            if not self._is_valid_position(game_map):
                self.x, self.y = old_x, old_y
                self.hitbox.x = self.x + self.hitbox_offset_x
                self.hitbox.y = self.y + self.hitbox_offset_y

        # Check for attack
        attack_key_pressed = keys[pygame.K_SPACE]
        cooldown_elapsed = current_time - self.last_attack_time
        can_attack = cooldown_elapsed >= self.attack_cooldown

        if attack_key_pressed and not self.attacking and can_attack:
            self.state = "attack"
            self.attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            self.current_frame = 0

        # Update animation
        self.animation_timer += 1

        if self.state == "idle":
            # Cycle through idle animation
            if self.animation_timer >= 1 / self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames["idle"])
                self.animation_timer = 0
        elif self.state == "attack":
            # Attack animation plays once at a fixed rate
            frames_per_second = 6
            elapsed = current_time - self.attack_start_time
            new_frame = min(
                int(elapsed * frames_per_second),
                len(self.frames["attack"]) - 1
            )

            if new_frame != self.current_frame:
                self.current_frame = new_frame

            # Return to idle when attack animation finishes
            if self.current_frame >= len(self.frames["attack"]) - 1:
                self.state = "idle"
                self.attacking = False
                self.current_frame = 0

                # Clean up per-animation flags used by the game loop
                if hasattr(self, '_attacked_this_animation'):
                    delattr(self, '_attacked_this_animation')

    def move(self, dx, dy, game_map=None):
        """
        Move the character if movement is valid.

        Args:
            dx (int): X-direction to move (-1, 0, 1).
            dy (int): Y-direction to move (-1, 0, 1).
            game_map: The game map for collision detection.

        Returns:
            bool: True if movement was successful, False otherwise.
        """
        # Store previous position
        old_x, old_y = self.x, self.y

        # Update position
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Update hitbox position
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y

        # Check if new position is valid
        if game_map and not self._is_valid_position(game_map):
            # Revert to previous position if invalid
            self.x, self.y = old_x, old_y
            self.hitbox.x = self.x + self.hitbox_offset_x
            self.hitbox.y = self.y + self.hitbox_offset_y
            return False

        return True

    @abstractmethod
    def attack(self, target=None):
        """
        Perform an attack.

        This method must be implemented by subclasses to define character-specific
        attack behaviour (e.g. melee for Warrior, projectile for Wizard).

        Args:
            target: The target character to attack (optional).

        Returns:
            bool: True if attack was successful, False otherwise.
        """
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False  # Still on cooldown

        # Update attack state
        self.state = "attack"
        self.current_frame = 0
        self.last_attack_time = current_time

        # If target is specified, deal damage
        if target and self._is_in_attack_range(target):
            target.take_damage(self.attack_damage)
            return True

        return False

    def draw(self, screen):
        """
        Draw the character with the current animation frame, centred on the hitbox.

        Args:
            screen: The pygame surface to draw on.
        """
        # Get the current frame based on state
        if self.state in self.frames and self.frames[self.state]:
            frame = self.frames[self.state][self.current_frame]
        else:
            return

        # Flip the frame if facing left
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        # Draw frame at sprite position; hitbox offset aligns it with visible content
        screen.blit(frame, (self.x, self.y))

        # Draw health bar above the hitbox
        health_bar_width = self.hitbox.width
        health_bar_height = 5
        health_ratio = self.health / self.max_health

        # Position health bar above the hitbox
        health_bar_x = self.hitbox.x
        health_bar_y = self.hitbox.y - 10

        # Background
        pygame.draw.rect(screen, (100, 0, 0),
                         (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

        # Health
        pygame.draw.rect(screen, (0, 200, 0),
                         (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
