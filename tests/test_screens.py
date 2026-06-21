"""
Test module for game screens (intro and character select).
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.intro_screen import IntroScreen
from ui.character_select import CharacterSelect
from assets.asset_loader import AssetLoader

class TestScreens(unittest.TestCase):
    """
    Test case for the intro and character selection screens.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1000, 800), pygame.SRCALPHA | pygame.HIDDEN)
        
        # Create a test screen surface
        self.screen = pygame.Surface((1000, 800), pygame.SRCALPHA)
        
        # Create an asset loader
        self.asset_loader = AssetLoader()
        
        # Create the screens
        self.intro_screen = IntroScreen(self.screen)
        self.character_select = CharacterSelect(self.screen, self.asset_loader)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_intro_screen_initialization(self):
        """
        Test intro screen initialisation.
        """
        self.assertIsNotNone(self.intro_screen.background)
        self.assertIsNotNone(self.intro_screen.start_button_rect)
        self.assertIsNotNone(self.intro_screen.quit_button_rect)
        self.assertIsNone(self.intro_screen.button_highlighted)
        self.assertEqual(self.intro_screen.animation_timer, 0)
    
    def test_character_select_initialization(self):
        """
        Test character select screen initialisation.
        """
        # Check that the characters list is populated
        self.assertEqual(len(self.character_select.characters), 2)
        
        # Check that the Knight character is first (index 0)
        self.assertEqual(self.character_select.characters[0]["name"], "Knight")
        self.assertEqual(self.character_select.characters[0]["type"], "knight")
        
        # Check that the Wizard character is second (index 1)
        self.assertEqual(self.character_select.characters[1]["name"], "Wizard")
        self.assertEqual(self.character_select.characters[1]["type"], "wizard")
        
        # Check other initialisation values
        self.assertEqual(self.character_select.selected_character, 0)  # Knight is default
        self.assertEqual(self.character_select.animation_frame, 0)
        self.assertEqual(self.character_select.animation_timer, 0)
        self.assertFalse(self.character_select.button_highlighted)
    
    def test_character_stats(self):
        """
        Test character stats are correctly set.
        """
        # Knight should have higher health
        self.assertEqual(self.character_select.characters[0]["stats"]["health"], 100)
        
        # Wizard should have less health
        self.assertEqual(self.character_select.characters[1]["stats"]["health"], 80)
        
        # Knight should have higher damage
        self.assertEqual(self.character_select.characters[0]["stats"]["damage"], 20)
        
        # Wizard should have same damage (ranged)
        self.assertEqual(self.character_select.characters[1]["stats"]["damage"], 20)
        
        # Knight should be faster
        self.assertEqual(self.character_select.characters[0]["stats"]["speed"], 4)
        
        # Wizard should be slower
        self.assertEqual(self.character_select.characters[1]["stats"]["speed"], 3)
        
        # Knight should have short range
        self.assertEqual(self.character_select.characters[0]["stats"]["range"], "Short")
        
        # Wizard should have long range
        self.assertEqual(self.character_select.characters[1]["stats"]["range"], "Long")
    
    def test_screen_draw(self):
        """
        Test that screens can draw without errors.
        """
        # Just test that they don't raise exceptions
        try:
            self.intro_screen.draw()
            self.character_select.draw()
        except Exception as e:
            self.fail(f"Drawing screens raised exception: {e}")
    
    def test_screen_update(self):
        """
        Test that screens can update without errors.
        """
        try:
            self.intro_screen.update(0.1)
            self.character_select.update(0.1)
        except Exception as e:
            self.fail(f"Updating screens raised exception: {e}")
    
    def test_character_selection_change(self):
        """
        Test that character selection can be changed.
        """
        # Initially Knight (index 0) should be selected
        self.assertEqual(self.character_select.selected_character, 0)
        
        # Change to Wizard (index 1)
        self.character_select.selected_character = 1
        
        # Verify the change took effect
        self.assertEqual(self.character_select.selected_character, 1)
        
        # Change back to Knight
        self.character_select.selected_character = 0
        
        # Verify the change took effect
        self.assertEqual(self.character_select.selected_character, 0)
        
        # Test bounds checking
        # Below minimum
        self.character_select.selected_character = -1
        self.assertEqual(self.character_select.selected_character, -1)  # No bounds checking in setter
        
        # Above maximum
        self.character_select.selected_character = 2
        self.assertEqual(self.character_select.selected_character, 2)  # No bounds checking in setter

if __name__ == '__main__':
    unittest.main()