#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tolik - The main character (like Isaac).
"""

import pygame
import math
from typing import List, Tuple
from ..constants import *
from ..utils.vector2d import Vector2D


class Tolik:
    """Main player character."""

    def __init__(self, x: float, y: float):
        """
        Initialize Tolik.

        Args:
            x: Starting X position
            y: Starting Y position
        """
        # Position and movement
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.size = TOLIK_SIZE

        # Stats
        self.max_health = TOLIK_MAX_HEALTH
        self.health = self.max_health
        self.speed = TOLIK_START_SPEED
        self.damage = TOLIK_START_DAMAGE
        self.tears_per_second = TOLIK_START_TEARS
        self.range = TOLIK_START_RANGE
        self.shot_speed = TOLIK_START_SHOT_SPEED

        # Shooting
        self.last_shoot_direction = Vector2D(0, 1)  # Down by default
        self.tear_cooldown = 0
        self.tear_delay = 1.0 / self.tears_per_second

        # Movement direction (for animation)
        self.facing_direction = 'down'  # 'up', 'down', 'left', 'right'

        # Special tears
        self.triple_shot = False
        self.homing_tears = False
        self.piercing_tears = False

        # State
        self.alive = True
        self.invincible = False
        self.invincibility_timer = 0

        # Inventory
        self.bombs = 1
        self.keys = 1
        self.coins = 0

        # Visual
        self.color = (255, 200, 180)  # Skin color
        self.head_color = (200, 150, 120)
        self.blink_timer = 0

    def update(self, dt: float):
        """
        Update Tolik.

        Args:
            dt: Delta time in seconds
        """
        # Update position
        self.position = self.position + self.velocity * dt

        # Update cooldowns
        if self.tear_cooldown > 0:
            self.tear_cooldown -= dt

        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False

        # Update blink
        self.blink_timer += dt

        # Constrain to room bounds
        self._constrain_to_room()

    def move(self, direction: Vector2D):
        """
        Set movement direction.

        Args:
            direction: Normalized direction vector
        """
        self.velocity = direction.normalize() * self.speed

        # Update facing direction for animation
        if abs(direction.x) > abs(direction.y):
            self.facing_direction = 'right' if direction.x > 0 else 'left'
        elif direction.y != 0:
            self.facing_direction = 'down' if direction.y > 0 else 'up'

    def stop(self):
        """Stop movement."""
        self.velocity = Vector2D(0, 0)

    def shoot(self, direction: Vector2D) -> List['Tear']:
        """
        Shoot tears in direction.

        Args:
            direction: Shoot direction

        Returns:
            List of Tear objects created
        """
        if self.tear_cooldown > 0:
            return []

        self.tear_cooldown = self.tear_delay
        tears = []

        # Import here to avoid circular import
        from .tear import Tear

        # Normalize direction
        dir_normalized = direction.normalize()
        if dir_normalized.magnitude() == 0:
            dir_normalized = self.last_shoot_direction
        else:
            self.last_shoot_direction = dir_normalized

        if self.triple_shot:
            # Three tears in a spread
            angles = [-0.3, 0, 0.3]  # -15°, 0°, +15° spread
            base_angle = dir_normalized.angle()

            for angle_offset in angles:
                tear_dir = Vector2D.from_angle(base_angle + angle_offset)
                tear = Tear(
                    self.position.x,
                    self.position.y,
                    tear_dir,
                    self.shot_speed,
                    self.damage,
                    self.range,
                    self.homing_tears,
                    self.piercing_tears
                )
                tears.append(tear)
        else:
            # Single tear
            tear = Tear(
                self.position.x,
                self.position.y,
                dir_normalized,
                self.shot_speed,
                self.damage,
                self.range,
                self.homing_tears,
                self.piercing_tears
            )
            tears.append(tear)

        return tears

    def take_damage(self, damage: int = 1):
        """
        Take damage.

        Args:
            damage: Damage amount (in half-hearts)
        """
        if self.invincible:
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
        else:
            # Become invincible temporarily
            self.invincible = True
            self.invincibility_timer = INVINCIBILITY_TIME

    def heal(self, amount: int = 2):
        """
        Heal health.

        Args:
            amount: Heal amount (in half-hearts)
        """
        self.health = min(self.health + amount, self.max_health)

    def add_heart_container(self):
        """Add a full heart container (2 half-hearts)."""
        self.max_health += 2
        self.health += 2

    def add_coins(self, amount: int):
        """Add coins."""
        self.coins += amount

    def add_bombs(self, amount: int):
        """Add bombs."""
        self.bombs += amount

    def add_keys(self, amount: int):
        """Add keys."""
        self.keys += amount

    def apply_stat_upgrade(self, stat: str, value: float):
        """
        Apply stat upgrade.

        Args:
            stat: Stat name ('damage', 'speed', 'tears', 'range', 'shot_speed')
            value: Value to add
        """
        if stat == 'damage':
            self.damage += value
        elif stat == 'speed':
            self.speed += value
        elif stat == 'tears':
            self.tears_per_second += value
            self.tear_delay = 1.0 / max(0.1, self.tears_per_second)
        elif stat == 'range':
            self.range += value
        elif stat == 'shot_speed':
            self.shot_speed += value

    def _constrain_to_room(self):
        """Keep Tolik inside room bounds."""
        half_size = self.size // 2

        # Left/Right bounds
        if self.position.x < ROOM_OFFSET_X + half_size:
            self.position.x = ROOM_OFFSET_X + half_size
        elif self.position.x > ROOM_OFFSET_X + ROOM_WIDTH - half_size:
            self.position.x = ROOM_OFFSET_X + ROOM_WIDTH - half_size

        # Top/Bottom bounds
        if self.position.y < ROOM_OFFSET_Y + half_size:
            self.position.y = ROOM_OFFSET_Y + half_size
        elif self.position.y > ROOM_OFFSET_Y + ROOM_HEIGHT - half_size:
            self.position.y = ROOM_OFFSET_Y + ROOM_HEIGHT - half_size

    def is_near_door(self, door_direction: str) -> bool:
        """
        Check if Tolik is near a door.

        Args:
            door_direction: Door direction

        Returns:
            True if near door
        """
        threshold = 40

        if door_direction == DOOR_TOP:
            return self.position.y < ROOM_OFFSET_Y + threshold
        elif door_direction == DOOR_BOTTOM:
            return self.position.y > ROOM_OFFSET_Y + ROOM_HEIGHT - threshold
        elif door_direction == DOOR_LEFT:
            return self.position.x < ROOM_OFFSET_X + threshold
        elif door_direction == DOOR_RIGHT:
            return self.position.x > ROOM_OFFSET_X + ROOM_WIDTH - threshold

        return False

    def get_rect(self) -> pygame.Rect:
        """
        Get collision rectangle.

        Returns:
            pygame.Rect
        """
        half_size = self.size // 2
        return pygame.Rect(
            self.position.x - half_size,
            self.position.y - half_size,
            self.size,
            self.size
        )

    def draw(self, screen: pygame.Surface):
        """
        Draw Tolik.

        Args:
            screen: Pygame surface
        """
        # Blink when invincible
        if self.invincible and int(self.blink_timer * 10) % 2 == 0:
            return

        pos = self.position.int_tuple()

        # Body (circle)
        pygame.draw.circle(screen, self.color, pos, self.size // 2)

        # Head (smaller circle on top)
        head_offset = 8 if self.facing_direction == 'up' else -8
        head_y = pos[1] - head_offset
        pygame.draw.circle(screen, self.head_color, (pos[0], head_y), self.size // 3)

        # Eyes
        eye_size = 3
        eye_offset_x = 6
        eye_offset_y = head_y - 3

        if self.facing_direction == 'left':
            eye_offset_x = -8
            pygame.draw.circle(screen, BLACK, (pos[0] + eye_offset_x, eye_offset_y), eye_size)
        elif self.facing_direction == 'right':
            eye_offset_x = 8
            pygame.draw.circle(screen, BLACK, (pos[0] + eye_offset_x, eye_offset_y), eye_size)
        else:
            # Two eyes
            pygame.draw.circle(screen, BLACK, (pos[0] - eye_offset_x, eye_offset_y), eye_size)
            pygame.draw.circle(screen, BLACK, (pos[0] + eye_offset_x, eye_offset_y), eye_size)

        # Draw health bar above (for debugging)
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 4
            bar_x = pos[0] - bar_width // 2
            bar_y = pos[1] - self.size - 10

            # Background
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))

            # Health
            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, RED, (bar_x, bar_y, health_width, bar_height))
