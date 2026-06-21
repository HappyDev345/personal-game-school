"""
Test module for trap class.
"""

import unittest
import pygame
import sys
import os
import time

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from objects.trap import Trap
from characters.warrior import Warrior
from core.map import TILE_SIZE

class TestTrap(unittest.TestCase):
    """
    Test case for the Trap class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        # Use the dummy video driver to prevent a visible window during testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Create simple surfaces for inactive and active trap images
        self.inactive_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.inactive_image.fill((100, 100, 100, 255))
        
        self.active_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.active_image.fill((200, 0, 0, 255))
        
        # Create a test trap
        self.trap = Trap(100, 100, self.inactive_image, self.active_image)
        
        # Create dummy animation frames for player
        self.player_idle_frames = [pygame.Surface((100, 125), pygame.SRCALPHA) for _ in range(4)]
        self.player_attack_frames = [pygame.Surface((120, 145), pygame.SRCALPHA) for _ in range(6)]
        
        # Create a test player
        self.player = Warrior(50, 50, self.player_idle_frames, self.player_attack_frames)
    
    def tearDown(self):
        """
        Clean up test fixtures.
        """
        pygame.quit()
    
    def test_trap_initialization(self):
        """
        Test trap initialisation.
        """
        self.assertEqual(self.trap.x, 100)
        self.assertEqual(self.trap.y, 100)
        self.assertEqual(self.trap.width, TILE_SIZE)
        self.assertEqual(self.trap.height, TILE_SIZE)
        self.assertEqual(self.trap.damage, 10)
        self.assertFalse(self.trap.was_triggered)
        self.assertEqual(self.trap.trigger_cooldown, 3.0)
        
        # Check new attributes
        self.assertFalse(self.trap.is_active)  # Traps start inactive (spikes down)
        self.assertIsNotNone(self.trap.cycle_time)  # Should have a cycle time
        self.assertIsNotNone(self.trap.cycle_start)  # Should have a cycle start time
        self.assertIsNotNone(self.trap.active_duration)  # Should have active duration
        self.assertEqual(self.trap.shake_intensity, 0)  # No shake initially
    
    def test_trigger(self):
        """
        Test triggering trap.
        """
        # Initial player health
        initial_health = self.player.health
        
        # Set the trap to active state (spikes up)
        self.trap.is_active = True
        
        # Trigger the trap
        damage = self.trap.trigger(self.player)
        
        # Verify trap was triggered and damage was dealt
        self.assertTrue(self.trap.was_triggered)
        self.assertEqual(damage, 10)
        self.assertEqual(self.player.health, initial_health - 10)
        
        # Try to trigger again immediately (should fail)
        damage = self.trap.trigger(self.player)
        self.assertEqual(damage, 0)  # No damage when already triggered
    
    def test_trap_cooldown(self):
        """
        Test trap cooldown.
        """
        # Set trap to active state
        self.trap.is_active = True
        
        # Trigger the trap
        self.trap.trigger(self.player)
        self.assertTrue(self.trap.was_triggered)
        
        # Manually reset the triggered time to simulate time passage
        self.trap.triggered_time = time.time() - 4.0  # Past the cooldown period
        
        # Update trap to reset it
        self.trap.update()
        
        # Should be able to trigger again
        self.assertFalse(self.trap.was_triggered)
        
        # Make sure trap is still active
        self.trap.is_active = True
        
        # Trigger again
        damage = self.trap.trigger(self.player)
        self.assertTrue(self.trap.was_triggered)
        self.assertEqual(damage, 10)
    
    def test_trap_visibility(self):
        """
        Test trap visibility states.
        """
        # Set visibility explicitly for testing
        self.trap.is_visible = False
        
        # Make trap active for triggering
        self.trap.is_active = True
        
        # Triggering should make trap visible
        self.trap.trigger(self.player)
        
        # Visibility should not be affected by triggering anymore (removed from trigger method)
        # Instead, visibility is set in game.py when player steps on the trap
        # This test now just confirms trap remains in the state we set it to
        self.assertFalse(self.trap.is_visible)
    
    def test_animation_effects(self):
        """
        Test trap animation effects.
        """
        # Make trap active for triggering
        self.trap.is_active = True
        
        # Trigger the trap
        self.trap.trigger(self.player)
        
        # Shake effect should be active immediately after triggering
        # We can test that the start_shake method was called by checking if shake_intensity is non-zero
        self.assertGreater(self.trap.shake_intensity, 0)
        
        # After shake duration, offsets should return to zero
        # Fast-forward time
        self.trap.shake_start_time = time.time() - 0.5  # Past shake duration
        self.trap.update()
        self.assertEqual(self.trap.shake_offset, [0, 0])
        self.assertEqual(self.trap.shake_intensity, 0)
    
    def test_player_null_safety(self):
        """
        Test trap handles null player safely.
        """
        # Make trap active
        self.trap.is_active = True
        
        # Should not crash when player is None
        damage = self.trap.trigger(None)
        self.assertEqual(damage, 0)
        self.assertTrue(self.trap.was_triggered)
        
    def test_trap_active_inactive(self):
        """
        Test trap only damages when active (spikes up).
        """
        # Set trap to inactive state (spikes down)
        self.trap.is_active = False
        
        # Get initial player health
        initial_health = self.player.health
        
        # Trigger the trap while inactive (should not cause damage)
        damage = self.trap.trigger(self.player)
        
        # Verify no damage was dealt and trap was not triggered
        self.assertEqual(damage, 0)
        self.assertEqual(self.player.health, initial_health)  # Health unchanged
        self.assertFalse(self.trap.was_triggered)  # Trap not marked as triggered
        
        # Now set trap to active and try again
        self.trap.is_active = True
        damage = self.trap.trigger(self.player)
        
        # Verify damage was dealt and trap was triggered
        self.assertEqual(damage, 10)
        self.assertEqual(self.player.health, initial_health - 10)
        self.assertTrue(self.trap.was_triggered)
        
    def test_trap_cycling(self):
        """
        Test trap cycling between active and inactive states.
        """
        # Set up a controlled cycle time for testing
        self.trap.cycle_time = 2.0  # 2 second cycle
        self.trap.active_duration = 1.0  # 1 second active
        
        # Set cycle to just start (spikes should be up)
        current_time = time.time()
        self.trap.cycle_start = current_time - 0.5  # 0.5 seconds into cycle
        
        # Update trap - should be active (spikes up)
        self.trap.update()
        self.assertTrue(self.trap.is_active)
        
        # Fast forward to inactive phase
        self.trap.cycle_start = current_time - 1.5  # 1.5 seconds into cycle (past active_duration)
        
        # Update trap - should be inactive (spikes down)
        self.trap.update()
        self.assertFalse(self.trap.is_active)

if __name__ == '__main__':
    unittest.main()