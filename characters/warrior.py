"""
Warrior module.

This module contains the Warrior class representing a player character with melee abilities.
"""

import pygame
import time
from characters.character import Character


class Warrior(Character):
    """Represents a warrior player character."""

    # Constants

    MAX_HEALTH = 100
    MAX_RAGE = 100
    ATTACK_DAMAGE = 20
    SPEED = 4
    ATTACK_RANGE = 100
    ATTACK_COOLDOWN = 0.5

    # Attributes

    max_health = None
    health = None
    attack_damage = None
    speed = None
    attack_range = None
    attack_cooldown = None
    rage = None
    max_rage = None
    blocking = None
    charging = None
    cleave_ready = None

    # Constructor

    def __init__(self, x, y, idle_frames, attack_frames, block_frames=None, charge_frames=None):
        """
        Initialise the warrior.

        Args:
            x (int): X-coordinate of the warrior.
            y (int): Y-coordinate of the warrior.
            idle_frames (list): List of idle animation frames.
            attack_frames (list): List of attack animation frames.
            block_frames (list): List of blocking animation frames (optional).
            charge_frames (list): List of charge animation frames (optional).
        """
        super().__init__(x, y, idle_frames, attack_frames)

        # Add warrior-specific animation states
        self.frames["block"] = block_frames if block_frames else []
        self.frames["charge"] = charge_frames if charge_frames else []

        # Override with warrior stats
        self.max_health = Warrior.MAX_HEALTH
        self.health = Warrior.MAX_HEALTH
        self.attack_damage = Warrior.ATTACK_DAMAGE
        self.speed = Warrior.SPEED
        self.attack_range = Warrior.ATTACK_RANGE
        self.attack_cooldown = Warrior.ATTACK_COOLDOWN

        # Warrior-specific attributes
        self.rage = 0
        self.max_rage = Warrior.MAX_RAGE
        self.blocking = False
        self.charging = False
        self.cleave_ready = False

    # Accessors

    def get_rage(self):
        """Return the current rage value."""
        return self.rage

    def get_max_rage(self):
        """Return the maximum rage value."""
        return self.max_rage

    def get_blocking(self):
        """Return whether the warrior is blocking."""
        return self.blocking

    def get_charging(self):
        """Return whether the warrior is charging."""
        return self.charging

    def get_cleave_ready(self):
        """Return whether cleave is ready."""
        return self.cleave_ready

    # Mutators

    def set_rage(self, new_rage):
        """Set the current rage value."""
        self.rage = new_rage

    def set_blocking(self, new_blocking):
        """Set the blocking state."""
        self.blocking = new_blocking

    def set_charging(self, new_charging):
        """Set the charging state."""
        self.charging = new_charging

    def set_cleave_ready(self, new_cleave_ready):
        """Set the cleave ready state."""
        self.cleave_ready = new_cleave_ready

    def take_damage(self, amount):
        """
        Take damage with potential blocking reduction.

        Args:
            amount (int): Amount of damage to take.

        Returns:
            bool: True if warrior died from damage, False otherwise.
        """
        # Handle blocking damage reduction
        if self.blocking:
            amount = max(1, amount // 2)  # Blocking reduces damage by half

        # Generate rage from damage taken
        rage_gain = amount * 0.5
        self.rage = min(self.max_rage, self.rage + rage_gain)

        # Call parent take_damage with modified amount
        return super().take_damage(amount)

    # Behaviours

    def update(self, game_map, enemies=None):
        """
        Update the warrior position and state.

        Args:
            game_map: The game map data for collision detection.
            enemies: Optional list of enemies for combat targeting.
        """
        # Call parent update
        super().update(game_map, enemies)

    def attack(self, target=None):
        """
        Perform a warrior attack with potential rage-powered abilities.

        Args:
            target: The target to attack (optional).

        Returns:
            bool: True if attack was successful, False otherwise.
        """
        # For now, use the base attack functionality
        return super().attack(target)

    def block(self):
        """
        Enter blocking stance to reduce incoming damage.

        Returns:
            bool: True if block was activated, False otherwise.
        """
        if not self.blocking and self.state != "attack":
            self.blocking = True
            self.state = "block"
            self.current_frame = 0
            return True

        return False

    def charge(self, target):
        """
        Charge quickly toward a target, dealing damage on impact.

        Args:
            target: The target to charge toward.

        Returns:
            bool: True if charge was successful, False otherwise.
        """
        return False

    def draw(self, screen):
        """
        Draw the warrior with the current animation frame.

        Args:
            screen: The pygame surface to draw on.
        """
        # Call parent draw method
        super().draw(screen)
