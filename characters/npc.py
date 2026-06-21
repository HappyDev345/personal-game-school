"""
NPC module.

This module contains the NPC class representing a non-player character in the game.

The NPC is a Priest who offers healing to the player in exchange for gold.
Pressing E within range opens a dialog; if the player has enough gold the
priest restores health and deducts the cost.
"""

import pygame
import math
import time
from core.map import TILE_SIZE
from core.game_object import GameObject


class NPC(GameObject):
    """Represents a non-player character that can be interacted with.

    The Priest NPC offers a paid healing service: for HEAL_COST gold the player
    receives HEAL_AMOUNT health points. The interaction box displays a contextual
    dialog depending on whether the player is already at full health, cannot
    afford the service, or successfully receives a blessing.
    """

    # Constants
    INTERACTION_RANGE = 100
    ANIMATION_SPEED = 0.2
    HITBOX_OFFSET_X = 33
    HITBOX_OFFSET_Y = 37
    INTERACTION_COOLDOWN = 1.5

    HEAL_COST = 20    # Gold required for a blessing
    HEAL_AMOUNT = 50  # Health points restored per blessing

    # Dialogue lines shown in the interaction box
    DIALOG_GREET    = ["Greetings, traveller.", f"Blessing costs {HEAL_COST} gold."]
    DIALOG_FULL     = ["You are already", "at full health."]
    DIALOG_POOR     = [f"You need {HEAL_COST} gold", "for a blessing."]
    DIALOG_HEALED   = [f"The Light heals you.", f"+{HEAL_AMOUNT} HP restored."]

    # Attributes
    interacting = None
    interaction_cooldown = None
    last_interaction_time = None
    interaction_range = None
    width = None
    height = None
    idle_frames = None
    current_frame = None
    animation_timer = None
    animation_speed = None
    facing_left = None
    hitbox_offset_x = None
    hitbox_offset_y = None
    hitbox = None
    dialog_lines = None

    # Constructor
    def __init__(self, x, y, idle_frames):
        """
        Initialise the NPC.

        Args:
            x (int): X-coordinate of the NPC.
            y (int): Y-coordinate of the NPC.
            idle_frames (list): List of idle animation frames.
        """
        hitbox_width = 25
        hitbox_height = 35
        super().__init__(x, y, hitbox_width, hitbox_height)

        self.width = idle_frames[0].get_width() if idle_frames else 90
        self.height = idle_frames[0].get_height() if idle_frames else 115

        # Animation
        self.idle_frames = idle_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = NPC.ANIMATION_SPEED
        self.facing_left = False

        # Hitbox
        self.hitbox_offset_x = NPC.HITBOX_OFFSET_X
        self.hitbox_offset_y = NPC.HITBOX_OFFSET_Y
        self.hitbox = pygame.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y,
            hitbox_width,
            hitbox_height
        )

        # Interaction state
        self.interacting = False
        self.interaction_cooldown = NPC.INTERACTION_COOLDOWN
        self.last_interaction_time = 0
        self.interaction_range = NPC.INTERACTION_RANGE

        # Dialog — starts with the greeting so the box is never blank
        self.dialog_lines = list(NPC.DIALOG_GREET)

    # Accessors
    def get_interacting(self):
        return self.interacting

    def get_interaction_range(self):
        return self.interaction_range

    def get_facing_left(self):
        return self.facing_left

    def get_dialog_lines(self):
        return self.dialog_lines

    def is_player_in_range(self, player):
        """
        Check if the player is within interaction range.

        Args:
            player: The player object.

        Returns:
            bool: True if the player is in range, False otherwise.
        """
        npc_centre_x = self.hitbox.centerx
        npc_centre_y = self.hitbox.centery
        player_centre_x = player.hitbox.centerx
        player_centre_y = player.hitbox.centery

        dist = math.sqrt(
            (npc_centre_x - player_centre_x) ** 2 +
            (npc_centre_y - player_centre_y) ** 2
        )
        return dist <= self.interaction_range

    # Mutators
    def set_interacting(self, new_interacting):
        self.interacting = new_interacting

    def set_facing_left(self, new_facing_left):
        self.facing_left = new_facing_left

    def interact(self, player, inventory):
        """
        Interact with the NPC.

        Attempts to heal the player for HEAL_COST gold. Sets dialog_lines to
        reflect the outcome:
          - Player is at full health: DIALOG_FULL
          - Player cannot afford the blessing: DIALOG_POOR
          - Successful heal: deduct gold, restore health, DIALOG_HEALED

        Interaction is gated by a cooldown so repeated key-presses do not
        trigger multiple effects in quick succession.

        Args:
            player: The player object (must have health, max_health, heal()).
            inventory (dict): The game inventory dict containing "gold".

        Returns:
            bool: True if the interaction was processed, False if on cooldown.
        """
        current_time = time.time()
        cooldown_elapsed = (
            current_time - self.last_interaction_time >= self.interaction_cooldown
        )

        if not cooldown_elapsed or self.interacting:
            return False

        self.interacting = True
        self.last_interaction_time = current_time

        # Determine outcome and update dialog
        if player.health >= player.max_health:
            self.dialog_lines = list(NPC.DIALOG_FULL)

        elif inventory.get("gold", 0) < NPC.HEAL_COST:
            self.dialog_lines = list(NPC.DIALOG_POOR)

        else:
            # Deduct cost and restore health
            inventory["gold"] -= NPC.HEAL_COST
            player.heal(NPC.HEAL_AMOUNT)
            self.dialog_lines = list(NPC.DIALOG_HEALED)

        return True

    # Behaviours
    def update(self, player=None):
        """
        Update the NPC's animation and interaction state.

        Args:
            player: The player object for direction-facing.
        """
        # Update hitbox position
        self.hitbox.x = self.x + self.hitbox_offset_x
        self.hitbox.y = self.y + self.hitbox_offset_y

        # Face the player
        if player:
            self.facing_left = player.hitbox.centerx < self.hitbox.centerx

        # Advance idle animation
        self.animation_timer += 1
        if self.animation_timer >= 1 / self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.animation_timer = 0

        # Reset interacting flag after cooldown so the box closes automatically
        current_time = time.time()
        if (self.interacting and
                current_time - self.last_interaction_time >= self.interaction_cooldown):
            self.interacting = False
            self.dialog_lines = list(NPC.DIALOG_GREET)  # Reset to greeting

    def draw(self, screen):
        """
        Draw the NPC with the current animation frame.

        Args:
            screen: The pygame surface to draw on.
        """
        frame = self.idle_frames[self.current_frame]

        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        screen.blit(frame, (self.x, self.y))

    def draw_interaction_box(self, screen):
        """
        Draw the dialog box with contextual healing text when interacting.

        The box is centred horizontally and anchored near the bottom of the
        screen. Two lines of dialog are rendered inside it.

        Args:
            screen: The pygame surface to draw on.
        """
        if not self.interacting:
            return

        box_width = min(320, screen.get_width() - 40)
        box_height = 110
        box_x = (screen.get_width() - box_width) // 2
        box_y = screen.get_height() - box_height - 50

        # Semi-transparent dark background
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 220))
        screen.blit(box_surface, (box_x, box_y))

        # Gold border
        dialog_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (212, 175, 55), dialog_rect, 2)

        # Priest name header
        header_font = pygame.font.SysFont("Arial", 14, bold=True)
        name_surf = header_font.render("Priest", True, (212, 175, 55))
        screen.blit(name_surf, (box_x + 12, box_y + 10))

        # Dialog text — up to two lines
        body_font = pygame.font.SysFont("Arial", 13)
        for i, line in enumerate(self.dialog_lines[:2]):
            text_surf = body_font.render(line, True, (255, 255, 255))
            screen.blit(text_surf, (box_x + 12, box_y + 34 + i * 22))

        # Prompt hint at the bottom
        hint_font = pygame.font.SysFont("Arial", 11)
        hint_surf = hint_font.render("[E] interact", True, (160, 160, 160))
        screen.blit(hint_surf, (box_x + box_width - hint_surf.get_width() - 10,
                                box_y + box_height - hint_surf.get_height() - 8))
