#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2D Vector math utility class.
"""

import math
from typing import Union


class Vector2D:
    """
    A 2D vector class for game physics and mathematics.

    Attributes:
        x (float): X component of the vector
        y (float): Y component of the vector
    """

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize a 2D vector.

        Args:
            x: X component (default: 0)
            y: Y component (default: 0)
        """
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        """
        Add two vectors.

        Args:
            other: Vector to add

        Returns:
            New vector representing the sum
        """
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        """
        Subtract two vectors.

        Args:
            other: Vector to subtract

        Returns:
            New vector representing the difference
        """
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Union[int, float]) -> 'Vector2D':
        """
        Multiply vector by a scalar.

        Args:
            scalar: Scalar value to multiply by

        Returns:
            New scaled vector
        """
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: Union[int, float]) -> 'Vector2D':
        """
        Divide vector by a scalar.

        Args:
            scalar: Scalar value to divide by

        Returns:
            New scaled vector

        Raises:
            ZeroDivisionError: If scalar is zero
        """
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __repr__(self) -> str:
        """String representation of the vector."""
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another vector."""
        if not isinstance(other, Vector2D):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def magnitude(self) -> float:
        """
        Calculate the magnitude (length) of the vector.

        Returns:
            Length of the vector
        """
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self) -> float:
        """
        Calculate the squared magnitude of the vector.
        Useful for distance comparisons without sqrt overhead.

        Returns:
            Squared length of the vector
        """
        return self.x * self.x + self.y * self.y

    def normalize(self) -> 'Vector2D':
        """
        Get a normalized (unit length) version of the vector.

        Returns:
            Unit vector in the same direction, or zero vector if magnitude is 0
        """
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)

    def rotate(self, angle: float) -> 'Vector2D':
        """
        Rotate the vector by an angle.

        Args:
            angle: Rotation angle in radians

        Returns:
            New rotated vector
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def dot(self, other: 'Vector2D') -> float:
        """
        Calculate dot product with another vector.

        Args:
            other: Vector to calculate dot product with

        Returns:
            Dot product value
        """
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: 'Vector2D') -> float:
        """
        Calculate distance to another vector.

        Args:
            other: Target vector

        Returns:
            Distance between vectors
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def distance_squared_to(self, other: 'Vector2D') -> float:
        """
        Calculate squared distance to another vector.
        Faster than distance_to for comparisons.

        Args:
            other: Target vector

        Returns:
            Squared distance between vectors
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def copy(self) -> 'Vector2D':
        """
        Create a copy of the vector.

        Returns:
            New vector with same values
        """
        return Vector2D(self.x, self.y)

    def limit(self, max_magnitude: float) -> 'Vector2D':
        """
        Limit the magnitude of the vector.

        Args:
            max_magnitude: Maximum allowed magnitude

        Returns:
            New vector with limited magnitude
        """
        mag = self.magnitude()
        if mag > max_magnitude:
            return self.normalize() * max_magnitude
        return self.copy()

    @staticmethod
    def from_angle(angle: float, magnitude: float = 1.0) -> 'Vector2D':
        """
        Create a vector from an angle and magnitude.

        Args:
            angle: Angle in radians
            magnitude: Length of the vector (default: 1.0)

        Returns:
            New vector pointing in the specified direction
        """
        return Vector2D(
            magnitude * math.cos(angle),
            magnitude * math.sin(angle)
        )
