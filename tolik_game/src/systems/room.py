#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Room system - individual rooms in the level.
"""

import pygame
import random
from typing import List, Dict, Optional, Tuple
from ..constants import *
from ..utils.vector2d import Vector2D


class Door:
    """Door connecting rooms."""

    def __init__(self, direction: str):
        """
        Initialize door.

        Args:
            direction: Door direction (top/bottom/left/right)
        """
        self.direction = direction
        self.locked = False
        self.open = True

    def lock(self):
        """Lock the door."""
        self.locked = True
        self.open = False

    def unlock(self):
        """Unlock the door."""
        self.locked = False
        self.open = True


class Room:
    """Individual room in the level."""

    def __init__(self, grid_x: int, grid_y: int, room_type: str = ROOM_TYPE_NORMAL):
        """
        Initialize room.

        Args:
            grid_x: X position in level grid
            grid_y: Y position in level grid
            room_type: Type of room
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.room_type = room_type

        # Doors
        self.doors: Dict[str, Door] = {}

        # State
        self.visited = False
        self.cleared = False

        # Enemies will be spawned by game logic
        self.enemy_count = 0

    def add_door(self, direction: str):
        """Add a door in direction."""
        self.doors[direction] = Door(direction)

    def has_door(self, direction: str) -> bool:
        """Check if room has door in direction."""
        return direction in self.doors

    def get_door(self, direction: str) -> Optional[Door]:
        """Get door in direction."""
        return self.doors.get(direction)

    def enter(self):
        """Called when player enters room."""
        self.visited = True

        # Lock doors if combat room
        if self.room_type == ROOM_TYPE_NORMAL and not self.cleared:
            for door in self.doors.values():
                door.lock()

    def clear(self):
        """Mark room as cleared."""
        self.cleared = True

        # Unlock all doors
        for door in self.doors.values():
            door.unlock()

    def get_spawn_positions(self, count: int) -> List[Tuple[float, float]]:
        """
        Get enemy spawn positions.

        Args:
            count: Number of positions

        Returns:
            List of (x, y) tuples
        """
        positions = []
        margin = 100

        for _ in range(count):
            x = random.randint(ROOM_OFFSET_X + margin, ROOM_OFFSET_X + ROOM_WIDTH - margin)
            y = random.randint(ROOM_OFFSET_Y + margin, ROOM_OFFSET_Y + ROOM_HEIGHT - margin)
            positions.append((x, y))

        return positions

    def draw(self, screen: pygame.Surface, floor_name: str):
        """
        Draw room.

        Args:
            screen: Pygame surface
            floor_name: Current floor name for colors
        """
        # Background
        floor_color = FLOOR_COLORS.get(floor_name, FLOOR_COLORS['basement'])
        wall_color = WALL_COLORS.get(floor_name, WALL_COLORS['basement'])

        # Draw walls
        pygame.draw.rect(screen, wall_color, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Draw floor
        pygame.draw.rect(screen, floor_color,
                        (ROOM_OFFSET_X, ROOM_OFFSET_Y, ROOM_WIDTH, ROOM_HEIGHT))

        # Draw doors
        for direction, door in self.doors.items():
            self._draw_door(screen, direction, door)

        # Draw room border
        pygame.draw.rect(screen, wall_color,
                        (ROOM_OFFSET_X, ROOM_OFFSET_Y, ROOM_WIDTH, ROOM_HEIGHT), 3)

    def _draw_door(self, screen: pygame.Surface, direction: str, door: Door):
        """Draw a door."""
        door_color = GREEN if door.open else RED

        if direction == DOOR_TOP:
            x = ROOM_OFFSET_X + ROOM_WIDTH // 2 - DOOR_WIDTH // 2
            y = ROOM_OFFSET_Y - DOOR_HEIGHT // 2
            pygame.draw.rect(screen, door_color, (x, y, DOOR_WIDTH, DOOR_HEIGHT))

        elif direction == DOOR_BOTTOM:
            x = ROOM_OFFSET_X + ROOM_WIDTH // 2 - DOOR_WIDTH // 2
            y = ROOM_OFFSET_Y + ROOM_HEIGHT - DOOR_HEIGHT // 2
            pygame.draw.rect(screen, door_color, (x, y, DOOR_WIDTH, DOOR_HEIGHT))

        elif direction == DOOR_LEFT:
            x = ROOM_OFFSET_X - DOOR_HEIGHT // 2
            y = ROOM_OFFSET_Y + ROOM_HEIGHT // 2 - DOOR_WIDTH // 2
            pygame.draw.rect(screen, door_color, (x, y, DOOR_HEIGHT, DOOR_WIDTH))

        elif direction == DOOR_RIGHT:
            x = ROOM_OFFSET_X + ROOM_WIDTH - DOOR_HEIGHT // 2
            y = ROOM_OFFSET_Y + ROOM_HEIGHT // 2 - DOOR_WIDTH // 2
            pygame.draw.rect(screen, door_color, (x, y, DOOR_HEIGHT, DOOR_WIDTH))
