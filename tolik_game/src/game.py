#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main game class for Tolik: Escape from the Basement.
"""

import pygame
import sys
import random
from typing import List
from .constants import *
from .utils.vector2d import Vector2D
from .entities.tolik import Tolik
from .entities.tear import Tear, EnemyTear
from .entities.enemy import Enemy, Shooter, Charger
from .systems.level import Level
from .systems.room import Room


class Game:
    """Main game controller."""

    def __init__(self):
        """Initialize game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tolik: Escape from the Basement")
        self.clock = pygame.time.Clock()

        # Game state
        self.state = STATE_PLAYING
        self.floor_number = 1
        self.score = 0

        # Player
        start_x = ROOM_OFFSET_X + ROOM_WIDTH // 2
        start_y = ROOM_OFFSET_Y + ROOM_HEIGHT // 2
        self.tolik = Tolik(start_x, start_y)

        # Level
        self.level = Level(FLOORS[0])

        # Entities
        self.tears: List[Tear] = []
        self.enemy_tears: List[EnemyTear] = []
        self.enemies: List[Enemy] = []

        # Spawn enemies in starting room
        self._spawn_room_enemies()

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def _spawn_room_enemies(self):
        """Spawn enemies in current room."""
        self.enemies.clear()

        room = self.level.current_room
        if not room:
            return

        # No enemies in certain rooms
        if room.room_type in [ROOM_TYPE_START, ROOM_TYPE_SHOP, ROOM_TYPE_TREASURE]:
            room.cleared = True
            return

        if room.room_type == ROOM_TYPE_BOSS:
            # TODO: Spawn boss
            return

        if room.cleared:
            return

        # Spawn normal enemies
        count_range = ROOM_ENEMY_COUNT.get(room.room_type, (3, 6))
        enemy_count = random.randint(*count_range)

        spawn_positions = room.get_spawn_positions(enemy_count)
        enemy_types = [ENEMY_FLY, ENEMY_SPIDER, ENEMY_BLOB, ENEMY_HOPPER]

        for pos in spawn_positions:
            enemy_type = random.choice(enemy_types)

            if enemy_type == ENEMY_SHOOTER:
                enemy = Shooter(pos[0], pos[1])
            elif enemy_type == ENEMY_CHARGER:
                enemy = Charger(pos[0], pos[1])
            else:
                enemy = Enemy(pos[0], pos[1], enemy_type)

            self.enemies.append(enemy)

        room.enemy_count = len(self.enemies)

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING

    def handle_input(self, dt: float):
        """Handle continuous input."""
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()

        # Movement (WASD)
        move_dir = Vector2D(0, 0)
        if keys[pygame.K_w]:
            move_dir.y -= 1
        if keys[pygame.K_s]:
            move_dir.y += 1
        if keys[pygame.K_a]:
            move_dir.x -= 1
        if keys[pygame.K_d]:
            move_dir.x += 1

        if move_dir.magnitude() > 0:
            self.tolik.move(move_dir)
        else:
            self.tolik.stop()

        # Shooting (Arrow keys)
        shoot_dir = Vector2D(0, 0)
        if keys[pygame.K_UP]:
            shoot_dir.y -= 1
        if keys[pygame.K_DOWN]:
            shoot_dir.y += 1
        if keys[pygame.K_LEFT]:
            shoot_dir.x -= 1
        if keys[pygame.K_RIGHT]:
            shoot_dir.x += 1

        if shoot_dir.magnitude() > 0:
            new_tears = self.tolik.shoot(shoot_dir)
            self.tears.extend(new_tears)

    def update(self, dt: float):
        """Update game logic."""
        if self.state != STATE_PLAYING:
            return

        # Update player
        self.tolik.update(dt)

        # Update tears
        for tear in self.tears[:]:
            tear.update(dt, self.enemies)
            if not tear.alive:
                self.tears.remove(tear)

        # Update enemy tears
        for tear in self.enemy_tears[:]:
            tear.update(dt)
            if not tear.alive:
                self.enemy_tears.remove(tear)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.tolik.position)

            # Enemy shooting
            if isinstance(enemy, Shooter) and enemy.alive:
                tear = enemy.shoot(self.tolik.position)
                if tear:
                    self.enemy_tears.append(tear)

        # Collision detection
        self._check_collisions()

        # Check room cleared
        self._check_room_cleared()

        # Check door transitions
        self._check_door_transitions()

        # Check game over
        if not self.tolik.alive:
            self.state = STATE_GAME_OVER

    def _check_collisions(self):
        """Check all collisions."""
        # Player tears vs enemies
        for tear in self.tears[:]:
            if not tear.alive:
                continue

            tear_rect = tear.get_rect()

            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                if not tear.can_hit_enemy(enemy):
                    continue

                enemy_rect = enemy.get_rect()

                if tear_rect.colliderect(enemy_rect):
                    enemy.take_damage(tear.damage)
                    tear.hit_enemy(enemy)

                    if not enemy.alive:
                        self.score += enemy.score_value

        # Enemy tears vs player
        if self.tolik.alive and not self.tolik.invincible:
            tolik_rect = self.tolik.get_rect()

            for tear in self.enemy_tears[:]:
                tear_rect = tear.get_rect()

                if tolik_rect.colliderect(tear_rect):
                    self.tolik.take_damage(tear.damage)
                    tear.alive = False

        # Enemies vs player (contact damage)
        if self.tolik.alive and not self.tolik.invincible:
            tolik_rect = self.tolik.get_rect()

            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                enemy_rect = enemy.get_rect()

                if tolik_rect.colliderect(enemy_rect):
                    self.tolik.take_damage(enemy.damage)

    def _check_room_cleared(self):
        """Check if current room is cleared."""
        room = self.level.current_room
        if not room or room.cleared:
            return

        # Check if all enemies dead
        all_dead = all(not enemy.alive for enemy in self.enemies)

        if all_dead and len(self.enemies) > 0:
            room.clear()

    def _check_door_transitions(self):
        """Check if player is entering a door."""
        room = self.level.current_room
        if not room:
            return

        # Only allow transitions if room cleared or safe room
        if not room.cleared and room.room_type == ROOM_TYPE_NORMAL:
            return

        # Check each door
        for direction in [DOOR_TOP, DOOR_BOTTOM, DOOR_LEFT, DOOR_RIGHT]:
            if self.tolik.is_near_door(direction):
                next_room = self.level.get_adjacent_room(room, direction)
                if next_room:
                    self._transition_to_room(next_room, direction)
                    break

    def _transition_to_room(self, next_room: Room, from_direction: str):
        """Transition to next room."""
        self.level.enter_room(next_room)

        # Clear projectiles
        self.tears.clear()
        self.enemy_tears.clear()

        # Reposition player at opposite door
        if from_direction == DOOR_TOP:
            self.tolik.position = Vector2D(
                ROOM_OFFSET_X + ROOM_WIDTH // 2,
                ROOM_OFFSET_Y + ROOM_HEIGHT - 60
            )
        elif from_direction == DOOR_BOTTOM:
            self.tolik.position = Vector2D(
                ROOM_OFFSET_X + ROOM_WIDTH // 2,
                ROOM_OFFSET_Y + 60
            )
        elif from_direction == DOOR_LEFT:
            self.tolik.position = Vector2D(
                ROOM_OFFSET_X + ROOM_WIDTH - 60,
                ROOM_OFFSET_Y + ROOM_HEIGHT // 2
            )
        elif from_direction == DOOR_RIGHT:
            self.tolik.position = Vector2D(
                ROOM_OFFSET_X + 60,
                ROOM_OFFSET_Y + ROOM_HEIGHT // 2
            )

        # Spawn enemies
        self._spawn_room_enemies()

    def draw(self):
        """Draw everything."""
        self.screen.fill(BLACK)

        # Draw room
        if self.level.current_room:
            self.level.current_room.draw(self.screen, self.level.floor_name)

        # Draw enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(self.screen)

        # Draw tears
        for tear in self.tears:
            tear.draw(self.screen)

        for tear in self.enemy_tears:
            tear.draw(self.screen)

        # Draw player
        self.tolik.draw(self.screen)

        # Draw HUD
        self._draw_hud()

        # Draw pause overlay
        if self.state == STATE_PAUSED:
            self._draw_pause()

        # Draw game over
        if self.state == STATE_GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hud(self):
        """Draw HUD."""
        # Hearts
        heart_x = 20
        heart_y = 20
        full_hearts = self.tolik.health // 2
        half_heart = self.tolik.health % 2

        for i in range(self.tolik.max_health // 2):
            x = heart_x + i * 30

            if i < full_hearts:
                # Full heart
                pygame.draw.circle(self.screen, RED, (x, heart_y), 10)
                pygame.draw.circle(self.screen, RED, (x + 12, heart_y), 10)
                points = [(x, heart_y + 8), (x + 6, heart_y + 20), (x + 12, heart_y + 8)]
                pygame.draw.polygon(self.screen, RED, points)
            elif i == full_hearts and half_heart:
                # Half heart
                pygame.draw.circle(self.screen, RED, (x, heart_y), 10)
                pygame.draw.circle(self.screen, GRAY, (x + 12, heart_y), 10, 2)
            else:
                # Empty
                pygame.draw.circle(self.screen, GRAY, (x, heart_y), 10, 2)
                pygame.draw.circle(self.screen, GRAY, (x + 12, heart_y), 10, 2)

        # Score
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (WINDOW_WIDTH - 150, 20))

        # Room counter
        room_text = self.font_small.render(
            f"Rooms: {self.level.get_visited_count()}/{self.level.get_room_count()}",
            True, WHITE
        )
        self.screen.blit(room_text, (WINDOW_WIDTH - 150, 50))

    def _draw_pause(self):
        """Draw pause overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("PAUSED", True, WHITE)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("GAME OVER", True, RED)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(text, rect)

        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.handle_input(dt)
            self.update(dt)
            self.draw()
