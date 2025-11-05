#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procedural level generator.
"""

import random
from typing import List, Dict, Tuple, Optional
from .room import Room
from ..constants import (
    ROOM_TYPE_NORMAL,
    ROOM_TYPE_BOSS,
    ROOM_TYPE_SHOP,
    ROOM_TYPE_TREASURE,
    ROOM_TYPE_START,
    LEVEL_MIN_ROOMS,
    LEVEL_MAX_ROOMS,
    LEVEL_SHOP_CHANCE,
    LEVEL_TREASURE_CHANCE,
    DOOR_TOP,
    DOOR_BOTTOM,
    DOOR_LEFT,
    DOOR_RIGHT,
    ROOM_DIFFICULTY_BASE,
    ROOM_DIFFICULTY_PER_ROOM,
    ROOM_MAX_DIFFICULTY,
    DIFFICULTY_ASTEROID_COUNT
)


class Level:
    """
    Procedurally generated level with rooms.

    Attributes:
        level_number (int): Level number (1-indexed)
        rooms (Dict): Rooms by grid position
        start_room (Room): Starting room
        boss_room (Room): Boss room
        current_room (Room): Current room player is in
        difficulty (int): Base difficulty setting
    """

    def __init__(self, level_number: int = 1, difficulty: int = 1):
        """
        Initialize and generate level.

        Args:
            level_number: Level number
            difficulty: Base difficulty (0=easy, 1=normal, 2=hard)
        """
        self.level_number = level_number
        self.difficulty = difficulty
        self.rooms: Dict[Tuple[int, int], Room] = {}
        self.start_room: Optional[Room] = None
        self.boss_room: Optional[Room] = None
        self.current_room: Optional[Room] = None

        # Generate the level
        self._generate()

    def _generate(self):
        """Generate the level layout."""
        # Determine room count
        room_count = random.randint(LEVEL_MIN_ROOMS, LEVEL_MAX_ROOMS)

        # Start at center
        start_pos = (0, 0)
        self.start_room = Room(0, 0, ROOM_TYPE_START)
        self.rooms[start_pos] = self.start_room
        self.current_room = self.start_room

        # Rooms to process
        to_process = [start_pos]
        processed = set()

        # Generate rooms
        while len(self.rooms) < room_count and to_process:
            current_pos = to_process.pop(0)

            if current_pos in processed:
                continue

            processed.add(current_pos)

            # Try to add rooms in each direction
            directions = [
                (DOOR_TOP, (current_pos[0], current_pos[1] - 1)),
                (DOOR_BOTTOM, (current_pos[0], current_pos[1] + 1)),
                (DOOR_LEFT, (current_pos[0] - 1, current_pos[1])),
                (DOOR_RIGHT, (current_pos[0] + 1, current_pos[1]))
            ]

            random.shuffle(directions)

            for direction, new_pos in directions:
                # Stop if we have enough rooms
                if len(self.rooms) >= room_count:
                    break

                # Skip if room already exists
                if new_pos in self.rooms:
                    continue

                # Chance to add room (decreases with distance)
                distance = abs(new_pos[0]) + abs(new_pos[1])
                chance = 0.7 - (distance * 0.1)

                if random.random() < chance:
                    # Determine room type
                    room_type = self._determine_room_type(len(self.rooms), room_count)

                    # Create room
                    new_room = Room(new_pos[0], new_pos[1], room_type)
                    self.rooms[new_pos] = new_room

                    # Connect rooms with doors
                    self._connect_rooms(current_pos, direction, new_pos)

                    # Add to processing queue
                    to_process.append(new_pos)

                    # Save boss room
                    if room_type == ROOM_TYPE_BOSS:
                        self.boss_room = new_room

        # Ensure we have a boss room
        if not self.boss_room:
            # Find furthest room from start
            furthest_pos = max(self.rooms.keys(),
                             key=lambda p: abs(p[0]) + abs(p[1]))
            furthest_room = self.rooms[furthest_pos]
            furthest_room.room_type = ROOM_TYPE_BOSS
            self.boss_room = furthest_room

        # Set difficulty for each room
        self._set_room_difficulties()

    def _determine_room_type(self, current_count: int, total_rooms: int) -> str:
        """
        Determine type for new room.

        Args:
            current_count: Current room count
            total_rooms: Target total rooms

        Returns:
            Room type
        """
        # Boss room at the end
        if current_count == total_rooms - 1:
            return ROOM_TYPE_BOSS

        # Special rooms with chance
        if random.random() < LEVEL_SHOP_CHANCE:
            return ROOM_TYPE_SHOP

        if random.random() < LEVEL_TREASURE_CHANCE:
            return ROOM_TYPE_TREASURE

        return ROOM_TYPE_NORMAL

    def _connect_rooms(self, pos1: Tuple[int, int], direction: str,
                      pos2: Tuple[int, int]):
        """
        Connect two rooms with doors.

        Args:
            pos1: First room position
            direction: Direction from pos1 to pos2
            pos2: Second room position
        """
        room1 = self.rooms[pos1]
        room2 = self.rooms[pos2]

        # Add door to room1
        room1.add_door(direction, pos2)

        # Add opposite door to room2
        opposite = {
            DOOR_TOP: DOOR_BOTTOM,
            DOOR_BOTTOM: DOOR_TOP,
            DOOR_LEFT: DOOR_RIGHT,
            DOOR_RIGHT: DOOR_LEFT
        }

        room2.add_door(opposite[direction], pos1)

    def _set_room_difficulties(self):
        """Set difficulty multiplier for each room based on distance from start."""
        if not self.start_room:
            return

        for pos, room in self.rooms.items():
            # Distance from start
            distance = abs(pos[0]) + abs(pos[1])

            # Calculate difficulty
            difficulty = ROOM_DIFFICULTY_BASE + (distance * ROOM_DIFFICULTY_PER_ROOM)
            difficulty = min(difficulty, ROOM_MAX_DIFFICULTY)

            room.set_difficulty(difficulty)

            # Set enemy count based on difficulty and type
            if room.room_type == ROOM_TYPE_NORMAL:
                base_count = DIFFICULTY_ASTEROID_COUNT.get(self.difficulty, 5)
                enemy_count = int(base_count * difficulty)
                room.set_enemy_count(enemy_count)
            elif room.room_type == ROOM_TYPE_BOSS:
                room.set_enemy_count(1)  # One boss

    def get_room_at(self, grid_x: int, grid_y: int) -> Optional[Room]:
        """
        Get room at grid position.

        Args:
            grid_x: Grid X
            grid_y: Grid Y

        Returns:
            Room or None
        """
        return self.rooms.get((grid_x, grid_y))

    def get_adjacent_room(self, room: Room, direction: str) -> Optional[Room]:
        """
        Get adjacent room in direction.

        Args:
            room: Current room
            direction: Direction

        Returns:
            Adjacent room or None
        """
        door = room.get_door(direction)
        if door and door.target_room:
            return self.rooms.get(door.target_room)
        return None

    def enter_room(self, room: Room):
        """
        Player enters a room.

        Args:
            room: Room to enter
        """
        self.current_room = room
        room.enter()

    def get_room_count(self) -> int:
        """Get total room count."""
        return len(self.rooms)

    def get_cleared_count(self) -> int:
        """Get number of cleared rooms."""
        return sum(1 for room in self.rooms.values() if room.cleared)

    def get_visited_count(self) -> int:
        """Get number of visited rooms."""
        return sum(1 for room in self.rooms.values() if room.visited)

    def is_level_complete(self) -> bool:
        """Check if level is complete (boss defeated)."""
        return self.boss_room is not None and self.boss_room.cleared

    def get_grid_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get min/max grid coordinates.

        Returns:
            (min_x, max_x, min_y, max_y)
        """
        positions = list(self.rooms.keys())
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]

        return (min(xs), max(xs), min(ys), max(ys))
