#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bullet projectile entity.
"""

import pygame
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..constants import BULLET_SPEED, BULLET_LIFETIME, GREEN


class Bullet(GameObject):
    """
    Bullet projectile fired by the ship.

    Attributes:
        lifetime (float): Time remaining before bullet expires
    """

    def __init__(self, x: float, y: float, angle: float):
        """
        Initialize bullet.

        Args:
            x: Initial X position
            y: Initial Y position
            angle: Direction angle in radians
        """
        super().__init__(x, y)
        self.angle = angle
        self.velocity = Vector2D.from_angle(angle, BULLET_SPEED)
        self.lifetime = BULLET_LIFETIME

        # Simple line shape
        self.vertices = [Vector2D(2, 0), Vector2D(-2, 0)]
        self.color = GREEN

    def update(self, dt: float):
        """
        Update bullet state.

        Args:
            dt: Delta time in seconds
        """
        super().update(dt)

        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen: pygame.Surface):
        """
        Draw bullet as a circle.

        Args:
            screen: Pygame surface to draw on
        """
        if self.alive:
            pygame.draw.circle(screen, self.color,
                             (int(self.position.x), int(self.position.y)), 3)
