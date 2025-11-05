#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Level generation system - procedural dungeons like Isaac.
"""

import random
from typing import Dict, List, Tuple, Optional
from ..constants import *
from .room import Room


class Level:
    """Procedurally generated level."""

    def __init__(self, floor_name: str = FLOOR_BASEMENT):
        """
        Initialize level.

        Args:
            floor_name: Floor type
        """
        self.floor_name = floor_name
        self.rooms: Dict[Tuple[int, int], Room] = {}
        self.start_room: Optional[Room] = None
        self.boss_room: Optional[Room] = None
        self.current_room: Optional[Room] = None

        self._generate()

    def _generate(self):
        """Generate level layout."""
        room_count = random.randint(LEVEL_MIN_ROOMS, LEVEL_MAX_ROOMS)

        # Start room at origin
        start_pos = (0, 0)
        self.start_room = Room(0, 0, ROOM_TYPE_START)
        self.rooms[start_pos] = self.start_room
        self.current_room = self.start_room

        # BFS generation
        to_process = [start_pos]
        processed = set()

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
                if len(self.rooms) >= room_count:
                    break
                if new_pos in self.rooms:
                    # Connect existing room
                    self.rooms[current_pos].add_door(direction)
                    opposite = self._opposite_direction(direction)
                    self.rooms[new_pos].add_door(opposite)
                    continue

                # Chance to add new room
                distance = abs(new_pos[0]) + abs(new_pos[1])
                chance = 0.7 - (distance * 0.05)

                if random.random() < chance:
                    # Determine room type
                    room_type = self._determine_room_type(len(self.rooms), room_count)

                    new_room = Room(new_pos[0], new_pos[1], room_type)
                    self.rooms[new_pos] = new_room

                    # Add doors
                    self.rooms[current_pos].add_door(direction)
                    opposite = self._opposite_direction(direction)
                    new_room.add_door(opposite)

                    if room_type == ROOM_TYPE_BOSS:
                        self.boss_room = new_room

                    to_process.append(new_pos)

        # Ensure boss room exists
        if not self.boss_room:
            # Find farthest room from start
            farthest_pos = max(self.rooms.keys(),
                             key=lambda p: abs(p[0]) + abs(p[1]))
            self.boss_room = self.rooms[farthest_pos]
            self.boss_room.room_type = ROOM_TYPE_BOSS

    def _determine_room_type(self, current_count: int, total_count: int) -> str:
        """Determine type for new room."""
        if current_count >= total_count - 1:
            return ROOM_TYPE_BOSS

        # Probabilities
        if random.random() < 0.1:
            return ROOM_TYPE_TREASURE
        elif random.random() < 0.05:
            return ROOM_TYPE_SHOP

        return ROOM_TYPE_NORMAL

    def _opposite_direction(self, direction: str) -> str:
        """Get opposite door direction."""
        opposites = {
            DOOR_TOP: DOOR_BOTTOM,
            DOOR_BOTTOM: DOOR_TOP,
            DOOR_LEFT: DOOR_RIGHT,
            DOOR_RIGHT: DOOR_LEFT
        }
        return opposites[direction]

    def enter_room(self, room: Room):
        """Enter a room."""
        self.current_room = room
        room.enter()

    def get_adjacent_room(self, room: Room, direction: str) -> Optional[Room]:
        """Get room adjacent to current in direction."""
        if not room.has_door(direction):
            return None

        offsets = {
            DOOR_TOP: (0, -1),
            DOOR_BOTTOM: (0, 1),
            DOOR_LEFT: (-1, 0),
            DOOR_RIGHT: (1, 0)
        }

        offset = offsets[direction]
        new_pos = (room.grid_x + offset[0], room.grid_y + offset[1])

        return self.rooms.get(new_pos)

    def is_level_complete(self) -> bool:
        """Check if boss room is cleared."""
        return self.boss_room and self.boss_room.cleared

    def get_room_count(self) -> int:
        """Get total room count."""
        return len(self.rooms)

    def get_visited_count(self) -> int:
        """Get visited room count."""
        return sum(1 for room in self.rooms.values() if room.visited)
