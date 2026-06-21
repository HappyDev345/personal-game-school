"""
Weapon module.

This module contains the Weapon class representing an equippable weapon item.

Picking up a weapon permanently boosts the player's attack_damage for the
remainder of the run. Only one weapon can be equipped at a time; equipping a
new one replaces the old bonus.
"""

import pygame
import time
from objects.item import Item


class Weapon(Item):
    """Represents a weapon item that can be picked up and equipped.

    On use(), the weapon's damage bonus is applied to the player's
    attack_damage. If the player already has a weapon equipped, the old bonus
    is removed first so bonuses never stack unintentionally.
    """

    # Constants
    DEFAULT_ATTACK_SPEED = 1.0   # Multiplier (1.0 = normal, <1 = slower, >1 = faster)

    # Attributes
    damage = None
    attack_speed = None
    damage_bonus_applied = None

    def __init__(self, x, y, width, height, rarity, name, damage, frames=None):
        """
        Initialise a Weapon item.

        Args:
            x (int): X-coordinate of the weapon.
            y (int): Y-coordinate of the weapon.
            width (int): Width of the weapon's hitbox.
            height (int): Height of the weapon's hitbox.
            rarity (str): Rarity tier (common, uncommon, rare, epic, legendary).
            name (str): Display name of the weapon.
            damage (int): Damage bonus granted when equipped.
            frames (list): Animation frames (optional).
        """
        super().__init__(x, y, width, height, "weapon", rarity, name, frames)

        self.damage = damage
        self.description = f"+{damage} attack damage"

        # Attack speed scales slightly with rarity
        rarity_speed = {
            "common":    0.9,
            "uncommon":  1.0,
            "rare":      1.1,
            "epic":      1.2,
            "legendary": 1.4,
        }
        self.attack_speed = rarity_speed.get(rarity, Weapon.DEFAULT_ATTACK_SPEED)

        # Tracks whether this weapon's bonus is currently on the player
        self.damage_bonus_applied = False

    # Accessors
    def get_damage(self):
        return self.damage

    def get_attack_speed(self):
        return self.attack_speed

    def get_damage_bonus_applied(self):
        return self.damage_bonus_applied

    # Behaviours
    def use(self, player):
        """
        Equip the weapon, applying its damage bonus to the player.

        If the player already has a weapon equipped (tracked via
        player.equipped_weapon), that weapon's bonus is removed first.
        The new bonus is then applied and this weapon is stored as the
        player's active weapon.

        Args:
            player: The player character object.

        Returns:
            bool: True if the weapon was equipped, False if already equipped.
        """
        if self.equipped:
            return False

        # Remove the previous weapon's bonus if one is equipped
        if hasattr(player, "equipped_weapon") and player.equipped_weapon is not None:
            old_weapon = player.equipped_weapon
            if old_weapon.damage_bonus_applied:
                player.attack_damage -= old_weapon.damage
                old_weapon.damage_bonus_applied = False
                old_weapon.equipped = False

        # Apply this weapon's damage bonus
        player.attack_damage += self.damage
        self.damage_bonus_applied = True
        self.equipped = True
        self.used = True

        # Store reference on the player for future swaps
        player.equipped_weapon = self

        return True
