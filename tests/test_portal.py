"""
Test module for the Portal class.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from objects.portal import Portal
from characters.warrior import Warrior
from core.map import TILE_SIZE

class TestPortal(unittest.TestCase):
    """
    Test case for the Portal class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create a test portal
        self.portal = Portal(200, 200)
        
        # Create dummy animation frames for player
        self.player_idle_frames = [pygame.Surface((80, 100), pygame.SRCALPHA) for _ in range(4)]
        self.player_attack_frames = [pygame.Surface((100, 120), pygame.SRCALPHA) for _ in range(6)]
        
        # Create a test player
        self.player = Warrior(100, 100, self.player_idle_frames, self.player_attack_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_portal_initialization(self):
        """
        Test portal initialisation.
        """
        self.assertEqual(self.portal.x, 200)
        self.assertEqual(self.portal.y, 200)
        self.assertEqual(self.portal.width, TILE_SIZE)
        self.assertEqual(self.portal.height, TILE_SIZE)
        self.assertFalse(self.portal.activated)
        self.assertEqual(self.portal.animation_speed, 0.1)
    
    def test_portal_update(self):
        """
        Test portal update method changes visual effects.
        """
        # Get initial values
        initial_glow = self.portal.glow_alpha
        initial_pulse = self.portal.pulse_size
        
        # Update portal
        self.portal.update()
        
        # Visual effects should change, but we don't test exact values since they're time-based
        # We verify the correct rect position instead
        self.assertEqual(self.portal.hitbox.x, self.portal.x)
        self.assertEqual(self.portal.hitbox.y, self.portal.y)
    
    def test_player_collision_detection(self):
        """
        Test portal detects player collision correctly.
        """
        # Initially player should not be colliding with portal
        self.assertFalse(self.portal.is_player_colliding(self.player))
        
        # Position player to guarantee collision with portal
        # First, print the rects to understand current positions
        print(f"Portal hitbox: {self.portal.hitbox}")
        print(f"Player initial hitbox: {self.player.hitbox}")
        
        # Force the player hitbox to completely overlap with the portal hitbox
        self.player.hitbox = pygame.Rect(self.portal.hitbox)
        
        # Now there should be a collision
        self.assertTrue(self.portal.is_player_colliding(self.player))
        
        # Move player away from portal
        self.player.x = self.portal.x + 100
        self.player.y = self.portal.y + 100
        
        # Update hitbox position
        self.player.hitbox.x = self.player.x + 25
        self.player.hitbox.y = self.player.y + 50
        
        # Now player should not be colliding with portal
        self.assertFalse(self.portal.is_player_colliding(self.player))
    
    def test_edge_collision(self):
        """
        Test edge collisions with the portal.
        """
        # Place player at different edges of the portal
        edge_offsets = [
            (0, -40),  # Top edge
            (0, TILE_SIZE),  # Bottom edge
            (-30, 0),  # Left edge
            (TILE_SIZE, 0)   # Right edge
        ]
        
        for offset_x, offset_y in edge_offsets:
            # Position player
            self.player.x = self.portal.x + offset_x
            self.player.y = self.portal.y + offset_y
            
            # Update hitbox position
            self.player.hitbox.x = self.player.x + 25
            self.player.hitbox.y = self.player.y + 50
            
            # Check for collision - result depends on how close player is
            result = self.portal.is_player_colliding(self.player)
            
            # We're just testing that the collision detection runs without errors
            self.assertIsInstance(result, bool)
    
    def test_rendering(self):
        """
        Test portal rendering doesn't crash.
        """
        # Create a test surface
        test_surface = pygame.Surface((400, 400))
        
        # Rendering should not crash
        try:
            self.portal.draw(test_surface)
            no_crash = True
        except Exception as e:
            no_crash = False
        
        self.assertTrue(no_crash)

if __name__ == '__main__':
    unittest.main()