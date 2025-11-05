#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tear projectile - Tolik's weapon.
"""

import pygame
import math
from ..constants import *
from ..utils.vector2d import Vector2D


class Tear:
    """Tear projectile shot by Tolik."""

    def __init__(self, x: float, y: float, direction: Vector2D, speed: float,
                 damage: float, range: float, homing: bool = False,
                 piercing: bool = False):
        """
        Initialize Tear.

        Args:
            x: Starting X position
            y: Starting Y position
            direction: Direction vector (will be normalized)
            speed: Tear speed
            damage: Damage dealt
            range: Max range in pixels
            homing: Whether tear homes toward enemies
            piercing: Whether tear pierces through enemies
        """
        self.position = Vector2D(x, y)
        self.start_position = Vector2D(x, y)
        self.velocity = direction.normalize() * speed
        self.damage = damage
        self.max_range = range
        self.speed = speed

        # Special properties
        self.homing = homing
        self.piercing = piercing
        self.hit_enemies = set()  # For piercing tears

        # State
        self.alive = True
        self.size = TEAR_SIZE

        # Visual
        self.color = TEAR_COLOR
        self.trail_positions = []  # For visual effect

    def update(self, dt: float, enemies: list = None):
        """
        Update tear.

        Args:
            dt: Delta time
            enemies: List of enemies (for homing)
        """
        # Homing behavior
        if self.homing and enemies:
            nearest_enemy = self._find_nearest_enemy(enemies)
            if nearest_enemy:
                self._home_toward(nearest_enemy, dt)

        # Move
        self.position = self.position + self.velocity * dt

        # Add to trail
        self.trail_positions.append(self.position.copy())
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)

        # Check if exceeded range
        distance_traveled = self.position.distance_to(self.start_position)
        if distance_traveled > self.max_range:
            self.alive = False

        # Check if out of bounds
        if not self._is_in_room():
            self.alive = False

    def _find_nearest_enemy(self, enemies: list):
        """Find nearest enemy for homing."""
        nearest = None
        min_distance = float('inf')

        for enemy in enemies:
            if not enemy.alive:
                continue

            dist = self.position.distance_squared_to(enemy.position)
            if dist < min_distance:
                min_distance = dist
                nearest = enemy

        return nearest

    def _home_toward(self, enemy, dt: float):
        """Home toward enemy."""
        # Calculate direction to enemy
        to_enemy = enemy.position - self.position
        desired_velocity = to_enemy.normalize() * self.speed

        # Lerp current velocity toward desired
        homing_strength = 5.0  # How fast to turn
        self.velocity = self.velocity + (desired_velocity - self.velocity) * dt * homing_strength

        # Maintain speed
        self.velocity = self.velocity.normalize() * self.speed

    def _is_in_room(self) -> bool:
        """Check if tear is inside room bounds."""
        return (ROOM_OFFSET_X <= self.position.x <= ROOM_OFFSET_X + ROOM_WIDTH and
                ROOM_OFFSET_Y <= self.position.y <= ROOM_OFFSET_Y + ROOM_HEIGHT)

    def hit_enemy(self, enemy):
        """
        Mark enemy as hit.

        Args:
            enemy: Enemy that was hit

        Returns:
            True if tear should continue (piercing), False otherwise
        """
        if self.piercing:
            self.hit_enemies.add(id(enemy))
            return True
        else:
            self.alive = False
            return False

    def can_hit_enemy(self, enemy) -> bool:
        """
        Check if tear can hit this enemy.

        Args:
            enemy: Enemy to check

        Returns:
            True if can hit
        """
        if not self.piercing:
            return True
        return id(enemy) not in self.hit_enemies

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        half_size = self.size // 2
        return pygame.Rect(
            self.position.x - half_size,
            self.position.y - half_size,
            self.size,
            self.size
        )

    def draw(self, screen: pygame.Surface):
        """
        Draw tear.

        Args:
            screen: Pygame surface
        """
        # Draw trail
        for i, trail_pos in enumerate(self.trail_positions):
            alpha = int(255 * (i + 1) / len(self.trail_positions))
            size = self.size * (i + 1) // len(self.trail_positions)
            trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            color_with_alpha = (*self.color, alpha // 2)
            pygame.draw.circle(trail_surface, color_with_alpha, (size, size), size)

            screen.blit(trail_surface, (trail_pos.x - size, trail_pos.y - size))

        # Draw main tear
        pos = self.position.int_tuple()

        # Outer glow
        glow_size = self.size + 2
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_color = (*self.color, 100)
        pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (pos[0] - glow_size, pos[1] - glow_size))

        # Main tear
        pygame.draw.circle(screen, self.color, pos, self.size)

        # Highlight
        highlight_pos = (pos[0] - self.size // 3, pos[1] - self.size // 3)
        highlight_size = self.size // 3
        pygame.draw.circle(screen, WHITE, highlight_pos, highlight_size)

        # Special effects indicator
        if self.homing:
            # Small red dot
            pygame.draw.circle(screen, RED, pos, 2)

        if self.piercing:
            # Small yellow dot
            pygame.draw.circle(screen, YELLOW, (pos[0], pos[1] + self.size // 2), 2)


class EnemyTear(Tear):
    """Tear shot by enemies (red color)."""

    def __init__(self, x: float, y: float, direction: Vector2D, speed: float, damage: float):
        """
        Initialize enemy tear.

        Args:
            x: Starting X
            y: Starting Y
            direction: Direction
            speed: Speed
            damage: Damage
        """
        super().__init__(x, y, direction, speed, damage, range=400, homing=False, piercing=False)
        self.color = (255, 80, 80)  # Red tears for enemies
