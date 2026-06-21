"""
Base GameObject class module.

This module contains the base GameObject class that all game objects inherit from.
"""

import pygame
from abc import ABC, abstractmethod


class GameObject(ABC):
    """Base class for all game objects."""

    # Constants
    # (Defined by subclasses)

    # Attributes

    x = None
    y = None
    width = None
    height = None
    hitbox = None

    # Constructor

    def __init__(self, x, y, width, height):
        """
        Initialise a game object.

        Args:
            x (int): X-coordinate of the object.
            y (int): Y-coordinate of the object.
            width (int): Width of the object's hitbox.
            height (int): Height of the object's hitbox.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(x, y, width, height)

    # Accessors

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def collides_with(self, other):
        """
        Check if this object collides with another object.

        Args:
            other (GameObject): The other game object to check collision with.

        Returns:
            bool: True if the objects collide, False otherwise.
        """
        return self.hitbox.colliderect(other.hitbox)

    # Mutators

    def set_x(self, new_x):
        self.x = new_x

    def set_y(self, new_y):
        self.y = new_y

    def set_width(self, new_width):
        self.width = new_width

    def set_height(self, new_height):
        self.height = new_height

    # Behaviours

    def update(self):
        """
        Update the object state.

        This method should be overridden by subclasses.
        """
        # Move hitbox with position
        self.hitbox.x = self.x
        self.hitbox.y = self.y

    @abstractmethod
    def draw(self, screen):
        """
        Draw the object.

        This method must be implemented by subclasses.

        Args:
            screen: The pygame surface to draw on.
        """
        pass
