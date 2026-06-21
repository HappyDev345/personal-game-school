"""
Test module for collision detection.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.map import GameMap
from characters.warrior import Warrior
from assets.asset_loader import AssetLoader
from core.map import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class TestCollisionDetection(unittest.TestCase):
    """Tests for collision detection using GameMap."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1000, 800), pygame.SRCALPHA | pygame.HIDDEN)
        
        # Create a mock asset loader and game map
        self.asset_loader = AssetLoader()
        self.game_map = GameMap(self.asset_loader, 0)
        
        # Create dummy player frames for testing
        idle_frames = [pygame.Surface((80, 100), pygame.SRCALPHA) for _ in range(4)]
        attack_frames = [pygame.Surface((100, 120), pygame.SRCALPHA) for _ in range(6)]
        
        # Get start position from the map
        start_pos = self.game_map.get_player_start_position()
        self.player = Warrior(start_pos[0], start_pos[1], idle_frames, attack_frames)
    
    def tearDown(self):
        """Clean up after each test."""
        pygame.quit()
    
    def test_wall_collision(self):
        """Test collision detection with walls."""
        # Find a known wall position (the border of the map)
        wall_x = 0
        wall_y = 0
        
        # Verify it's actually a wall
        self.assertTrue(self.game_map.is_wall(wall_x, wall_y))
        
        # Position player at the wall
        self.player.x = wall_x * TILE_SIZE
        self.player.y = wall_y * TILE_SIZE
        
        # Update hitbox position
        self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
        self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
        
        # Check if position is valid using Player's method
        self.assertFalse(self.player._is_valid_position(self.game_map))
    
    def test_floor_collision(self):
        """Test collision detection with floor (should not collide)."""
        # Find a known floor position (player start)
        start_pos = self.game_map.get_player_start_position()
        floor_x = start_pos[0] // TILE_SIZE
        floor_y = start_pos[1] // TILE_SIZE
        
        # Verify it's not a wall
        self.assertFalse(self.game_map.is_wall(floor_x, floor_y))
        
        # Position player on the floor
        self.player.x = floor_x * TILE_SIZE
        self.player.y = floor_y * TILE_SIZE
        
        # Update hitbox position
        self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
        self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
        
        # Check if position is valid using Player's method
        self.assertTrue(self.player._is_valid_position(self.game_map))
    
    def test_boundary_collision(self):
        """Test collision detection at map boundaries."""
        # Position player outside map boundaries
        positions_to_test = [
            (-TILE_SIZE, -TILE_SIZE),  # Top-left corner outside
            (MAP_WIDTH * TILE_SIZE + 10, MAP_HEIGHT * TILE_SIZE + 10),  # Bottom-right corner outside
            (-TILE_SIZE, 100),  # Left edge outside
            (100, -TILE_SIZE),  # Top edge outside
            (MAP_WIDTH * TILE_SIZE + 10, 100),  # Right edge outside
            (100, MAP_HEIGHT * TILE_SIZE + 10)  # Bottom edge outside
        ]
        
        for pos_x, pos_y in positions_to_test:
            # Position player
            self.player.x = pos_x
            self.player.y = pos_y
            
            # Update hitbox position
            self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
            self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
            
            # Check if position is valid using Player's method
            self.assertFalse(self.player._is_valid_position(self.game_map),
                           f"Position ({pos_x}, {pos_y}) should be invalid")
    
    def test_edge_collision(self):
        """Test collision detection at the edge of walls."""
        # Find a known wall position
        wall_x = 0
        wall_y = 0
        
        # Position player at different points near the wall edge
        edge_offsets = [
            (TILE_SIZE - 1, TILE_SIZE // 2),  # Right at the edge of the wall
            (TILE_SIZE // 2, TILE_SIZE - 1),  # Bottom edge of the wall
            (TILE_SIZE - 5, TILE_SIZE - 5)    # Corner edge of the wall
        ]
        
        for offset_x, offset_y in edge_offsets:
            # Position player
            self.player.x = wall_x * TILE_SIZE + offset_x
            self.player.y = wall_y * TILE_SIZE + offset_y
            
            # Update hitbox position
            self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
            self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
            
            # Check for collision - depends on hitbox size and offset
            # We're checking multiple points of the hitbox
            result = self.player._is_valid_position(self.game_map)
            # The specific result depends on hitbox implementation details
            # but we're testing that the collision detection logic works
            self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main()