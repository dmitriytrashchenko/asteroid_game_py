#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asteroid entity.
"""

import math
import random
from typing import List
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..constants import (
    ASTEROID_BASE_SIZE,
    ASTEROID_MIN_VERTICES,
    ASTEROID_MAX_VERTICES,
    ASTEROID_MIN_ROTATION_SPEED,
    ASTEROID_MAX_ROTATION_SPEED,
    DIFFICULTY_SPEED_MULTIPLIER,
    DIFFICULTY_NORMAL,
    WHITE
)


class Asteroid(GameObject):
    """
    Asteroid obstacle.

    Attributes:
        size (int): Asteroid size (1=small, 2=medium, 3=large)
        rotation_speed (float): Angular velocity in radians/second
        difficulty (int): Difficulty level affecting speed
    """

    def __init__(self, x: float, y: float, size: int = 3,
                 difficulty: int = DIFFICULTY_NORMAL,
                 velocity: Vector2D = None):
        """
        Initialize asteroid.

        Args:
            x: Initial X position
            y: Initial Y position
            size: Asteroid size (1-3)
            difficulty: Difficulty level
            velocity: Initial velocity (random if None)
        """
        super().__init__(x, y)
        self.size = max(1, min(3, size))
        self.difficulty = difficulty
        self.rotation_speed = random.uniform(
            ASTEROID_MIN_ROTATION_SPEED,
            ASTEROID_MAX_ROTATION_SPEED
        )

        # Generate random asteroid shape
        self._generate_shape()

        # Set velocity
        if velocity is not None:
            self.velocity = velocity
        else:
            self._generate_velocity()

        self.color = WHITE

    def _generate_shape(self):
        """Generate random polygon shape for asteroid."""
        num_vertices = random.randint(ASTEROID_MIN_VERTICES, ASTEROID_MAX_VERTICES)
        radius = ASTEROID_BASE_SIZE * self.size
        self.vertices = []

        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            # Add some randomness to radius
            r = radius + random.randint(-radius // 3, radius // 3)
            vertex = Vector2D(r * math.cos(angle), r * math.sin(angle))
            self.vertices.append(vertex)

    def _generate_velocity(self):
        """Generate random velocity based on difficulty."""
        # Base speed depends on size (smaller = faster)
        base_speed = 30 + (4 - self.size) * 15

        # Apply difficulty multiplier
        speed_multiplier = DIFFICULTY_SPEED_MULTIPLIER.get(self.difficulty, 1.0)
        speed = base_speed * speed_multiplier + random.uniform(0, 30)

        # Random direction
        direction = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2D.from_angle(direction, speed)

    def update(self, dt: float):
        """
        Update asteroid state.

        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        # Rotate asteroid
        self.angle += self.rotation_speed * dt

    def split(self, difficulty: int = None) -> List['Asteroid']:
        """
        Split asteroid into smaller pieces.

        Args:
            difficulty: Difficulty level for new asteroids (uses current if None)

        Returns:
            List of new smaller asteroids (empty if size is 1)
        """
        if self.size <= 1:
            return []

        if difficulty is None:
            difficulty = self.difficulty

        new_asteroids = []
        new_size = self.size - 1

        # Create 2-3 smaller asteroids
        num_pieces = random.randint(2, 3)

        for i in range(num_pieces):
            # Spread out in different directions
            angle_offset = (2 * math.pi * i) / num_pieces + random.uniform(-0.5, 0.5)

            # Inherit some parent velocity and add perpendicular component
            speed_boost = 20 + random.uniform(0, 30)
            new_velocity = Vector2D.from_angle(angle_offset, speed_boost) + self.velocity * 0.5

            # Create new asteroid
            new_asteroid = Asteroid(
                self.position.x,
                self.position.y,
                new_size,
                difficulty,
                new_velocity
            )
            new_asteroids.append(new_asteroid)

        return new_asteroids

    def get_score_value(self) -> int:
        """
        Get score value for destroying this asteroid.

        Returns:
            Score points based on size
        """
        # Smaller asteroids are worth more points
        score_values = {
            3: 20,  # Large
            2: 50,  # Medium
            1: 100  # Small
        }
        return score_values.get(self.size, 20)
