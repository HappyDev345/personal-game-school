"""
Potion module.

This module contains the Potion class representing a consumable potion item.

Three effect types are supported:
  - "health"  — instantly restores health
  - "speed"   — temporarily boosts movement speed for SPEED_DURATION seconds
  - "strength" — temporarily boosts attack damage for STRENGTH_DURATION seconds
"""

import pygame
import time
from objects.item import Item


class Potion(Item):
    """Represents a consumable potion with a single use effect.

    Health potions restore HP immediately. Speed and strength potions apply a
    timed buff stored directly on the player object; game.py's update loop
    calls player.update_buffs() each frame to expire them.
    """

    # Constants
    SPEED_DURATION     = 8.0   # seconds the speed buff lasts
    STRENGTH_DURATION  = 10.0  # seconds the strength buff lasts
    SPEED_BONUS        = 1.2   # added to player.speed while buff is active
    STRENGTH_BONUS     = 15    # added to player.attack_damage while buff is active

    # Attributes
    effect_type = None
    effect_amount = None
    duration = None

    def __init__(self, x, y, width, height, rarity, name, effect_type, effect_amount, frames=None):
        """
        Initialise a Potion item.

        Args:
            x (int): X-coordinate of the potion.
            y (int): Y-coordinate of the potion.
            width (int): Width of the potion's hitbox.
            height (int): Height of the potion's hitbox.
            rarity (str): Rarity tier.
            name (str): Display name of the potion.
            effect_type (str): One of "health", "speed", or "strength".
            effect_amount (int): Magnitude of the effect.
            frames (list): Animation frames (optional).
        """
        super().__init__(x, y, width, height, "potion", rarity, name, frames)

        self.effect_type = effect_type
        self.effect_amount = effect_amount

        # Duration only applies to timed buffs
        durations = {
            "speed":    Potion.SPEED_DURATION,
            "strength": Potion.STRENGTH_DURATION,
            "health":   0,
        }
        self.duration = durations.get(effect_type, 0)

        # Human-readable description
        descriptions = {
            "health":   f"Restores {effect_amount} HP",
            "speed":    f"+{Potion.SPEED_BONUS} speed for {int(Potion.SPEED_DURATION)}s",
            "strength": f"+{Potion.STRENGTH_BONUS} damage for {int(Potion.STRENGTH_DURATION)}s",
        }
        self.description = descriptions.get(effect_type, "")

    # Accessors
    def get_effect_type(self):
        return self.effect_type

    def get_effect_amount(self):
        return self.effect_amount

    def get_duration(self):
        return self.duration

    # Behaviours
    def use(self, player):
        """
        Consume the potion and apply its effect to the player.

        Health potions call player.heal() immediately. Speed and strength
        potions store a buff dict on the player (player.active_buffs) which
        the game loop should tick each frame via player.update_buffs().

        Args:
            player: The player character object.

        Returns:
            bool: True if the potion was consumed, False if already used.
        """
        if self.used:
            return False

        if self.effect_type == "health":
            player.heal(self.effect_amount)

        elif self.effect_type in ("speed", "strength"):
            # Initialise the buff tracker on the player if it doesn't exist
            if not hasattr(player, "active_buffs"):
                player.active_buffs = {}

            buff_key = self.effect_type
            expiry = time.time() + self.duration

            # If the buff is already running, just extend the expiry
            if buff_key in player.active_buffs:
                player.active_buffs[buff_key]["expiry"] = expiry
            else:
                # Apply the stat boost and record it
                if self.effect_type == "speed":
                    player.speed += Potion.SPEED_BONUS
                    player.active_buffs[buff_key] = {
                        "expiry": expiry,
                        "bonus":  Potion.SPEED_BONUS,
                    }
                elif self.effect_type == "strength":
                    player.attack_damage += Potion.STRENGTH_BONUS
                    player.active_buffs[buff_key] = {
                        "expiry": expiry,
                        "bonus":  Potion.STRENGTH_BONUS,
                    }

        self.used = True
        self.collected = True
        return True

    def update_buffs(self, player):
        """
        Expire any timed buffs whose duration has elapsed.

        This should be called once per frame from game.py's update loop.

        Args:
            player: The player character object.
        """
        if not hasattr(player, "active_buffs"):
            return

        now = time.time()
        expired = [k for k, v in player.active_buffs.items() if now >= v["expiry"]]

        for key in expired:
            buff = player.active_buffs.pop(key)
            if key == "speed":
                player.speed -= buff["bonus"]
            elif key == "strength":
                player.attack_damage -= buff["bonus"]
