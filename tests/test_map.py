"""
Test module for the GameMap class.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.map import GameMap
from assets.asset_loader import AssetLoader
from characters.warrior import Warrior
from core.map import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class TestMap(unittest.TestCase):
    """
    Test case for the GameMap class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1000, 800), pygame.SRCALPHA | pygame.HIDDEN)
        
        # Create a mock asset loader and game map
        self.asset_loader = AssetLoader()
        self.game_map = GameMap(self.asset_loader, 0)  # Level 0
        
        # Create dummy player frames for testing
        idle_frames = [pygame.Surface((80, 100), pygame.SRCALPHA) for _ in range(4)]
        attack_frames = [pygame.Surface((100, 120), pygame.SRCALPHA) for _ in range(6)]
        
        # Get start position from the map
        start_pos = self.game_map.get_player_start_position()
        self.player = Warrior(start_pos[0], start_pos[1], idle_frames, attack_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_map_initialization(self):
        """
        Test map initialisation.
        """
        self.assertEqual(self.game_map.level, 0)
        self.assertIsNotNone(self.game_map.current_map)
        self.assertIsNotNone(self.game_map.tile_variations)
        self.assertIsNotNone(self.game_map.start_position)
        self.assertIsNotNone(self.game_map.exit_position)
    
    def test_find_player_start_position(self):
        """
        Test finding player start position.
        """
        # Reset and find again
        self.game_map.start_position = None
        self.game_map.find_player_start_position()
        
        # Should find the position from the map
        self.assertIsNotNone(self.game_map.start_position)
        # Start position is actually a tuple of coordinates
        self.assertEqual(len(self.game_map.start_position), 2)
        self.assertIsInstance(self.game_map.start_position[0], int)
        self.assertIsInstance(self.game_map.start_position[1], int)
    
    def test_find_exit_position(self):
        """
        Test finding exit position.
        """
        # Reset and find again
        self.game_map.exit_position = None
        self.game_map.find_exit_position()
        
        # Should find the position from the map
        self.assertIsNotNone(self.game_map.exit_position)
        # Exit position is actually a tuple of coordinates
        self.assertEqual(len(self.game_map.exit_position), 2)
        self.assertIsInstance(self.game_map.exit_position[0], int)
        self.assertIsInstance(self.game_map.exit_position[1], int)
    
    def test_is_wall(self):
        """
        Test the is_wall method.
        """
        # Test a known wall tile (border of the map)
        self.assertTrue(self.game_map.is_wall(0, 0))
        
        # Test a known floor tile (where the player starts)
        start_pos_tiles = (self.game_map.start_position[0] // TILE_SIZE, 
                           self.game_map.start_position[1] // TILE_SIZE)
        self.assertFalse(self.game_map.is_wall(start_pos_tiles[0], start_pos_tiles[1]))
        
        # Test out of bounds (should be considered a wall)
        self.assertTrue(self.game_map.is_wall(-1, -1))
        self.assertTrue(self.game_map.is_wall(MAP_WIDTH + 1, MAP_HEIGHT + 1))
    
    def test_change_level(self):
        """
        Test changing map level.
        """
        # Initial level
        self.assertEqual(self.game_map.level, 0)
        
        # Change to level 1
        result = self.game_map.change_level(1)
        self.assertTrue(result)
        self.assertEqual(self.game_map.level, 1)
        
        # Try to change to an invalid level
        result = self.game_map.change_level(99)
        self.assertFalse(result)
        self.assertEqual(self.game_map.level, 1)  # Should remain at level 1
    
    def test_get_player_start_position(self):
        """
        Test getting player start position.
        """
        start_pos = self.game_map.get_player_start_position()
        self.assertIsNotNone(start_pos)
        self.assertEqual(len(start_pos), 2)
        self.assertEqual(start_pos, self.game_map.start_position)
    
    def test_get_exit_position(self):
        """
        Test getting exit position.
        """
        exit_pos = self.game_map.get_exit_position()
        self.assertIsNotNone(exit_pos)
        self.assertEqual(len(exit_pos), 2)
        self.assertEqual(exit_pos, self.game_map.exit_position)
    
    def test_map_tiles(self):
        """
        Test map tiles generation.
        """
        # Verify tile variations were created
        self.assertEqual(len(self.game_map.tile_variations), MAP_HEIGHT)
        self.assertEqual(len(self.game_map.tile_variations[0]), MAP_WIDTH)
        
        # Test that each tile has a valid variation index
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                variation = self.game_map.tile_variations[y][x]
                self.assertIsInstance(variation, int)
                # Variations should be in a reasonable range based on implementation
                self.assertGreaterEqual(variation, 0)
                self.assertLess(variation, 8)  # Based on the number of variations in the asset loader

if __name__ == '__main__':
    unittest.main()