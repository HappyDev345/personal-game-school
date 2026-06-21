#!/usr/bin/env python3
"""
Main entry point for the Dungeon Game.

This module initialises and runs the game.

Usage:
  python main.py
"""

import pygame
import sys
from core.game import Game


def main():
    """Initialise and run the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
