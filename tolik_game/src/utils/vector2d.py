#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2D Vector class for physics and movement.
"""

import math
from typing import Tuple


class Vector2D:
    """2D vector for positions, velocities, and directions."""

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize vector.

        Args:
            x: X component
            y: Y component
        """
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        """Add two vectors."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        """Subtract two vectors."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2D':
        """Multiply vector by scalar."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2D':
        """Divide vector by scalar."""
        if scalar == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / scalar, self.y / scalar)

    def __repr__(self) -> str:
        """String representation."""
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def magnitude(self) -> float:
        """Get vector length."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self) -> float:
        """Get squared magnitude (faster than magnitude)."""
        return self.x * self.x + self.y * self.y

    def normalize(self) -> 'Vector2D':
        """Get unit vector in same direction."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def normalized(self):
        """Normalize this vector in place."""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
        return self

    def limit(self, max_magnitude: float) -> 'Vector2D':
        """Limit vector magnitude."""
        mag = self.magnitude()
        if mag > max_magnitude:
            return self.normalize() * max_magnitude
        return Vector2D(self.x, self.y)

    def dot(self, other: 'Vector2D') -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: 'Vector2D') -> float:
        """Distance to another vector."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def distance_squared_to(self, other: 'Vector2D') -> float:
        """Squared distance (faster)."""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def copy(self) -> 'Vector2D':
        """Create a copy."""
        return Vector2D(self.x, self.y)

    def tuple(self) -> Tuple[float, float]:
        """Get as tuple."""
        return (self.x, self.y)

    def int_tuple(self) -> Tuple[int, int]:
        """Get as integer tuple."""
        return (int(self.x), int(self.y))

    @staticmethod
    def from_angle(angle: float, magnitude: float = 1.0) -> 'Vector2D':
        """
        Create vector from angle and magnitude.

        Args:
            angle: Angle in radians (0 = right, pi/2 = down)
            magnitude: Vector length

        Returns:
            New vector
        """
        return Vector2D(
            magnitude * math.cos(angle),
            magnitude * math.sin(angle)
        )

    def angle(self) -> float:
        """Get angle in radians."""
        return math.atan2(self.y, self.x)

    @staticmethod
    def zero() -> 'Vector2D':
        """Get zero vector."""
        return Vector2D(0, 0)

    @staticmethod
    def up() -> 'Vector2D':
        """Get up vector."""
        return Vector2D(0, -1)

    @staticmethod
    def down() -> 'Vector2D':
        """Get down vector."""
        return Vector2D(0, 1)

    @staticmethod
    def left() -> 'Vector2D':
        """Get left vector."""
        return Vector2D(-1, 0)

    @staticmethod
    def right() -> 'Vector2D':
        """Get right vector."""
        return Vector2D(1, 0)
