#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Room system for roguelike gameplay.
"""

from typing import List, Dict, Optional, Tuple
from ..constants import (
    ROOM_TYPE_NORMAL,
    ROOM_TYPE_BOSS,
    ROOM_TYPE_SHOP,
    ROOM_TYPE_TREASURE,
    ROOM_TYPE_START,
    DOOR_TOP,
    DOOR_BOTTOM,
    DOOR_LEFT,
    DOOR_RIGHT,
    ROOM_WIDTH,
    ROOM_HEIGHT
)


class Door:
    """
    Door connecting rooms.

    Attributes:
        direction (str): Direction (top/bottom/left/right)
        is_open (bool): Whether door is open
        target_room (tuple): Grid position of target room
    """

    def __init__(self, direction: str, target_room: Optional[Tuple[int, int]] = None):
        """
        Initialize door.

        Args:
            direction: Door direction
            target_room: Target room grid position
        """
        self.direction = direction
        self.is_open = False
        self.target_room = target_room
        self.locked = False

    def open(self):
        """Open the door."""
        if not self.locked:
            self.is_open = True

    def close(self):
        """Close the door."""
        self.is_open = False

    def lock(self):
        """Lock the door."""
        self.locked = True
        self.is_open = False

    def unlock(self):
        """Unlock the door."""
        self.locked = False


class Room:
    """
    Single room in the dungeon.

    Attributes:
        grid_x (int): X position in level grid
        grid_y (int): Y position in level grid
        room_type (str): Type of room
        doors (Dict[str, Door]): Doors by direction
        cleared (bool): Whether room is cleared
        visited (bool): Whether player has visited
        enemies_count (int): Number of enemies to spawn
        difficulty (float): Room difficulty multiplier
    """

    def __init__(self, grid_x: int, grid_y: int, room_type: str = ROOM_TYPE_NORMAL):
        """
        Initialize room.

        Args:
            grid_x: X position in grid
            grid_y: Y position in grid
            room_type: Type of room
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.room_type = room_type
        self.doors: Dict[str, Door] = {}
        self.cleared = False
        self.visited = False
        self.enemies_count = 0
        self.difficulty = 1.0

        # Auto-clear special rooms
        if room_type in [ROOM_TYPE_START, ROOM_TYPE_SHOP, ROOM_TYPE_TREASURE]:
            self.cleared = True

    def add_door(self, direction: str, target_room: Optional[Tuple[int, int]] = None):
        """
        Add door to room.

        Args:
            direction: Door direction
            target_room: Target room position
        """
        door = Door(direction, target_room)
        self.doors[direction] = door

        # Special rooms have open doors
        if self.room_type in [ROOM_TYPE_START, ROOM_TYPE_SHOP, ROOM_TYPE_TREASURE]:
            door.open()

    def has_door(self, direction: str) -> bool:
        """
        Check if room has door in direction.

        Args:
            direction: Direction to check

        Returns:
            True if door exists
        """
        return direction in self.doors

    def get_door(self, direction: str) -> Optional[Door]:
        """
        Get door in direction.

        Args:
            direction: Direction

        Returns:
            Door or None
        """
        return self.doors.get(direction)

    def clear(self):
        """Mark room as cleared and open doors."""
        self.cleared = True
        for door in self.doors.values():
            door.unlock()
            door.open()

    def enter(self):
        """Player enters room."""
        self.visited = True

        # Lock doors in combat rooms until cleared
        if self.room_type == ROOM_TYPE_NORMAL and not self.cleared:
            for door in self.doors.values():
                door.lock()

    def set_enemy_count(self, count: int):
        """
        Set number of enemies in room.

        Args:
            count: Enemy count
        """
        self.enemies_count = count

    def set_difficulty(self, difficulty: float):
        """
        Set room difficulty.

        Args:
            difficulty: Difficulty multiplier
        """
        self.difficulty = difficulty

    def is_boss_room(self) -> bool:
        """Check if this is a boss room."""
        return self.room_type == ROOM_TYPE_BOSS

    def is_shop_room(self) -> bool:
        """Check if this is a shop room."""
        return self.room_type == ROOM_TYPE_SHOP

    def is_treasure_room(self) -> bool:
        """Check if this is a treasure room."""
        return self.room_type == ROOM_TYPE_TREASURE

    def is_start_room(self) -> bool:
        """Check if this is the start room."""
        return self.room_type == ROOM_TYPE_START

    def get_spawn_positions(self, padding: int = 100) -> List[Tuple[int, int]]:
        """
        Get valid spawn positions for enemies/items.

        Args:
            padding: Padding from edges

        Returns:
            List of (x, y) positions
        """
        positions = []

        # Generate grid of spawn points
        step = 150
        for x in range(padding, ROOM_WIDTH - padding, step):
            for y in range(padding, ROOM_HEIGHT - padding, step):
                positions.append((x, y))

        return positions

    def __repr__(self) -> str:
        """String representation."""
        return f"Room({self.grid_x},{self.grid_y},{self.room_type})"
