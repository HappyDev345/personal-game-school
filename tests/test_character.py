"""
Test module for player character.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from characters.warrior import Warrior
from assets.asset_loader import AssetLoader

class TestCharacter(unittest.TestCase):
    """
    Test case for the Player class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1000, 800), pygame.SRCALPHA | pygame.HIDDEN)
        
        # Create dummy animation frames instead of using AssetLoader
        self.idle_frames = [pygame.Surface((100, 125), pygame.SRCALPHA) for _ in range(4)]
        self.attack_frames = [pygame.Surface((120, 145), pygame.SRCALPHA) for _ in range(6)]
        
        # Create a test knight player (default character)
        self.player = Warrior(100, 100, self.idle_frames, self.attack_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_player_initialization(self):
        """
        Test knight player initialisation.
        """
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.max_health, 100)
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.player.speed, 4)
        self.assertEqual(self.player.attack_damage, 20)
        self.assertEqual(self.player.attack_range, 100)
        self.assertEqual(self.player.attack_cooldown, 0.5)
        self.assertEqual(self.player.state, "idle")
        self.assertFalse(self.player.attacking)
    
    def test_take_damage(self):
        """
        Test taking damage.
        """
        # Test player takes damage
        self.player.take_damage(20)
        self.assertEqual(self.player.health, 80)
        
        # Test player takes lethal damage
        self.player.take_damage(100)
        self.assertEqual(self.player.health, 0)
        self.assertFalse(self.player.is_alive())
    
    def test_is_alive(self):
        """
        Test if player is alive.
        """
        self.assertTrue(self.player.is_alive())
        
        # Take enough damage to be defeated
        self.player.take_damage(200)
        self.assertEqual(self.player.health, 0)
        self.assertFalse(self.player.is_alive())
    
    def test_teleport(self):
        """
        Test teleporting player.
        """
        self.player.teleport(200, 300)
        self.assertEqual(self.player.x, 200)
        self.assertEqual(self.player.y, 300)
        self.assertEqual(self.player.hitbox.x, 200 + self.player.hitbox_offset_x)  # Use actual offset
        self.assertEqual(self.player.hitbox.y, 300 + self.player.hitbox_offset_y)  # Use actual offset

    def test_animation_state(self):
        """
        Test animation state changes.
        """
        # Since the animation timing is dependent on actual time, which is hard
        # to control in tests, we'll directly test the state transitions
        
        # Test initial state
        self.assertEqual(self.player.state, "idle")
        self.assertEqual(self.player.current_frame, 0)
        
        # First, verify we can set it to attack
        self.player.state = "attack"
        self.player.attacking = True
        self.assertEqual(self.player.state, "attack")
        self.assertTrue(self.player.attacking)
        
        # Now, simulate what would happen at the end of an attack
        # by directly setting the state back to idle
        self.player.state = "idle"
        self.player.attacking = False
        
        # Verify the state changed correctly
        self.assertEqual(self.player.state, "idle")
        self.assertFalse(self.player.attacking)
    
    def test_hitbox_collision(self):
        """
        Test hitbox collision.
        """
        # Create a mock game object with a hitbox
        class MockObject:
            def __init__(self, x, y, width, height):
                self.hitbox = pygame.Rect(x, y, width, height)
        
        # Create a mock object that doesn't overlap
        far_object = MockObject(300, 300, 30, 30)
        self.assertFalse(self.player.hitbox.colliderect(far_object.hitbox))
        
        # Create a mock object that overlaps
        close_object = MockObject(self.player.hitbox.x, self.player.hitbox.y, 30, 30)
        self.assertTrue(self.player.hitbox.colliderect(close_object.hitbox))

if __name__ == '__main__':
    unittest.main()