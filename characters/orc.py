"""
Orc module.

This module contains the Orc class representing an orc enemy type in the game.

The Orc is a heavy, hard-hitting enemy that becomes enraged when low on health,
gaining increased speed and damage at the cost of slower attacks.
"""

import pygame
import math
import time
from characters.enemy import Enemy


class Orc(Enemy):
    """Represents an Orc enemy type.

    The Orc is a tanky, high-damage enemy that is slower than the Skeleton but
    can withstand far more punishment. When its health drops below 30%, it enters
    a Berserker Rage: movement speed and attack damage both increase, making it
    significantly more dangerous at low health.
    """

    # Constants
    MAX_HEALTH = 100          # Much tankier than Skeleton (40)
    ATTACK_DAMAGE = 20        # Hits harder than Skeleton (15)
    SPEED = 0.5               # Slower than Skeleton (1.5)
    AGGRO_RANGE = 180         # Slightly shorter sight range than Skeleton (220)
    ATTACK_RANGE = 80         # Longer melee reach due to size
    ATTACK_COOLDOWN = 2.5     # Slower attack rate than Skeleton

    ENRAGE_THRESHOLD = 0.30   # Enrage when health drops below 30%
    ENRAGE_SPEED_BONUS = 0.8  # Extra speed added when enraged
    ENRAGE_DAMAGE_BONUS = 10  # Extra damage added when enraged

    # Attributes
    enraged = None
    enrage_threshold = None
    enrage_speed_bonus = None
    enrage_damage_bonus = None
    enrage_flash_timer = None

    # Constructor
    def __init__(self, x, y, frames):
        """
        Initialise the Orc.

        Args:
            x (int): X-coordinate of the Orc.
            y (int): Y-coordinate of the Orc.
            frames (dict): Dictionary of animation frames for different states.
        """
        super().__init__(x, y, frames)

        # Override base enemy stats with Orc-specific values
        self.max_health = Orc.MAX_HEALTH
        self.health = Orc.MAX_HEALTH
        self.attack_damage = Orc.ATTACK_DAMAGE
        self.speed = Orc.SPEED
        self.aggro_range = Orc.AGGRO_RANGE
        self.attack_range = Orc.ATTACK_RANGE
        self.attack_cooldown = Orc.ATTACK_COOLDOWN

        # Orc-specific: Berserker Rage state
        self.enraged = False
        self.enrage_threshold = Orc.ENRAGE_THRESHOLD
        self.enrage_speed_bonus = Orc.ENRAGE_SPEED_BONUS
        self.enrage_damage_bonus = Orc.ENRAGE_DAMAGE_BONUS
        self.enrage_flash_timer = 0  # Used to drive the red flash visual effect

    # Accessors
    def get_enraged(self):
        return self.enraged

    def get_enrage_threshold(self):
        return self.enrage_threshold

    # Mutators
    def set_enraged(self, new_enraged):
        self.enraged = new_enraged

    def take_damage(self, amount):
        """
        Take damage, entering Berserker Rage when health drops below the threshold.

        When the Orc first crosses the enrage threshold it permanently gains bonus
        speed and attack damage for the rest of the encounter, representing the
        desperate fury of a wounded orc.

        Args:
            amount (int): The amount of damage to take.

        Returns:
            bool: True if the Orc died, False otherwise.
        """
        died = super().take_damage(amount)

        # Check whether the Orc should enter Berserker Rage (only triggers once)
        if not self.enraged and self.health <= self.max_health * self.enrage_threshold:
            self.enraged = True
            self.speed += self.enrage_speed_bonus
            self.attack_damage += self.enrage_damage_bonus

        return died

    # Behaviours
    def update(self, player):
        """
        Update the Orc based on its state and the player.

        Advances the enrage flash timer used by draw() to render the red tint
        visual effect when the Orc is enraged, then delegates to the base
        enemy update loop.

        Args:
            player: The player object to interact with.
        """
        # Advance the flash timer so draw() can pulse the enrage overlay
        if self.enraged:
            self.enrage_flash_timer += 1

        # Delegate movement, AI, and animation to the base enemy
        super().update(player)

    def draw(self, screen):
        """
        Draw the Orc with its current animation frame.

        When enraged, a semi-transparent red overlay is pulsed over the Orc's
        hitbox to make the visual state immediately obvious to the player.

        Args:
            screen: The pygame surface to draw on.
        """
        # Draw sprite and health bar via the base enemy draw method
        super().draw(screen)

        # Draw enrage visual effect: a pulsing red glow around the Orc
        if self.enraged and not self.is_dying:
            # Pulse the alpha between 60 and 160 using a sine wave
            pulse = math.sin(self.enrage_flash_timer * 0.15)  # -1 to 1
            alpha = int(110 + pulse * 50)                     # 60 to 160

            # Build a surface that matches the hitbox and fill it with red
            glow_size = max(self.hitbox.width, self.hitbox.height) + 14
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (200, 30, 30, alpha),
                (glow_size // 2, glow_size // 2),
                glow_size // 2
            )

            # Centre the glow on the Orc's hitbox
            screen.blit(
                glow_surface,
                (self.hitbox.centerx - glow_size // 2,
                 self.hitbox.centery - glow_size // 2)
            )
