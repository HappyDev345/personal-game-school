"""
Test module for enemy class.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from characters.enemy import Enemy
from characters.warrior import Warrior
from assets.asset_loader import AssetLoader


class ConcreteEnemy(Enemy):
    """Concrete Enemy subclass for testing (Enemy is abstract)."""

    def take_damage(self, amount):
        return super().take_damage(amount)


class TestEnemy(unittest.TestCase):
    """
    Test case for the Enemy class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create dummy animation frames for enemy
        self.enemy_frames = {
            "idle": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(4)],
            "attack": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(6)],
            "hurt": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(4)],
            "death": [pygame.Surface((90, 115), pygame.SRCALPHA) for _ in range(8)]
        }
        
        # Create a test enemy (using ConcreteEnemy since Enemy is abstract)
        self.enemy = ConcreteEnemy(200, 200, self.enemy_frames)
        
        # Create dummy animation frames for player
        self.player_idle_frames = [pygame.Surface((100, 125), pygame.SRCALPHA) for _ in range(4)]
        self.player_attack_frames = [pygame.Surface((120, 145), pygame.SRCALPHA) for _ in range(6)]
        
        # Create a test player (knight)
        self.player = Warrior(100, 100, self.player_idle_frames, self.player_attack_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_enemy_initialization(self):
        """
        Test enemy initialisation.
        """
        self.assertEqual(self.enemy.x, 200)
        self.assertEqual(self.enemy.y, 200)
        self.assertEqual(self.enemy.max_health, 50)
        self.assertEqual(self.enemy.health, 50)
        self.assertEqual(self.enemy.speed, 1)
        self.assertEqual(self.enemy.attack_damage, 10)
        self.assertEqual(self.enemy.attack_range, 80)
        self.assertEqual(self.enemy.aggro_range, 200)
        self.assertEqual(self.enemy.state, "idle")
        self.assertTrue(self.enemy.is_alive())
        self.assertFalse(self.enemy.is_dying)
    
    def test_take_damage(self):
        """
        Test taking damage.
        """
        # Test enemy takes damage
        result = self.enemy.take_damage(20)
        self.assertEqual(self.enemy.health, 30)
        self.assertFalse(result)  # Enemy is still alive
        self.assertEqual(self.enemy.state, "hurt")
        
        # Test enemy takes lethal damage
        result = self.enemy.take_damage(50)
        self.assertEqual(self.enemy.health, 0)
        self.assertTrue(result)  # Enemy died
        self.assertEqual(self.enemy.state, "death")
        self.assertTrue(self.enemy.is_dying)
    
    def test_is_alive(self):
        """
        Test if enemy is alive.
        """
        self.assertTrue(self.enemy.is_alive())
        
        # Make enemy dying
        self.enemy.is_dying = True
        self.assertFalse(self.enemy.is_alive())
        
        # Reset and take enough damage to be defeated
        self.enemy.is_dying = False
        self.enemy.take_damage(100)
        self.assertEqual(self.enemy.health, 0)
        self.assertFalse(self.enemy.is_alive())
    
    def test_enemy_movement(self):
        """
        Test enemy movement.
        """
        # Position player in aggro range but not in attack range
        self.player.x = self.enemy.x + 120
        self.player.y = self.enemy.y
        self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
        self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
        
        # Original enemy position
        original_x = self.enemy.x
        original_y = self.enemy.y
        
        # Update enemy
        self.enemy.update(self.player)
        
        # Enemy should move toward player
        self.assertNotEqual(self.enemy.x, original_x)
        self.assertNotEqual(self.enemy.y, original_y)
        
        # Check if enemy gets closer to player
        dx = self.player.hitbox.centerx - self.enemy.hitbox.centerx
        dy = self.player.hitbox.centery - self.enemy.hitbox.centery
        
        # Check if the enemy moved in the correct direction
        if dx > 0:
            self.assertGreater(self.enemy.x, original_x)
        elif dx < 0:
            self.assertLess(self.enemy.x, original_x)
            
        if dy > 0:
            self.assertGreater(self.enemy.y, original_y)
        elif dy < 0:
            self.assertLess(self.enemy.y, original_y)
    
    def test_enemy_attack(self):
        """
        Test enemy attack.
        """
        # Position player in attack range
        self.player.x = self.enemy.x + 20
        self.player.y = self.enemy.y
        self.player.hitbox.x = self.player.x + self.player.hitbox_offset_x
        self.player.hitbox.y = self.player.y + self.player.hitbox_offset_y
        
        # Set last attack time far in the past
        self.enemy.last_attack_time = 0
        
        # Update enemy
        self.enemy.update(self.player)
        
        # Enemy should enter attack state
        self.assertEqual(self.enemy.state, "attack")
        
        # Manually force the enemy to complete its attack animation
        # by setting current_frame to the end of the attack animation
        self.enemy.animation_start_time = time.time() - 10  # Set a time in the past
        self.enemy.current_frame = len(self.enemy.frames["attack"]) - 1
        
        # Update one more time to trigger state change
        self.enemy.update(self.player)
        
        # Enemy should have returned to idle state
        self.assertEqual(self.enemy.state, "idle")
    
    def test_death_animation(self):
        """
        Test enemy death animation.
        """
        # Kill the enemy
        self.enemy.take_damage(100)
        
        # Enemy should be dying and in death state
        self.assertTrue(self.enemy.is_dying)
        self.assertEqual(self.enemy.state, "death")
        
        # Initial death frame
        self.assertEqual(self.enemy.current_frame, 0)
        
        # Update to advance death animation
        for _ in range(10):
            self.enemy.update(self.player)
        
        # Death frame should advance but not complete
        self.assertGreater(self.enemy.current_frame, 0)
        self.assertLess(self.enemy.current_frame, len(self.enemy_frames["death"]))
        
        # Directly set the death timer to force the animation to complete
        self.enemy.death_timer = 10  # Large enough to ensure we're at the end of the animation
        self.enemy.update(self.player)
        
        # Death animation should be on the last frame
        self.assertEqual(self.enemy.current_frame, len(self.enemy_frames["death"]) - 1)

if __name__ == '__main__':
    unittest.main()