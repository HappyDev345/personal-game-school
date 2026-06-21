"""
Map module.

This module contains functionality for generating and rendering the game map.
"""

import pygame
import random

# Tile settings
TILE_SIZE = 50
MAP_WIDTH = 20
MAP_HEIGHT = 16

# Map legend:
# 0 - Floor
# 1 - Wall
# 2 - Start position (Level 1 only)
# 3 - Exit portal

# Maps for different levels
MAPS = [
    # Level 1 - Simple straight path to portal
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # Level 2 - Path with some obstacles
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # Level 3 - Winding path with more obstacles
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
]

def determine_wall_type(x, y, game_map):
    """
    Determine the appropriate wall tile type based on surrounding tiles.
    
    Args:
        x (int): X coordinate in the map.
        y (int): Y coordinate in the map.
        game_map (list): The game map data.
        
    Returns:
        int: Index to use from the wall tile set (0-7).
    """
    # Check the 4 adjacent tiles: N, E, S, W
    n = y > 0 and game_map[y-1][x] == 1  # North is wall
    s = y < len(game_map)-1 and game_map[y+1][x] == 1  # South is wall
    e = x < len(game_map[0])-1 and game_map[y][x+1] == 1  # East is wall
    w = x > 0 and game_map[y][x-1] == 1  # West is wall
    
    # Also check non-wall tiles (for outer corners)
    n_floor = y > 0 and game_map[y-1][x] != 1  # North is floor or other non-wall
    s_floor = y < len(game_map)-1 and game_map[y+1][x] != 1  # South is floor
    e_floor = x < len(game_map[0])-1 and game_map[y][x+1] != 1  # East is floor
    w_floor = x > 0 and game_map[y][x-1] != 1  # West is floor
    
    # Check diagonal tiles for better corner detection
    nw_floor = y > 0 and x > 0 and game_map[y-1][x-1] != 1  # Northwest is floor
    ne_floor = y > 0 and x < len(game_map[0])-1 and game_map[y-1][x+1] != 1  # Northeast is floor
    sw_floor = y < len(game_map)-1 and x > 0 and game_map[y+1][x-1] != 1  # Southwest is floor
    se_floor = y < len(game_map)-1 and x < len(game_map[0])-1 and game_map[y+1][x+1] != 1  # Southeast is floor
    
    # Detect outer corners (walls with adjacent floor on two sides)
    # Use the new angle corner assets (indices 4-7)
    
    # Top-left outer corner (wall on south and east, floor on north and west)
    if s and e and n_floor and w_floor and nw_floor:
        return 4  # Top-left angle asset
    
    # Top-right outer corner (wall on south and west, floor on north and east)
    elif s and w and n_floor and e_floor and ne_floor:
        return 5  # Top-right angle asset
    
    # Bottom-left outer corner (wall on north and east, floor on south and west)
    elif n and e and s_floor and w_floor and sw_floor:
        return 6  # Bottom-left angle asset
    
    # Bottom-right outer corner (wall on north and west, floor on south and east)
    elif n and w and s_floor and e_floor and se_floor:
        return 7  # Bottom-right angle asset
    else:
        # Calculate number of connections in each direction
        h_connections = (1 if e else 0) + (1 if w else 0)  # Horizontal connections
        v_connections = (1 if n else 0) + (1 if s else 0)  # Vertical connections

        # Determine if this wall is horizontal or vertical
        is_horizontal = False
        if h_connections + v_connections == 1:
            # End piece with one connection
            is_horizontal = (e or w)
        elif h_connections > v_connections:
            is_horizontal = True
        elif v_connections > h_connections:
            is_horizontal = False
        else:
            # Equal connections — check for horizontal run
            if e and w:
                is_horizontal = True
            elif (e and x+2 < len(game_map[0]) and game_map[y][x+2] == 1) or \
                 (w and x-2 >= 0 and game_map[y][x-2] == 1):
                is_horizontal = True

        # Pick the correct facing based on which side has floor
        if is_horizontal:
            # Floor to the south → top wall (face down), floor to the north → bottom wall (face up)
            if s_floor and not n_floor:
                return 0  # Top wall (floor below)
            elif n_floor and not s_floor:
                return 2  # Bottom wall (floor above)
            else:
                return 0  # Default horizontal
        else:
            # Floor to the east → left wall (face right), floor to the west → right wall (face left)
            if e_floor and not w_floor:
                return 3  # Left wall (floor to the right)
            elif w_floor and not e_floor:
                return 1  # Right wall (floor to the left)
            else:
                return 1  # Default vertical

def generate_map_with_variations(level_map):
    """
    Generate a map with tile variations.
    
    Args:
        level_map (list): The level map data.
        
    Returns:
        list: 2D array of tile variant indices.
    """
    # Create a 2D array to store tile variant indices
    tile_map = []
    
    # Coherent patterns for floor tiles - use patterns rather than pure randomness
    floor_patterns = [
        # Checkered pattern
        [[0, 1], [2, 3]],
        # Line pattern
        [[0, 1], [0, 1]],
        # Random but consistent pattern
        [[2, 2], [3, 3]]
    ]
    
    # Choose one pattern for the floor
    floor_pattern = random.choice(floor_patterns)
    pattern_size = 2  # 2x2 patterns
    
    # First pass: Determine all wall variants based on surrounding tiles
    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            if level_map[y][x] == 1:  # Wall tile
                # Determine wall type based on surrounding tiles
                variant = determine_wall_type(x, y, level_map)
            else:  # Floor, start or exit tile
                # Apply coherent pattern for floor-like tiles
                pattern_x = (x // pattern_size) % 2
                pattern_y = (y // pattern_size) % 2
                variant = floor_pattern[pattern_y][pattern_x]
                
            row.append(variant)
        tile_map.append(row)
    
    return tile_map

class GameMap:
    """Represents the game map with tiles."""
    
    def __init__(self, asset_loader, level=0):
        """
        Initialise the game map.
        
        Args:
            asset_loader: The asset loader to get tile images.
            level (int): The level number to load (0-indexed).
        """
        self.asset_loader = asset_loader
        self.level = level
        self.current_map = MAPS[level]
        self.tile_variations = generate_map_with_variations(self.current_map)
        self.find_player_start_position()
        self.find_exit_position()
    
    def find_player_start_position(self):
        """
        Find the starting position for the player based on the map.
        
        Returns:
            tuple: (x, y) coordinates or None if not found.
        """
        self.start_position = None
        
        # For level 1, look for position 2 (start)
        if self.level == 0:
            for y in range(len(self.current_map)):
                for x in range(len(self.current_map[y])):
                    if self.current_map[y][x] == 2:
                        self.start_position = (x * TILE_SIZE, y * TILE_SIZE)
                        return
        
        # For other levels, use a safer position finding approach
        if self.start_position is None:
            # Find a good floor tile that isn't surrounded by walls
            safe_positions = []
            
            # Scan the map for good positions (floor tiles with open space around them)
            for y in range(1, len(self.current_map) - 1):
                for x in range(1, len(self.current_map[y]) - 1):
                    # Check if this is a floor tile
                    if self.current_map[y][x] == 0:
                        # Check that there's at least a 3x3 area of non-wall tiles
                        open_area = True
                        for check_y in range(y-1, y+2):
                            for check_x in range(x-1, x+2):
                                if self.current_map[check_y][check_x] == 1:
                                    open_area = False
                                    break
                            if not open_area:
                                break
                                
                        if open_area:
                            # This is a good position with open space around it
                            safe_positions.append((x, y))
            
            # If we found any safe positions, pick one (preferably closer to the centre)
            if safe_positions:
                # Sort by distance from centre
                center_x, center_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
                safe_positions.sort(key=lambda pos: abs(pos[0] - center_x) + abs(pos[1] - center_y))
                best_pos = safe_positions[0]
                self.start_position = (best_pos[0] * TILE_SIZE, best_pos[1] * TILE_SIZE)
                return
            
            # If no good positions were found, use level-specific hardcoded positions that are known to be safe
            if self.level == 1:  # Level 2
                # Hard-coded safe position for level 2 (verified) - now with plenty of room
                self.start_position = (TILE_SIZE * 1, TILE_SIZE * 1)  # Top-left open area (1,1) with large open space
            elif self.level == 2:  # Level 3
                # Hard-coded safe position for level 3 (verified)
                self.start_position = (TILE_SIZE * 1, TILE_SIZE * 1)  # Top-left open area (1,1)
            else:
                # Default fallback
                # Check multiple possible positions until we find one that isn't a wall
                for test_x, test_y in [(2, 2), (1, 1), (3, 3), (4, 4), (5, 5)]:
                    if self.current_map[test_y][test_x] == 0:  # If it's a floor
                        self.start_position = (TILE_SIZE * test_x, TILE_SIZE * test_y)
                        return
                
                # If all else fails, use a hardcoded position
                self.start_position = (TILE_SIZE * 1, TILE_SIZE * 1)
    
    def find_exit_position(self):
        """
        Find the exit portal position based on the map.
        
        Returns:
            tuple: (x, y) coordinates or None if not found.
        """
        self.exit_position = None
        
        for y in range(len(self.current_map)):
            for x in range(len(self.current_map[y])):
                if self.current_map[y][x] == 3:
                    self.exit_position = (x * TILE_SIZE, y * TILE_SIZE)
                    return
        
        # If no exit is defined, use a default position
        if self.exit_position is None:
            self.exit_position = (TILE_SIZE * (MAP_WIDTH - 2), TILE_SIZE * (MAP_HEIGHT - 2))
    
    def change_level(self, new_level):
        """
        Change to a new level.
        
        Args:
            new_level (int): The level number to change to.
            
        Returns:
            bool: True if level changed successfully, False otherwise.
        """
        if new_level < 0 or new_level >= len(MAPS):
            return False
            
        self.level = new_level
        self.current_map = MAPS[new_level]
        self.tile_variations = generate_map_with_variations(self.current_map)
        self.find_player_start_position()
        self.find_exit_position()
        return True
    
    def get_player_start_position(self):
        """
        Get the starting position for the player.
        
        Returns:
            tuple: (x, y) coordinates.
        """
        return self.start_position
    
    def get_exit_position(self):
        """
        Get the exit portal position.
        
        Returns:
            tuple: (x, y) coordinates.
        """
        return self.exit_position
    
    def is_wall(self, tile_x, tile_y):
        """
        Check if a tile is a wall.
        
        Args:
            tile_x (int): X coordinate in tiles.
            tile_y (int): Y coordinate in tiles.
            
        Returns:
            bool: True if the tile is a wall, False otherwise.
        """
        if (tile_x < 0 or tile_x >= MAP_WIDTH or 
            tile_y < 0 or tile_y >= MAP_HEIGHT):
            return True  # Out of bounds is considered a wall
            
        return self.current_map[tile_y][tile_x] == 1
    
    def draw(self, screen):
        """
        Draw the map with tile variations.
        
        Args:
            screen: The pygame surface to draw on.
        """
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_type = self.current_map[y][x]
                
                if tile_type == 1:  # Wall
                    screen.blit(self.asset_loader.get_tile("wall", self.tile_variations[y][x]), rect)
                else:  # Floor, start or exit
                    screen.blit(self.asset_loader.get_tile("floor", self.tile_variations[y][x]), rect)