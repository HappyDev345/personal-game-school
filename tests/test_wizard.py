"""
Test module for wizard character.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from characters.wizard import Wizard
from characters.projectile import Projectile
from characters.enemy import Enemy
from assets.asset_loader import AssetLoader


class ConcreteEnemy(Enemy):
    """Concrete Enemy subclass for testing (Enemy is abstract)."""

    def take_damage(self, amount):
        return super().take_damage(amount)


class MockGameMap:
    """Mock game map for testing."""
    
    def __init__(self):
        # Import for testing
        from core.map import TILE_SIZE
        self.tile_size = TILE_SIZE
        
    def is_wall(self, x, y):
        """Check if the given tile is a wall."""
        # Simple test - everything beyond x=10 is a wall
        # Ensure we're handling int values
        x = int(x)
        y = int(y)
        return x > 10

class TestWizard(unittest.TestCase):
    """
    Test case for the Wizard class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Initialise pygame with the NOFRAME flag to prevent visible windows during tests
        pygame.init()
        # Use pygame.HIDDEN or pygame.NOFRAME to prevent a visible window
        # Or use a dummy environment variable
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.set_mode((1000, 800), pygame.SRCALPHA | pygame.HIDDEN)
        
        # Create dummy animation frames
        self.idle_frames = [pygame.Surface((100, 125), pygame.SRCALPHA) for _ in range(4)]
        self.attack_frames = [pygame.Surface((120, 145), pygame.SRCALPHA) for _ in range(6)]
        
        # Create a test wizard
        self.wizard = Wizard(100, 100, self.idle_frames, self.attack_frames)
        
        # Create a mock game map
        self.game_map = MockGameMap()
        self.wizard.game_map = self.game_map
        
        # Create enemy frames for test enemies
        self.enemy_frames = {
            "idle": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(4)],
            "attack": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(6)],
            "hurt": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(4)],
            "death": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(8)]
        }
        
        # Create test enemies
        self.enemies = [
            ConcreteEnemy(200, 100, self.enemy_frames),
            ConcreteEnemy(300, 150, self.enemy_frames)
        ]
        
        # Add game map to enemies
        for enemy in self.enemies:
            enemy.game_map = self.game_map
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_wizard_initialization(self):
        """
        Test wizard initialisation.
        """
        self.assertEqual(self.wizard.x, 100)
        self.assertEqual(self.wizard.y, 100)
        self.assertEqual(self.wizard.max_health, 80)  # Wizards have less health
        self.assertEqual(self.wizard.health, 80)
        self.assertEqual(self.wizard.speed, 3)  # Wizards are slower
        self.assertEqual(self.wizard.attack_damage, 20)  # Magic does more damage
        self.assertEqual(self.wizard.attack_range, 300)  # Much longer attack range
        self.assertEqual(self.wizard.attack_cooldown, 0.8)  # Longer cooldown
        self.assertEqual(self.wizard.state, "idle")
        self.assertFalse(self.wizard.attacking)
        
        # Check wizard-specific attributes
        self.assertEqual(len(self.wizard.projectiles), 0)
        self.assertEqual(len(self.wizard.magic_particles), 0)
    
    def test_wizard_hitbox_properties(self):
        """
        Test that the wizard's hitbox has the correct properties.
        """
        # Check hitbox dimensions match the computed content rect
        self.assertEqual(self.wizard.hitbox.width, self.wizard.content_rect.width)
        self.assertEqual(self.wizard.hitbox.height, self.wizard.content_rect.height)

        # Check hitbox position follows offset
        self.assertEqual(self.wizard.hitbox.x, self.wizard.x + self.wizard.hitbox_offset_x)
        self.assertEqual(self.wizard.hitbox.y, self.wizard.y + self.wizard.hitbox_offset_y)

        # Check hitbox offsets match content rect position
        self.assertEqual(self.wizard.hitbox_offset_x, self.wizard.content_rect.x)
        self.assertEqual(self.wizard.hitbox_offset_y, self.wizard.content_rect.y)
    
    def test_wizard_hitbox_movement(self):
        """
        Test that the wizard's hitbox moves with the wizard.
        """
        # Record initial position
        initial_hitbox_x = self.wizard.hitbox.x
        initial_hitbox_y = self.wizard.hitbox.y
        
        # Move the wizard
        self.wizard.x += 50
        self.wizard.y += 30
        
        # Update the wizard to reflect movement
        self.wizard.update(self.game_map)
        
        # Hitbox should move by the same amount
        self.assertEqual(self.wizard.hitbox.x, initial_hitbox_x + 50)
        self.assertEqual(self.wizard.hitbox.y, initial_hitbox_y + 30)
    
    def test_particle_rendering_edge_cases(self):
        """
        Test edge cases for particle rendering to ensure colour and size handling is robust.
        """
        # Create a test surface
        test_screen = pygame.Surface((1000, 800))
        
        # Create a projectile
        projectile = Projectile(100, 100, 200, 200, damage=20)
        
        # Test with various problematic colours and sizes
        edge_cases = [
            # Very small size that would cause zero-sized surface
            {'size': 0.1, 'color': (0, 100, 255), 'fade_ratio': 0.01},
            # Invalid colour (tuple with wrong length)
            {'size': 2.0, 'color': (0,), 'fade_ratio': 0.5},
            # Non-tuple colour
            {'size': 2.0, 'color': "blue", 'fade_ratio': 0.5},
            # Negative alpha
            {'size': 2.0, 'color': (0, 100, 255), 'fade_ratio': -0.1},
            # Very large alpha
            {'size': 2.0, 'color': (0, 100, 255), 'fade_ratio': 10.0},
            # Non-integer colour values
            {'size': 2.0, 'color': (0.5, 99.9, 255.1), 'fade_ratio': 0.5},
        ]
        
        # Create the wizard's magic particles with edge cases
        self.wizard.magic_particles = []
        for case in edge_cases:
            self.wizard.magic_particles.append({
                'x': 100,
                'y': 100,
                'size': case['size'],
                'lifetime': 0.5,
                'creation_time': time.time() - 0.1,
                'color': case['color'],
                'speed': 1.0,
                'direction': 0.0
            })
        
        # This should not raise any exceptions
        try:
            self.wizard.draw(test_screen)
            test_passed = True
        except Exception as e:
            test_passed = False
            self.fail(f"Particle rendering raised an exception: {e}")
            
        self.assertTrue(test_passed, "Particle rendering should handle all edge cases without exceptions")
    
    def test_attack_projectile_creation(self):
        """
        Test that attacking creates a projectile.
        """
        # Before attacking, there should be no projectiles
        self.assertEqual(len(self.wizard.projectiles), 0)
        
        # Call the attack method
        self.wizard.attack()
        
        # There should now be one projectile
        self.assertEqual(len(self.wizard.projectiles), 1)
        
        # Projectile should have the wizard's attack damage
        projectile = self.wizard.projectiles[0]
        self.assertEqual(projectile.damage, self.wizard.attack_damage)
    
    def test_attack_targets_closest_enemy(self):
        """
        Test that attack targets the closest enemy when provided.
        """
        # Position enemies at different locations
        self.enemies[0].x = 50  # To the left
        self.enemies[0].hitbox.x = self.enemies[0].x + 33
        self.enemies[1].x = 300  # To the right
        self.enemies[1].hitbox.x = self.enemies[1].x + 33
        
        # Wizard starts facing right
        self.wizard.facing_left = False
        
        # Attack with enemies list
        self.wizard.attack(self.enemies)
        
        # Wizard direction should have changed to left (toward closest enemy)
        self.assertTrue(self.wizard.facing_left)
        
        # Clear projectiles
        self.wizard.projectiles = []
        
        # Now position wizard so enemy[1] is closest
        self.wizard.x = 200
        self.wizard.hitbox.x = self.wizard.x + self.wizard.hitbox_offset_x
        
        # Attack again
        self.wizard.attack(self.enemies)
        
        # Wizard direction should have changed to right (toward closest enemy)
        self.assertFalse(self.wizard.facing_left)
    
    def test_projectile_movement(self):
        """
        Test projectile movement.
        """
        # Create a projectile heading right
        projectile = Projectile(100, 100, 200, 100, damage=20)
        self.wizard.projectiles.append(projectile)
        
        # Record initial position
        initial_x = projectile.x
        
        # Update the projectile
        projectile.update([], self.game_map)
        
        # Projectile should have moved in x direction
        self.assertNotEqual(projectile.x, initial_x)
    
    def test_projectile_lifetime(self):
        """
        Test projectile lifetime expiration.
        """
        # Create a projectile
        projectile = Projectile(100, 100, 200, 100, damage=20)
        self.wizard.projectiles.append(projectile)
        
        # Set its creation time to well in the past
        projectile.creation_time = time.time() - 10
        
        # Update projectile to check for lifetime expiration
        result = projectile.update([], self.game_map)
        
        # Projectile should be marked for removal
        self.assertTrue(result)
    
    def test_attack_range(self):
        """
        Test wizard's attack range differs from knight.
        """
        # Create an enemy within the wizard's special range
        enemy = ConcreteEnemy(350, 100, self.enemy_frames)  # Outside knight range (100) but inside wizard range (300)
        enemy.hitbox.x = enemy.x + 33  # Update hitbox
        
        # Check if enemy is in attack range
        in_range = self.wizard._is_in_attack_range(enemy)
        
        # Should be in range for wizard
        self.assertTrue(in_range)


if __name__ == '__main__':
    unittest.main()