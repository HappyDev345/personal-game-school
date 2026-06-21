"""
Test module for the UI class.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.ui import UI
from characters.warrior import Warrior
from characters.enemy import Enemy
from core.game import SCREEN_WIDTH, SCREEN_HEIGHT


class ConcreteEnemy(Enemy):
    """Concrete Enemy subclass for testing (Enemy is abstract)."""

    def take_damage(self, amount):
        return super().take_damage(amount)


class TestUI(unittest.TestCase):
    """
    Test case for the UI class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create a UI instance
        self.ui = UI()
        
        # Create a test screen
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create dummy animation frames for player and enemy
        self.player_frames = {
            "idle": [pygame.Surface((80, 100), pygame.SRCALPHA) for _ in range(4)],
            "attack": [pygame.Surface((100, 120), pygame.SRCALPHA) for _ in range(6)]
        }
        
        self.enemy_frames = {
            "idle": [pygame.Surface((70, 90), pygame.SRCALPHA) for _ in range(4)],
            "attack": [pygame.Surface((70, 90), pygame.SRCALPHA) for _ in range(6)],
            "hurt": [pygame.Surface((70, 90), pygame.SRCALPHA) for _ in range(4)],
            "death": [pygame.Surface((70, 90), pygame.SRCALPHA) for _ in range(8)]
        }
        
        # Create a test player and enemy
        self.player = Warrior(100, 100, self.player_frames["idle"], self.player_frames["attack"])
        self.enemy = ConcreteEnemy(200, 200, self.enemy_frames)
        
        # Create a test inventory
        self.inventory = {"gold": 100, "health_potions": 3}
        
        # Set a test score
        self.score = 500
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_ui_initialization(self):
        """
        Test UI initialisation.
        """
        self.assertEqual(self.ui.message, "")
        self.assertEqual(self.ui.message_timer, 0)
        self.assertEqual(self.ui.message_duration, 3.0)
        self.assertIsNotNone(self.ui.font)
    
    def test_set_message(self):
        """
        Test setting a message.
        """
        test_message = "Test Message"
        
        # Initial state
        self.assertEqual(self.ui.message, "")
        
        # Set a message
        self.ui.set_message(test_message)
        
        # Verify message was set
        self.assertEqual(self.ui.message, test_message)
        
        # Message timer should be set to current time
        self.assertGreater(self.ui.message_timer, 0)
        self.assertLessEqual(self.ui.message_timer, time.time())
    
    def test_message_display_timing(self):
        """
        Test message display timing.
        """
        # Set a message
        self.ui.set_message("Test Message")
        
        # Verify message will display (time differential is less than duration)
        self.assertLess(time.time() - self.ui.message_timer, self.ui.message_duration)
        
        # Set message timer to past the display duration
        self.ui.message_timer = time.time() - self.ui.message_duration - 1
        
        # Verify message should no longer display
        self.assertGreater(time.time() - self.ui.message_timer, self.ui.message_duration)
    
    def test_draw_basic_ui(self):
        """
        Test drawing basic UI elements doesn't crash.
        """
        # Test rendering the UI without debug info
        try:
            self.ui.draw(self.screen, self.player, self.inventory, self.score)
            basic_render_ok = True
        except Exception as e:
            basic_render_ok = False
        
        self.assertTrue(basic_render_ok)
    
    def test_draw_with_debug(self):
        """
        Test drawing UI with debug info doesn't crash.
        """
        # Test rendering with debug info
        try:
            self.ui.draw(self.screen, self.player, self.inventory, self.score, True, self.enemy)
            debug_render_ok = True
        except Exception as e:
            debug_render_ok = False
        
        self.assertTrue(debug_render_ok)
    
    def test_draw_with_message(self):
        """
        Test drawing UI with an active message doesn't crash.
        """
        # Set a message
        self.ui.set_message("Test Message")
        
        # Test rendering with message
        try:
            self.ui.draw(self.screen, self.player, self.inventory, self.score)
            message_render_ok = True
        except Exception as e:
            message_render_ok = False
        
        self.assertTrue(message_render_ok)
    
    def test_draw_instructions(self):
        """
        Test drawing instructions doesn't crash.
        """
        # Test rendering instructions
        try:
            self.ui.draw_instructions(self.screen)
            instructions_render_ok = True
        except Exception as e:
            instructions_render_ok = False
        
        self.assertTrue(instructions_render_ok)
    
    def test_draw_debug_info(self):
        """
        Test drawing debug info with and without enemy doesn't crash.
        """
        # Test with enemy
        try:
            self.ui.draw_debug_info(self.screen, self.player, self.enemy)
            with_enemy_ok = True
        except Exception as e:
            with_enemy_ok = False
        
        self.assertTrue(with_enemy_ok)
        
        # Test without enemy
        try:
            self.ui.draw_debug_info(self.screen, self.player)
            without_enemy_ok = True
        except Exception as e:
            without_enemy_ok = False
        
        self.assertTrue(without_enemy_ok)

if __name__ == '__main__':
    unittest.main()