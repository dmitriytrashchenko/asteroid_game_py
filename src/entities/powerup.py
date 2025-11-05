#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Power-up collectibles.
"""

import pygame
import math
from typing import Tuple
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..constants import (
    POWERUP_LIFETIME,
    POWERUP_SIZE,
    POWERUP_SHIELD,
    POWERUP_RAPID_FIRE,
    POWERUP_TRIPLE_SHOT,
    POWERUP_EXTRA_LIFE,
    POWERUP_COLORS,
    WHITE
)


class PowerUp(GameObject):
    """
    Collectible power-up item.

    Attributes:
        powerup_type (str): Type of power-up
        lifetime (float): Time before power-up disappears
        pulse_timer (float): Timer for pulsing animation
    """

    def __init__(self, x: float, y: float, powerup_type: str):
        """
        Initialize power-up.

        Args:
            x: Initial X position
            y: Initial Y position
            powerup_type: Type of power-up (shield, rapid_fire, triple_shot, extra_life)
        """
        super().__init__(x, y)
        self.powerup_type = powerup_type
        self.lifetime = POWERUP_LIFETIME
        self.pulse_timer = 0
        self.color = POWERUP_COLORS.get(powerup_type, WHITE)

        # Create shape based on type
        self._create_shape()

        # Small initial velocity (drifting)
        import random
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(10, 30)
        self.velocity = Vector2D.from_angle(angle, speed)

    def _create_shape(self):
        """Create visual shape based on power-up type."""
        if self.powerup_type == POWERUP_SHIELD:
            # Hexagon for shield
            self.vertices = self._create_polygon(6, POWERUP_SIZE)
        elif self.powerup_type == POWERUP_RAPID_FIRE:
            # Triangle for rapid fire
            self.vertices = self._create_polygon(3, POWERUP_SIZE)
        elif self.powerup_type == POWERUP_TRIPLE_SHOT:
            # Pentagon for triple shot
            self.vertices = self._create_polygon(5, POWERUP_SIZE)
        elif self.powerup_type == POWERUP_EXTRA_LIFE:
            # Plus sign for extra life
            self.vertices = self._create_plus(POWERUP_SIZE)
        else:
            # Default square
            self.vertices = self._create_polygon(4, POWERUP_SIZE)

    def _create_polygon(self, sides: int, radius: float) -> list:
        """
        Create regular polygon vertices.

        Args:
            sides: Number of polygon sides
            radius: Polygon radius

        Returns:
            List of Vector2D vertices
        """
        vertices = []
        for i in range(sides):
            angle = (2 * math.pi * i) / sides
            vertex = Vector2D(
                radius * math.cos(angle),
                radius * math.sin(angle)
            )
            vertices.append(vertex)
        return vertices

    def _create_plus(self, size: float) -> list:
        """
        Create plus sign shape.

        Args:
            size: Size of the plus

        Returns:
            List of Vector2D vertices
        """
        thickness = size / 3
        return [
            # Horizontal bar
            Vector2D(-size, -thickness),
            Vector2D(-size, thickness),
            Vector2D(-thickness, thickness),
            Vector2D(-thickness, size),
            Vector2D(thickness, size),
            Vector2D(thickness, thickness),
            Vector2D(size, thickness),
            Vector2D(size, -thickness),
            Vector2D(thickness, -thickness),
            Vector2D(thickness, -size),
            Vector2D(-thickness, -size),
            Vector2D(-thickness, -thickness),
        ]

    def update(self, dt: float):
        """
        Update power-up state.

        Args:
            dt: Delta time in seconds
        """
        super().update(dt)

        # Rotate slowly
        self.angle += 1.0 * dt

        # Update pulse animation
        self.pulse_timer += dt * 3

        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen: pygame.Surface):
        """
        Draw power-up with pulsing effect.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        # Calculate pulse scale
        pulse_scale = 1.0 + 0.2 * math.sin(self.pulse_timer)

        # Transform and scale vertices
        transformed_vertices = []
        for vertex in self.vertices:
            # Scale
            scaled = vertex * pulse_scale
            # Rotate
            rotated = scaled.rotate(self.angle)
            # Translate
            world_pos = rotated + self.position
            transformed_vertices.append((world_pos.x, world_pos.y))

        # Draw filled polygon
        if len(transformed_vertices) > 2:
            pygame.draw.polygon(screen, self.color, transformed_vertices)
            # Draw outline
            pygame.draw.polygon(screen, WHITE, transformed_vertices, 2)

        # Draw type indicator letter
        self._draw_type_indicator(screen)

    def _draw_type_indicator(self, screen: pygame.Surface):
        """
        Draw letter indicator for power-up type.

        Args:
            screen: Pygame surface to draw on
        """
        font = pygame.font.Font(None, 16)
        indicators = {
            POWERUP_SHIELD: 'S',
            POWERUP_RAPID_FIRE: 'R',
            POWERUP_TRIPLE_SHOT: 'T',
            POWERUP_EXTRA_LIFE: '+'
        }

        text = indicators.get(self.powerup_type, '?')
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(int(self.position.x), int(self.position.y))
        )
        screen.blit(text_surface, text_rect)

    def get_type(self) -> str:
        """
        Get power-up type.

        Returns:
            Power-up type string
        """
        return self.powerup_type

    def get_description(self) -> str:
        """
        Get human-readable description.

        Returns:
            Power-up description in Russian
        """
        descriptions = {
            POWERUP_SHIELD: "Щит",
            POWERUP_RAPID_FIRE: "Быстрая стрельба",
            POWERUP_TRIPLE_SHOT: "Тройной выстрел",
            POWERUP_EXTRA_LIFE: "Дополнительная жизнь"
        }
        return descriptions.get(self.powerup_type, "Неизвестно")
