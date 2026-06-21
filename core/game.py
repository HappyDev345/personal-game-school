"""
Game module.

This module contains the Game class that manages the game state and main loop.
"""

import pygame
import time
import random
import sys
import math
import os

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

from core.map import TILE_SIZE, MAPS, MAP_WIDTH, MAP_HEIGHT
from assets.asset_loader import AssetLoader

# Create a global asset loader instance that can be imported by other modules
asset_loader_instance = None
from characters.warrior import Warrior
from characters.wizard import Wizard
from characters.enemy import Enemy
from characters.orc import Orc
from characters.skeleton import Skeleton
from characters.npc import NPC
from objects.trap import Trap
from objects.chest import Chest
from objects.coin import Coin
from objects.weapon import Weapon
from objects.potion import Potion
from core.map import GameMap
from ui.ui import UI
from objects.portal import Portal
from objects.torch import Torch
from ui.intro_screen import IntroScreen
from ui.character_select import CharacterSelect

class Game:
    """Manages game state and main loop."""
    
    def __init__(self):
        """Initialise the game."""
        # Initialise pygame
        pygame.init()
        
        # Set up display - explicitly set to None to use default driver
        os.environ.pop('SDL_VIDEODRIVER', None)
        
        # Try to create a visible window with more explicit flags
        try:
            # Try with default flags first
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e1:
            try:
                # Try with SHOWN flag to force visibility
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SHOWN)
            except Exception as e2:
                # Fall back to basic mode as last resort
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0)
        
        pygame.display.set_caption("Dungeon Game")
        self.clock = pygame.time.Clock()
        
        # Load assets
        self.asset_loader = AssetLoader()
        
        # Set the global asset loader instance for other modules to use
        global asset_loader_instance
        asset_loader_instance = self.asset_loader
        
        # Create intro screen and character select screen
        self.intro_screen = IntroScreen(self.screen)
        self.character_select = CharacterSelect(self.screen, self.asset_loader)
        
        # Set up game state
        self.current_level = 0
        self.total_levels = len(MAPS)
        self.level_completed = False
        self.level_transition_timer = 0
        self.level_transition_delay = 1.0  # seconds
        
        # Create game map
        self.game_map = GameMap(self.asset_loader, self.current_level)
        
        # Character selection (default to knight)
        self.selected_character_type = "knight"
        
        # Create player at the map's start position
        self._create_player()
        
        # Create enemy frames dictionary for reuse
        self.enemy_frames = {
            "idle": self.asset_loader.get_enemy_frames("idle"),
            "attack": self.asset_loader.get_enemy_frames("attack"),
            "hurt": self.asset_loader.get_enemy_frames("hurt"),
            "death": self.asset_loader.get_enemy_frames("death")
        }

        # Create orc-specific frames (uses Orc sprites, falls back to skeleton if missing)
        self.orc_frames = {
            "idle": self.asset_loader.get_orc_frames("idle"),
            "attack": self.asset_loader.get_orc_frames("attack"),
            "hurt": self.asset_loader.get_orc_frames("hurt"),
            "death": self.asset_loader.get_orc_frames("death")
        }
        
        # Create enemies, portal, and objects
        self.setup_level()
        
        # Set up UI
        self.ui = UI()
        
        # Game state
        self.inventory = {"gold": 0, "health_potions": 0}
        self.score = 0
        self.running = True
        self.game_completed = False
        self.in_intro_screen = True  # Start at the intro screen
        self.in_character_select = False
        
        # NPC state
        self.npc = None
        
        # Game over state
        self.game_over = False
        self.game_over_timer = 0
        self.restart_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 + 120, 150, 40)
        self.quit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 + 170, 150, 40)
        self.button_highlighted = None  # Tracks which button is currently highlighted (if any)
    
    def _create_player(self):
        """Create the player character based on the selected type."""
        # Get the map's start position
        start_pos = self.game_map.get_player_start_position()
        
        # Create the appropriate player type
        if self.selected_character_type == "wizard":
            idle_frames = self.asset_loader.get_player_idle_frames("wizard")
            attack_frames = self.asset_loader.get_player_attack_frames("wizard")
            self.player = Wizard(start_pos[0], start_pos[1], idle_frames, attack_frames)
        else:
            # Default to knight
            idle_frames = self.asset_loader.get_player_idle_frames("knight")
            attack_frames = self.asset_loader.get_player_attack_frames("knight")
            self.player = Warrior(start_pos[0], start_pos[1], idle_frames, attack_frames)
    
    def setup_level(self):
        """Set up level-specific objects like enemies, traps, chests, and portal."""
        # Clear existing objects
        self.enemies = []
        self.chests = []
        self.traps = []
        self.coins = []
        self.torches = []
        self.items = []
        self.npc = None  # Clear NPC for each level
        
        # Load coin frames for later use
        self.coin_frames = self.asset_loader.get_coin_frames()
        
        # Get exit position from the map
        exit_pos = self.game_map.get_exit_position()
        self.portal = Portal(exit_pos[0], exit_pos[1])
        
        # Helper function to ensure objects are placed on valid floor tiles
        def validate_object_position(x, y):
            """Validate that an object position and its entire hitbox are on floor tiles, not walls."""
            # Check the object's main position
            tile_x = x // TILE_SIZE
            tile_y = y // TILE_SIZE
            
            # Calculate hitbox positions for a typical enemy (25x35 hitbox with offset 33, 37)
            # Check all 4 corners of the hitbox plus the centre
            hitbox_points = [
                # Hitbox top-left
                ((x + 33) // TILE_SIZE, (y + 37) // TILE_SIZE),
                # Hitbox top-right
                ((x + 33 + 25) // TILE_SIZE, (y + 37) // TILE_SIZE),
                # Hitbox bottom-left
                ((x + 33) // TILE_SIZE, (y + 37 + 35) // TILE_SIZE),
                # Hitbox bottom-right
                ((x + 33 + 25) // TILE_SIZE, (y + 37 + 35) // TILE_SIZE),
                # Hitbox centre
                ((x + 33 + 12) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE)
            ]
            
            # Additional buffer points around hitbox for better spacing from walls
            buffer_size = 5  # 5 pixel buffer
            buffer_points = [
                # Above hitbox
                ((x + 33 + 12) // TILE_SIZE, (y + 37 - buffer_size) // TILE_SIZE),
                # Below hitbox
                ((x + 33 + 12) // TILE_SIZE, (y + 37 + 35 + buffer_size) // TILE_SIZE),
                # Left of hitbox
                ((x + 33 - buffer_size) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE),
                # Right of hitbox
                ((x + 33 + 25 + buffer_size) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE)
            ]
            
            # Combine all check points
            all_check_points = [
                (tile_x, tile_y),  # Original object position
                *hitbox_points,    # Hitbox corners and centre
                *buffer_points     # Buffer points around hitbox
            ]
            
            # Check all points - require ALL to be on valid floor tiles
            for check_x, check_y in all_check_points:
                # First check map bounds
                if not (0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT):
                    return False
                
                # Then check if any point is over a wall
                if self.game_map.is_wall(check_x, check_y):
                    return False
            
            # All checks passed, position is valid
            return True
        
        # Define the function to create enemies at valid positions
        def create_enemy(x, y):
            # Create the enemy (using Orc since Enemy is abstract)
            enemy = Orc(x, y, self.orc_frames)
            # Add reference to game map for collision detection
            enemy.game_map = self.game_map
            return enemy

        def create_skeleton(x, y):
            enemy = Skeleton(x, y, self.enemy_frames)
            enemy.game_map = self.game_map
            return enemy
            
        # Define the function to create traps with the peak assets
        def create_trap(x, y):
            # Create the trap with proper assets
            inactive_img = self.asset_loader.get_trap_inactive_image()
            active_img = self.asset_loader.get_trap_active_image()
            trap = Trap(x, y, inactive_img, active_img)
            return trap
        
        # Place enemies, chests, and traps based on level, ensuring they're on floor tiles
        if self.current_level == 0:
            # Level 1 - Tutorial level: skeletons only, easier introduction
            self.enemies = [
                create_skeleton(2 * TILE_SIZE, 6 * TILE_SIZE),
                create_skeleton(2 * TILE_SIZE, 13 * TILE_SIZE),
                create_skeleton(11 * TILE_SIZE, 10 * TILE_SIZE)
            ]
            
            # Create chests at strategic locations
            self.chests = [
                # Chest in the starting area to teach interaction
                Chest(4 * TILE_SIZE, 2 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Chest guarded by enemy
                Chest(6 * TILE_SIZE, 13 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Chest near the exit
                Chest(17 * TILE_SIZE, 13 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames())
            ]
            
            # Create traps on the paths (never on walls)
            self.traps = [
                # Trap in the centre path to teach trap mechanics
                create_trap(12 * TILE_SIZE, 7 * TILE_SIZE),
                # Trap guarding the exit path
                create_trap(16 * TILE_SIZE, 10 * TILE_SIZE),
                # Trap in the bottom path
                create_trap(9 * TILE_SIZE, 12 * TILE_SIZE)
            ]

            # Items: a common sword to introduce the weapon system
            self.items = [
                Weapon(8 * TILE_SIZE, 4 * TILE_SIZE, 24, 24,
                       "common", "Iron Sword", damage=8,
                       frames=self.asset_loader.get_weapon_frames()),
                Potion(8 * TILE_SIZE, 12 * TILE_SIZE, 20, 20,
                       "common", "Health Potion", "health", 30,
                       frames=self.asset_loader.get_potion_frames()),
            ]
        elif self.current_level == 1:
            # Level 2 - Dungeon maze: lots of orcs and skeletons
            self.enemies = [
                # Upper section enemies
                create_skeleton(3 * TILE_SIZE, 3 * TILE_SIZE),
                create_enemy(5 * TILE_SIZE, 2 * TILE_SIZE),
                create_skeleton(7 * TILE_SIZE, 4 * TILE_SIZE),
                create_enemy(11 * TILE_SIZE, 2 * TILE_SIZE),
                create_skeleton(14 * TILE_SIZE, 3 * TILE_SIZE),
                create_enemy(16 * TILE_SIZE, 5 * TILE_SIZE),
                # Middle section enemies
                create_enemy(2 * TILE_SIZE, 7 * TILE_SIZE),
                create_skeleton(6 * TILE_SIZE, 8 * TILE_SIZE),
                create_enemy(9 * TILE_SIZE, 7 * TILE_SIZE),
                create_skeleton(12 * TILE_SIZE, 9 * TILE_SIZE),
                create_enemy(15 * TILE_SIZE, 7 * TILE_SIZE),
                # Lower section enemies
                create_skeleton(4 * TILE_SIZE, 12 * TILE_SIZE),
                create_enemy(8 * TILE_SIZE, 11 * TILE_SIZE),
                create_skeleton(11 * TILE_SIZE, 13 * TILE_SIZE),
                create_enemy(15 * TILE_SIZE, 12 * TILE_SIZE)
            ]

            # Traps strategically placed at intersections
            self.traps = [
                # Trap at maze intersection
                create_trap(3 * TILE_SIZE, 11 * TILE_SIZE),
                # Trap in narrow corridor
                create_trap(10 * TILE_SIZE, 5 * TILE_SIZE),
                # Trap near exit
                create_trap(3 * TILE_SIZE, 13 * TILE_SIZE),
                # Trap in upper path
                create_trap(14 * TILE_SIZE, 4 * TILE_SIZE),
                # Trap in lower path
                create_trap(17 * TILE_SIZE, 13 * TILE_SIZE)
            ]

            # Chests hidden throughout the maze
            self.chests = [
                # Chest hidden in a corner
                Chest(18 * TILE_SIZE, 1 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Chest in the central maze
                Chest(6 * TILE_SIZE, 9 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Chest near exit
                Chest(15 * TILE_SIZE, 13 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames())
            ]
            
            # Create an NPC in level 2 (priest character)
            # Reuse the validate_object_position function to find a valid position
            def find_valid_npc_position():
                # List of potential positions to try in order of preference
                npc_positions = [
                    (15 * TILE_SIZE, 6 * TILE_SIZE),  # Try this position first
                    (11 * TILE_SIZE, 11 * TILE_SIZE), # Alternative position
                    (8 * TILE_SIZE, 3 * TILE_SIZE),   # Another alternative
                    (14 * TILE_SIZE, 14 * TILE_SIZE)  # Final alternative
                ]
                
                # Try each position
                for pos in npc_positions:
                    # Check if position is valid using the same validation function used for other objects
                    if validate_object_position(pos[0], pos[1]):
                        return pos
                
                # If all positions are invalid, use a safe fallback
                return (13 * TILE_SIZE, 7 * TILE_SIZE)
            
            # Find a valid position and create the NPC
            npc_x, npc_y = find_valid_npc_position()
            self.npc = NPC(npc_x, npc_y, self.asset_loader.get_priest_idle_frames())

            # Items: uncommon sword and a speed potion for the maze run
            self.items = [
                Weapon(2 * TILE_SIZE, 4 * TILE_SIZE, 24, 24,
                       "uncommon", "Steel Sword", damage=14,
                       frames=self.asset_loader.get_weapon_frames()),
                Potion(18 * TILE_SIZE, 8 * TILE_SIZE, 20, 20,
                       "uncommon", "Speed Potion", "speed", 0,
                       frames=self.asset_loader.get_potion_frames()),
                Potion(9 * TILE_SIZE, 12 * TILE_SIZE, 20, 20,
                       "common", "Health Potion", "health", 40,
                       frames=self.asset_loader.get_potion_frames()),
            ]
        else:
            # Level 3 - Advanced dungeon: lots of orcs, maximum difficulty
            self.enemies = [
                # Upper section
                create_enemy(2 * TILE_SIZE, 2 * TILE_SIZE),
                create_enemy(5 * TILE_SIZE, 1 * TILE_SIZE),
                create_enemy(8 * TILE_SIZE, 3 * TILE_SIZE),
                create_enemy(11 * TILE_SIZE, 2 * TILE_SIZE),
                create_enemy(14 * TILE_SIZE, 4 * TILE_SIZE),
                create_enemy(17 * TILE_SIZE, 3 * TILE_SIZE),
                # Upper-middle section
                create_enemy(3 * TILE_SIZE, 6 * TILE_SIZE),
                create_enemy(7 * TILE_SIZE, 5 * TILE_SIZE),
                create_enemy(10 * TILE_SIZE, 7 * TILE_SIZE),
                create_enemy(14 * TILE_SIZE, 6 * TILE_SIZE),
                create_enemy(17 * TILE_SIZE, 8 * TILE_SIZE),
                # Middle section
                create_enemy(2 * TILE_SIZE, 10 * TILE_SIZE),
                create_enemy(6 * TILE_SIZE, 9 * TILE_SIZE),
                create_enemy(11 * TILE_SIZE, 10 * TILE_SIZE),
                create_enemy(15 * TILE_SIZE, 10 * TILE_SIZE),
                # Lower section
                create_enemy(4 * TILE_SIZE, 13 * TILE_SIZE),
                create_enemy(9 * TILE_SIZE, 14 * TILE_SIZE),
                create_enemy(13 * TILE_SIZE, 12 * TILE_SIZE),
                create_enemy(17 * TILE_SIZE, 13 * TILE_SIZE)
            ]

            # Strategic trap placement in corridors and chokepoints
            self.traps = [
                # Upper section traps
                create_trap(7 * TILE_SIZE, 3 * TILE_SIZE),
                create_trap(9 * TILE_SIZE, 2 * TILE_SIZE),
                create_trap(11 * TILE_SIZE, 4 * TILE_SIZE),
                # Middle section traps
                create_trap(3 * TILE_SIZE, 9 * TILE_SIZE),
                create_trap(11 * TILE_SIZE, 7 * TILE_SIZE),
                # Lower section traps
                create_trap(7 * TILE_SIZE, 13 * TILE_SIZE),
                create_trap(16 * TILE_SIZE, 11 * TILE_SIZE),
                create_trap(14 * TILE_SIZE, 14 * TILE_SIZE)
            ]

            # Reward chests distributed throughout the level
            self.chests = [
                # Upper section chest - well guarded
                Chest(16 * TILE_SIZE, 4 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Middle section chests
                Chest(2 * TILE_SIZE, 7 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                Chest(18 * TILE_SIZE, 9 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames()),
                # Lower section chest near exit
                Chest(3 * TILE_SIZE, 13 * TILE_SIZE, self.asset_loader.get_chest_closed_frames(), self.asset_loader.get_chest_open_frames())
            ]

            # Items: rare weapon and strength potion for the final gauntlet
            self.items = [
                Weapon(11 * TILE_SIZE, 6 * TILE_SIZE, 24, 24,
                       "rare", "Enchanted Blade", damage=22,
                       frames=self.asset_loader.get_weapon_frames()),
                Potion(6 * TILE_SIZE, 11 * TILE_SIZE, 20, 20,
                       "rare", "Strength Potion", "strength", 0,
                       frames=self.asset_loader.get_potion_frames()),
                Potion(16 * TILE_SIZE, 12 * TILE_SIZE, 20, 20,
                       "uncommon", "Health Potion", "health", 50,
                       frames=self.asset_loader.get_potion_frames()),
            ]
            
        # Validate and adjust positions if needed
        self._validate_object_positions()

        # Safety check: move any items that landed in walls to nearest floor tile
        self._validate_item_positions()
            
        # Add decorative torches along walls
        self._add_decorative_torches()
    
    def _validate_object_positions(self):
        """Validate and adjust object positions to ensure they're on valid floor tiles."""
        # Helper function to validate object positions
        def validate_object_position(x, y):
            tile_x = x // TILE_SIZE
            tile_y = y // TILE_SIZE
            
            hitbox_points = [
                ((x + 33) // TILE_SIZE, (y + 37) // TILE_SIZE),
                ((x + 33 + 25) // TILE_SIZE, (y + 37) // TILE_SIZE),
                ((x + 33) // TILE_SIZE, (y + 37 + 35) // TILE_SIZE),
                ((x + 33 + 25) // TILE_SIZE, (y + 37 + 35) // TILE_SIZE),
                ((x + 33 + 12) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE)
            ]
            
            buffer_size = 5
            buffer_points = [
                ((x + 33 + 12) // TILE_SIZE, (y + 37 - buffer_size) // TILE_SIZE),
                ((x + 33 + 12) // TILE_SIZE, (y + 37 + 35 + buffer_size) // TILE_SIZE),
                ((x + 33 - buffer_size) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE),
                ((x + 33 + 25 + buffer_size) // TILE_SIZE, (y + 37 + 17) // TILE_SIZE)
            ]
            
            all_check_points = [(tile_x, tile_y), *hitbox_points, *buffer_points]
            
            for check_x, check_y in all_check_points:
                if not (0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT):
                    return False
                if self.game_map.is_wall(check_x, check_y):
                    return False
            
            return True
        
        # Helper function to find a valid nearby position
        def find_valid_position(x, y):
            # Try a grid search around the object
            for radius in range(1, 5):
                for offset_x in range(-radius, radius + 1):
                    for offset_y in range(-radius, radius + 1):
                        new_x = x + offset_x * TILE_SIZE
                        new_y = y + offset_y * TILE_SIZE
                        if validate_object_position(new_x, new_y):
                            return new_x, new_y
            
            # If grid search fails, try some known good positions for each level
            if self.current_level == 0:  # Level 1
                safe_positions = [
                    (2 * TILE_SIZE, 2 * TILE_SIZE),
                    (2 * TILE_SIZE, 6 * TILE_SIZE),
                    (2 * TILE_SIZE, 10 * TILE_SIZE),
                    (11 * TILE_SIZE, 10 * TILE_SIZE),
                    (16 * TILE_SIZE, 13 * TILE_SIZE)
                ]
            elif self.current_level == 1:  # Level 2
                safe_positions = [
                    (2 * TILE_SIZE, 2 * TILE_SIZE),
                    (6 * TILE_SIZE, 12 * TILE_SIZE),
                    (16 * TILE_SIZE, 2 * TILE_SIZE),
                    (16 * TILE_SIZE, 10 * TILE_SIZE),
                    (3 * TILE_SIZE, 4 * TILE_SIZE),
                    (11 * TILE_SIZE, 8 * TILE_SIZE)
                ]
            else:  # Level 3
                safe_positions = [
                    (2 * TILE_SIZE, 2 * TILE_SIZE),
                    (3 * TILE_SIZE, 11 * TILE_SIZE),
                    (17 * TILE_SIZE, 2 * TILE_SIZE),
                    (3 * TILE_SIZE, 7 * TILE_SIZE),
                    (6 * TILE_SIZE, 11 * TILE_SIZE),
                    (16 * TILE_SIZE, 12 * TILE_SIZE)
                ]
            
            # Check each safe position
            for safe_x, safe_y in safe_positions:
                if validate_object_position(safe_x, safe_y):
                    return safe_x, safe_y
                    
            return None, None  # No valid position found
        
        # Define functions for creating objects
        def recreate_enemy(x, y, enemy_type):
            """Re-create an enemy of the same type at a new valid position."""
            if isinstance(enemy_type, Orc):
                enemy = Orc(x, y, self.orc_frames)
            else:
                enemy = Skeleton(x, y, self.enemy_frames)
            enemy.game_map = self.game_map
            return enemy
            
        def create_trap(x, y):
            inactive_img = self.asset_loader.get_trap_inactive_image()
            active_img = self.asset_loader.get_trap_active_image()
            trap = Trap(x, y, inactive_img, active_img)
            return trap
        
        # Validate and adjust traps
        adjusted_traps = []
        for trap in self.traps:
            if validate_object_position(trap.x, trap.y):
                adjusted_traps.append(trap)
            else:
                new_x, new_y = find_valid_position(trap.x, trap.y)
                if new_x is not None:
                    adjusted_traps.append(create_trap(new_x, new_y))
        self.traps = adjusted_traps
        
        # Validate and adjust enemies
        adjusted_enemies = []
        for enemy in self.enemies:
            # Add game map reference to ALL enemies for collision detection
            enemy.game_map = self.game_map
            
            if validate_object_position(enemy.x, enemy.y):
                # Position is valid, keep the enemy
                adjusted_enemies.append(enemy)
            else:
                new_x, new_y = find_valid_position(enemy.x, enemy.y)
                if new_x is not None:
                    # Re-create same enemy type at valid position
                    new_enemy = recreate_enemy(new_x, new_y, enemy)
                    adjusted_enemies.append(new_enemy)
        self.enemies = adjusted_enemies
        
        # Validate and adjust chests
        adjusted_chests = []
        for chest in self.chests:
            if validate_object_position(chest.x, chest.y):
                adjusted_chests.append(chest)
            else:
                new_x, new_y = find_valid_position(chest.x, chest.y)
                if new_x is not None:
                    adjusted_chests.append(
                        Chest(new_x, new_y, 
                             self.asset_loader.get_chest_closed_frames(),
                             self.asset_loader.get_chest_open_frames())
                    )
        self.chests = adjusted_chests
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If in game over state, restart the game instead of quitting
                    if self.game_over:
                        self.restart_game()
                    else:
                        # Return to intro screen when escape is pressed during gameplay
                        self.in_intro_screen = True
                elif self.game_over and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    # Allow player to restart with enter, space, or r key
                    self.restart_game()
            
            # Handle mouse events for game over buttons
            elif self.game_over:
                if event.type == pygame.MOUSEMOTION:
                    # Check if mouse is over restart or quit button
                    mouse_pos = pygame.mouse.get_pos()
                    if self.restart_button_rect.collidepoint(mouse_pos):
                        self.button_highlighted = "restart"
                    elif self.quit_button_rect.collidepoint(mouse_pos):
                        self.button_highlighted = "quit"
                    else:
                        self.button_highlighted = None
                        
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.restart_button_rect.collidepoint(mouse_pos):
                        self.restart_game()
                    elif self.quit_button_rect.collidepoint(mouse_pos):
                        self.running = False
    
    def update(self):
        """Update game state."""
        # Handle level transitions
        if self.level_completed:
            self.level_transition_timer += 1/FPS
            if self.level_transition_timer >= self.level_transition_delay:
                self.change_level(self.current_level + 1)
            return

        # Handle game over state
        if self.game_over:
            # We no longer automatically restart - player must choose
            # Just increment timer for animation effects
            self.game_over_timer += 1/FPS
            return

        # Check for player death
        if not self.player.is_alive():
            self.trigger_game_over()
            return

        # Check if all enemies are dead to activate portal
        alive_enemies = sum(1 for enemy in self.enemies if enemy.is_alive())
        self.portal.set_activated(alive_enemies == 0)

        # Update the portal
        self.portal.update()

        # Check for level completion (player touching portal)
        if self.portal.is_player_colliding(self.player):
            self.complete_level()
            return
        
        # Update player based on their type
        if isinstance(self.player, Wizard):
            # For wizard, pass the enemies list for projectile collision
            # Wizard.update() handles projectile creation internally
            self.player.update(self.game_map, self.enemies)
        else:
            # Regular player (Knight) update
            self.player.update(self.game_map, None)
            
            # Then check for attack against any enemy in range
            # Use frame 2 (earlier in animation) for more responsive feeling
            if self.player.attacking and self.player.current_frame == 2 and not hasattr(self.player, '_attacked_this_animation'):
                # Mark that we've dealt damage for this attack
                setattr(self.player, '_attacked_this_animation', True)
                # Check all enemies for potential hits
                for enemy in self.enemies:
                    if enemy.is_alive() and self.player._is_in_attack_range(enemy):
                        enemy.take_damage(self.player.attack_damage)
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.update(self.player)
        
        # Update NPC if present
        if self.npc:
            self.npc.update(self.player)
            
            # Check for NPC interaction - only process if E key is pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and self.npc.is_player_in_range(self.player):
                # Pass inventory so the priest can check/deduct gold
                self.npc.interact(self.player, self.inventory)
        
        # Check for dead enemies
        self.check_dead_enemies()
        
        # Update chests
        self.update_chests()
        
        # Update traps
        self.update_traps()
        
        # Update coins
        self.update_coins()

        # Update items (pickup detection and buff expiry)
        self.update_items()
        
        # Update decorative torches
        for torch in self.torches:
            torch.update()
        
        # Check for health potion use
        self.check_health_potion_use()
    
    def check_dead_enemies(self):
        """Check for dead enemies to spawn replacements and drop coins."""
        for enemy in self.enemies:
            # Check if enemy just died (is_dying flag is True but hasn't spawned a coin yet)
            if enemy.is_dying and not hasattr(enemy, 'has_dropped_coin'):
                # Mark the enemy as having dropped a coin to avoid multiple drops
                enemy.has_dropped_coin = True
                
                # Enemy has just died, drop a coin and award score immediately
                self.score += 10
                
                # Create a new coin at the enemy's hitbox centre for precise positioning
                new_coin = Coin(
                    enemy.hitbox.centerx - (self.coin_frames[0].get_width() // 2),
                    enemy.hitbox.centery - (self.coin_frames[0].get_height() // 2),
                    self.coin_frames
                )
                self.coins.append(new_coin)
    
    def update_chests(self):
        """Update and check chest interactions."""
        for chest in self.chests:
            chest.update()
            
            # Check for chest interaction (E key and collision)
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_e] and 
                self.player.hitbox.colliderect(chest.hitbox) and 
                not chest.is_open):
                # Open the chest
                contents = chest.open()
                if contents:
                    # Add items to inventory
                    self.inventory["gold"] += contents["gold"]
                    if contents["health_potion"]:
                        self.inventory["health_potions"] += 1
                    
                    # Display message
                    message = f"Found {contents['gold']} gold" + (
                        " and a health potion!" if contents["health_potion"] else "!"
                    )
                    self.ui.set_message(message)
                    
                    # Add to score
                    self.score += contents["gold"]
    
    def update_traps(self):
        """Update and check trap interactions."""
        for trap in self.traps:
            trap.update()
            
            # Store whether the player is currently on this trap
            player_on_trap = self.player.hitbox.colliderect(trap.hitbox)
            
            if player_on_trap:
                # Make trap visible when player steps on it
                trap.is_visible = True
                
                # Only apply damage when spikes are active (up)
                if trap.is_active:
                    damage = trap.trigger(self.player)
                    if damage > 0:
                        self.ui.set_message(f"Ouch! Trap deals {damage} damage!")
                    elif trap.was_triggered:
                        # Player is on active spikes but in cooldown period
                        self.ui.set_message("Careful! The spikes are up!")
                else:
                    # Player is on inactive trap (spikes down) - safe to walk over
                    self.ui.set_message("Watch out for the trap!")
    
    def update_coins(self):
        """Update and check coin interactions."""
        for coin in self.coins:
            coin.update()
            
            # Check for coin collection (player collision)
            if (self.player.hitbox.colliderect(coin.hitbox) and 
                not coin.collected):
                gold_value = coin.collect()
                if gold_value > 0:
                    # Add gold to inventory
                    self.inventory["gold"] += gold_value
                    self.score += gold_value
                    self.ui.set_message(f"Collected {gold_value} gold!")
        
        # Remove collected coins
        self.coins = [coin for coin in self.coins if not coin.collected]

    def update_items(self):
        """Update items and handle player pickup and buff expiry."""
        for item in self.items:
            item.update()

            # Auto-pickup on collision
            if (not item.collected and
                    self.player.hitbox.colliderect(item.hitbox)):
                result = item.use(self.player)
                if result:
                    item.collect()
                    if item.item_type == "weapon":
                        self.ui.set_message(
                            f"Equipped {item.name}! +{item.damage} attack damage."
                        )
                    elif item.item_type == "potion":
                        messages = {
                            "health":   f"Drank {item.name}! Restored HP.",
                            "speed":    f"Drank {item.name}! Speed boosted for {int(item.duration)}s.",
                            "strength": f"Drank {item.name}! Damage boosted for {int(item.duration)}s.",
                        }
                        self.ui.set_message(messages.get(item.effect_type, f"Used {item.name}!"))

        # Remove collected items
        self.items = [i for i in self.items if not i.collected]

        # Tick active buffs on the player each frame (independent of item list)
        self._tick_player_buffs()

    def _validate_item_positions(self):
        """Move any items that spawned inside walls to the nearest valid floor tile."""
        from core.map import TILE_SIZE
        adjusted = []
        for item in self.items:
            tile_x = int(item.x // TILE_SIZE)
            tile_y = int(item.y // TILE_SIZE)
            if not self.game_map.is_wall(tile_x, tile_y):
                adjusted.append(item)
                continue
            # Search outward in a spiral for the nearest floor tile
            found = False
            for radius in range(1, 6):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        nx, ny = tile_x + dx, tile_y + dy
                        if not self.game_map.is_wall(nx, ny):
                            item.x = nx * TILE_SIZE
                            item.y = ny * TILE_SIZE
                            item.hitbox.x = item.x
                            item.hitbox.y = item.y
                            adjusted.append(item)
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
        self.items = adjusted
    
    def _tick_player_buffs(self):
        """Expire any timed potion buffs whose duration has elapsed."""
        import time
        if not hasattr(self.player, "active_buffs"):
            return

        now = time.time()
        expired = [k for k, v in self.player.active_buffs.items()
                   if now >= v["expiry"]]
        for key in expired:
            buff = self.player.active_buffs.pop(key)
            if key == "speed":
                self.player.speed -= buff["bonus"]
                self.ui.set_message("Speed boost wore off.")
            elif key == "strength":
                self.player.attack_damage -= buff["bonus"]
                self.ui.set_message("Strength boost wore off.")

    def check_health_potion_use(self):
        """Check for health potion use."""
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_h] and 
            self.inventory["health_potions"] > 0 and 
            self.player.health < self.player.max_health):
            # Use a health potion
            healing = min(30, self.player.max_health - self.player.health)
            self.player.health += healing
            self.inventory["health_potions"] -= 1
            self.ui.set_message(f"Used a health potion. Healed for {healing} health!")
    
    def complete_level(self):
        """Handle completing the current level."""
        self.level_completed = True
        self.level_transition_timer = 0
        self.ui.set_message(f"Level {self.current_level + 1} completed!")
        # Bonus score for completing level
        self.score += 100 * (self.current_level + 1)
    
    def change_level(self, new_level):
        """Change to a new level."""
        if new_level >= self.total_levels:
            self.game_completed = True
            self.ui.set_message("Congratulations! You've completed the dungeon!")
            return
        
        self.current_level = new_level
        self.level_completed = False
        
        # Change the map
        self.game_map.change_level(new_level)
        
        # Move player to the start position
        start_pos = self.game_map.get_player_start_position()
        
        # Ensure the player starts at a valid non-wall position
        start_tile_x = start_pos[0] // TILE_SIZE
        start_tile_y = start_pos[1] // TILE_SIZE
        is_wall = self.game_map.is_wall(start_tile_x, start_tile_y)
        
        if is_wall:
            # Emergency fix - find a non-wall position nearby
            for test_x in range(1, MAP_WIDTH-1):
                for test_y in range(1, MAP_HEIGHT-1):
                    if not self.game_map.is_wall(test_x, test_y):
                        start_pos = (test_x * TILE_SIZE, test_y * TILE_SIZE)
                        break
                else:
                    continue
                break
        
        # Teleport the player to the start position
        self.player.teleport(start_pos[0], start_pos[1])
        
        # Set up the new level objects
        self.setup_level()
        
        # Level start message
        self.ui.set_message(f"Level {new_level + 1} - Get to the portal!")
    
    def _add_decorative_torches(self):
        """Add decorative torches along walls in the level."""
        # Get torch frames
        torch_frames = self.asset_loader.get_torch_frames()
        if not torch_frames:
            return
            
        # Clear existing torches
        self.torches = []
        
        # Place torches along walls at strategic locations
        wall_positions = []
        
        # First identify suitable wall positions
        for y in range(1, MAP_HEIGHT - 1):
            for x in range(1, MAP_WIDTH - 1):
                # Check if this is a wall
                if self.game_map.is_wall(x, y):
                    # Check if this wall has adjacent floor tiles (good for torch placement)
                    adjacent_floor = False
                    
                    # Check all adjacent tiles
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        adj_x, adj_y = x + dx, y + dy
                        if (0 <= adj_x < MAP_WIDTH and 0 <= adj_y < MAP_HEIGHT and 
                            not self.game_map.is_wall(adj_x, adj_y)):
                            adjacent_floor = True
                            break
                    
                    if adjacent_floor:
                        wall_positions.append((x, y))
        
        # Sample a limited number of wall positions to place torches
        # Determine number of torches based on level
        num_torches = {
            0: 2,   # Level 1: 2 torches
            1: 3,   # Level 2: 3 torches
            2: 3    # Level 3: 3 torches
        }.get(self.current_level, 2)
        
        # If we have less wall positions than desired torches, use all available
        if len(wall_positions) <= num_torches:
            selected_positions = wall_positions
        else:
            # Sample wall positions at regular intervals to distribute torches
            step = len(wall_positions) // num_torches
            selected_positions = [wall_positions[i] for i in range(0, len(wall_positions), step)][:num_torches]
        
        # Create torches at selected positions
        for x, y in selected_positions:
            # Place torch slightly offset from the wall
            # Determine the offset direction by checking adjacent floor tiles
            offset_x, offset_y = 0, 0
            
            # Check each direction for floor tiles
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_x, adj_y = x + dx, y + dy
                if (0 <= adj_x < MAP_WIDTH and 0 <= adj_y < MAP_HEIGHT and 
                    not self.game_map.is_wall(adj_x, adj_y)):
                    # Offset toward the floor tile, but slightly back
                    offset_x = dx * 0.4
                    offset_y = dy * 0.4
                    break
            
            # Create torch at wall position with slight offset
            torch_x = (x + offset_x) * TILE_SIZE
            torch_y = (y + offset_y) * TILE_SIZE
            
            # Add some randomness to torch positions for natural placement
            torch_x += random.uniform(-5, 5)
            torch_y += random.uniform(-5, 5)
            
            self.torches.append(Torch(torch_x, torch_y, torch_frames))
    
    def draw(self):
        """Draw everything."""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw map
        self.game_map.draw(self.screen)
        
        # Draw portal
        self.portal.draw(self.screen)
        
        # Draw torches first (behind other objects)
        for torch in self.torches:
            torch.draw(self.screen)
        
        # Draw traps
        for trap in self.traps:
            trap.draw(self.screen)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw items (weapons, potions)
        for item in self.items:
            item.draw(self.screen)

        # Draw chests
        for chest in self.chests:
            chest.draw(self.screen)
        
        # Draw NPC if present (before enemies)
        if self.npc:
            self.npc.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw NPC interaction box if NPC is interacting
        if self.npc and self.npc.interacting:
            self.npc.draw_interaction_box(self.screen)
        
        # Draw level transition overlay if needed
        if self.level_completed:
            self.draw_level_transition()
            
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
        
        # Draw UI
        # Find nearest enemy for UI display
        nearest_enemy = None
        nearest_dist = float('inf')
        
        for enemy in self.enemies:
            if enemy.is_alive():
                dist = math.sqrt((self.player.hitbox.centerx - enemy.hitbox.centerx)**2 + 
                               (self.player.hitbox.centery - enemy.hitbox.centery)**2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_enemy = enemy
        
        self.ui.draw(self.screen, self.player, self.inventory, self.score, 
                   nearest_enemy, self.current_level + 1)
        
        # Update display
        pygame.display.flip()
    
    def trigger_game_over(self):
        """Handle player death and trigger game over screen."""
        self.game_over = True
        self.game_over_timer = 0
        self.ui.set_message("You have died!")
        
        # Ensure we're not in intro screen mode
        self.in_intro_screen = False
    
    def restart_game(self, skip_intro=False):
        """
        Restart the game after player death or character selection.
        
        Args:
            skip_intro (bool): Whether to skip the intro screen on restart.
        """
        # Reset game state
        self.current_level = 0
        self.game_over = False
        self.game_over_timer = 0
        self.level_completed = False
        self.level_transition_timer = 0
        self.in_intro_screen = not skip_intro  # Skip intro screen if specified
        self.in_character_select = False
        
        # Reset score and inventory
        self.score = 0
        self.inventory = {"gold": 0, "health_potions": 0}
        
        # Create new game map
        self.game_map = GameMap(self.asset_loader, self.current_level)
        
        # Create new player at start position with the current character type
        if skip_intro:
            # Use existing character type - already created in _create_player()
            pass
        else:
            # Reset to default character (knight) when restarting from scratch
            self.selected_character_type = "knight"
            self._create_player()
        
        # Set up level
        self.setup_level()
        
        # Display restart message
        self.ui.set_message("Game restarted! Good luck!")
    
    def draw_game_over(self):
        """Draw the game over screen with interactive buttons."""
        # Background blur and darkening effect
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Pulsing blood-red effect - intensity changes over time
        pulse = (math.sin(self.game_over_timer * 2) * 0.3) + 0.7
        red_intensity = int(170 * pulse)
        overlay.fill((red_intensity, 0, 0, 170))  # Red-tinted overlay for game over
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message (with slight shake effect)
        shake_amount = 1.5 if self.game_over_timer < 1.0 else 0
        shake_x = random.uniform(-shake_amount, shake_amount) if shake_amount > 0 else 0
        shake_y = random.uniform(-shake_amount, shake_amount) if shake_amount > 0 else 0
        
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2 + shake_x, SCREEN_HEIGHT//2 - 70 + shake_y))
        self.screen.blit(text, text_rect)
        
        # Draw score
        font = pygame.font.Font(None, 42)
        text = font.render(f"Final Score: {self.score}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
        
        # Draw level reached
        font = pygame.font.Font(None, 30)
        text = font.render(f"Level Reached: {self.current_level + 1}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(text, text_rect)
        
        # Draw restart button
        restart_color = (0, 200, 0) if self.button_highlighted == "restart" else (0, 150, 0)  # Brighter when highlighted
        pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.restart_button_rect, 2, border_radius=5)  # White border
        
        restart_font = pygame.font.Font(None, 32)
        restart_text = restart_font.render("Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Draw quit button
        quit_color = (200, 0, 0) if self.button_highlighted == "quit" else (150, 0, 0)  # Brighter when highlighted
        pygame.draw.rect(self.screen, quit_color, self.quit_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.quit_button_rect, 2, border_radius=5)  # White border
        
        quit_font = pygame.font.Font(None, 32)
        quit_text = quit_font.render("Quit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Draw help text
        help_font = pygame.font.Font(None, 24)
        help_text = help_font.render("Press SPACE, ENTER or R to restart", True, WHITE)
        help_text_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(help_text, help_text_rect)
        
    def draw_level_transition(self):
        """Draw a transition overlay when changing levels."""
        # Calculate opacity based on transition timer
        max_opacity = 180  # Max opacity of overlay
        progress = self.level_transition_timer / self.level_transition_delay
        opacity = int(max_opacity * progress)
        
        # Ensure opacity is valid (between 0 and 255)
        opacity = max(0, min(255, opacity))
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, opacity))
        self.screen.blit(overlay, (0, 0))
        
        # Draw level transition message
        if not self.game_completed:
            font = pygame.font.Font(None, 48)
            text = font.render(f"Level {self.current_level + 1} Completed!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render(f"Prepare for Level {self.current_level + 2}...", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(text, text_rect)
        else:
            font = pygame.font.Font(None, 48)
            text = font.render("Congratulations!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render("You've conquered the dungeon!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render(f"Final Score: {self.score}", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(text, text_rect)
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Handle the intro screen if needed
            if self.in_intro_screen:
                action = self.intro_screen.run()
                if action == 'quit':
                    self.running = False
                elif action == 'start':
                    self.in_intro_screen = False
                    self.in_character_select = True
                continue
            
            # Handle the character select screen if needed
            if self.in_character_select:
                result = self.character_select.run()
                if result == 'quit':
                    self.running = False
                elif result == 'back':
                    self.in_intro_screen = True
                    self.in_character_select = False
                elif isinstance(result, dict):  # Character was selected
                    self.selected_character_type = result["type"]
                    # Create the player with the selected character type
                    self._create_player()
                    self.in_character_select = False
                    # Reset game state when starting new game with new character
                    self.restart_game(skip_intro=True)
                continue
                
            # Regular game loop
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()