"""
Asset Loader module.

This module handles loading and managing all game assets.
"""

import pygame
import os
import random
import math
from core.map import TILE_SIZE

# Colours used for fallback rendering
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

class AssetLoader:
    """Loads and manages game assets."""
    
    def __init__(self):
        """Initialise the asset loader."""
        self.assets = {
            "tiles": {
                "wall": [],  # We'll use multiple wall tiles
                "floor": []  # We'll use multiple floor tiles
            },
            "objects": {
                "chest_closed": [],
                "chest_open": [],
                "trap_inactive": None,
                "trap_active": None,
                "coin": [],
                "torch": [],
                "weapon": [],   # Arrow sprite frames for weapons
                "potion": []    # Flask sprite frames for potions
            },
            "player": {
                "idle": [],
                "attack": []
            },
            "enemy": {
                "idle": [],
                "attack": [],
                "hurt": [],
                "death": []
            },
            "orc": {
                "idle": [],
                "attack": [],
                "hurt": [],
                "death": []
            },
            "npc": {
                "priest": {
                    "idle": []
                }
            }
        }
        self.load_assets()
    
    def load_assets(self):
        """Load all game assets."""
        # Get the assets directory (where this file lives)
        assets_dir = os.path.dirname(os.path.abspath(__file__))
        
        # IMPORTANT: Load peak trap animations FIRST to ensure they're prioritized
        self._load_peaks_animations(assets_dir)
        
        # Try to load torch animations
        self._load_torch_animations(assets_dir)
        
        # Try to load coin animations
        self._load_coin_animations(assets_dir)
        
        # Try to load chest animations
        self._load_chest_animations(assets_dir)
        
        # Try to load priest animations for NPC
        self._load_priest_animations(assets_dir)
        
        # Try to load new wall and floor assets directly from image files
        # Load floor tile
        floor_path = os.path.join(assets_dir,"character and tileset", "Dungeon_floor.png")
        right_wall_path = os.path.join(assets_dir,"character and tileset", "Right wall.png")
        top_wall_path = os.path.join(assets_dir,"character and tileset", "Top_wall.png")
        
        # Track if we successfully loaded the new assets
        loaded_new_assets = False
        
        # Try to load the new assets
        try:
            if os.path.exists(floor_path) and os.path.exists(right_wall_path) and os.path.exists(top_wall_path):
                # Load floor tile
                floor_image = pygame.image.load(floor_path).convert_alpha()
                floor_image = pygame.transform.scale(floor_image, (TILE_SIZE, TILE_SIZE))
                
                # Create 4 variants of the floor with slight rotations for variety
                for i in range(4):
                    rotated_floor = pygame.transform.rotate(floor_image, i * 90)
                    self.assets["tiles"]["floor"].append(rotated_floor)
                
                # Load wall tiles
                top_wall = pygame.image.load(top_wall_path).convert_alpha()
                top_wall = pygame.transform.scale(top_wall, (TILE_SIZE, TILE_SIZE))
                right_wall = pygame.image.load(right_wall_path).convert_alpha()
                right_wall = pygame.transform.scale(right_wall, (TILE_SIZE, TILE_SIZE))
                
                # Create rotated versions for different wall orientations
                bottom_wall = pygame.transform.rotate(top_wall, 180)
                left_wall = pygame.transform.flip(right_wall, True, False)
                
                # Add the walls to the asset dictionary in the correct order for map.py
                # Index 0: Top wall — horizontal, face pointing down (floor below)
                # Index 1: Right wall — vertical, face pointing left (floor to the left)
                # Index 2: Bottom wall — horizontal, face pointing up (floor above)
                # Index 3: Left wall — vertical, face pointing right (floor to the right)
                self.assets["tiles"]["wall"].append(top_wall)      # Index 0: Top wall
                self.assets["tiles"]["wall"].append(right_wall)    # Index 1: Right wall
                self.assets["tiles"]["wall"].append(bottom_wall)   # Index 2: Bottom wall (rotated 180°)
                self.assets["tiles"]["wall"].append(left_wall)     # Index 3: Left wall (flipped)
                
                # Load corner wall pieces from dedicated assets
                top_left_angle_path = os.path.join(assets_dir,"character and tileset", "top_left_angle_wall.png")
                top_right_angle_path = os.path.join(assets_dir,"character and tileset", "top_right_angle_wall.png")
                bottom_left_angle_path = os.path.join(assets_dir,"character and tileset", "bottom_left_angle_wall.png")
                bottom_right_angle_path = os.path.join(assets_dir,"character and tileset", "bottom_right_angle_wall.png")
                
                # Load and scale corner pieces
                if os.path.exists(top_left_angle_path) and os.path.exists(top_right_angle_path) and \
                   os.path.exists(bottom_left_angle_path) and os.path.exists(bottom_right_angle_path):
                    # Top-left corner
                    top_left_angle = pygame.image.load(top_left_angle_path).convert_alpha()
                    top_left_angle = pygame.transform.scale(top_left_angle, (TILE_SIZE, TILE_SIZE))
                    self.assets["tiles"]["wall"].append(top_left_angle)
                    
                    # Top-right corner
                    top_right_angle = pygame.image.load(top_right_angle_path).convert_alpha()
                    top_right_angle = pygame.transform.scale(top_right_angle, (TILE_SIZE, TILE_SIZE))
                    self.assets["tiles"]["wall"].append(top_right_angle)
                    
                    # Bottom-left corner
                    bottom_left_angle = pygame.image.load(bottom_left_angle_path).convert_alpha()
                    bottom_left_angle = pygame.transform.scale(bottom_left_angle, (TILE_SIZE, TILE_SIZE))
                    self.assets["tiles"]["wall"].append(bottom_left_angle)
                    
                    # Bottom-right corner
                    bottom_right_angle = pygame.image.load(bottom_right_angle_path).convert_alpha()
                    bottom_right_angle = pygame.transform.scale(bottom_right_angle, (TILE_SIZE, TILE_SIZE))
                    self.assets["tiles"]["wall"].append(bottom_right_angle)
                else:
                    # Fallback: Create corner pieces by combining straight wall pieces
                    for i in range(4):  # Create 4 different corner pieces
                        corner = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        if i % 2 == 0:
                            corner.blit(top_wall, (0, 0))
                            if i == 0:
                                corner.blit(left_wall, (0, 0))
                            else:
                                corner.blit(right_wall, (0, 0))
                        else:
                            corner.blit(bottom_wall, (0, 0))
                            if i == 1:
                                corner.blit(left_wall, (0, 0))
                            else:
                                corner.blit(right_wall, (0, 0))
                        self.assets["tiles"]["wall"].append(corner)
                
                loaded_new_assets = True
                
                # Only create fallback chest animations if not already loaded
                if not self.assets["objects"]["chest_closed"] or not self.assets["objects"]["chest_open"]:
                    self._create_fallback_chest_animations()
                
                # Only create fallback torch animations if not already loaded
                if not self.assets["objects"]["torch"]:
                    self._create_fallback_torch_animations()
        except Exception:
            loaded_new_assets = False
        
        # If loading new assets failed, try the old tileset method
        if not loaded_new_assets:
            # Try to load dungeon tileset
            tileset_path = os.path.join(assets_dir,"character and tileset", "Dungeon_Tileset.png")
            if os.path.exists(tileset_path):
                try:
                    tileset = pygame.image.load(tileset_path).convert_alpha()
                    
                    # Extract tiles from the tileset
                    tile_width, tile_height = 16, 16  # Based on typical tilesets
                    
                    # Extract floor tiles (4 variants)
                    for i in range(4):
                        floor_rect = pygame.Rect(i * tile_width, 0, tile_width, tile_height)
                        floor_image = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                        floor_image.blit(tileset, (0, 0), floor_rect)
                        floor_image = pygame.transform.scale(floor_image, (TILE_SIZE, TILE_SIZE))
                        self.assets["tiles"]["floor"].append(floor_image)
                    
                    # Extract wall tiles (8 variants for better coherence)
                    # Extract corner walls first
                    corner_positions = [(0, 1), (3, 1)]  # Left wall, right wall
                    for x, y in corner_positions:
                        wall_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                        wall_image = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                        wall_image.blit(tileset, (0, 0), wall_rect)
                        wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
                        self.assets["tiles"]["wall"].append(wall_image)
                    
                    # Extract straight walls
                    for i in range(1, 3):  # Middle wall sections
                        wall_rect = pygame.Rect(i * tile_width, 1 * tile_height, tile_width, tile_height)
                        wall_image = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                        wall_image.blit(tileset, (0, 0), wall_rect)
                        wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
                        self.assets["tiles"]["wall"].append(wall_image)
                    
                    # Extract more wall variants from row 2 if available (for more variety)
                    for i in range(4):
                        wall_rect = pygame.Rect(i * tile_width, 2 * tile_height, tile_width, tile_height)
                        wall_image = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                        wall_image.blit(tileset, (0, 0), wall_rect)
                        wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
                        self.assets["tiles"]["wall"].append(wall_image)
                    
                    # Load trap assets
                    self._load_trap_assets(tileset, tile_width, tile_height)
                    
                except Exception:
                    self._create_fallback_tiles()
                    # Only create fallback objects if peak assets aren't already loaded
                    if self.assets["objects"]["trap_inactive"] is None or self.assets["objects"]["trap_active"] is None:
                        self._create_fallback_objects()
            else:
                # Create fallback tiles if tileset not found
                self._create_fallback_tiles()
                # Only create fallback objects if peak assets aren't already loaded
                if self.assets["objects"]["trap_inactive"] is None or self.assets["objects"]["trap_active"] is None:
                    self._create_fallback_objects()
        
        # Load player animations
        self._load_player_animations(assets_dir)
        
        # Load enemy animations
        self._load_enemy_animations(assets_dir)
        
        # Load orc animations
        self._load_orc_animations(assets_dir)

        # Load weapon and potion item sprites
        self._load_item_animations(assets_dir)
    
    def _load_trap_assets(self, tileset, tile_width, tile_height):
        """Load trap assets from tileset."""
        
        # Skip loading if we already have peak assets loaded
        if self.assets["objects"]["trap_inactive"] is not None and self.assets["objects"]["trap_active"] is not None:
            return
            
        # Find trap in the tileset (typically spikes are in row 6-7)
        trap_inactive_rect = pygame.Rect(2 * tile_width, 6 * tile_height, tile_width, tile_height)
        trap_active_rect = pygame.Rect(3 * tile_width, 6 * tile_height, tile_width, tile_height)
        
        # Extract trap images
        trap_inactive = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
        trap_inactive.blit(tileset, (0, 0), trap_inactive_rect)
        trap_inactive = pygame.transform.scale(trap_inactive, (TILE_SIZE, TILE_SIZE))
        
        # Add "TRAP" text to the inactive trap
        if TILE_SIZE >= 30:  # Only add text if tile is big enough
            font = pygame.font.Font(None, 12)
            text = font.render("TRAP", True, (200, 0, 0))
            # Add a semitransparent background behind text for better visibility
            text_bg = pygame.Surface((text.get_width() + 2, text.get_height() + 2), pygame.SRCALPHA)
            text_bg.fill((255, 255, 255, 180))
            # Position the text in the middle of the trap
            text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            text_bg_rect = text_bg.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            # Add background and text
            trap_inactive.blit(text_bg, text_bg_rect)
            trap_inactive.blit(text, text_rect)
        
        self.assets["objects"]["trap_inactive"] = trap_inactive
        
        trap_active = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
        trap_active.blit(tileset, (0, 0), trap_active_rect)
        trap_active = pygame.transform.scale(trap_active, (TILE_SIZE, TILE_SIZE))
        
        # Add "OUCH!" text to the active trap
        if TILE_SIZE >= 30:  # Only add text if tile is big enough
            font = pygame.font.Font(None, 12)
            text = font.render("OUCH!", True, (200, 0, 0))
            # Add a semitransparent background behind text for better visibility
            text_bg = pygame.Surface((text.get_width() + 2, text.get_height() + 2), pygame.SRCALPHA)
            text_bg.fill((255, 255, 255, 180))
            # Position the text in the middle of the trap
            text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//4))
            text_bg_rect = text_bg.get_rect(center=(TILE_SIZE//2, TILE_SIZE//4))
            # Add background and text
            trap_active.blit(text_bg, text_bg_rect)
            trap_active.blit(text, text_rect)
        
        self.assets["objects"]["trap_active"] = trap_active
    
    def _load_player_animations(self, assets_dir):
        """Load player character animations."""
        # Store animations by character type
        self.assets["player"] = {
            "knight": {
                "idle": [],
                "attack": []
            },
            "wizard": {
                "idle": [],
                "attack": [],
                "projectile_effect": None  # Will hold wizard projectile effect asset if found
            }
        }
        
        # Load Knight animations
        self._load_knight_animations(assets_dir)
        
        # Load Wizard animations
        self._load_wizard_animations(assets_dir)
    
    def _load_knight_animations(self, assets_dir):
        """Load knight character animations."""
        # Load knight idle animation
        idle_path = os.path.join(assets_dir,"Knight", "Knight", "Knight-Idle.png")
        if os.path.exists(idle_path):
            try:
                idle_sheet = pygame.image.load(idle_path).convert_alpha()
                
                # Extract frames from the idle spritesheet
                frame_width = idle_sheet.get_width() // 6  # Knight idle has 6 frames
                frame_height = idle_sheet.get_height()
                
                # Create each frame
                for i in range(6):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(idle_sheet, (0, 0), frame_rect)
                    
                    # Scale the frame to a larger size
                    frame = pygame.transform.scale(frame, (100, 125))
                    self.assets["player"]["knight"]["idle"].append(frame)
            except Exception:
                self._create_fallback_idle_animation("knight")
        else:
            self._create_fallback_idle_animation("knight")
        
        # Load knight attack animation
        attack_path = os.path.join(assets_dir,"Knight", "Knight", "Knight-Attack01.png")
        if os.path.exists(attack_path):
            try:
                attack_sheet = pygame.image.load(attack_path).convert_alpha()
                
                # Extract frames from the attack spritesheet
                frame_count = 7  # Knight attack has 7 frames
                frame_width = attack_sheet.get_width() // frame_count
                frame_height = attack_sheet.get_height()
                
                # Create each frame
                for i in range(frame_count):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(attack_sheet, (0, 0), frame_rect)
                    
                    # Scale the frame to a larger size
                    frame = pygame.transform.scale(frame, (120, 145))
                    self.assets["player"]["knight"]["attack"].append(frame)
            except Exception:
                self._create_fallback_attack_animation("knight")
        else:
            self._create_fallback_attack_animation("knight")
            
    def _load_wizard_animations(self, assets_dir):
        """Load wizard character animations."""
        # Load wizard idle animation
        idle_path = os.path.join(assets_dir,"Wizard", "Wizard", "Wizard-Idle.png")
        if os.path.exists(idle_path):
            try:
                idle_sheet = pygame.image.load(idle_path).convert_alpha()
                
                # Extract frames from the idle spritesheet
                frame_width = idle_sheet.get_width() // 6  # Wizard idle has 6 frames
                frame_height = idle_sheet.get_height()
                
                # Create each frame
                for i in range(6):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(idle_sheet, (0, 0), frame_rect)
                    
                    # Scale the frame to a larger size
                    frame = pygame.transform.scale(frame, (100, 125))
                    self.assets["player"]["wizard"]["idle"].append(frame)
            except Exception:
                self._create_fallback_idle_animation("wizard")
        else:
            self._create_fallback_idle_animation("wizard")
        
        # Load wizard attack animation - try multiple paths
        src_dir = os.path.join(os.path.dirname(assets_dir), "src")
        
        # List of possible paths to try for wizard attack animation
        possible_attack_paths = [
            # Original asset paths
            os.path.join(assets_dir,"Wizard", "Wizard", "Wizard-Attack01.png"),
            # With shadows version
            os.path.join(assets_dir,"Wizard", "Wizard with shadows", "Wizard-Attack01.png"),
            # Alternative attack animation
            os.path.join(assets_dir,"Wizard", "Wizard", "Wizard-Attack02.png")
        ]
        
        # Try each path until we find a valid one
        attack_loaded = False
        for attack_path in possible_attack_paths:
            if os.path.exists(attack_path):
                try:
                    attack_sheet = pygame.image.load(attack_path).convert_alpha()

                    # Extract frames from the attack spritesheet
                    frame_count = 6  # Wizard attack has 6 frames (600px / 100px per frame)
                    frame_width = attack_sheet.get_width() // frame_count
                    frame_height = attack_sheet.get_height()

                    # Create each frame
                    for i in range(frame_count):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(attack_sheet, (0, 0), frame_rect)

                        # Scale the frame to a larger size
                        frame = pygame.transform.scale(frame, (120, 145))
                        self.assets["player"]["wizard"]["attack"].append(frame)
                    
                    attack_loaded = True
                    break
                except Exception:
                    continue
                
        if not attack_loaded:
            self._create_fallback_attack_animation("wizard")
            
        # Load wizard projectile effect - try multiple paths
        # Based on the directory structure, we should look in the src/assets directory
        src_dir = os.path.join(os.path.dirname(assets_dir), "src")
        
        # List of possible paths to try
        possible_effect_paths = [
            # Original asset paths
            os.path.join(assets_dir,"images", "characters", "Wizard", "Wizard", "Wizard-Attack01_Effect.png"),
            # Path inside src directory
            os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard", "Wizard-Attack01_Effect.png"),
            # With shadows version
            os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard with shadows", "Wizard-Attack01_Effect.png"),
            # Alternative names
            os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard", "Wizard-Attack02_Effect.png"),
            # World directory 
            os.path.join(src_dir, "assets", "images", "world", "wizard_projectile.png")
        ]
        
        # Try each path until we find a valid one
        effect_loaded = False
        for path in possible_effect_paths:
            if os.path.exists(path):
                try:
                    # Load the projectile effect image
                    effect_image = pygame.image.load(path).convert_alpha()
                    
                    # Scale the effect to an appropriate size for a projectile (but keep aspect ratio)
                    original_width = effect_image.get_width()
                    original_height = effect_image.get_height()
                    scale_factor = 48 / max(original_width, original_height)  # Larger size for visibility
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    
                    effect_image = pygame.transform.scale(effect_image, (new_width, new_height))
                    
                    # Store the projectile effect
                    self.assets["player"]["wizard"]["projectile_effect"] = effect_image
                    effect_loaded = True
                    break
                except Exception:
                    continue
        
        if not effect_loaded:
            # Create a fallback projectile effect
            try:
                # Create a simple magic effect surface
                effect_size = 32
                effect_image = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
                
                # Draw a multi-layered magic effect
                pygame.draw.circle(effect_image, (0, 80, 255, 180), (effect_size//2, effect_size//2), effect_size//2 - 2)
                pygame.draw.circle(effect_image, (50, 180, 255, 220), (effect_size//2, effect_size//2), effect_size//2 - 6)
                pygame.draw.circle(effect_image, (200, 230, 255, 250), (effect_size//2, effect_size//2), effect_size//4)
                
                # Add some "sparkles"
                for _ in range(5):
                    angle = random.random() * 2 * math.pi
                    dist = random.randint(5, effect_size//2 - 4)
                    x = int(effect_size//2 + math.cos(angle) * dist)
                    y = int(effect_size//2 + math.sin(angle) * dist)
                    size = random.randint(1, 3)
                    pygame.draw.circle(effect_image, (255, 255, 255, 255), (x, y), size)
                
                self.assets["player"]["wizard"]["projectile_effect"] = effect_image
            except Exception:
                pass
    
    def _load_enemy_animations(self, assets_dir):
        """Load enemy animations."""
        # Try to load skeleton animations
        base_path = os.path.join(assets_dir,"Skeleton", "Skeleton")
        
        # Animation types and expected frame counts
        animations = {
            "idle": {"file": "Skeleton-Idle.png", "frames": 6},
            "attack": {"file": "Skeleton-Attack01.png", "frames": 7},
            "hurt": {"file": "Skeleton-Hurt.png", "frames": 4},
            "death": {"file": "Skeleton-Death.png", "frames": 8}
        }
        
        # Load each animation type
        for anim_type, info in animations.items():
            anim_path = os.path.join(base_path, info["file"])
            
            if os.path.exists(anim_path):
                try:
                    sheet = pygame.image.load(anim_path).convert_alpha()
                    
                    # Extract frames
                    frame_count = info["frames"]
                    frame_width = sheet.get_width() // frame_count
                    frame_height = sheet.get_height()
                    
                    # Create each frame
                    for i in range(frame_count):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), frame_rect)
                        
                        # Scale the frame to a larger size
                        frame = pygame.transform.scale(frame, (90, 115))
                        self.assets["enemy"][anim_type].append(frame)
                except Exception:
                    self._create_fallback_enemy_animation(anim_type)
            else:
                self._create_fallback_enemy_animation(anim_type)
    
    def _load_orc_animations(self, assets_dir):
        """Load orc enemy animations from the Orc sprite sheets."""
        base_path = os.path.join(assets_dir, "Orc", "Orc")

        animations = {
            "idle":   {"file": "Orc-Idle.png",    "frames": 6},
            "attack": {"file": "Orc-Attack01.png", "frames": 6},
            "hurt":   {"file": "Orc-Hurt.png",     "frames": 4},
            "death":  {"file": "Orc-Death.png",    "frames": 4},
        }

        for anim_type, info in animations.items():
            anim_path = os.path.join(base_path, info["file"])

            if os.path.exists(anim_path):
                try:
                    sheet = pygame.image.load(anim_path).convert_alpha()
                    frame_count = info["frames"]
                    frame_width = sheet.get_width() // frame_count
                    frame_height = sheet.get_height()

                    for i in range(frame_count):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sheet, (0, 0), frame_rect)
                        frame = pygame.transform.scale(frame, (90, 115))
                        self.assets["orc"][anim_type].append(frame)
                except Exception:
                    # Fall back to skeleton frames if orc sprites fail to load
                    self.assets["orc"][anim_type] = list(self.assets["enemy"][anim_type])
            else:
                # Fall back to skeleton frames if orc sprites are missing
                self.assets["orc"][anim_type] = list(self.assets["enemy"][anim_type])

    def _load_item_animations(self, assets_dir):
        """Load weapon and potion item sprites from individual frame files."""
        base = os.path.join(assets_dir, "items and trap_animation")

        # Weapon frames — use arrow sprites (4 frames, individually named)
        arrow_dir = os.path.join(base, "arrow")
        for i in range(1, 5):
            path = os.path.join(arrow_dir, f"arrow_{i}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (32, 32))
                    self.assets["objects"]["weapon"].append(img)
                except Exception:
                    pass

        # Potion frames — use flask_1 sprites (4 frames)
        flask_dir = os.path.join(base, "flasks")
        for i in range(1, 5):
            path = os.path.join(flask_dir, f"flasks_1_{i}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (32, 32))
                    self.assets["objects"]["potion"].append(img)
                except Exception:
                    pass

    def _load_coin_animations(self, assets_dir):
        """Load coin animation frames."""
        # Define the path to coin animation frames
        coin_dir = os.path.join(assets_dir,"items and trap_animation", "coin")
        
        # Check if coin directory exists
        if os.path.exists(coin_dir):
            try:
                # Load all coin frames (numbered 1-4)
                for i in range(1, 5):
                    coin_path = os.path.join(coin_dir, f"coin_{i}.png")
                    if os.path.exists(coin_path):
                        coin_frame = pygame.image.load(coin_path).convert_alpha()
                        # Scale the coin to a good size for the game
                        coin_frame = pygame.transform.scale(coin_frame, (TILE_SIZE // 2, TILE_SIZE // 2))
                        self.assets["objects"]["coin"].append(coin_frame)
            except Exception:
                self._create_fallback_coin_animation()
        else:
            self._create_fallback_coin_animation()
    
    def _load_chest_animations(self, assets_dir):
        """Load chest animation frames."""
        # Define the path to chest animation frames
        chest_dir = os.path.join(assets_dir,"items and trap_animation", "chest")
        
        # Check if chest directory exists
        if os.path.exists(chest_dir):
            try:
                # Load all closed chest frames (numbered 1-4)
                for i in range(1, 5):
                    chest_path = os.path.join(chest_dir, f"chest_{i}.png")
                    if os.path.exists(chest_path):
                        chest_frame = pygame.image.load(chest_path).convert_alpha()
                        # Scale the chest to 80% of the tile size
                        chest_frame = pygame.transform.scale(chest_frame, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
                        self.assets["objects"]["chest_closed"].append(chest_frame)
                
                # Load all open chest frames (numbered 1-4)
                for i in range(1, 5):
                    chest_path = os.path.join(chest_dir, f"chest_open_{i}.png")
                    if os.path.exists(chest_path):
                        chest_frame = pygame.image.load(chest_path).convert_alpha()
                        # Scale the chest to 80% of the tile size
                        chest_frame = pygame.transform.scale(chest_frame, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
                        self.assets["objects"]["chest_open"].append(chest_frame)
            except Exception:
                self._create_fallback_chest_animations()
        else:
            self._create_fallback_chest_animations()
    
    def _create_fallback_tiles(self):
        """Create fallback tile images."""
        # Create a few wall tile variants - more coherent system
        # First create corner variants
        corner_colors = [(120, 100, 80), (125, 105, 85)]
        for color in corner_colors:
            wall_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_surf.fill(color)
            # Add border to simulate stone texture
            pygame.draw.rect(wall_surf, (60, 50, 40), wall_surf.get_rect(), 2)
            # Add diagonal line to simulate corner
            pygame.draw.line(wall_surf, (60, 50, 40), (0, 0), (TILE_SIZE, TILE_SIZE), 1)
            self.assets["tiles"]["wall"].append(wall_surf)
        
        # Create straight wall variants
        straight_colors = [(110, 90, 70), (115, 95, 75)]
        for color in straight_colors:
            wall_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_surf.fill(color)
            pygame.draw.rect(wall_surf, (60, 50, 40), wall_surf.get_rect(), 2)
            # Add horizontal lines to simulate stone texture
            pygame.draw.line(wall_surf, (60, 50, 40), (0, TILE_SIZE//3), (TILE_SIZE, TILE_SIZE//3), 1)
            pygame.draw.line(wall_surf, (60, 50, 40), (0, 2*TILE_SIZE//3), (TILE_SIZE, 2*TILE_SIZE//3), 1)
            self.assets["tiles"]["wall"].append(wall_surf)
            
        # Add more wall variants (T-junctions, etc.)
        for i in range(4):
            wall_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            color = (100 + i*5, 80 + i*5, 60 + i*5)
            wall_surf.fill(color)
            pygame.draw.rect(wall_surf, (60, 50, 40), wall_surf.get_rect(), 2)
            # Add some brick-like texture
            for j in range(1, 3):
                offset = (j % 2) * (TILE_SIZE // 4)
                for k in range(2):
                    pygame.draw.rect(wall_surf, (60, 50, 40), 
                                   (offset + k*(TILE_SIZE//2), j*(TILE_SIZE//3), 
                                    TILE_SIZE//4, TILE_SIZE//6), 1)
            self.assets["tiles"]["wall"].append(wall_surf)
        
        # Create coherent floor tile variants
        floor_base_color = (70, 70, 70)
        floor_patterns = [
            # Regular stone
            lambda surf: pygame.draw.rect(surf, (85, 85, 85), surf.get_rect(), 1),
            # Cracked stone
            lambda surf: [pygame.draw.line(surf, (85, 85, 85), 
                                        (TILE_SIZE//2, TILE_SIZE//2), 
                                        (TILE_SIZE//2 + dx, TILE_SIZE//2 + dy), 1) 
                         for dx, dy in [(10, 10), (-10, 10), (10, -10), (-10, -10)]],
            # Dotted pattern
            lambda surf: [pygame.draw.circle(surf, (85, 85, 85), 
                                          (x * TILE_SIZE//3, y * TILE_SIZE//3), 1)
                         for x in range(1, 3) for y in range(1, 3)],
            # Grid pattern
            lambda surf: [pygame.draw.line(surf, (85, 85, 85), 
                                        (x * TILE_SIZE//2, 0), 
                                        (x * TILE_SIZE//2, TILE_SIZE), 1) 
                         for x in range(1, 2)] + 
                     [pygame.draw.line(surf, (85, 85, 85), 
                                       (0, y * TILE_SIZE//2), 
                                       (TILE_SIZE, y * TILE_SIZE//2), 1) 
                      for y in range(1, 2)]
        ]
        
        for i, pattern_func in enumerate(floor_patterns):
            floor_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            # Vary the colour slightly
            color = (floor_base_color[0] + i*2, floor_base_color[1] + i*2, floor_base_color[2] + i*2)
            floor_surf.fill(color)
            # Apply the pattern
            pattern_func(floor_surf)
            self.assets["tiles"]["floor"].append(floor_surf)
    
    def _create_fallback_chest_animations(self):
        """Create fallback chest animation frames if assets couldn't be loaded."""
        # Create closed chest animations (4 frames with slight variations)
        for i in range(4):
            chest_closed = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Main box
            pygame.draw.rect(chest_closed, (139, 69, 19), (5, 10, TILE_SIZE-10, TILE_SIZE-15))
            
            # Lid - slight colour variation for animation effect
            lid_color = (101 + i*5, 67 + i*2, 33 + i*3)
            pygame.draw.rect(chest_closed, lid_color, (0, 0, TILE_SIZE, 15))
            
            # Lock - slightly different position for animation effect
            offset = math.sin(i * math.pi/2) * 2
            pygame.draw.rect(chest_closed, (255, 215, 0), 
                           (TILE_SIZE//2 - 5, 5 + offset, 10, 8))
            
            # Add "CHEST" text
            if TILE_SIZE >= 30:  # Only add text if tile is big enough
                font = pygame.font.Font(None, 12)
                text = font.render("CHEST", True, (0, 0, 0))
                # Position the text in the middle of the chest
                text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
                chest_closed.blit(text, text_rect)
                
            self.assets["objects"]["chest_closed"].append(chest_closed)
        
        # Create open chest animations (4 frames showing opening sequence)
        for i in range(4):
            chest_open = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Main box
            pygame.draw.rect(chest_open, (139, 69, 19), (5, 10, TILE_SIZE-10, TILE_SIZE-15))
            
            # Lid opening animation - angle increases with each frame
            opening_angle = i * 30  # 0, 30, 60, 90 degrees
            lid_width = 15
            lid_height = TILE_SIZE - 10
            
            # Position lid based on opening angle
            lid_x = TILE_SIZE - 15 + (i * 3)
            lid_y = -5 - (i * 3)
            
            # Draw lid with different angle for each frame
            pygame.draw.rect(chest_open, (101, 67, 33), 
                           (lid_x, lid_y, lid_width, lid_height), 0, 3)
            
            # Gold inside - more visible with each frame
            visibility = min(255, 100 + i * 50)
            gold_color = (255, 215, 0, visibility)
            
            # Create gold surface with alpha
            gold_surf = pygame.Surface((TILE_SIZE-10, TILE_SIZE-20), pygame.SRCALPHA)
            pygame.draw.circle(gold_surf, gold_color, (TILE_SIZE//2 - 5, TILE_SIZE//2 - 5), 8)
            pygame.draw.circle(gold_surf, gold_color, (TILE_SIZE//2 - 15, TILE_SIZE//2), 6)
            pygame.draw.circle(gold_surf, gold_color, (TILE_SIZE//2 + 5, TILE_SIZE//2), 7)
            
            # Add gold with proper alpha blending
            chest_open.blit(gold_surf, (5, 10))
            
            # Add "OPEN" text
            if TILE_SIZE >= 30 and i >= 2:  # Only add text for later frames when chest is more open
                font = pygame.font.Font(None, 12)
                text = font.render("OPEN", True, (0, 0, 0))
                # Position the text in the middle of the chest
                text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//1.5))
                chest_open.blit(text, text_rect)
                
            self.assets["objects"]["chest_open"].append(chest_open)
    
    def _load_peaks_animations(self, assets_dir):
        """Load peaks (spike trap) assets from the world/peaks directory."""
        peaks_dir = os.path.join(assets_dir,"items and trap_animation", "peaks")
        
        try:
            if os.path.exists(peaks_dir):
                # Load peaks frames
                active_frame = None
                inactive_frames = []
                
                # Find all peaks frames
                for i in range(1, 5):
                    frame_path = os.path.join(peaks_dir, f"peaks_{i}.png")
                    if os.path.exists(frame_path):
                        frame = pygame.image.load(frame_path).convert_alpha()
                        # Scale to 80% of tile size
                        frame = pygame.transform.scale(frame, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
                        
                        # First frame is active (spikes up), others are inactive (spikes down)
                        if i == 1:
                            active_frame = frame
                        else:
                            inactive_frames.append(frame)
                
                # Set the assets
                if active_frame and inactive_frames:
                    self.assets["objects"]["trap_active"] = active_frame
                    # Use the middle frame for the inactive state
                    self.assets["objects"]["trap_inactive"] = inactive_frames[1]  # peaks_3.png
                    return True
        except Exception:
            pass
        
        # If loading fails, fallback will be used later
        return False
    
    def _load_torch_animations(self, assets_dir):
        """Load torch animations from the world/torch directory."""
        torch_dir = os.path.join(assets_dir,"items and trap_animation", "torch")
        
        try:
            if os.path.exists(torch_dir):
                # We'll use the standard torch (not side_torch or candlestick)
                torch_frames = []
                
                # Load torch animation frames
                for i in range(1, 5):
                    frame_path = os.path.join(torch_dir, f"torch_{i}.png")
                    if os.path.exists(frame_path):
                        frame = pygame.image.load(frame_path).convert_alpha()
                        # Scale to 80% of tile size
                        frame = pygame.transform.scale(frame, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8)))
                        torch_frames.append(frame)
                
                if torch_frames:
                    self.assets["objects"]["torch"] = torch_frames
                    return True
        except Exception:
            pass
        
        # If loading fails, create fallback torch animations
        self._create_fallback_torch_animations()
        return False
    
    def _create_fallback_torch_animations(self):
        """Create fallback torch animation when assets can't be loaded."""
        for i in range(4):
            torch_frame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Torch base
            pygame.draw.rect(torch_frame, (100, 50, 0), 
                           (TILE_SIZE//2 - 3, TILE_SIZE//2, 6, TILE_SIZE//2 - 5))
            
            # Torch flame - animated with different heights
            flame_height = 10 + (i * 2) % 6
            flame_width = 8 + (i * 2) % 4
            
            # Draw flame
            pygame.draw.polygon(torch_frame, (255, 200, 0), [
                (TILE_SIZE//2, TILE_SIZE//2 - flame_height),  # Top
                (TILE_SIZE//2 - flame_width//2, TILE_SIZE//2),  # Left
                (TILE_SIZE//2 + flame_width//2, TILE_SIZE//2)   # Right
            ])
            
            # Add orange layer
            pygame.draw.polygon(torch_frame, (255, 130, 0), [
                (TILE_SIZE//2, TILE_SIZE//2 - flame_height + 3),  # Top
                (TILE_SIZE//2 - flame_width//2 + 2, TILE_SIZE//2 - 2),  # Left
                (TILE_SIZE//2 + flame_width//2 - 2, TILE_SIZE//2 - 2)   # Right
            ])
            
            # Add red core
            pygame.draw.polygon(torch_frame, (255, 60, 0), [
                (TILE_SIZE//2, TILE_SIZE//2 - flame_height//2),  # Top
                (TILE_SIZE//2 - flame_width//4, TILE_SIZE//2 - 2),  # Left
                (TILE_SIZE//2 + flame_width//4, TILE_SIZE//2 - 2)   # Right
            ])
            
            # Add glow effect
            glow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # Radius fluctuates with animation
            glow_radius = 15 + (i * 2) % 5
            pygame.draw.circle(glow_surf, (255, 200, 0, 30), 
                             (TILE_SIZE//2, TILE_SIZE//2 - 5), glow_radius)
            torch_frame.blit(glow_surf, (0, 0))
            
            self.assets["objects"]["torch"].append(torch_frame)
    
    def _create_fallback_objects(self):
        """Create fallback object images for traps and chests."""
        # Create fallback chest animations
        self._create_fallback_chest_animations()
        
        # Only create fallback traps if they're not already loaded
        if self.assets["objects"]["trap_inactive"] is None:
            # Create fallback trap inactive
            trap_inactive = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # Base plate
            pygame.draw.rect(trap_inactive, (100, 100, 100), (0, 0, TILE_SIZE, TILE_SIZE))
            # Spike holes
            for i in range(3):
                for j in range(3):
                    pygame.draw.circle(trap_inactive, (50, 50, 50), 
                                     (10 + i*10, 10 + j*10), 2)
                    
            # Add "TRAP" text
            if TILE_SIZE >= 30:  # Only add text if tile is big enough
                font = pygame.font.Font(None, 12)
                text = font.render("TRAP", True, (200, 0, 0))
                # Position the text in the middle of the trap
                text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
                trap_inactive.blit(text, text_rect)
                
            self.assets["objects"]["trap_inactive"] = trap_inactive
        
        if self.assets["objects"]["trap_active"] is None:
            # Create fallback trap active
            trap_active = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # Base plate
            pygame.draw.rect(trap_active, (100, 100, 100), (0, 0, TILE_SIZE, TILE_SIZE))
            # Spikes
            for i in range(3):
                for j in range(3):
                    pygame.draw.polygon(trap_active, (200, 200, 200), [
                        (10 + i*10, 10 + j*10 - 8),  # Tip
                        (7 + i*10, 10 + j*10 + 2),   # Left base
                        (13 + i*10, 10 + j*10 + 2)   # Right base
                    ])
            
            # Add "OUCH!" text
            if TILE_SIZE >= 30:  # Only add text if tile is big enough
                font = pygame.font.Font(None, 12)
                text = font.render("OUCH!", True, (200, 0, 0))
                # Position the text in the middle of the trap
                text_rect = text.get_rect(center=(TILE_SIZE//2, TILE_SIZE//4))
                trap_active.blit(text, text_rect)
                
            self.assets["objects"]["trap_active"] = trap_active
        
        # Create fallback torch animations if not loaded
        if not self.assets["objects"]["torch"]:
            self._create_fallback_torch_animations()
    
    def _create_fallback_idle_animation(self, character_type="knight"):
        """
        Create a fallback idle animation.
        
        Args:
            character_type: The type of character to create animation for ("knight" or "wizard").
        """
        for i in range(4):  # Create 4 frames
            frame = pygame.Surface((100, 125), pygame.SRCALPHA)
            
            # Body
            body_color = BLUE if character_type == "knight" else PURPLE
            pygame.draw.rect(frame, body_color, (20, 30, 40, 60))
            
            # Head
            pygame.draw.circle(frame, (200, 150, 150), (40, 20), 15)
            
            # Eyes
            pygame.draw.circle(frame, WHITE, (35, 17), 3)
            pygame.draw.circle(frame, WHITE, (45, 17), 3)
            
            # Simple animation - bob up and down
            offset = 2 if i % 2 == 0 else 0
            
            # Outline
            outline_color = (50, 50, 200) if character_type == "knight" else (100, 0, 150)
            pygame.draw.rect(frame, outline_color, (20, 30 - offset, 40, 60), 2)
            
            # Add wizard-specific details
            if character_type == "wizard":
                # Wizard hat
                pygame.draw.polygon(frame, PURPLE, [(30, 17), (40, 0), (50, 17)])
                pygame.draw.line(frame, (180, 180, 0), (35, 12), (45, 12), 2)
                
                # Magic effect
                if i % 2 == 0:
                    pygame.draw.circle(frame, (100, 100, 255, 100), (60, 50), 5)
            
            self.assets["player"][character_type]["idle"].append(frame)
    
    def _create_fallback_attack_animation(self, character_type="knight"):
        """
        Create a fallback attack animation.
        
        Args:
            character_type: The type of character to create animation for ("knight" or "wizard").
        """
        for i in range(6):  # Create 6 frames of attack
            frame = pygame.Surface((120, 145), pygame.SRCALPHA)
            
            # Body
            body_color = BLUE if character_type == "knight" else PURPLE
            pygame.draw.rect(frame, body_color, (30, 40, 40, 60))
            
            # Head
            pygame.draw.circle(frame, (200, 150, 150), (50, 30), 15)
            
            # Eyes
            pygame.draw.circle(frame, WHITE, (45, 27), 3)
            pygame.draw.circle(frame, WHITE, (55, 27), 3)
            
            # Add wizard-specific details
            if character_type == "wizard":
                # Wizard hat
                pygame.draw.polygon(frame, PURPLE, [(40, 27), (50, 10), (60, 27)])
                pygame.draw.line(frame, (180, 180, 0), (45, 22), (55, 22), 2)
                
                # Magic staff and effect
                pygame.draw.line(frame, (100, 60, 20), (50, 60), (70 + i * 5, 40 - i * 5), 3)
                
                # Magic effect growing with animation
                effect_size = 5 + i * 2
                pygame.draw.circle(frame, (100, 100, 255, 150), (75 + i * 5, 35 - i * 5), effect_size)
            else:
                # Knight weapon animation
                if i < 3:
                    # Draw arm raising a sword
                    angle = i * 30  # 0, 30, 60 degrees
                    arm_x = 70 + i * 5
                    arm_y = 50 - i * 5
                    pygame.draw.line(frame, (200, 150, 150), (70, 50), (arm_x, arm_y), 5)
                    pygame.draw.rect(frame, (200, 200, 200), (arm_x, arm_y, 5, 20))
                else:
                    # Draw arm swinging sword
                    angle = 60 - (i - 3) * 30  # 60, 30, 0 degrees
                    arm_x = 85 - (i - 3) * 5
                    arm_y = 35 + (i - 3) * 5
                    pygame.draw.line(frame, (200, 150, 150), (70, 50), (arm_x, arm_y), 5)
                    pygame.draw.rect(frame, (200, 200, 200), (arm_x, arm_y, 5, 20))
            
            # Outline
            outline_color = (50, 50, 200) if character_type == "knight" else (100, 0, 150)
            pygame.draw.rect(frame, outline_color, (30, 40, 40, 60), 2)
            
            self.assets["player"][character_type]["attack"].append(frame)
    
    def _create_fallback_enemy_animation(self, anim_type):
        """Create fallback enemy animations."""
        frame_count = 4  # Default frame count
        
        if anim_type == "attack":
            frame_count = 6
        elif anim_type == "death":
            frame_count = 8
        
        for i in range(frame_count):
            frame = pygame.Surface((90, 115), pygame.SRCALPHA)
            
            # Body
            body_color = (150, 50, 50)  # Red for enemy
            pygame.draw.rect(frame, body_color, (15, 30, 40, 50))
            
            # Head
            pygame.draw.circle(frame, (150, 150, 150), (35, 20), 15)
            
            # Eyes
            pygame.draw.circle(frame, (255, 0, 0), (30, 17), 3)  # Red eyes
            pygame.draw.circle(frame, (255, 0, 0), (40, 17), 3)
            
            # Animation based on type
            if anim_type == "idle":
                # Simple bob
                offset = 2 if i % 2 == 0 else 0
                pygame.draw.rect(frame, (100, 0, 0), (15, 30 - offset, 40, 50), 2)
            elif anim_type == "attack":
                # Similar to player attack
                if i < 3:
                    arm_x = 15 - i * 5
                    arm_y = 50 - i * 5
                    pygame.draw.line(frame, (150, 150, 150), (15, 50), (arm_x, arm_y), 5)
                else:
                    arm_x = 0 + (i - 3) * 5
                    arm_y = 35 + (i - 3) * 5
                    pygame.draw.line(frame, (150, 150, 150), (15, 50), (arm_x, arm_y), 5)
            elif anim_type == "hurt":
                # Flash red and shift
                alpha = 150 + (i * 50) % 100
                overlay = pygame.Surface((40, 50), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, alpha))
                frame.blit(overlay, (15, 30))
            elif anim_type == "death":
                # Fall over
                angle = i * 10
                frame = pygame.transform.rotate(frame, angle)
                alpha = 255 - (i * 30)
                if alpha < 0:
                    alpha = 0
                frame.set_alpha(alpha)
            
            # Outline
            pygame.draw.rect(frame, (100, 0, 0), (15, 30, 40, 50), 2)
            
            self.assets["enemy"][anim_type].append(frame)
    
    def _create_fallback_coin_animation(self):
        """Create fallback coin animation frames if assets couldn't be loaded."""
        for i in range(4):
            # Create a simple coin animation
            coin_frame = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
            
            # Rotate the coin for different frames
            rotation = i * 90
            if rotation == 0 or rotation == 180:
                # Show the coin face
                pygame.draw.circle(coin_frame, (255, 215, 0), (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4 - 2)
                pygame.draw.circle(coin_frame, (212, 175, 55), (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4 - 4)
                
                # Add details based on rotation
                if rotation == 0:
                    # Face side - add a simple icon
                    font = pygame.font.Font(None, TILE_SIZE // 3)
                    text = font.render("$", True, (255, 255, 200))
                    text_rect = text.get_rect(center=(TILE_SIZE // 4, TILE_SIZE // 4))
                    coin_frame.blit(text, text_rect)
            else:
                # Edge view - thinner ellipse
                pygame.draw.ellipse(coin_frame, (255, 215, 0), 
                                  (2, TILE_SIZE // 8, TILE_SIZE // 2 - 4, TILE_SIZE // 4))
                pygame.draw.ellipse(coin_frame, (212, 175, 55), 
                                  (4, TILE_SIZE // 8 + 2, TILE_SIZE // 2 - 8, TILE_SIZE // 4 - 4))
            
            # Add a shine effect
            pygame.draw.arc(coin_frame, (255, 255, 220), 
                           (TILE_SIZE // 8, TILE_SIZE // 8, TILE_SIZE // 4, TILE_SIZE // 4),
                           0, 3.14 / 2, 2)
            
            self.assets["objects"]["coin"].append(coin_frame)
    
    # Getter methods
    def get_tile(self, tile_type, index=None):
        """Get a tile image by type."""
        tiles = self.assets["tiles"].get(tile_type, [])
        if not tiles:
            return None
        
        if index is None:
            # Return a random tile variant
            return random.choice(tiles)
        else:
            # Return a specific tile
            return tiles[index % len(tiles)]
    
    def get_player_idle_frames(self, character_type="knight"):
        """
        Get the player idle animation frames.
        
        Args:
            character_type: The character type ("knight" or "wizard").
            
        Returns:
            list: Animation frames for the specified character type.
        """
        return self.assets["player"][character_type]["idle"]
    
    def get_player_attack_frames(self, character_type="knight"):
        """
        Get the player attack animation frames.
        
        Args:
            character_type: The character type ("knight" or "wizard").
            
        Returns:
            list: Animation frames for the specified character type.
        """
        return self.assets["player"][character_type]["attack"]
        
    def get_wizard_projectile_effect(self):
        """
        Get the wizard projectile effect image.
        
        Returns:
            Surface or None: The projectile effect image if loaded, None otherwise.
        """
        # Check if we already have it loaded
        if "wizard" in self.assets["player"] and "projectile_effect" in self.assets["player"]["wizard"]:
            effect = self.assets["player"]["wizard"]["projectile_effect"]
            if effect:
                return effect
                
        # Try to load it on demand from various paths
        try:
            # Try all the usual paths
            import os
            assets_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(os.path.dirname(assets_dir), "src")
            
            # Try all possible paths for the wizard projectile effect
            possible_paths = [
                # Path in the assets directory
                os.path.join(assets_dir,"images", "characters", "Wizard", "Wizard", "Wizard-Attack01_Effect.png"),
                # Try Attack02_Effect as well
                os.path.join(assets_dir,"images", "characters", "Wizard", "Wizard", "Wizard-Attack02_Effect.png"),
                # Path inside src directory - standard wizard
                os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard", "Wizard-Attack01_Effect.png"),
                # Path inside src directory - wizard with shadows
                os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard with shadows", "Wizard-Attack01_Effect.png"),
                # Alternative wizard projectile
                os.path.join(src_dir, "assets", "images", "characters", "Wizard", "Wizard", "Wizard-Attack02_Effect.png")
            ]
            
            # Try loading from each path
            for path in possible_paths:
                if os.path.exists(path):
                    effect_image = pygame.image.load(path).convert_alpha()
                    
                    # Store the unmodified effect image regardless
                    self.assets["player"]["wizard"]["projectile_effect"] = effect_image
                    return effect_image
            
            # If we get here, we couldn't find the effect image
            return None
            
        except Exception:
            return None
    
    def get_enemy_frames(self, anim_type):
        """Get enemy animation frames."""
        return self.assets["enemy"][anim_type]

    def get_orc_frames(self, anim_type):
        """Get orc enemy animation frames."""
        return self.assets["orc"][anim_type]
        
    def get_chest_closed_frames(self):
        """Get the closed chest animation frames."""
        return self.assets["objects"]["chest_closed"]
    
    def get_chest_open_frames(self):
        """Get the open chest animation frames."""
        return self.assets["objects"]["chest_open"]
    
    def get_trap_inactive_image(self):
        """Get the inactive trap image."""
        return self.assets["objects"]["trap_inactive"]
    
    def get_trap_active_image(self):
        """Get the active trap image."""
        return self.assets["objects"]["trap_active"]
    
    def get_coin_frames(self):
        """Get the coin animation frames."""
        return self.assets["objects"]["coin"]

    def get_weapon_frames(self):
        """Get the weapon (arrow) animation frames."""
        return self.assets["objects"]["weapon"]

    def get_potion_frames(self):
        """Get the potion (flask) animation frames."""
        return self.assets["objects"]["potion"]
        
    def get_torch_frames(self):
        """Get the torch animation frames."""
        return self.assets["objects"]["torch"]
        
    def get_priest_idle_frames(self):
        """Get the priest idle animation frames for NPC."""
        return self.assets["npc"]["priest"]["idle"]
    
    def _load_priest_animations(self, assets_dir):
        """Load priest character animations for NPC."""
        # Load priest idle animation
        idle_path = os.path.join(assets_dir,"Priest", "Priest", "Priest-Idle.png")
        if os.path.exists(idle_path):
            try:
                idle_sheet = pygame.image.load(idle_path).convert_alpha()
                
                # Extract frames from the idle spritesheet
                frame_count = 6  # Priest idle has 6 frames
                frame_width = idle_sheet.get_width() // frame_count
                frame_height = idle_sheet.get_height()
                
                # Create each frame
                for i in range(frame_count):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(idle_sheet, (0, 0), frame_rect)
                    
                    # Scale the frame to a consistent size with other characters
                    frame = pygame.transform.scale(frame, (90, 115))
                    self.assets["npc"]["priest"]["idle"].append(frame)
            except Exception:
                self._create_fallback_priest_animation()
        else:
            self._create_fallback_priest_animation()
    
    def _create_fallback_priest_animation(self):
        """Create fallback priest animation."""
        # Standard dimensions used by other characters
        frame_width, frame_height = 90, 115
        
        for i in range(4):  # Create 4 frames
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            
            # Body - white/holy colour
            body_color = (220, 220, 250)
            pygame.draw.rect(frame, body_color, (frame_width//6, frame_height//4, frame_width//2.25, frame_height//2.3))
            
            # Head
            head_x, head_y = frame_width//2.5, frame_height//5.75
            pygame.draw.circle(frame, (240, 240, 240), (head_x, head_y), frame_width//6)
            
            # Eyes
            pygame.draw.circle(frame, (50, 130, 240), (head_x - 5, head_y - 3), 3)  # Blue eyes
            pygame.draw.circle(frame, (50, 130, 240), (head_x + 5, head_y - 3), 3)
            
            # Simple animation - bob up and down
            offset = 2 if i % 2 == 0 else 0
            
            # Robes
            pygame.draw.rect(frame, (180, 180, 230), 
                          (frame_width//9, frame_height//1.75 - offset, frame_width//1.8, frame_height//2.9))
            
            # Holy symbol
            symbol_x, symbol_y = frame_width//2.57, frame_height//2.88
            pygame.draw.line(frame, (255, 255, 100), 
                          (symbol_x, symbol_y), (symbol_x, symbol_y + 15), 3)
            pygame.draw.line(frame, (255, 255, 100), 
                          (symbol_x - 10, symbol_y + 5), (symbol_x + 10, symbol_y + 5), 3)
            
            self.assets["npc"]["priest"]["idle"].append(frame)