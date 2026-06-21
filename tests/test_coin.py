"""
Test module for the Coin class.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from objects.coin import Coin

class TestCoin(unittest.TestCase):
    """
    Test case for the Coin class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create dummy animation frames for coin
        self.coin_frames = [pygame.Surface((20, 20), pygame.SRCALPHA) for _ in range(4)]
        
        # Create a test coin
        self.coin = Coin(100, 100, self.coin_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_coin_initialization(self):
        """
        Test coin initialisation.
        """
        self.assertEqual(self.coin.x, 100)
        self.assertEqual(self.coin.y, 100)
        self.assertEqual(self.coin.width, 20)
        self.assertEqual(self.coin.height, 20)
        self.assertEqual(self.coin.current_frame, 0)
        self.assertEqual(self.coin.animation_timer, 0)
        self.assertFalse(self.coin.collected)
        self.assertEqual(self.coin.lifetime, 600)  # 10 seconds at 60 FPS
    
    def test_coin_animation(self):
        """
        Test coin animation updates correctly.
        """
        # Initial frame
        initial_frame = self.coin.current_frame
        
        # Update coin multiple times to trigger animation
        for _ in range(10):
            self.coin.update()
        
        # Check if animation has advanced (if animation speed allows)
        # We can't guarantee the exact frame due to animation speed, but we can check that it updates
        self.coin.animation_timer = 1  # Force animation timer to be high
        self.coin.update()
        self.assertNotEqual(self.coin.current_frame, initial_frame)
    
    def test_coin_collection(self):
        """
        Test coin collection.
        """
        # Initially the coin should not be collected
        self.assertFalse(self.coin.collected)
        
        # Collect the coin
        gold_value = self.coin.collect()
        
        # Verify collection behaviour
        self.assertTrue(self.coin.collected)
        self.assertGreaterEqual(gold_value, 5)  # Random value between 5-15
        self.assertLessEqual(gold_value, 15)
        
        # Collecting again should return 0
        second_value = self.coin.collect()
        self.assertEqual(second_value, 0)
    
    def test_coin_lifetime(self):
        """
        Test coin lifetime behaviour.
        """
        # Force the lifetime to be almost zero
        self.coin.lifetime = 2
        
        # Verify coin is not collected initially
        self.assertFalse(self.coin.collected)
        
        # Update until lifetime expires
        self.coin.update()
        self.coin.update()
        self.coin.update()  # Should expire now
        
        # Verify coin is now collected due to expired lifetime
        self.assertTrue(self.coin.collected)
    
    def test_bobbing_animation(self):
        """
        Test coin bobbing animation.
        """
        # Initial bobbing values
        initial_offset = self.coin.bobbing_offset
        initial_direction = self.coin.bobbing_direction
        
        # Update the coin to bobbing
        for _ in range(5):
            self.coin.update()
        
        # Check that the bobbing offset has changed
        self.assertNotEqual(self.coin.bobbing_offset, initial_offset)
        
        # If the bobbing goes beyond threshold, direction should reverse
        # Force the offset to be close to threshold
        self.coin.bobbing_offset = 2.9
        original_direction = self.coin.bobbing_direction
        
        # Update multiple times to trigger direction change
        for _ in range(5):
            self.coin.update()
            if self.coin.bobbing_direction != original_direction:
                break
                
        # Direction should eventually reverse
        self.assertNotEqual(self.coin.bobbing_direction, original_direction)
    
    def test_coin_hitbox_follows_bobbing(self):
        """
        Test that coin hitbox moves with bobbing animation.
        """
        # Initial hitbox position
        initial_hitbox_y = self.coin.hitbox.y
        
        # Update the coin to bobbing
        self.coin.update()
        
        # Check that the hitbox y position changes with bobbing offset
        # Due to potential floating point to int conversion, we check that it's close enough
        self.assertAlmostEqual(self.coin.hitbox.y, self.coin.y + self.coin.bobbing_offset, delta=1)
        
        # After several updates, the hitbox should definitely move
        for _ in range(10):
            self.coin.update()
        self.assertNotEqual(self.coin.hitbox.y, initial_hitbox_y)

if __name__ == '__main__':
    unittest.main()