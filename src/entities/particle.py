#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Particle effects system.
"""

import pygame
import random
from typing import Tuple, List
from .game_object import GameObject
from ..utils.vector2d import Vector2D
from ..constants import (
    PARTICLE_LIFETIME,
    PARTICLE_MIN_SPEED,
    PARTICLE_MAX_SPEED,
    PARTICLE_COUNT_EXPLOSION,
    WHITE,
    RED,
    YELLOW,
    ORANGE
)


class Particle(GameObject):
    """
    Visual particle effect.

    Attributes:
        lifetime (float): Time remaining before particle expires
        max_lifetime (float): Initial lifetime for fade calculation
    """

    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = WHITE,
                 lifetime: float = PARTICLE_LIFETIME):
        """
        Initialize particle.

        Args:
            x: Initial X position
            y: Initial Y position
            color: Particle color RGB tuple
            lifetime: Particle lifetime in seconds
        """
        super().__init__(x, y)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime

        # Random velocity
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(PARTICLE_MIN_SPEED, PARTICLE_MAX_SPEED)
        self.velocity = Vector2D.from_angle(angle, speed)

        # Small size
        self.size = random.randint(1, 3)

    def update(self, dt: float):
        """
        Update particle state.

        Args:
            dt: Delta time in seconds
        """
        super().update(dt)

        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

        # Apply friction
        self.velocity = self.velocity * 0.98

    def draw(self, screen: pygame.Surface):
        """
        Draw particle with fade effect.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = max(0, min(255, alpha))

        # Create color with alpha
        color_with_alpha = (*self.color, alpha)

        # Draw particle
        pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(screen, self.color, pos, self.size)


class ParticleSystem:
    """
    Manages multiple particles.

    Attributes:
        particles (List[Particle]): List of active particles
    """

    def __init__(self):
        """Initialize particle system."""
        self.particles: List[Particle] = []

    def create_explosion(self, x: float, y: float, color: Tuple[int, int, int] = WHITE,
                        count: int = PARTICLE_COUNT_EXPLOSION):
        """
        Create an explosion effect.

        Args:
            x: Explosion center X
            y: Explosion center Y
            color: Particle color
            count: Number of particles
        """
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)

    def create_asteroid_explosion(self, x: float, y: float, size: int = 3):
        """
        Create explosion for asteroid destruction.

        Args:
            x: Explosion center X
            y: Explosion center Y
            size: Asteroid size (affects particle count)
        """
        count = PARTICLE_COUNT_EXPLOSION * size
        colors = [WHITE, (200, 200, 200), (150, 150, 150)]

        for _ in range(count):
            color = random.choice(colors)
            particle = Particle(x, y, color)
            self.particles.append(particle)

    def create_ship_explosion(self, x: float, y: float):
        """
        Create explosion for ship destruction.

        Args:
            x: Explosion center X
            y: Explosion center Y
        """
        count = PARTICLE_COUNT_EXPLOSION * 2
        colors = [RED, ORANGE, YELLOW, WHITE]

        for _ in range(count):
            color = random.choice(colors)
            lifetime = random.uniform(0.5, 1.5)
            particle = Particle(x, y, color, lifetime)
            self.particles.append(particle)

    def create_thrust_particles(self, x: float, y: float, angle: float):
        """
        Create engine thrust particles.

        Args:
            x: Particle spawn X
            y: Particle spawn Y
            angle: Direction angle (opposite to thrust)
        """
        # Create 1-2 particles per frame
        if random.random() < 0.7:
            colors = [RED, ORANGE, YELLOW]
            color = random.choice(colors)

            particle = Particle(x, y, color, 0.3)
            # Add some spread to the angle
            spread_angle = angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(30, 80)
            particle.velocity = Vector2D.from_angle(spread_angle, speed)
            particle.size = random.randint(1, 2)

            self.particles.append(particle)

    def update(self, dt: float):
        """
        Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Update particles
        for particle in self.particles:
            particle.update(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen: pygame.Surface):
        """
        Draw all particles.

        Args:
            screen: Pygame surface to draw on
        """
        for particle in self.particles:
            particle.draw(screen)

    def clear(self):
        """Remove all particles."""
        self.particles.clear()

    def get_particle_count(self) -> int:
        """
        Get current number of active particles.

        Returns:
            Number of particles
        """
        return len(self.particles)
