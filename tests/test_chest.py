"""
Test module for the Chest class.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from objects.chest import Chest
from core.map import TILE_SIZE

class TestChest(unittest.TestCase):
    """
    Test case for the Chest class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create simple surfaces for chest animation frames
        self.closed_frames = []
        self.open_frames = []
        
        # Create 4 frames for closed chest
        for i in range(4):
            frame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            frame.fill((139, 69, 19))  # Brown colour for closed chest
            # Add a small identifier to each frame
            pygame.draw.rect(frame, (200, 100, 50), (i*5, i*5, 10, 10))
            self.closed_frames.append(frame)
        
        # Create 4 frames for open chest
        for i in range(4):
            frame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            frame.fill((101, 67, 33))  # Darker brown for open chest
            # Add a small identifier to each frame
            pygame.draw.rect(frame, (220, 220, 100), (i*5, i*5, 15, 15))
            self.open_frames.append(frame)
        
        # Create a test chest
        self.chest = Chest(150, 150, self.closed_frames, self.open_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_chest_initialization(self):
        """
        Test chest initialisation.
        """
        self.assertEqual(self.chest.x, 150)
        self.assertEqual(self.chest.y, 150)
        self.assertEqual(self.chest.width, TILE_SIZE)
        self.assertEqual(self.chest.height, TILE_SIZE)
        self.assertFalse(self.chest.is_open)
        self.assertIsNone(self.chest.floating_text)
        
        # Verify random content generation is within bounds
        self.assertGreaterEqual(self.chest.gold, 10)
        self.assertLessEqual(self.chest.gold, 30)
        self.assertIn(self.chest.health_potion, [True, False])
    
    def test_chest_bobbing_animation(self):
        """
        Test chest bobbing animation.
        """
        # Initial bobbing values
        initial_offset = self.chest.bobbing_offset
        initial_direction = self.chest.bobbing_direction
        
        # Update the chest
        self.chest.update()
        
        # Check that the bobbing offset changes for unopened chest
        self.assertNotEqual(self.chest.bobbing_offset, initial_offset)
        
        # Test direction reversal at limits
        # Force the offset to be close to threshold
        self.chest.bobbing_offset = 1.9
        self.chest.update()
        
        # If we hit the threshold, direction should reverse
        if abs(self.chest.bobbing_offset) > 2:
            self.assertNotEqual(self.chest.bobbing_direction, initial_direction)
            
        # Open the chest and verify bobbing stops
        self.chest.open()
        original_offset = self.chest.bobbing_offset
        self.chest.update()
        
        # Bobbing offset should not change for open chest
        self.assertEqual(self.chest.bobbing_offset, original_offset)
    
    def test_opening_chest(self):
        """
        Test opening the chest.
        """
        # Chest should initially be closed
        self.assertFalse(self.chest.is_open)
        
        # Open the chest
        contents = self.chest.open()
        
        # Verify chest is opened
        self.assertTrue(self.chest.is_open)
        self.assertIsNotNone(contents)
        
        # Verify chest contains expected content types
        self.assertIn("gold", contents)
        self.assertIn("health_potion", contents)
        
        # Verify gold amount is the same as chest's gold property
        self.assertEqual(contents["gold"], self.chest.gold)
        
        # Verify health potion is the same as chest's health_potion property
        self.assertEqual(contents["health_potion"], self.chest.health_potion)
        
        # Verify opening an already opened chest returns None
        second_open = self.chest.open()
        self.assertIsNone(second_open)
    
    def test_floating_text(self):
        """
        Test floating text is set when chest is opened.
        """
        # Initially, no floating text
        self.assertIsNone(self.chest.floating_text)
        
        # Open the chest
        self.chest.open()
        
        # Floating text should now be set
        self.assertIsNotNone(self.chest.floating_text)
        
        # Text should contain gold amount
        self.assertIn(str(self.chest.gold), self.chest.floating_text)
        
        # If chest has health potion, text should mention it
        if self.chest.health_potion:
            self.assertIn("Health Potion", self.chest.floating_text)
    
    def test_rendering(self):
        """
        Test chest rendering doesn't crash.
        """
        # Create a test surface
        test_surface = pygame.Surface((400, 400))
        
        # Test rendering closed chest
        try:
            self.chest.draw(test_surface)
            closed_render_ok = True
        except Exception as e:
            closed_render_ok = False
        
        self.assertTrue(closed_render_ok)
        
        # Test rendering open chest
        self.chest.open()
        try:
            self.chest.draw(test_surface)
            open_render_ok = True
        except Exception as e:
            open_render_ok = False
        
        self.assertTrue(open_render_ok)
        
        # Test rendering with floating text
        self.chest.floating_text = "Test Text"
        self.chest.opened_time = time.time()
        
        try:
            self.chest.draw(test_surface)
            text_render_ok = True
        except Exception as e:
            text_render_ok = False
        
        self.assertTrue(text_render_ok)

if __name__ == '__main__':
    unittest.main()