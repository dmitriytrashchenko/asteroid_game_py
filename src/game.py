#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main game controller.
"""

import pygame
import sys
import math
import random
from typing import List, Optional

from .constants import *
from .utils.settings import Settings
from .utils.vector2d import Vector2D
from .entities.ship import Ship
from .entities.asteroid import Asteroid
from .entities.bullet import Bullet
from .entities.particle import ParticleSystem
from .entities.powerup import PowerUp
from .ui.button import Button
from .ui.slider import Slider
from .managers.sound_manager import SoundManager
from .managers.highscore_manager import HighScoreManager
from .managers.achievement_manager import AchievementManager


class Game:
    """
    Main game class managing all game logic and states.

    Attributes:
        screen (pygame.Surface): Main game window
        clock (pygame.time.Clock): Game clock
        settings (Settings): Game settings
        state (int): Current game state
        Various game objects and managers
    """

    def __init__(self):
        """Initialize game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Векторные Астероиды v3.0")
        self.clock = pygame.time.Clock()

        # Managers
        self.settings = Settings()
        self.sound_manager = SoundManager(self.settings)
        self.highscore_manager = HighScoreManager()
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem()

        # Game state
        self.state = STATE_MENU
        self.ship: Optional[Ship] = None
        self.bullets: List[Bullet] = []
        self.asteroids: List[Asteroid] = []
        self.powerups: List[PowerUp] = []

        # Game stats
        self.score = 0
        self.lives = MAX_LIVES
        self.wave = 1
        self.asteroids_destroyed = 0
        self.powerups_collected = 0
        self.game_time = 0
        self.respawn_timer = 0
        self.last_shot_time = 0

        # Wave stats for achievements
        self.wave_hit_count = 0

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # UI
        self._setup_menus()

    def _setup_menus(self):
        """Setup all menu buttons and UI elements."""
        # Main menu
        self.menu_buttons = [
            Button(WIDTH//2 - 100, 250, 200, 50, "НОВАЯ ИГРА", self.start_game),
            Button(WIDTH//2 - 100, 320, 200, 50, "РЕКОРДЫ", lambda: self._set_state(STATE_HIGHSCORES)),
            Button(WIDTH//2 - 100, 390, 200, 50, "ДОСТИЖЕНИЯ", lambda: self._set_state(STATE_ACHIEVEMENTS)),
            Button(WIDTH//2 - 100, 460, 200, 50, "НАСТРОЙКИ", lambda: self._set_state(STATE_SETTINGS)),
            Button(WIDTH//2 - 100, 530, 200, 50, "ВЫХОД", self.quit_game)
        ]

        # Settings menu
        self.settings_sliders = [
            Slider(WIDTH//2 - 150, 200, 300, 0.0, 1.0,
                  self.settings.music_volume, "Музыка"),
            Slider(WIDTH//2 - 150, 280, 300, 0.0, 1.0,
                  self.settings.sound_volume, "Звуки")
        ]

        self.difficulty_buttons = [
            Button(WIDTH//2 - 210, 360, 130, 40, "ЛЕГКО",
                  lambda: self._set_difficulty(DIFFICULTY_EASY)),
            Button(WIDTH//2 - 65, 360, 130, 40, "НОРМАЛЬНО",
                  lambda: self._set_difficulty(DIFFICULTY_NORMAL)),
            Button(WIDTH//2 + 80, 360, 130, 40, "СЛОЖНО",
                  lambda: self._set_difficulty(DIFFICULTY_HARD))
        ]

        self.settings_buttons = [
            Button(WIDTH//2 - 100, 480, 200, 50, "НАЗАД",
                  lambda: self._set_state(STATE_MENU))
        ]

        # High scores menu
        self.highscore_buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "НАЗАД",
                  lambda: self._set_state(STATE_MENU))
        ]

        # Achievements menu
        self.achievement_buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "НАЗАД",
                  lambda: self._set_state(STATE_MENU))
        ]

    def _set_state(self, state: int):
        """
        Change game state.

        Args:
            state: New state to set
        """
        self.state = state

    def _set_difficulty(self, difficulty: int):
        """
        Set game difficulty.

        Args:
            difficulty: Difficulty level
        """
        self.settings.difficulty = difficulty
        self.settings.save_settings()

    def start_game(self):
        """Start a new game."""
        # Reset stats
        self.score = 0
        self.lives = MAX_LIVES
        self.wave = 1
        self.asteroids_destroyed = 0
        self.powerups_collected = 0
        self.game_time = 0
        self.wave_hit_count = 0

        # Clear objects
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.particle_system.clear()

        # Create ship
        self.ship = Ship(WIDTH // 2, HEIGHT // 2, self.settings)
        self.ship.make_invulnerable()

        # Start first wave
        self._start_wave()

        self.state = STATE_PLAYING

    def _start_wave(self):
        """Start a new wave of asteroids."""
        # Clear existing asteroids and powerups
        self.asteroids = []
        self.powerups = []
        self.wave_hit_count = 0

        # Calculate asteroid count (increases with wave)
        base_count = DIFFICULTY_ASTEROID_COUNT.get(self.settings.difficulty, 5)
        asteroid_count = base_count + (self.wave - 1) * 2

        # Spawn asteroids
        for _ in range(asteroid_count):
            x, y = self._get_safe_spawn_position()
            size = random.randint(2, 3)  # Medium or large
            asteroid = Asteroid(x, y, size, self.settings.difficulty)
            self.asteroids.append(asteroid)

        # Check wave achievement
        self.achievement_manager.check_achievement('wave', self.wave)

    def _get_safe_spawn_position(self) -> tuple:
        """
        Get a spawn position away from ship.

        Returns:
            (x, y) tuple
        """
        if not self.ship:
            return (random.randint(0, WIDTH), random.randint(0, HEIGHT))

        while True:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)

            dx = x - self.ship.position.x
            dy = y - self.ship.position.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > ASTEROID_MIN_SPAWN_DISTANCE:
                return (x, y)

    def quit_game(self):
        """Quit the game."""
        self.settings.save_settings()
        self.achievement_manager.save_achievements()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            # Handle UI events based on state
            if self.state == STATE_MENU:
                for button in self.menu_buttons:
                    button.handle_event(event)

            elif self.state == STATE_SETTINGS:
                for slider in self.settings_sliders:
                    slider.handle_event(event)
                for button in self.difficulty_buttons:
                    button.handle_event(event)
                for button in self.settings_buttons:
                    button.handle_event(event)

                # Update settings from sliders
                self.settings.music_volume = self.settings_sliders[0].get_value()
                self.settings.sound_volume = self.settings_sliders[1].get_value()
                self.sound_manager.update_volume()
                self.settings.save_settings()

            elif self.state == STATE_HIGHSCORES:
                for button in self.highscore_buttons:
                    button.handle_event(event)

            elif self.state == STATE_ACHIEVEMENTS:
                for button in self.achievement_buttons:
                    button.handle_event(event)

    def _handle_keydown(self, event: pygame.event.Event):
        """
        Handle key press events.

        Args:
            event: Key down event
        """
        if self.state == STATE_PLAYING:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
        elif self.state == STATE_PAUSED:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            elif event.key == pygame.K_m:
                self.state = STATE_MENU
        elif self.state == STATE_GAME_OVER:
            if event.key == pygame.K_r:
                self.start_game()
            elif event.key == pygame.K_m:
                self.state = STATE_MENU

    def handle_input(self):
        """Handle continuous keyboard input."""
        if self.state != STATE_PLAYING or not self.ship or not self.ship.alive:
            return

        keys = pygame.key.get_pressed()

        # Reset controls
        self.ship.reset_controls()

        # Movement
        if keys[self.settings.controls['thrust']]:
            self.ship.thrust = 1
            # Create thrust particles
            if random.random() < 0.5:
                rear_pos = Vector2D(-10, 0).rotate(self.ship.angle) + self.ship.position
                self.particle_system.create_thrust_particles(
                    rear_pos.x, rear_pos.y, self.ship.angle + math.pi
                )

        if keys[self.settings.controls['left']]:
            self.ship.rotation_speed = -SHIP_ROTATION_SPEED

        if keys[self.settings.controls['right']]:
            self.ship.rotation_speed = SHIP_ROTATION_SPEED

        # Shooting
        if keys[self.settings.controls['shoot']]:
            self._shoot()

    def _shoot(self):
        """Fire bullet(s) from ship."""
        if not self.ship or not self.ship.alive:
            return

        # Check cooldown
        current_time = pygame.time.get_ticks()
        cooldown = RAPID_FIRE_COOLDOWN if self.ship.has_powerup(POWERUP_RAPID_FIRE) else SHOT_COOLDOWN

        if current_time - self.last_shot_time < cooldown:
            return

        self.last_shot_time = current_time

        # Triple shot power-up
        if self.ship.has_powerup(POWERUP_TRIPLE_SHOT):
            angles = [self.ship.angle - 0.2, self.ship.angle, self.ship.angle + 0.2]
        else:
            angles = [self.ship.angle]

        # Create bullets
        for angle in angles:
            nose_pos = Vector2D(15, 0).rotate(self.ship.angle) + self.ship.position
            bullet = Bullet(nose_pos.x, nose_pos.y, angle)
            self.bullets.append(bullet)

        self.sound_manager.play_shoot()

    def update(self, dt: float):
        """
        Update game logic.

        Args:
            dt: Delta time in seconds
        """
        if self.state == STATE_PLAYING:
            self._update_game(dt)

        # Always update particles
        self.particle_system.update(dt)

    def _update_game(self, dt: float):
        """
        Update game state.

        Args:
            dt: Delta time in seconds
        """
        # Update game time
        self.game_time += dt

        # Check time achievements
        self.achievement_manager.check_achievement('time', int(self.game_time))

        # Update respawn timer
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self._respawn_ship()

        # Update ship
        if self.ship and self.ship.alive:
            self.ship.update(dt)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.alive:
                self.bullets.remove(bullet)

        # Update asteroids
        for asteroid in self.asteroids:
            asteroid.update(dt)

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if not powerup.alive:
                self.powerups.remove(powerup)

        # Check collisions
        self._check_collisions()

        # Check wave complete
        if len(self.asteroids) == 0 and self.ship and self.ship.alive:
            # No hit achievement
            if self.wave_hit_count == 0:
                self.achievement_manager.check_achievement('no_hit', 1)

            self.wave += 1
            self._start_wave()

    def _check_collisions(self):
        """Check all collision interactions."""
        if not self.ship:
            return

        # Bullet vs Asteroid
        for bullet in self.bullets[:]:
            if not bullet.alive:
                continue

            for asteroid in self.asteroids[:]:
                if bullet.collides_with(asteroid):
                    # Destroy bullet
                    bullet.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

                    # Destroy asteroid
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)

                    # Add score
                    score_value = asteroid.get_score_value()
                    difficulty_multiplier = [SCORE_MULTIPLIER_EASY, SCORE_MULTIPLIER_NORMAL, SCORE_MULTIPLIER_HARD][self.settings.difficulty]
                    self.score += score_value * difficulty_multiplier

                    # Increment destroyed count
                    self.asteroids_destroyed += 1

                    # Check achievements
                    self.achievement_manager.check_achievement('score', self.score)
                    self.achievement_manager.check_achievement('asteroids', self.asteroids_destroyed)

                    # Create explosion effect
                    self.particle_system.create_asteroid_explosion(
                        asteroid.position.x, asteroid.position.y, asteroid.size
                    )
                    self.sound_manager.play_explosion(asteroid.size > 1)

                    # Split asteroid
                    new_asteroids = asteroid.split(self.settings.difficulty)
                    self.asteroids.extend(new_asteroids)

                    # Maybe spawn powerup
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        powerup_type = random.choice([
                            POWERUP_SHIELD,
                            POWERUP_RAPID_FIRE,
                            POWERUP_TRIPLE_SHOT,
                            POWERUP_EXTRA_LIFE
                        ])
                        powerup = PowerUp(asteroid.position.x, asteroid.position.y, powerup_type)
                        self.powerups.append(powerup)

                    break

        # Ship vs Asteroid
        if self.ship and self.ship.alive and self.ship.can_be_hit():
            for asteroid in self.asteroids:
                if self.ship.collides_with(asteroid):
                    self._ship_hit()
                    break

        # Ship vs PowerUp
        if self.ship and self.ship.alive:
            for powerup in self.powerups[:]:
                if self.ship.collides_with(powerup):
                    self._collect_powerup(powerup)
                    if powerup in self.powerups:
                        self.powerups.remove(powerup)

    def _ship_hit(self):
        """Handle ship being hit."""
        if not self.ship:
            return

        self.wave_hit_count += 1

        # Create explosion
        self.particle_system.create_ship_explosion(
            self.ship.position.x, self.ship.position.y
        )
        self.sound_manager.play_ship_hit()

        # Lose life
        self.lives -= 1
        self.ship.alive = False

        if self.lives > 0:
            # Respawn after delay
            self.respawn_timer = RESPAWN_DELAY
        else:
            # Game over
            self._game_over()

    def _respawn_ship(self):
        """Respawn the ship."""
        self.ship = Ship(WIDTH // 2, HEIGHT // 2, self.settings)
        self.ship.make_invulnerable()

    def _collect_powerup(self, powerup: PowerUp):
        """
        Collect a power-up.

        Args:
            powerup: PowerUp object
        """
        powerup_type = powerup.get_type()

        if powerup_type == POWERUP_EXTRA_LIFE:
            self.lives = min(self.lives + 1, 5)
        else:
            self.ship.activate_powerup(powerup_type, POWERUP_DURATION)

        self.powerups_collected += 1
        self.achievement_manager.check_achievement('powerups', self.powerups_collected)

        self.sound_manager.play_powerup()

    def _game_over(self):
        """Handle game over."""
        # Save high score
        position = self.highscore_manager.add_score(
            self.score, self.wave, self.settings.difficulty
        )

        # Save achievements
        self.achievement_manager.save_achievements()

        self.state = STATE_GAME_OVER

    def draw(self):
        """Draw everything."""
        self.screen.fill(BLACK)

        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_SETTINGS:
            self._draw_settings()
        elif self.state == STATE_PLAYING:
            self._draw_game()
        elif self.state == STATE_PAUSED:
            self._draw_game()
            self._draw_pause()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over()
        elif self.state == STATE_HIGHSCORES:
            self._draw_highscores()
        elif self.state == STATE_ACHIEVEMENTS:
            self._draw_achievements()

        # Always draw particles on top
        self.particle_system.draw(self.screen)

        # Draw achievement notifications
        self._draw_achievement_notifications()

        pygame.display.flip()

    def _draw_menu(self):
        """Draw main menu."""
        # Title
        title = self.font_large.render("АСТЕРОИДЫ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 120))
        self.screen.blit(title, title_rect)

        # Version
        version = self.font_small.render("v3.0", True, GRAY)
        self.screen.blit(version, (WIDTH - 60, HEIGHT - 30))

        # Decorative asteroids
        for i in range(8):
            angle = i * math.pi / 4 + pygame.time.get_ticks() / 1000
            x = WIDTH//2 + math.cos(angle) * 150
            y = 120 + math.sin(angle) * 60
            size = 3 + int(2 * math.sin(pygame.time.get_ticks() / 500 + i))
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), size, 1)

        # High score
        high_score = self.highscore_manager.get_highest_score()
        hs_text = self.font_small.render(f"Рекорд: {high_score}", True, YELLOW)
        self.screen.blit(hs_text, (10, HEIGHT - 30))

        # Buttons
        for button in self.menu_buttons:
            button.draw(self.screen)

    def _draw_settings(self):
        """Draw settings menu."""
        # Title
        title = self.font_large.render("НАСТРОЙКИ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        self.screen.blit(title, title_rect)

        # Sliders
        for slider in self.settings_sliders:
            slider.draw(self.screen)

        # Difficulty label
        diff_label = self.font_medium.render("Сложность:", True, WHITE)
        self.screen.blit(diff_label, (WIDTH//2 - 210, 320))

        # Difficulty buttons (highlight selected)
        for i, button in enumerate(self.difficulty_buttons):
            if i == self.settings.difficulty:
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
            button.draw(self.screen)

        # Back button
        for button in self.settings_buttons:
            button.draw(self.screen)

    def _draw_game(self):
        """Draw game screen."""
        # Draw game objects
        if self.ship:
            self.ship.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw HUD
        self._draw_hud()

    def _draw_hud(self):
        """Draw heads-up display."""
        # Score
        score_text = self.font_medium.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.font_small.render(f"Жизни: {'♥' * self.lives}", True, RED)
        self.screen.blit(lives_text, (10, 50))

        # Wave
        wave_text = self.font_small.render(f"Волна: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 75))

        # High score
        high_score = self.highscore_manager.get_highest_score()
        hs_text = self.font_small.render(f"Рекорд: {high_score}", True, YELLOW)
        self.screen.blit(hs_text, (WIDTH - 150, 10))

        # Active powerups
        y_offset = 40
        for powerup_type, time_remaining in self.ship.active_powerups.items() if self.ship else []:
            powerup = PowerUp(0, 0, powerup_type)
            text = f"{powerup.get_description()}: {int(time_remaining)}s"
            powerup_text = self.font_small.render(text, True, POWERUP_COLORS.get(powerup_type, WHITE))
            self.screen.blit(powerup_text, (WIDTH - 250, y_offset))
            y_offset += 25

    def _draw_pause(self):
        """Draw pause overlay."""
        # Darken screen
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.font_large.render("ПАУЗА", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)

        # Instructions
        inst_text = self.font_medium.render("ESC - продолжить  |  M - меню", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        self.screen.blit(inst_text, inst_rect)

    def _draw_game_over(self):
        """Draw game over screen."""
        self.screen.fill(BLACK)

        # Game Over
        go_text = self.font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        go_rect = go_text.get_rect(center=(WIDTH//2, 150))
        self.screen.blit(go_text, go_rect)

        # Stats
        stats_y = 250
        stats = [
            f"Финальный счет: {self.score}",
            f"Волна: {self.wave}",
            f"Уничтожено астероидов: {self.asteroids_destroyed}",
            f"Собрано бонусов: {self.powerups_collected}",
            f"Время: {int(self.game_time)}с"
        ]

        for stat in stats:
            stat_text = self.font_small.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WIDTH//2, stats_y))
            self.screen.blit(stat_text, stat_rect)
            stats_y += 30

        # New high score?
        if self.score == self.highscore_manager.get_highest_score() and self.score > 0:
            new_record = self.font_medium.render("НОВЫЙ РЕКОРД!", True, YELLOW)
            new_record_rect = new_record.get_rect(center=(WIDTH//2, stats_y + 20))
            self.screen.blit(new_record, new_record_rect)

        # Instructions
        inst_text = self.font_medium.render("R - заново  |  M - меню", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        self.screen.blit(inst_text, inst_rect)

    def _draw_highscores(self):
        """Draw high scores screen."""
        # Title
        title = self.font_large.render("ТАБЛИЦА РЕКОРДОВ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 60))
        self.screen.blit(title, title_rect)

        # Scores
        scores = self.highscore_manager.get_top_scores(10)
        y_offset = 130

        for i, entry in enumerate(scores):
            rank = i + 1
            color = YELLOW if rank <= 3 else WHITE

            # Rank and score
            rank_text = self.font_medium.render(
                f"{rank}. {entry.score:6d}  Волна {entry.wave:2d}  {self.highscore_manager.get_difficulty_name(entry.difficulty)}",
                True, color
            )
            self.screen.blit(rank_text, (WIDTH//2 - 250, y_offset))

            # Date
            date_text = self.font_small.render(entry.get_formatted_date(), True, GRAY)
            self.screen.blit(date_text, (WIDTH//2 + 150, y_offset + 5))

            y_offset += 40

        # Back button
        for button in self.highscore_buttons:
            button.draw(self.screen)

    def _draw_achievements(self):
        """Draw achievements screen."""
        # Title
        title = self.font_large.render("ДОСТИЖЕНИЯ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 40))
        self.screen.blit(title, title_rect)

        # Progress
        progress = self.achievement_manager.get_completion_percentage()
        progress_text = self.font_small.render(
            f"Прогресс: {self.achievement_manager.get_unlocked_count()}/{self.achievement_manager.get_total_count()} ({progress:.0f}%)",
            True, YELLOW
        )
        self.screen.blit(progress_text, (WIDTH//2 - 100, 90))

        # Achievements (scrollable list)
        achievements = self.achievement_manager.get_all_achievements()
        y_offset = 130
        max_display = 10

        for achievement in achievements[:max_display]:
            color = GREEN if achievement.unlocked else GRAY

            # Name and description
            name_text = self.font_small.render(
                f"{'✓' if achievement.unlocked else '○'} {achievement.name}",
                True, color
            )
            self.screen.blit(name_text, (50, y_offset))

            desc_text = self.font_small.render(
                achievement.description, True, color
            )
            self.screen.blit(desc_text, (70, y_offset + 20))

            y_offset += 50

        # Back button
        for button in self.achievement_buttons:
            button.draw(self.screen)

    def _draw_achievement_notifications(self):
        """Draw achievement unlock notifications."""
        newly_unlocked = self.achievement_manager.get_newly_unlocked()

        if newly_unlocked:
            # Show first unlocked achievement
            achievement = newly_unlocked[0]

            # Draw notification box
            box_width = 400
            box_height = 80
            box_x = WIDTH//2 - box_width//2
            box_y = 50

            pygame.draw.rect(self.screen, YELLOW, (box_x, box_y, box_width, box_height), 3)

            # Title
            title_text = self.font_medium.render("ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", True, YELLOW)
            title_rect = title_text.get_rect(center=(WIDTH//2, box_y + 25))
            self.screen.blit(title_text, title_rect)

            # Achievement name
            name_text = self.font_small.render(achievement.name, True, WHITE)
            name_rect = name_text.get_rect(center=(WIDTH//2, box_y + 55))
            self.screen.blit(name_text, name_rect)

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.handle_input()
            self.update(dt)
            self.draw()

        self.quit_game()
