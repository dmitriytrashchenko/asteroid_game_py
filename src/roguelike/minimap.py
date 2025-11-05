#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimap for room navigation.
"""

import pygame
from typing import Optional
from .level import Level
from .room import Room
from ..constants import (
    MINIMAP_SIZE,
    MINIMAP_ROOM_SIZE,
    MINIMAP_PADDING,
    MINIMAP_X,
    MINIMAP_Y,
    ROOM_TYPE_BOSS,
    ROOM_TYPE_SHOP,
    ROOM_TYPE_TREASURE,
    ROOM_TYPE_START,
    WHITE,
    GRAY,
    RED,
    YELLOW,
    GREEN,
    CYAN
)


class Minimap:
    """
    Minimap display for level navigation.

    Attributes:
        level (Level): Current level
        x (int): Minimap X position
        y (int): Minimap Y position
    """

    def __init__(self, level: Level, x: int = MINIMAP_X, y: int = MINIMAP_Y):
        """
        Initialize minimap.

        Args:
            level: Level to display
            x: X position on screen
            y: Y position on screen
        """
        self.level = level
        self.x = x
        self.y = y

    def draw(self, screen: pygame.Surface):
        """
        Draw minimap.

        Args:
            screen: Pygame surface
        """
        # Draw background
        pygame.draw.rect(screen, (20, 20, 20),
                        (self.x, self.y, MINIMAP_SIZE, MINIMAP_SIZE))
        pygame.draw.rect(screen, WHITE,
                        (self.x, self.y, MINIMAP_SIZE, MINIMAP_SIZE), 2)

        # Get level bounds
        min_x, max_x, min_y, max_y = self.level.get_grid_bounds()

        # Calculate scale
        grid_width = max_x - min_x + 1
        grid_height = max_y - min_y + 1
        scale = (MINIMAP_SIZE - MINIMAP_PADDING * 2) / max(grid_width, grid_height)

        # Center offset
        center_x = self.x + MINIMAP_SIZE // 2
        center_y = self.y + MINIMAP_SIZE // 2

        # Draw rooms
        for pos, room in self.level.rooms.items():
            # Calculate position on minimap
            room_x = center_x + (pos[0] - (min_x + max_x) / 2) * scale * MINIMAP_ROOM_SIZE
            room_y = center_y + (pos[1] - (min_y + max_y) / 2) * scale * MINIMAP_ROOM_SIZE

            # Determine color
            if room == self.level.current_room:
                color = WHITE  # Current room
            elif not room.visited:
                continue  # Don't show unvisited rooms
            elif room.room_type == ROOM_TYPE_BOSS:
                color = RED
            elif room.room_type == ROOM_TYPE_SHOP:
                color = GREEN
            elif room.room_type == ROOM_TYPE_TREASURE:
                color = YELLOW
            elif room.cleared:
                color = GRAY
            else:
                color = WHITE

            # Draw room
            size = int(MINIMAP_ROOM_SIZE * scale * 0.8)
            pygame.draw.rect(screen, color,
                           (int(room_x - size/2), int(room_y - size/2), size, size))

            # Draw doors
            if room.visited:
                door_size = int(size * 0.3)
                if room.has_door('top'):
                    pygame.draw.rect(screen, color,
                                   (int(room_x - door_size/2), int(room_y - size/2 - door_size/2),
                                    door_size, door_size))
                if room.has_door('bottom'):
                    pygame.draw.rect(screen, color,
                                   (int(room_x - door_size/2), int(room_y + size/2 - door_size/2),
                                    door_size, door_size))
                if room.has_door('left'):
                    pygame.draw.rect(screen, color,
                                   (int(room_x - size/2 - door_size/2), int(room_y - door_size/2),
                                    door_size, door_size))
                if room.has_door('right'):
                    pygame.draw.rect(screen, color,
                                   (int(room_x + size/2 - door_size/2), int(room_y - door_size/2),
                                    door_size, door_size))
