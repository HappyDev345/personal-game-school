"""
UI module.

This module contains the UI class for rendering game user interface elements.
"""

import pygame
import time
import math
# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Colours
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

class UI:
    """Handles game user interface rendering."""
    
    def __init__(self):
        """Initialise the UI."""
        self.font = pygame.font.SysFont(None, 24)
        self.message = ""
        self.message_timer = 0
        self.message_duration = 3.0  # seconds
    
    def set_message(self, message):
        """
        Set a temporary message to display.
        
        Args:
            message (str): The message to display.
        """
        self.message = message
        self.message_timer = time.time()
    
    def draw(self, screen, player, inventory, score, enemy=None, level_num=1):
        """
        Draw the game UI.
        
        Args:
            screen: The pygame surface to draw on.
            player: The player object.
            inventory (dict): Player's inventory.
            score (int): Current game score.
            enemy: Optional enemy object for targeting information.
            level_num (int): Current level number.
        """
        # Health text
        health_text = self.font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (10, 10))
        
        # Level and score
        level_text = self.font.render(f"Level: {level_num}", True, WHITE)
        screen.blit(level_text, (10, 40))
        
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 70))
        
        # Inventory
        inventory_text = self.font.render(f"Gold: {inventory['gold']} | Potions: {inventory['health_potions']}", True, WHITE)
        screen.blit(inventory_text, (10, 100))

        # Attack damage — shows base + any weapon/strength buff bonus
        atk_text = self.font.render(f"Attack: {player.attack_damage}", True, WHITE)
        screen.blit(atk_text, (10, 130))

        # Equipped weapon name
        if hasattr(player, "equipped_weapon") and player.equipped_weapon is not None:
            weapon_colour = (255, 215, 0)  # Gold
            weapon_text = self.font.render(f"Weapon: {player.equipped_weapon.name}", True, weapon_colour)
            screen.blit(weapon_text, (10, 155))

        # Active buff timers
        if hasattr(player, "active_buffs") and player.active_buffs:
            buff_y = 180
            for buff_key, buff in player.active_buffs.items():
                remaining = max(0, buff["expiry"] - time.time())
                label = "SPD" if buff_key == "speed" else "STR"
                buff_colour = (100, 200, 255) if buff_key == "speed" else (255, 100, 100)
                buff_text = self.font.render(f"{label} buff: {remaining:.1f}s", True, buff_colour)
                screen.blit(buff_text, (10, buff_y))
                buff_y += 25
        
        # Show message if active
        if self.message and time.time() - self.message_timer < self.message_duration:
            # Render text first so we can measure its width
            message_surf = self.font.render(self.message, True, YELLOW)
            msg_width = message_surf.get_width() + 20  # Add padding

            # Create a semi-transparent background sized to the text
            message_bg = pygame.Surface((msg_width, 30), pygame.SRCALPHA)
            message_bg.fill((0, 0, 0, 150))
            screen.blit(message_bg, (SCREEN_WIDTH//2 - msg_width//2, SCREEN_HEIGHT - 100))

            # Draw message
            screen.blit(message_surf, (SCREEN_WIDTH//2 - message_surf.get_width()//2, SCREEN_HEIGHT - 95))
        
        # Draw instructions
        self.draw_instructions(screen)
    
    def draw_instructions(self, screen):
        """
        Draw game instructions.
        
        Args:
            screen: The pygame surface to draw on.
        """
        instructions = [
            "Controls:",
            "WASD/Arrows: Move",
            "SPACE: Attack",
            "E: Open Chests",
            "H: Use Potion",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH - 150, 10 + i * 20))
    
    def draw_debug_info(self, screen, player, enemy=None):
        """
        Draw debug information.
        
        This method has been removed for production.
        
        Args:
            screen: The pygame surface to draw on.
            player: The player object.
            enemy: Optional enemy object.
        """
        # Debug visualization removed for production
        pass