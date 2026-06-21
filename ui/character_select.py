"""
Character Select module.

This module contains the CharacterSelect class for handling the character selection screen.
"""

import pygame
import math
import time
import random
# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

class CharacterSelect:
    """Manages the character selection screen."""

    def __init__(self, screen, asset_loader):
        """
        Initialise the character selection screen.

        Args:
            screen: The pygame surface to draw on.
            asset_loader: The asset loader instance.
        """
        self.screen = screen
        self.asset_loader = asset_loader

        # Create all fonts once in __init__ (not per-frame in draw)
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 44)
        self.font_small = pygame.font.Font(None, 30)
        self.font_tiny = pygame.font.Font(None, 26)

        # Load or create background
        self.background = self._create_background()

        # Card layout calculations
        card_width = 280
        card_height = 420
        card_spacing = 100

        # Centre cards vertically, leaving room for description and button below
        card_y = 120

        # Centre cards horizontally
        total_width = (card_width * 2) + card_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        self.characters = [
            {
                "name": "Knight",
                "type": "knight",
                "description": "Strong melee fighter with high health",
                "stats": {
                    "health": 100,
                    "damage": 20,
                    "speed": 4,
                    "range": "Short"
                },
                "special": "Shield Block",
                "frames": asset_loader.get_player_idle_frames("knight"),
                "color": BLUE,
                "rect": pygame.Rect(start_x, card_y, card_width, card_height)
            },
            {
                "name": "Wizard",
                "type": "wizard",
                "description": "Magic user with ranged attacks",
                "stats": {
                    "health": 80,
                    "damage": 20,
                    "speed": 3,
                    "range": "Long"
                },
                "special": "Projectiles",
                "frames": asset_loader.get_player_idle_frames("wizard"),
                "color": PURPLE,
                "rect": pygame.Rect(start_x + card_width + card_spacing, card_y, card_width, card_height)
            }
        ]

        # Pre-compute crop rects so sprites fill the display circle
        for character in self.characters:
            # Find the union bounding rect across all frames
            union_rect = None
            for frame in character["frames"]:
                bbox = frame.get_bounding_rect()
                if union_rect is None:
                    union_rect = bbox.copy()
                else:
                    union_rect.union_ip(bbox)
            # Add a small margin around the content
            margin = 4
            union_rect.inflate_ip(margin * 2, margin * 2)
            union_rect.clamp_ip(pygame.Rect(0, 0, character["frames"][0].get_width(), character["frames"][0].get_height()))
            character["crop_rect"] = union_rect

        # Selection state
        self.selected_character = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.confirm_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.button_highlighted = False
        self.pulse_timer = 0

    def update(self, dt):
        """
        Update character selection animations.

        Args:
            dt: Time delta in seconds.
        """
        # Update character animation
        self.animation_timer += dt
        if self.animation_timer >= 0.15:
            self.animation_frame = (self.animation_frame + 1) % len(self.characters[self.selected_character]["frames"])
            self.animation_timer = 0

        # Update pulse effect for selected character
        self.pulse_timer += dt * 3

    def _create_background(self):
        """Create a stylish background for the character selection screen."""
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw a gradient from dark grey to deeper grey for stone/dungeon effect
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(40 + 20 * (1 - ratio))
            g = int(40 + 20 * (1 - ratio))
            b = int(50 + 20 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))

        # Add a "stone texture" pattern
        for i in range(200):
            stone_x = random.randint(0, SCREEN_WIDTH)
            stone_y = random.randint(0, SCREEN_HEIGHT)
            stone_size = random.randint(5, 25)

            stone_color = (
                random.randint(45, 75),
                random.randint(45, 75),
                random.randint(55, 85)
            )

            pygame.draw.rect(
                background,
                stone_color,
                (stone_x, stone_y, stone_size, stone_size),
                border_radius=stone_size // 3
            )

            if random.random() > 0.7:
                highlight_color = (
                    min(255, stone_color[0] + 15),
                    min(255, stone_color[1] + 15),
                    min(255, stone_color[2] + 15)
                )
                pygame.draw.rect(
                    background,
                    highlight_color,
                    (stone_x, stone_y, stone_size // 2, stone_size // 2),
                    border_radius=stone_size // 6
                )

        # Torch-like yellow-orange glow in corners
        for corner in [(50, 50), (SCREEN_WIDTH - 50, 50),
                       (50, SCREEN_HEIGHT - 50), (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)]:
            glow_size = 150
            glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            pygame.draw.circle(glow, (100, 70, 0, 30), (glow_size//2, glow_size//2), glow_size//2)
            pygame.draw.circle(glow, (150, 100, 0, 20), (glow_size//2, glow_size//2), glow_size//3)
            pygame.draw.circle(glow, (200, 150, 0, 10), (glow_size//2, glow_size//2), glow_size//4)

            background.blit(glow, (corner[0] - glow_size//2, corner[1] - glow_size//2))

        # Tile border pattern
        tile_size = 20
        border_width = 3

        for x in range(0, SCREEN_WIDTH, tile_size):
            pygame.draw.rect(background, (60, 60, 70),
                           (x, 0, tile_size, tile_size), border_width)
            pygame.draw.rect(background, (60, 60, 70),
                           (x, SCREEN_HEIGHT - tile_size, tile_size, tile_size), border_width)

        for y in range(0, SCREEN_HEIGHT, tile_size):
            pygame.draw.rect(background, (60, 60, 70),
                           (0, y, tile_size, tile_size), border_width)
            pygame.draw.rect(background, (60, 60, 70),
                           (SCREEN_WIDTH - tile_size, y, tile_size, tile_size), border_width)

        # Semi-transparent overlay (lighter so decoration is visible)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        background.blit(overlay, (0, 0))

        return background

    def handle_events(self):
        """
        Handle pygame events for the character selection screen.

        Returns:
            dict or None: Selected character data if confirmed, None otherwise.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_character = max(0, self.selected_character - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_character = min(len(self.characters) - 1, self.selected_character + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.characters[self.selected_character]

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for i, character in enumerate(self.characters):
                    if character["rect"].collidepoint(mouse_pos):
                        self.selected_character = i

                self.button_highlighted = self.confirm_button_rect.collidepoint(mouse_pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.confirm_button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, WHITE, self.confirm_button_rect, border_radius=10)
                    pygame.display.flip()
                    pygame.time.delay(100)
                    return self.characters[self.selected_character]

                for i, character in enumerate(self.characters):
                    if character["rect"].collidepoint(mouse_pos):
                        if self.selected_character == i:
                            return self.characters[self.selected_character]
                        else:
                            self.selected_character = i

        return None

    def draw(self):
        """Draw the character selection screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Draw header
        header_text = self.font_large.render("Select Your Character", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH//2, 55))

        header_bg_rect = header_rect.inflate(40, 16)
        header_bg = pygame.Surface((header_bg_rect.width, header_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(header_bg, (0, 0, 0, 160), (0, 0, header_bg_rect.width, header_bg_rect.height), border_radius=10)
        self.screen.blit(header_bg, header_bg_rect.topleft)
        self.screen.blit(header_text, header_rect)

        # Decorative line under header
        line_y = header_rect.bottom + 5
        line_width = SCREEN_WIDTH // 2
        pygame.draw.line(self.screen, (180, 180, 200),
                      (SCREEN_WIDTH//2 - line_width//2, line_y),
                      (SCREEN_WIDTH//2 + line_width//2, line_y), 2)

        # Draw character cards
        for i, character in enumerate(self.characters):
            is_selected = (i == self.selected_character)
            card_color = character["color"]

            if is_selected:
                pulse = (math.sin(self.pulse_timer) * 0.2) + 0.8
                r = min(255, int(card_color[0] * pulse) + 30)
                g = min(255, int(card_color[1] * pulse) + 30)
                b = min(255, int(card_color[2] * pulse) + 30)
                card_color = (r, g, b)
                border_width = 3
            else:
                border_width = 1

            # Card background
            pygame.draw.rect(self.screen, (20, 20, 30), character["rect"], border_radius=10)
            pygame.draw.rect(self.screen, card_color, character["rect"], border_width + 2, border_radius=10)
            if is_selected:
                pygame.draw.rect(self.screen, WHITE, character["rect"], border_width, border_radius=10)

            # --- Name banner ---
            banner_rect = pygame.Rect(
                character["rect"].left + 6,
                character["rect"].top + 10,
                character["rect"].width - 12,
                40
            )
            banner_bg = pygame.Surface((banner_rect.width, banner_rect.height), pygame.SRCALPHA)
            banner_colour = tuple(list(card_color[:3]) + [200])
            pygame.draw.rect(banner_bg, banner_colour, (0, 0, banner_rect.width, banner_rect.height), border_radius=6)
            self.screen.blit(banner_bg, banner_rect.topleft)

            name_text = self.font_medium.render(character["name"], True, WHITE)
            name_rect = name_text.get_rect(center=banner_rect.center)
            self.screen.blit(name_text, name_rect)

            # --- Character sprite ---
            sprite_top = banner_rect.bottom + 10
            sprite_area_size = 160
            sprite_area_rect = pygame.Rect(
                character["rect"].centerx - sprite_area_size//2,
                sprite_top,
                sprite_area_size,
                sprite_area_size
            )

            # Circular background for sprite
            sprite_bg = pygame.Surface((sprite_area_size, sprite_area_size), pygame.SRCALPHA)
            pygame.draw.ellipse(sprite_bg, (40, 40, 55, 120), (0, 0, sprite_area_size, sprite_area_size))
            self.screen.blit(sprite_bg, sprite_area_rect.topleft)

            # Glow for selected character
            if is_selected:
                glow_radius = sprite_area_size // 2 + 8
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                for rad in range(glow_radius, 0, -4):
                    alpha = 60 - (rad * 50 // glow_radius)
                    if alpha > 0:
                        pygame.draw.circle(glow_surface, (card_color[0], card_color[1], card_color[2], alpha),
                                        (glow_radius, glow_radius), rad)
                glow_pos = (sprite_area_rect.centerx - glow_radius, sprite_area_rect.centery - glow_radius)
                self.screen.blit(glow_surface, glow_pos)

            # Draw the sprite — crop to content then scale to fill circle
            if is_selected:
                frame = character["frames"][self.animation_frame]
            else:
                frame = character["frames"][0]

            crop = character["crop_rect"]
            cropped = frame.subsurface(crop)
            # Scale cropped content to fill most of the circle area
            display_size = sprite_area_size - 10
            # Maintain aspect ratio
            scale_factor = min(display_size / crop.width, display_size / crop.height)
            scaled_w = int(crop.width * scale_factor)
            scaled_h = int(crop.height * scale_factor)
            scaled_frame = pygame.transform.scale(cropped, (scaled_w, scaled_h))
            frame_rect = scaled_frame.get_rect(center=sprite_area_rect.center)
            self.screen.blit(scaled_frame, frame_rect)

            # --- Stats panel (fully inside the card) ---
            stats_top = sprite_area_rect.bottom + 8
            stats_bottom = character["rect"].bottom - 10
            stats_height = stats_bottom - stats_top
            stats_width = character["rect"].width - 20

            stats_panel_rect = pygame.Rect(
                character["rect"].centerx - stats_width//2,
                stats_top,
                stats_width,
                stats_height
            )

            # Stats panel background
            stats_bg = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
            pygame.draw.rect(stats_bg, (25, 25, 40, 180), (0, 0, stats_width, stats_height), border_radius=6)
            self.screen.blit(stats_bg, stats_panel_rect.topleft)

            # Draw stats
            bar_width = 70
            bar_height = 9
            stats_y = stats_panel_rect.top + 14
            max_stats = {"health": 100, "damage": 25, "speed": 5}
            stat_colours = {
                "health": (30, 200, 30),
                "damage": (200, 40, 40),
                "speed": (40, 100, 220)
            }

            for stat_name, stat_value in character["stats"].items():
                if stat_name == "range":
                    continue

                stat_label = self.font_tiny.render(f"{stat_name.capitalize()}:", True, WHITE)
                label_rect = stat_label.get_rect(left=stats_panel_rect.left + 8, centery=stats_y)
                self.screen.blit(stat_label, label_rect)

                # Stat bar
                bar_x = label_rect.right + 4
                bar_bg_rect = pygame.Rect(bar_x, stats_y - bar_height//2, bar_width, bar_height)
                pygame.draw.rect(self.screen, (60, 60, 60), bar_bg_rect, border_radius=3)

                if stat_name in max_stats and max_stats[stat_name] > 0:
                    fill_width = int(bar_width * (stat_value / max_stats[stat_name]))
                    fill_rect = pygame.Rect(bar_bg_rect.left, bar_bg_rect.top, fill_width, bar_height)
                    fill_color = stat_colours.get(stat_name, (150, 150, 150))
                    pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=3)

                # Numeric value
                value_text = self.font_tiny.render(str(stat_value), True, WHITE)
                value_rect = value_text.get_rect(left=bar_bg_rect.right + 4, centery=stats_y)
                self.screen.blit(value_text, value_rect)

                stats_y += 22

            # Range
            range_label = self.font_tiny.render("Range:", True, WHITE)
            range_value = self.font_tiny.render(character['stats']['range'], True, WHITE)
            range_label_rect = range_label.get_rect(left=stats_panel_rect.left + 8, centery=stats_y)
            self.screen.blit(range_label, range_label_rect)
            range_value_rect = range_value.get_rect(left=range_label_rect.right + 4, centery=stats_y)
            self.screen.blit(range_value, range_value_rect)

            stats_y += 16

            # Special ability
            if "special" in character:
                spec_label = self.font_tiny.render("Special:", True, (220, 220, 100))
                spec_text = self.font_tiny.render(character['special'], True, (220, 220, 100))
                spec_label_rect = spec_label.get_rect(left=stats_panel_rect.left + 8, centery=stats_y)
                self.screen.blit(spec_label, spec_label_rect)
                spec_text_rect = spec_text.get_rect(left=spec_label_rect.right + 4, centery=stats_y)
                self.screen.blit(spec_text, spec_text_rect)

        # --- Description panel ---
        info_panel_width = 640
        info_panel_height = 75

        char_card_bottom = max(char["rect"].bottom for char in self.characters)

        info_panel_rect = pygame.Rect(
            SCREEN_WIDTH//2 - info_panel_width//2,
            char_card_bottom + 20,
            info_panel_width,
            info_panel_height
        )

        # Info panel background
        info_bg = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        selected_color = self.characters[self.selected_character]["color"]
        pygame.draw.rect(
            info_bg,
            (int(selected_color[0]*0.3), int(selected_color[1]*0.3), int(selected_color[2]*0.3), 200),
            (0, 0, info_panel_width, info_panel_height),
            border_radius=12
        )
        self.screen.blit(info_bg, info_panel_rect.topleft)

        pygame.draw.rect(self.screen, selected_color, info_panel_rect, 2, border_radius=12)

        # Character icon
        icon_size = 60
        icon_frame = self.characters[self.selected_character]["frames"][0]
        icon = pygame.transform.scale(icon_frame, (icon_size, icon_size))
        icon_rect = icon.get_rect(left=info_panel_rect.left + 15, centery=info_panel_rect.centery)

        icon_bg = pygame.Surface((icon_size+8, icon_size+8), pygame.SRCALPHA)
        pygame.draw.circle(icon_bg, (40, 40, 50, 180), (icon_size//2+4, icon_size//2+4), icon_size//2+4)
        self.screen.blit(icon_bg, (icon_rect.left-4, icon_rect.top-4))
        self.screen.blit(icon, icon_rect)

        # Description text
        desc_title = self.font_medium.render(self.characters[self.selected_character]["name"] + ":", True, WHITE)
        desc_title_rect = desc_title.get_rect(left=icon_rect.right + 15, top=info_panel_rect.top + 10)
        self.screen.blit(desc_title, desc_title_rect)

        desc_text = self.font_small.render(self.characters[self.selected_character]["description"], True, (200, 200, 200))
        desc_rect = desc_text.get_rect(left=icon_rect.right + 15, top=desc_title_rect.bottom + 3)
        self.screen.blit(desc_text, desc_rect)

        # --- Confirm button ---
        button_width = 200
        button_height = 50

        self.confirm_button_rect = pygame.Rect(
            SCREEN_WIDTH//2 - button_width//2,
            info_panel_rect.bottom + 15,
            button_width,
            button_height
        )

        base_color = (0, 180, 0)
        if self.button_highlighted:
            pulse_intensity = (math.sin(self.pulse_timer * 2) * 0.2) + 0.8
            button_color = (
                min(255, int(base_color[0] + 40 * pulse_intensity)),
                min(255, int(base_color[1] + 40 * pulse_intensity)),
                min(255, int(base_color[2] + 40 * pulse_intensity))
            )
        else:
            button_color = base_color

        # Button shadow
        shadow_rect = self.confirm_button_rect.inflate(4, 4)
        shadow_rect.move_ip(2, 2)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 120), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Button fill (solid rounded rect instead of broken gradient)
        pygame.draw.rect(self.screen, button_color, self.confirm_button_rect, border_radius=10)

        # Subtle highlight on top half for depth
        highlight_rect = pygame.Rect(
            self.confirm_button_rect.left + 2,
            self.confirm_button_rect.top + 2,
            self.confirm_button_rect.width - 4,
            self.confirm_button_rect.height // 2
        )
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 40), (0, 0, highlight_rect.width, highlight_rect.height), border_radius=8)
        self.screen.blit(highlight_surf, highlight_rect.topleft)

        # Glow when highlighted
        if self.button_highlighted:
            glow_rect = self.confirm_button_rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (100, 255, 100, 60), (0, 0, glow_rect.width, glow_rect.height),
                          4, border_radius=14)
            self.screen.blit(glow_surface, glow_rect.topleft)
            confirm_text = self.font_medium.render("Confirm", True, WHITE)
        else:
            confirm_text = self.font_medium.render("Confirm", True, WHITE)

        # Button outline
        pygame.draw.rect(self.screen, WHITE, self.confirm_button_rect, 2, border_radius=10)

        # Button text
        confirm_text_rect = confirm_text.get_rect(center=self.confirm_button_rect.center)
        self.screen.blit(confirm_text, confirm_text_rect)

    def run(self):
        """
        Run the character selection screen.

        Returns:
            dict, "back", or "quit": Selected character data if a character was selected,
                                     "back" to go back to main menu, or "quit" to exit.
        """
        clock = pygame.time.Clock()

        while True:
            # Handle events
            result = self.handle_events()
            if result is not None:
                return result

            # Update and draw
            dt = clock.tick(60) / 1000.0
            self.update(dt)
            self.draw()

            # Update display
            pygame.display.flip()
