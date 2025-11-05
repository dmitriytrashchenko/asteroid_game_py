#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss entities with attack patterns.
"""

import pygame
import math
import random
from typing import List
from .game_object import GameObject
from .asteroid import Asteroid
from .bullet import Bullet
from ..utils.vector2d import Vector2D
from ..constants import (
    BOSS_HEALTH_BASE,
    BOSS_HEALTH_PER_LEVEL,
    BOSS_SIZE_MULTIPLIER,
    BOSS_DAMAGE,
    BOSS_SPEED,
    BOSS_ATTACK_COOLDOWN,
    BOSS_PROJECTILE_COUNT,
    BOSS_PROJECTILE_SPEED,
    BOSS_ASTEROID_KING,
    BOSS_VOID_HUNTER,
    BOSS_STAR_DESTROYER,
    RED,
    ORANGE,
    PURPLE,
    WIDTH,
    HEIGHT
)


class BossProjectile(GameObject):
    """
    Boss projectile.

    Attributes:
        damage (int): Damage dealt
        lifetime (float): Time before despawn
    """

    def __init__(self, x: float, y: float, angle: float, speed: float = BOSS_PROJECTILE_SPEED):
        """
        Initialize boss projectile.

        Args:
            x: X position
            y: Y position
            angle: Direction angle
            speed: Projectile speed
        """
        super().__init__(x, y)
        self.angle = angle
        self.velocity = Vector2D.from_angle(angle, speed)
        self.damage = BOSS_DAMAGE
        self.lifetime = 5.0
        self.color = RED

        # Triangle shape
        self.vertices = [
            Vector2D(8, 0),
            Vector2D(-4, -4),
            Vector2D(-4, 4)
        ]

    def update(self, dt: float):
        """Update projectile."""
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False


class Boss(GameObject):
    """
    Base boss class.

    Attributes:
        boss_type (str): Type of boss
        max_health (int): Maximum health
        health (int): Current health
        attack_cooldown (float): Time until next attack
        level (int): Boss level
    """

    def __init__(self, x: float, y: float, boss_type: str, level: int = 1):
        """
        Initialize boss.

        Args:
            x: X position
            y: Y position
            boss_type: Boss type
            level: Boss level
        """
        super().__init__(x, y)
        self.boss_type = boss_type
        self.level = level

        # Health
        self.max_health = BOSS_HEALTH_BASE + (level * BOSS_HEALTH_PER_LEVEL)
        self.health = self.max_health

        # Combat
        self.attack_cooldown = 0
        self.attack_timer = BOSS_ATTACK_COOLDOWN
        self.damage = BOSS_DAMAGE

        # Movement
        self.velocity = Vector2D(0, 0)
        self.target_position: Vector2D = None

        # Generate shape based on type
        self._generate_shape()

    def _generate_shape(self):
        """Generate boss shape."""
        if self.boss_type == BOSS_ASTEROID_KING:
            self.color = ORANGE
            # Large irregular asteroid
            num_vertices = 12
            radius = 50
            self.vertices = []
            for i in range(num_vertices):
                angle = (2 * math.pi * i) / num_vertices
                r = radius + random.randint(-15, 15)
                self.vertices.append(Vector2D(r * math.cos(angle), r * math.sin(angle)))

        elif self.boss_type == BOSS_VOID_HUNTER:
            self.color = PURPLE
            # Sharp angular ship
            self.vertices = [
                Vector2D(40, 0),
                Vector2D(-20, -30),
                Vector2D(-10, -15),
                Vector2D(-30, 0),
                Vector2D(-10, 15),
                Vector2D(-20, 30)
            ]

        elif self.boss_type == BOSS_STAR_DESTROYER:
            self.color = RED
            # Star shape
            points = 8
            outer = 45
            inner = 20
            self.vertices = []
            for i in range(points * 2):
                angle = (math.pi * i) / points
                radius = outer if i % 2 == 0 else inner
                self.vertices.append(Vector2D(radius * math.cos(angle), radius * math.sin(angle)))

    def take_damage(self, damage: int):
        """
        Take damage.

        Args:
            damage: Damage amount
        """
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def get_health_percentage(self) -> float:
        """
        Get health as percentage.

        Returns:
            Health percentage (0-1)
        """
        return self.health / self.max_health if self.max_health > 0 else 0

    def update(self, dt: float, player_pos: Vector2D = None):
        """
        Update boss AI and movement.

        Args:
            dt: Delta time
            player_pos: Player position for targeting
        """
        if not self.alive:
            return

        # Update attack timer
        self.attack_timer -= dt

        # Boss-specific behavior
        if self.boss_type == BOSS_ASTEROID_KING:
            self._update_asteroid_king(dt, player_pos)
        elif self.boss_type == BOSS_VOID_HUNTER:
            self._update_void_hunter(dt, player_pos)
        elif self.boss_type == BOSS_STAR_DESTROYER:
            self._update_star_destroyer(dt, player_pos)

        # Update position
        super().update(dt)

        # Rotate
        self.angle += 0.5 * dt

    def _update_asteroid_king(self, dt: float, player_pos: Vector2D):
        """Asteroid King AI - slow movement, summons asteroids."""
        if player_pos:
            # Slow chase
            direction = (player_pos - self.position).normalize()
            self.velocity = direction * (BOSS_SPEED * 0.5)

    def _update_void_hunter(self, dt: float, player_pos: Vector2D):
        """Void Hunter AI - teleports and shoots bursts."""
        # Mostly stationary, occasional teleport
        self.velocity = self.velocity * 0.95

    def _update_star_destroyer(self, dt: float, player_pos: Vector2D):
        """Star Destroyer AI - circles player."""
        if player_pos:
            # Circle around player
            to_player = player_pos - self.position
            distance = to_player.magnitude()

            if distance > 200:
                # Move closer
                direction = to_player.normalize()
                self.velocity = direction * BOSS_SPEED
            else:
                # Circle
                perpendicular = Vector2D(-to_player.y, to_player.x).normalize()
                self.velocity = perpendicular * BOSS_SPEED

    def can_attack(self) -> bool:
        """Check if boss can attack."""
        return self.attack_timer <= 0

    def attack(self, player_pos: Vector2D) -> List[BossProjectile]:
        """
        Execute boss attack.

        Args:
            player_pos: Player position

        Returns:
            List of projectiles created
        """
        if not self.can_attack():
            return []

        self.attack_timer = BOSS_ATTACK_COOLDOWN
        projectiles = []

        if self.boss_type == BOSS_ASTEROID_KING:
            # Radial burst
            for i in range(BOSS_PROJECTILE_COUNT):
                angle = (2 * math.pi * i) / BOSS_PROJECTILE_COUNT
                projectile = BossProjectile(self.position.x, self.position.y, angle)
                projectiles.append(projectile)

        elif self.boss_type == BOSS_VOID_HUNTER:
            # Triple shot at player
            if player_pos:
                base_angle = math.atan2(player_pos.y - self.position.y,
                                       player_pos.x - self.position.x)
                for offset in [-0.3, 0, 0.3]:
                    angle = base_angle + offset
                    projectile = BossProjectile(self.position.x, self.position.y, angle, 250)
                    projectiles.append(projectile)

        elif self.boss_type == BOSS_STAR_DESTROYER:
            # Spiral pattern
            for i in range(6):
                angle = self.angle + (math.pi * i / 3)
                projectile = BossProjectile(self.position.x, self.position.y, angle)
                projectiles.append(projectile)

        return projectiles

    def summon_asteroids(self, count: int = 3) -> List[Asteroid]:
        """
        Summon asteroids (Asteroid King ability).

        Args:
            count: Number of asteroids

        Returns:
            List of summoned asteroids
        """
        asteroids = []
        for _ in range(count):
            # Spawn around boss
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 150)
            x = self.position.x + math.cos(angle) * distance
            y = self.position.y + math.sin(angle) * distance

            # Clamp to screen
            x = max(50, min(WIDTH - 50, x))
            y = max(50, min(HEIGHT - 50, y))

            asteroid = Asteroid(x, y, random.randint(1, 2))
            asteroids.append(asteroid)

        return asteroids

    def draw(self, screen: pygame.Surface):
        """Draw boss with health bar."""
        if not self.alive:
            return

        # Draw boss
        super().draw(screen)

        # Draw health bar
        bar_width = 100
        bar_height = 10
        bar_x = self.position.x - bar_width // 2
        bar_y = self.position.y - self.get_radius() - 20

        # Background
        pygame.draw.rect(screen, (50, 50, 50),
                        (bar_x, bar_y, bar_width, bar_height))

        # Health
        health_width = int(bar_width * self.get_health_percentage())
        health_color = (
            int(255 * (1 - self.get_health_percentage())),
            int(255 * self.get_health_percentage()),
            0
        )
        pygame.draw.rect(screen, health_color,
                        (bar_x, bar_y, health_width, bar_height))

        # Border
        pygame.draw.rect(screen, (255, 255, 255),
                        (bar_x, bar_y, bar_width, bar_height), 1)
