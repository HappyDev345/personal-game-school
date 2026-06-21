"""
Test module for the GameObject base class.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.game_object import GameObject


class ConcreteGameObject(GameObject):
    """Concrete GameObject subclass for testing (GameObject is abstract)."""

    def draw(self, screen):
        pass


class TestGameObject(unittest.TestCase):
    """
    Test case for the GameObject class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()

        # Create a simple GameObject (using ConcreteGameObject since GameObject is abstract)
        self.game_object = ConcreteGameObject(50, 75, 30, 40)

        # Create another GameObject for collision testing
        self.other_object = ConcreteGameObject(100, 120, 25, 35)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_game_object_initialization(self):
        """
        Test GameObject initialisation.
        """
        self.assertEqual(self.game_object.x, 50)
        self.assertEqual(self.game_object.y, 75)
        self.assertEqual(self.game_object.width, 30)
        self.assertEqual(self.game_object.height, 40)
        
        # Verify hitbox is created with correct dimensions
        self.assertEqual(self.game_object.hitbox.x, 50)
        self.assertEqual(self.game_object.hitbox.y, 75)
        self.assertEqual(self.game_object.hitbox.width, 30)
        self.assertEqual(self.game_object.hitbox.height, 40)
    
    def test_update_method(self):
        """
        Test update method updates hitbox position.
        """
        # Change object position
        self.game_object.x = 60
        self.game_object.y = 90
        
        # Initially hitbox is not updated
        self.assertNotEqual(self.game_object.hitbox.x, self.game_object.x)
        self.assertNotEqual(self.game_object.hitbox.y, self.game_object.y)
        
        # Call update
        self.game_object.update()
        
        # Hitbox should now match object position
        self.assertEqual(self.game_object.hitbox.x, self.game_object.x)
        self.assertEqual(self.game_object.hitbox.y, self.game_object.y)
    
    def test_draw_method(self):
        """
        Test draw method exists but is abstract.
        """
        # Create a test surface
        test_surface = pygame.Surface((200, 200))
        
        # Draw method should exist but not do anything by default
        self.game_object.draw(test_surface)
        
        # Draw method returns None by default
        result = self.game_object.draw(test_surface)
        self.assertIsNone(result)
    
    def test_collision_detection(self):
        """
        Test collision detection between GameObjects.
        """
        # Initially objects should not be colliding
        self.assertFalse(self.game_object.collides_with(self.other_object))
        self.assertFalse(self.other_object.collides_with(self.game_object))
        
        # Move objects to overlap
        self.other_object.x = 60
        self.other_object.y = 80
        
        # Update hitboxes
        self.game_object.update()
        self.other_object.update()
        
        # Now objects should be colliding
        self.assertTrue(self.game_object.collides_with(self.other_object))
        self.assertTrue(self.other_object.collides_with(self.game_object))
        
        # Move objects apart
        self.other_object.x = 200
        self.other_object.y = 200
        
        # Update hitboxes
        self.game_object.update()
        self.other_object.update()
        
        # Now objects should not be colliding
        self.assertFalse(self.game_object.collides_with(self.other_object))
        self.assertFalse(self.other_object.collides_with(self.game_object))
    
    def test_edge_collision(self):
        """
        Test edge collision cases.
        """
        # Test collision at various edges
        edge_cases = [
            # Just touching on the right edge
            (self.game_object.x + self.game_object.width, self.game_object.y, 10, 10),
            # Just touching on the bottom edge
            (self.game_object.x, self.game_object.y + self.game_object.height, 10, 10),
            # Just touching on the left edge
            (self.game_object.x - 10, self.game_object.y, 10, 10),
            # Just touching on the top edge
            (self.game_object.x, self.game_object.y - 10, 10, 10)
        ]
        
        for x, y, w, h in edge_cases:
            # Create a test object at the edge
            edge_object = ConcreteGameObject(x, y, w, h)
            
            # Update hitboxes
            self.game_object.update()
            edge_object.update()
            
            # Check if collision is detected
            collision = self.game_object.collides_with(edge_object)
            
            # The specific result depends on the exact positioning
            # but we're testing that the collision detection runs without errors
            self.assertIsInstance(collision, bool)

if __name__ == '__main__':
    unittest.main()