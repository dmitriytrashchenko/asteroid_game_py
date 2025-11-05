#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base game object class for all entities.
"""

import pygame
from typing import List, Tuple
from ..utils.vector2d import Vector2D
from ..constants import WIDTH, HEIGHT, WHITE


class GameObject:
    """
    Base class for all game objects.

    Attributes:
        position (Vector2D): Object position in world space
        velocity (Vector2D): Object velocity vector
        angle (float): Object rotation angle in radians
        vertices (List[Vector2D]): Object's shape vertices
        alive (bool): Whether the object is active
    """

    def __init__(self, x: float, y: float):
        """
        Initialize game object.

        Args:
            x: Initial X position
            y: Initial Y position
        """
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.angle: float = 0
        self.vertices: List[Vector2D] = []
        self.alive: bool = True
        self.color: Tuple[int, int, int] = WHITE

    def update(self, dt: float):
        """
        Update object state.

        Args:
            dt: Delta time in seconds
        """
        # Update position
        self.position = self.position + self.velocity * dt

        # Screen wrapping
        self.position.x = self.position.x % WIDTH
        self.position.y = self.position.y % HEIGHT

    def draw(self, screen: pygame.Surface):
        """
        Draw the object on screen.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive or len(self.vertices) < 2:
            return

        # Transform vertices
        transformed_vertices = self._get_transformed_vertices()

        # Draw polygon or line
        if len(transformed_vertices) > 2:
            pygame.draw.polygon(screen, self.color, transformed_vertices, 2)
        elif len(transformed_vertices) == 2:
            pygame.draw.line(screen, self.color,
                           transformed_vertices[0],
                           transformed_vertices[1], 2)

    def _get_transformed_vertices(self) -> List[Tuple[float, float]]:
        """
        Get vertices transformed to world space.

        Returns:
            List of (x, y) tuples representing transformed vertices
        """
        transformed = []
        for vertex in self.vertices:
            # Rotate vertex
            rotated = vertex.rotate(self.angle)
            # Translate to world position
            world_pos = rotated + self.position
            transformed.append((world_pos.x, world_pos.y))
        return transformed

    def get_radius(self) -> float:
        """
        Get the bounding radius of the object.

        Returns:
            Maximum distance from center to any vertex
        """
        if not self.vertices:
            return 0

        max_dist = 0
        for vertex in self.vertices:
            dist = vertex.magnitude()
            if dist > max_dist:
                max_dist = dist
        return max_dist

    def collides_with(self, other: 'GameObject') -> bool:
        """
        Check collision with another game object.
        Uses optimized distance check with bounding circles.

        Args:
            other: GameObject to check collision with

        Returns:
            True if objects are colliding, False otherwise
        """
        if not self.alive or not other.alive:
            return False

        # Get radii
        r1 = self.get_radius()
        r2 = other.get_radius()
        max_dist = r1 + r2

        # Fast AABB check
        dx = abs(self.position.x - other.position.x)
        dy = abs(self.position.y - other.position.y)

        if dx > max_dist or dy > max_dist:
            return False

        # Precise distance check (squared to avoid sqrt)
        distance_sq = dx * dx + dy * dy
        max_dist_sq = max_dist * max_dist

        return distance_sq < max_dist_sq

    def is_off_screen(self, margin: float = 0) -> bool:
        """
        Check if object is off screen.

        Args:
            margin: Extra margin around screen edges

        Returns:
            True if object is completely off screen
        """
        radius = self.get_radius()
        return (self.position.x < -radius - margin or
                self.position.x > WIDTH + radius + margin or
                self.position.y < -radius - margin or
                self.position.y > HEIGHT + radius + margin)

    def get_forward_vector(self) -> Vector2D:
        """
        Get the forward direction vector based on current angle.

        Returns:
            Normalized forward vector
        """
        return Vector2D.from_angle(self.angle)

    def wrap_position(self):
        """Wrap position around screen edges."""
        self.position.x = self.position.x % WIDTH
        self.position.y = self.position.y % HEIGHT
