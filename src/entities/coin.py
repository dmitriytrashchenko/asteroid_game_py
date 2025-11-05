#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coin collectible entity for currency system.
"""

import pygame
import math
import random
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..constants import (
    COIN_LIFETIME,
    COIN_VALUE_SMALL,
    COIN_VALUE_MEDIUM,
    COIN_VALUE_LARGE,
    GOLD,
    SILVER,
    YELLOW
)


class Coin(GameObject):
    """
    Collectible coin that gives currency.

    Attributes:
        value (int): Currency value of the coin
        lifetime (float): Time before coin disappears
        bob_timer (float): Timer for bobbing animation
    """

    def __init__(self, x: float, y: float, value: int = COIN_VALUE_SMALL):
        """
        Initialize coin.

        Args:
            x: Initial X position
            y: Initial Y position
            value: Coin value (1, 5, or 10)
        """
        super().__init__(x, y)
        self.value = value
        self.lifetime = COIN_LIFETIME
        self.bob_timer = random.uniform(0, math.pi * 2)

        # Set color and size based on value
        if value >= COIN_VALUE_LARGE:
            self.color = GOLD
            self.size = 8
        elif value >= COIN_VALUE_MEDIUM:
            self.color = SILVER
            self.size = 6
        else:
            self.color = YELLOW
            self.size = 4

        # Small initial velocity (scatter effect)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(30, 80)
        self.velocity = Vector2D.from_angle(angle, speed)

    def update(self, dt: float):
        """
        Update coin state.

        Args:
            dt: Delta time in seconds
        """
        super().update(dt)

        # Apply friction
        self.velocity = self.velocity * 0.95

        # Update bob animation
        self.bob_timer += dt * 5

        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen: pygame.Surface):
        """
        Draw coin with bobbing animation.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        # Calculate bob offset
        bob_offset = math.sin(self.bob_timer) * 3

        # Draw coin as circle with outline
        pos = (int(self.position.x), int(self.position.y + bob_offset))
        pygame.draw.circle(screen, self.color, pos, self.size)
        pygame.draw.circle(screen, (255, 255, 255), pos, self.size, 1)

        # Draw value indicator for larger coins
        if self.value > COIN_VALUE_SMALL:
            font = pygame.font.Font(None, 14)
            text = font.render(str(self.value), True, (0, 0, 0))
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)

    def get_value(self) -> int:
        """
        Get coin value.

        Returns:
            Coin currency value
        """
        return self.value
