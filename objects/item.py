"""
Item module.

This module contains the Item base class representing collectible items in the game.
Weapon and Potion are subclasses that override use() to apply their specific effects.
"""

import pygame
import math
from core.game_object import GameObject


# Rarity multipliers applied to base value
RARITY_MULTIPLIERS = {
    "common":    1.0,
    "uncommon":  1.5,
    "rare":      2.5,
    "epic":      4.0,
    "legendary": 7.0,
}

# Base gold values by item type
BASE_VALUES = {
    "weapon": 20,
    "potion": 10,
    "armour": 15,
    "spellbook": 25,
}


class Item(GameObject):
    """Represents a collectible item in the game.

    Stats (value) are set automatically based on type and rarity. Subclasses
    override use() to apply their specific effect to the player.
    """

    # Attributes
    item_type = None
    rarity = None
    name = None
    description = None
    value = None
    frames = None
    current_frame = None
    animation_timer = None
    animation_speed = None
    collected = None
    used = None
    equipped = None
    bob_offset = None
    bob_timer = None

    def __init__(self, x, y, width, height, item_type, rarity, name, frames=None):
        """
        Initialise the item.

        Args:
            x (int): X-coordinate of the item.
            y (int): Y-coordinate of the item.
            width (int): Width of the item's hitbox.
            height (int): Height of the item's hitbox.
            item_type (str): Type of item (weapon, potion, etc.).
            rarity (str): Rarity of the item (common, uncommon, rare, etc.).
            name (str): Name of the item.
            frames (list): List of animation frames for the item (optional).
        """
        super().__init__(x, y, width, height)

        self.item_type = item_type
        self.rarity = rarity
        self.name = name
        self.description = ""

        # Set value based on type and rarity
        base = BASE_VALUES.get(item_type, 10)
        multiplier = RARITY_MULTIPLIERS.get(rarity, 1.0)
        self.value = int(base * multiplier)

        # Animation
        self.frames = frames if frames else []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        # State
        self.collected = False
        self.used = False
        self.equipped = False

        # Floating bob effect
        self.bob_timer = 0
        self.bob_offset = 0

    # Accessors
    def get_item_type(self):
        return self.item_type

    def get_rarity(self):
        return self.rarity

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_collected(self):
        return self.collected

    def get_used(self):
        return self.used

    def get_equipped(self):
        return self.equipped

    # Mutators
    def set_description(self, description):
        self.description = description

    def set_collected(self, collected):
        self.collected = collected

    # Behaviours
    def update(self):
        """Update the item's animation and floating bob effect."""
        super().update()

        if self.collected:
            return

        # Advance sprite animation
        if self.frames:
            self.animation_timer += 1
            if self.animation_timer >= 1 / self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0

        # Gentle floating bob using a sine wave
        self.bob_timer += 0.08
        self.bob_offset = math.sin(self.bob_timer) * 4

    def collect(self):
        """
        Mark the item as collected.

        Returns:
            dict: Item properties, or None if already collected.
        """
        if not self.collected:
            self.collected = True
            return {
                "name": self.name,
                "type": self.item_type,
                "rarity": self.rarity,
                "value": self.value,
            }
        return None

    def use(self, player):
        """
        Use the item. Overridden by subclasses to apply specific effects.

        Args:
            player: The player object.

        Returns:
            bool: True if successfully used, False otherwise.
        """
        return False

    def draw(self, screen):
        """
        Draw the item with a floating bob effect and a coloured rarity glow.

        Args:
            screen: The pygame surface to draw on.
        """
        if self.collected or not self.frames:
            return

        # Rarity glow colours
        glow_colours = {
            "common":    (200, 200, 200, 60),
            "uncommon":  (30,  200,  30, 70),
            "rare":      (30,   80, 220, 80),
            "epic":      (160,  30, 220, 90),
            "legendary": (255, 160,   0, 100),
        }
        glow_colour = glow_colours.get(self.rarity, (200, 200, 200, 60))

        frame = self.frames[self.current_frame]
        draw_y = self.y + int(self.bob_offset)

        # Draw glow behind the sprite
        glow_radius = max(frame.get_width(), frame.get_height()) // 2 + 6
        glow_surf = pygame.Surface(
            (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            glow_surf, glow_colour,
            (glow_radius, glow_radius), glow_radius
        )
        screen.blit(
            glow_surf,
            (self.x + frame.get_width() // 2 - glow_radius,
             draw_y + frame.get_height() // 2 - glow_radius)
        )

        # Draw the sprite
        screen.blit(frame, (self.x, draw_y))
