#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enemy classes - various monsters for Tolik to fight.
"""

import pygame
import math
import random
from typing import List, Optional
from ..constants import *
from ..utils.vector2d import Vector2D
from .tear import EnemyTear


class Enemy:
    """Base enemy class."""

    def __init__(self, x: float, y: float, enemy_type: str):
        """
        Initialize enemy.

        Args:
            x: X position
            y: Y position
            enemy_type: Type of enemy
        """
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.enemy_type = enemy_type

        # Stats from constants
        stats = ENEMY_STATS[enemy_type]
        self.max_health = stats['health']
        self.health = self.max_health
        self.speed = stats['speed']
        self.damage = stats['damage']
        self.size = stats['size']
        self.color = stats['color']
        self.behavior = stats['behavior']
        self.score_value = stats['score']

        # State
        self.alive = True
        self.state_timer = 0
        self.behavior_timer = random.uniform(0, 2)

        # Visual
        self.blink_timer = 0
        self.flash_white = False

    def update(self, dt: float, player_pos: Optional[Vector2D] = None):
        """
        Update enemy AI and movement.

        Args:
            dt: Delta time
            player_pos: Player position for AI
        """
        self.state_timer += dt
        self.behavior_timer += dt

        # Update based on behavior
        if self.behavior == 'fly_random':
            self._update_fly_random(dt)
        elif self.behavior == 'chase':
            self._update_chase(dt, player_pos)
        elif self.behavior == 'wander':
            self._update_wander(dt)
        elif self.behavior == 'hop':
            self._update_hop(dt, player_pos)

        # Move
        self.position = self.position + self.velocity * dt

        # Constrain to room
        self._constrain_to_room()

        # Update blink
        if self.blink_timer > 0:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.flash_white = False

    def _update_fly_random(self, dt: float):
        """Random flying movement."""
        if self.behavior_timer > 1.5:
            self.behavior_timer = 0
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = Vector2D.from_angle(angle, self.speed)

    def _update_chase(self, dt: float, player_pos: Optional[Vector2D]):
        """Chase player."""
        if player_pos:
            direction = (player_pos - self.position).normalize()
            self.velocity = direction * self.speed

    def _update_wander(self, dt: float):
        """Slow wandering movement."""
        if self.behavior_timer > 2.0:
            self.behavior_timer = 0
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = Vector2D.from_angle(angle, self.speed)

    def _update_hop(self, dt: float, player_pos: Optional[Vector2D]):
        """Hop toward player periodically."""
        if self.velocity.magnitude() < 10:
            # Stopped, ready to hop
            if self.behavior_timer > 1.0 and player_pos:
                self.behavior_timer = 0
                direction = (player_pos - self.position).normalize()
                self.velocity = direction * self.speed
        else:
            # Slowing down
            self.velocity = self.velocity * 0.95

    def _constrain_to_room(self):
        """Keep enemy inside room."""
        margin = self.size // 2

        if self.position.x < ROOM_OFFSET_X + margin:
            self.position.x = ROOM_OFFSET_X + margin
            self.velocity.x = abs(self.velocity.x)
        elif self.position.x > ROOM_OFFSET_X + ROOM_WIDTH - margin:
            self.position.x = ROOM_OFFSET_X + ROOM_WIDTH - margin
            self.velocity.x = -abs(self.velocity.x)

        if self.position.y < ROOM_OFFSET_Y + margin:
            self.position.y = ROOM_OFFSET_Y + margin
            self.velocity.y = abs(self.velocity.y)
        elif self.position.y > ROOM_OFFSET_Y + ROOM_HEIGHT - margin:
            self.position.y = ROOM_OFFSET_Y + ROOM_HEIGHT - margin
            self.velocity.y = -abs(self.velocity.y)

    def take_damage(self, damage: float):
        """
        Take damage.

        Args:
            damage: Damage amount
        """
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # Visual feedback
        self.flash_white = True
        self.blink_timer = 0.1

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
        Draw enemy.

        Args:
            screen: Pygame surface
        """
        pos = self.position.int_tuple()

        # Color (flash white when hit)
        color = WHITE if self.flash_white else self.color

        # Draw based on type
        if self.enemy_type == ENEMY_FLY:
            self._draw_fly(screen, pos, color)
        elif self.enemy_type == ENEMY_SPIDER:
            self._draw_spider(screen, pos, color)
        elif self.enemy_type == ENEMY_BLOB:
            self._draw_blob(screen, pos, color)
        elif self.enemy_type == ENEMY_HOPPER:
            self._draw_hopper(screen, pos, color)
        else:
            # Default circle
            pygame.draw.circle(screen, color, pos, self.size // 2)

        # Health bar
        if self.health < self.max_health:
            self._draw_health_bar(screen, pos)

    def _draw_fly(self, screen: pygame.Surface, pos: tuple, color: tuple):
        """Draw fly enemy."""
        # Body
        pygame.draw.circle(screen, color, pos, self.size // 2)
        # Eyes
        eye_offset = self.size // 4
        pygame.draw.circle(screen, BLACK, (pos[0] - eye_offset, pos[1] - 2), 3)
        pygame.draw.circle(screen, BLACK, (pos[0] + eye_offset, pos[1] - 2), 3)

    def _draw_spider(self, screen: pygame.Surface, pos: tuple, color: tuple):
        """Draw spider enemy."""
        # Body
        pygame.draw.circle(screen, color, pos, self.size // 2)
        # Legs (8 lines)
        for i in range(8):
            angle = i * math.pi / 4
            start_x = pos[0] + math.cos(angle) * (self.size // 3)
            start_y = pos[1] + math.sin(angle) * (self.size // 3)
            end_x = pos[0] + math.cos(angle) * self.size // 2
            end_y = pos[1] + math.sin(angle) * self.size // 2
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 2)

    def _draw_blob(self, screen: pygame.Surface, pos: tuple, color: tuple):
        """Draw blob enemy."""
        # Oval shape
        rect = pygame.Rect(pos[0] - self.size // 2, pos[1] - self.size // 3,
                          self.size, self.size * 2 // 3)
        pygame.draw.ellipse(screen, color, rect)
        # Slime drops
        for i in range(3):
            drop_x = pos[0] + random.randint(-self.size // 4, self.size // 4)
            drop_y = pos[1] + self.size // 3
            pygame.draw.circle(screen, color, (drop_x, drop_y), 3)

    def _draw_hopper(self, screen: pygame.Surface, pos: tuple, color: tuple):
        """Draw hopper enemy."""
        # Body
        pygame.draw.circle(screen, color, pos, self.size // 2)
        # Legs
        leg_length = self.size // 2
        pygame.draw.line(screen, color, pos, (pos[0] - leg_length, pos[1] + leg_length), 3)
        pygame.draw.line(screen, color, pos, (pos[0] + leg_length, pos[1] + leg_length), 3)

    def _draw_health_bar(self, screen: pygame.Surface, pos: tuple):
        """Draw health bar above enemy."""
        bar_width = self.size
        bar_height = 4
        bar_x = pos[0] - bar_width // 2
        bar_y = pos[1] - self.size - 8

        # Background
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))

        # Health
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, health_width, bar_height))


class Shooter(Enemy):
    """Enemy that shoots tears at player."""

    def __init__(self, x: float, y: float):
        """Initialize shooter."""
        super().__init__(x, y, ENEMY_SHOOTER)
        self.shoot_cooldown = 0
        self.shoot_delay = 2.0

    def update(self, dt: float, player_pos: Optional[Vector2D] = None):
        """Update shooter."""
        super().update(dt, player_pos)

        # Shooting
        self.shoot_cooldown -= dt

    def can_shoot(self) -> bool:
        """Check if can shoot."""
        return self.shoot_cooldown <= 0

    def shoot(self, player_pos: Vector2D) -> Optional[EnemyTear]:
        """
        Shoot at player.

        Args:
            player_pos: Player position

        Returns:
            EnemyTear or None
        """
        if not self.can_shoot():
            return None

        self.shoot_cooldown = self.shoot_delay

        direction = (player_pos - self.position).normalize()
        tear = EnemyTear(
            self.position.x,
            self.position.y,
            direction,
            speed=250,
            damage=self.damage
        )

        return tear


class Charger(Enemy):
    """Enemy that charges at player."""

    def __init__(self, x: float, y: float):
        """Initialize charger."""
        super().__init__(x, y, ENEMY_CHARGER)
        self.charging = False
        self.charge_direction = Vector2D(0, 0)

    def update(self, dt: float, player_pos: Optional[Vector2D] = None):
        """Update charger."""
        if not player_pos:
            super().update(dt, player_pos)
            return

        if not self.charging:
            # Wait then charge
            if self.behavior_timer > 2.0:
                self.behavior_timer = 0
                self.charging = True
                self.charge_direction = (player_pos - self.position).normalize()
                self.velocity = self.charge_direction * self.speed
        else:
            # Charging
            if self.behavior_timer > 1.5:
                self.charging = False
                self.velocity = Vector2D(0, 0)

        self.position = self.position + self.velocity * dt
        self._constrain_to_room()

        if self.blink_timer > 0:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.flash_white = False
