#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Player ship entity.
"""

import pygame
import random
from typing import Optional
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..utils.settings import Settings
from ..constants import (
    SHIP_THRUST_POWER,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION,
    WHITE,
    RED,
    CYAN,
    SHIP_INVULNERABILITY_TIME,
    SHIP_BLINK_INTERVAL,
    POWERUP_SHIELD
)


class Ship(GameObject):
    """
    Player-controlled spaceship.

    Attributes:
        settings (Settings): Game settings
        thrust (float): Current thrust level (0-1)
        rotation_speed (float): Current rotation speed
        invulnerable (bool): Whether ship is invulnerable
        invulnerability_timer (float): Time remaining for invulnerability
        blink_timer (float): Timer for visual blinking effect
        active_powerups (dict): Currently active power-ups
        has_shield (bool): Whether shield power-up is active
    """

    def __init__(self, x: float, y: float, settings: Settings):
        """
        Initialize ship.

        Args:
            x: Initial X position
            y: Initial Y position
            settings: Game settings instance
        """
        super().__init__(x, y)
        self.settings = settings
        self.thrust: float = 0
        self.rotation_speed: float = 0

        # Ship shape (triangle pointing right)
        self.vertices = [
            Vector2D(15, 0),    # nose
            Vector2D(-10, -8),  # left wing
            Vector2D(-5, 0),    # center rear
            Vector2D(-10, 8)    # right wing
        ]

        # Invulnerability (after respawn)
        self.invulnerable: bool = False
        self.invulnerability_timer: float = 0
        self.blink_timer: float = 0
        self.visible: bool = True

        # Power-ups
        self.active_powerups: dict = {}
        self.has_shield: bool = False

    def update(self, dt: float):
        """
        Update ship state.

        Args:
            dt: Delta time in seconds
        """
        # Update rotation
        self.angle += self.rotation_speed * dt

        # Apply thrust
        if self.thrust > 0:
            thrust_vector = Vector2D.from_angle(self.angle, SHIP_THRUST_POWER * self.thrust)
            self.velocity = self.velocity + thrust_vector * dt

        # Limit speed
        if self.velocity.magnitude() > SHIP_MAX_SPEED:
            self.velocity = self.velocity.normalize() * SHIP_MAX_SPEED

        # Apply friction
        self.velocity = self.velocity * SHIP_FRICTION

        # Update invulnerability
        if self.invulnerable:
            self.invulnerability_timer -= dt
            self.blink_timer += dt

            # Blinking effect
            if self.blink_timer >= SHIP_BLINK_INTERVAL:
                self.visible = not self.visible
                self.blink_timer = 0

            if self.invulnerability_timer <= 0:
                self.invulnerable = False
                self.visible = True

        # Update power-up timers
        expired_powerups = []
        for powerup_type, time_remaining in self.active_powerups.items():
            self.active_powerups[powerup_type] = time_remaining - dt
            if self.active_powerups[powerup_type] <= 0:
                expired_powerups.append(powerup_type)

        # Remove expired power-ups
        for powerup_type in expired_powerups:
            del self.active_powerups[powerup_type]
            if powerup_type == POWERUP_SHIELD:
                self.has_shield = False

        super().update(dt)

    def draw(self, screen: pygame.Surface):
        """
        Draw ship with effects.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        # Don't draw if blinking and invisible
        if self.invulnerable and not self.visible:
            return

        # Draw shield if active
        if self.has_shield:
            shield_radius = int(self.get_radius() + 10)
            pygame.draw.circle(screen, CYAN,
                             (int(self.position.x), int(self.position.y)),
                             shield_radius, 2)

        # Draw ship
        super().draw(screen)

        # Draw engine flame
        if self.thrust > 0:
            self._draw_engine_flame(screen)

    def _draw_engine_flame(self, screen: pygame.Surface):
        """
        Draw engine flame effect.

        Args:
            screen: Pygame surface to draw on
        """
        flame_vertices = [
            Vector2D(-5, 0),
            Vector2D(-15 - random.randint(0, 5), -3),
            Vector2D(-15 - random.randint(0, 5), 3)
        ]

        transformed_flame = []
        for vertex in flame_vertices:
            rotated = vertex.rotate(self.angle)
            world_pos = rotated + self.position
            transformed_flame.append((world_pos.x, world_pos.y))

        pygame.draw.polygon(screen, RED, transformed_flame)

    def make_invulnerable(self, duration: Optional[float] = None):
        """
        Make ship invulnerable for a duration.

        Args:
            duration: Invulnerability duration in seconds (default: SHIP_INVULNERABILITY_TIME)
        """
        self.invulnerable = True
        self.invulnerability_timer = duration if duration else SHIP_INVULNERABILITY_TIME
        self.blink_timer = 0
        self.visible = True

    def activate_powerup(self, powerup_type: str, duration: float):
        """
        Activate a power-up.

        Args:
            powerup_type: Type of power-up
            duration: Duration in seconds
        """
        self.active_powerups[powerup_type] = duration
        if powerup_type == POWERUP_SHIELD:
            self.has_shield = True

    def has_powerup(self, powerup_type: str) -> bool:
        """
        Check if a power-up is active.

        Args:
            powerup_type: Type of power-up to check

        Returns:
            True if power-up is active
        """
        return powerup_type in self.active_powerups

    def reset_controls(self):
        """Reset thrust and rotation to zero."""
        self.thrust = 0
        self.rotation_speed = 0

    def can_be_hit(self) -> bool:
        """
        Check if ship can be hit by asteroids.

        Returns:
            True if ship can be damaged
        """
        return not self.invulnerable and not self.has_shield
