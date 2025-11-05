#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main game controller - v4.0 Roguelike Edition.
"""

import pygame
import sys
import math
import random
from typing import List, Optional

from .constants import *
from .utils.settings import Settings
from .utils.vector2d import Vector2D
from .utils.localization import get_localization, t
from .entities.ship import Ship
from .entities.asteroid import Asteroid
from .entities.bullet import Bullet
from .entities.particle import ParticleSystem
from .entities.powerup import PowerUp
from .entities.coin import Coin
from .entities.boss import Boss, BossProjectile
from .ui.button import Button
from .ui.slider import Slider
from .managers.sound_manager import SoundManager
from .managers.highscore_manager import HighScoreManager
from .managers.achievement_manager import AchievementManager
from .managers.progress_manager import ProgressManager
from .roguelike.level import Level
from .roguelike.minimap import Minimap
from .roguelike.shop import Shop


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

        # Settings and localization
        self.settings = Settings()
        self.localization = get_localization()
        self.localization.set_language(self.settings.language)

        # Display setup with fullscreen support
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids v4.0 - Roguelike Edition")
        self.clock = pygame.time.Clock()

        # Managers
        self.sound_manager = SoundManager(self.settings)
        self.highscore_manager = HighScoreManager()
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem()
        self.progress_manager = ProgressManager()

        # Game state
        self.state = STATE_MENU
        self.ship: Optional[Ship] = None
        self.bullets: List[Bullet] = []
        self.asteroids: List[Asteroid] = []
        self.powerups: List[PowerUp] = []
        self.coins: List[Coin] = []
        self.boss_projectiles: List[BossProjectile] = []

        # Roguelike systems
        self.level: Optional[Level] = None
        self.minimap: Optional[Minimap] = None
        self.shop: Optional[Shop] = None
        self.boss: Optional[Boss] = None

        # Game stats
        self.score = 0
        self.player_coins = 0
        self.current_level_number = 1
        self.asteroids_destroyed = 0
        self.powerups_collected = 0
        self.bosses_defeated = 0
        self.rooms_cleared = 0
        self.game_time = 0
        self.respawn_timer = 0
        self.last_shot_time = 0

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
            Button(WIDTH//2 - 100, 250, 200, 50, t('menu.new_game'), self.start_game),
            Button(WIDTH//2 - 100, 320, 200, 50, t('menu.meta_progression'), lambda: self._set_state(STATE_META_PROGRESSION)),
            Button(WIDTH//2 - 100, 390, 200, 50, t('menu.highscores'), lambda: self._set_state(STATE_HIGHSCORES)),
            Button(WIDTH//2 - 100, 460, 200, 50, t('menu.achievements'), lambda: self._set_state(STATE_ACHIEVEMENTS)),
            Button(WIDTH//2 - 100, 530, 200, 50, t('menu.settings'), lambda: self._set_state(STATE_SETTINGS)),
            Button(WIDTH//2 - 100, 600, 200, 50, t('menu.quit'), self.quit_game)
        ]

        # Settings menu
        self.settings_sliders = [
            Slider(WIDTH//2 - 150, 200, 300, 0.0, 1.0,
                  self.settings.music_volume, t('settings.music')),
            Slider(WIDTH//2 - 150, 280, 300, 0.0, 1.0,
                  self.settings.sound_volume, t('settings.sound'))
        ]

        self.difficulty_buttons = [
            Button(WIDTH//2 - 210, 380, 130, 40, t('settings.difficulty_easy'),
                  lambda: self._set_difficulty(DIFFICULTY_EASY)),
            Button(WIDTH//2 - 65, 380, 130, 40, t('settings.difficulty_normal'),
                  lambda: self._set_difficulty(DIFFICULTY_NORMAL)),
            Button(WIDTH//2 + 80, 380, 130, 40, t('settings.difficulty_hard'),
                  lambda: self._set_difficulty(DIFFICULTY_HARD))
        ]

        self.language_buttons = [
            Button(WIDTH//2 - 100, 460, 90, 40, "RU",
                  lambda: self._set_language('ru')),
            Button(WIDTH//2 + 10, 460, 90, 40, "EN",
                  lambda: self._set_language('en'))
        ]

        self.fullscreen_button = Button(WIDTH//2 - 100, 530, 200, 40,
                                        t('settings.fullscreen'),
                                        self._toggle_fullscreen)

        self.settings_buttons = [
            Button(WIDTH//2 - 100, 600, 200, 50, t('menu.back'),
                  lambda: self._set_state(STATE_MENU))
        ]

        # High scores menu
        self.highscore_buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, t('menu.back'),
                  lambda: self._set_state(STATE_MENU))
        ]

        # Achievements menu
        self.achievement_buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, t('menu.back'),
                  lambda: self._set_state(STATE_MENU))
        ]

        # Meta-progression menu
        self.meta_buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, t('menu.back'),
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

    def _set_language(self, language: str):
        """
        Set game language.

        Args:
            language: Language code ('ru' or 'en')
        """
        self.settings.language = language
        self.settings.save_settings()
        self.localization.set_language(language)
        # Rebuild menus with new language
        self._setup_menus()

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.settings.fullscreen = not self.settings.fullscreen
        self.settings.save_settings()

        # Recreate display
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids v4.0 - Roguelike Edition")

    def start_game(self):
        """Start a new roguelike run."""
        # Reset stats
        self.score = 0
        self.current_level_number = 1
        self.asteroids_destroyed = 0
        self.powerups_collected = 0
        self.bosses_defeated = 0
        self.rooms_cleared = 0
        self.game_time = 0

        # Clear objects
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.coins = []
        self.boss_projectiles = []
        self.boss = None
        self.particle_system.clear()

        # Create ship with meta-progression upgrades
        self.ship = Ship(WIDTH // 2, HEIGHT // 2, self.settings)
        self.ship.apply_upgrades(
            max_health_bonus=self.progress_manager.get_max_health_bonus(),
            damage_bonus=self.progress_manager.get_damage_bonus(),
            fire_rate_bonus=self.progress_manager.get_fire_rate_bonus(),
            speed_bonus=self.progress_manager.get_move_speed_bonus()
        )
        self.ship.make_invulnerable()

        # Starting coins from meta-progression
        self.player_coins = self.progress_manager.get_starting_coins()

        # Generate first level
        self.level = Level(level_number=self.current_level_number, difficulty=self.settings.difficulty)
        self.minimap = Minimap(self.level)

        # Enter starting room
        self.level.enter_room(self.level.start_room)

        # Spawn enemies in starting room
        self._spawn_room_enemies()

        self.state = STATE_PLAYING

    def _spawn_room_enemies(self):
        """Spawn enemies based on current room type."""
        if not self.level or not self.level.current_room:
            return

        room = self.level.current_room

        # Clear existing enemies
        self.asteroids = []
        self.boss = None

        if room.room_type == ROOM_TYPE_BOSS:
            # Spawn boss
            boss_types = [BOSS_ASTEROID_KING, BOSS_VOID_HUNTER, BOSS_STAR_DESTROYER]
            boss_type = random.choice(boss_types)
            self.boss = Boss(WIDTH // 2, HEIGHT // 2, boss_type, self.current_level_number)

        elif room.room_type == ROOM_TYPE_NORMAL:
            # Spawn asteroids
            count = room.enemies_count
            for _ in range(count):
                pos = random.choice(room.get_spawn_positions())
                size = random.randint(2, 3)
                asteroid = Asteroid(pos[0], pos[1], size, self.settings.difficulty)
                self.asteroids.append(asteroid)

        elif room.room_type == ROOM_TYPE_SHOP:
            # Open shop
            self.shop = Shop()
            self.state = STATE_SHOP

        elif room.room_type == ROOM_TYPE_TREASURE:
            # Spawn coins and maybe a powerup
            for _ in range(random.randint(5, 10)):
                x = random.randint(100, WIDTH - 100)
                y = random.randint(100, HEIGHT - 100)
                value = random.choice([COIN_VALUE_SMALL, COIN_VALUE_MEDIUM, COIN_VALUE_LARGE])
                coin = Coin(x, y, value)
                self.coins.append(coin)

            # Maybe spawn powerup
            if random.random() < 0.5:
                powerup_type = random.choice([POWERUP_SHIELD, POWERUP_RAPID_FIRE,
                                             POWERUP_TRIPLE_SHOT])
                powerup = PowerUp(WIDTH // 2, HEIGHT // 2, powerup_type)
                self.powerups.append(powerup)

            # Treasure rooms are instantly cleared
            room.clear()

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

    def _check_room_cleared(self):
        """Check if current room is cleared and open doors."""
        if not self.level or not self.level.current_room:
            return

        room = self.level.current_room

        # Check if all enemies are dead
        enemies_alive = len(self.asteroids) > 0 or (self.boss and self.boss.alive)

        if not enemies_alive and not room.cleared:
            # Room cleared!
            room.clear()
            self.rooms_cleared += 1

            # Drop coins
            if room.room_type != ROOM_TYPE_TREASURE:
                coin_count = random.randint(2, 5)
                for _ in range(coin_count):
                    x = random.randint(100, WIDTH - 100)
                    y = random.randint(100, HEIGHT - 100)
                    coin = Coin(x, y, COIN_VALUE_SMALL)
                    self.coins.append(coin)

    def _check_door_transitions(self):
        """Check if player is touching a door to transition rooms."""
        if not self.ship or not self.level or not self.level.current_room:
            return

        room = self.level.current_room

        # Only allow transitions if room is cleared or is safe room
        if not room.cleared and room.room_type not in [ROOM_TYPE_START, ROOM_TYPE_SHOP, ROOM_TYPE_TREASURE]:
            return

        # Check each door
        ship_x, ship_y = self.ship.position.x, self.ship.position.y

        # Top door
        if room.has_door(DOOR_TOP) and ship_y < 50:
            self._transition_to_room(DOOR_TOP)

        # Bottom door
        elif room.has_door(DOOR_BOTTOM) and ship_y > HEIGHT - 50:
            self._transition_to_room(DOOR_BOTTOM)

        # Left door
        elif room.has_door(DOOR_LEFT) and ship_x < 50:
            self._transition_to_room(DOOR_LEFT)

        # Right door
        elif room.has_door(DOOR_RIGHT) and ship_x > WIDTH - 50:
            self._transition_to_room(DOOR_RIGHT)

    def _transition_to_room(self, direction: str):
        """
        Transition to adjacent room.

        Args:
            direction: Direction of door
        """
        if not self.level or not self.level.current_room:
            return

        current_room = self.level.current_room
        next_room = self.level.get_adjacent_room(current_room, direction)

        if next_room:
            # Enter new room
            self.level.enter_room(next_room)

            # Clear projectiles
            self.bullets = []
            self.boss_projectiles = []

            # Reposition ship
            if direction == DOOR_TOP:
                self.ship.position = Vector2D(WIDTH // 2, HEIGHT - 100)
            elif direction == DOOR_BOTTOM:
                self.ship.position = Vector2D(WIDTH // 2, 100)
            elif direction == DOOR_LEFT:
                self.ship.position = Vector2D(WIDTH - 100, HEIGHT // 2)
            elif direction == DOOR_RIGHT:
                self.ship.position = Vector2D(100, HEIGHT // 2)

            # Reset velocity
            self.ship.velocity = Vector2D(0, 0)

            # Spawn enemies if not cleared
            if not next_room.cleared:
                self._spawn_room_enemies()

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
                for button in self.language_buttons:
                    button.handle_event(event)
                self.fullscreen_button.handle_event(event)
                for button in self.settings_buttons:
                    button.handle_event(event)

                # Update settings from sliders
                self.settings.music_volume = self.settings_sliders[0].get_value()
                self.settings.sound_volume = self.settings_sliders[1].get_value()
                self.sound_manager.update_volume()
                self.settings.save_settings()

            elif self.state == STATE_SHOP:
                self._handle_shop_input(event)

            elif self.state == STATE_META_PROGRESSION:
                self._handle_meta_input(event)
                for button in self.meta_buttons:
                    button.handle_event(event)

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

    def _handle_shop_input(self, event: pygame.event.Event):
        """Handle shop input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                # Leave shop
                self.state = STATE_PLAYING
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                # Purchase item
                item_index = event.key - pygame.K_1
                if self.shop and self.shop.can_purchase(item_index, self.player_coins):
                    item = self.shop.purchase_item(item_index)
                    self.player_coins -= item.price

                    # Apply item effect
                    if item.effect_type == 'restore_health':
                        if self.ship:
                            self.ship.heal(2)
                    elif item.effect_type == 'max_health':
                        if self.ship:
                            self.ship.increase_max_health(2)
                    elif item.effect_type == 'damage':
                        if self.ship:
                            self.ship.damage += 1
                    elif item.effect_type == 'fire_rate':
                        if self.ship:
                            self.ship.fire_rate_multiplier += 0.2
                    elif item.effect_type == 'speed':
                        if self.ship:
                            self.ship.speed_multiplier += 0.15

                    self.sound_manager.play_powerup()
            elif event.key == pygame.K_r:
                # Reroll shop
                if self.player_coins >= SHOP_REROLL_COST:
                    self.shop.reroll()
                    self.player_coins -= SHOP_REROLL_COST
                    self.sound_manager.play_powerup()

    def _handle_meta_input(self, event: pygame.event.Event):
        """Handle meta-progression input."""
        if event.type == pygame.KEYDOWN:
            upgrade_keys = {
                pygame.K_1: UPGRADE_MAX_HEALTH,
                pygame.K_2: UPGRADE_BASE_DAMAGE,
                pygame.K_3: UPGRADE_FIRE_RATE,
                pygame.K_4: UPGRADE_MOVE_SPEED,
                pygame.K_5: UPGRADE_STARTING_COINS,
                pygame.K_6: UPGRADE_COIN_MULTIPLIER
            }

            if event.key in upgrade_keys:
                upgrade_type = upgrade_keys[event.key]
                if self.progress_manager.can_afford_upgrade(upgrade_type):
                    self.progress_manager.purchase_upgrade(upgrade_type)
                    self.sound_manager.play_powerup()
                else:
                    self.sound_manager.play_ship_hit()

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

        # Update boss
        if self.boss and self.boss.alive:
            player_pos = self.ship.position if self.ship and self.ship.alive else None
            self.boss.update(dt, player_pos)

            # Boss attack
            if self.boss.can_attack():
                projectiles = self.boss.attack(player_pos)
                self.boss_projectiles.extend(projectiles)

        # Update boss projectiles
        for projectile in self.boss_projectiles[:]:
            projectile.update(dt)
            if not projectile.alive:
                self.boss_projectiles.remove(projectile)

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

        # Update coins
        for coin in self.coins[:]:
            coin.update(dt)
            if not coin.alive:
                self.coins.remove(coin)

        # Check collisions
        self._check_collisions()

        # Check room cleared
        self._check_room_cleared()

        # Check door transitions
        self._check_door_transitions()

        # Check level complete
        if self.level and self.level.is_level_complete():
            self._next_level()

    def _next_level(self):
        """Advance to next level."""
        self.current_level_number += 1

        # Clear objects
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.coins = []
        self.boss_projectiles = []
        self.boss = None

        # Generate new level
        self.level = Level(level_number=self.current_level_number, difficulty=self.settings.difficulty)
        self.minimap = Minimap(self.level)

        # Enter starting room
        self.level.enter_room(self.level.start_room)

        # Reset ship position
        self.ship.position = Vector2D(WIDTH // 2, HEIGHT // 2)
        self.ship.velocity = Vector2D(0, 0)
        self.ship.make_invulnerable()

        # Spawn enemies
        self._spawn_room_enemies()

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

        # Bullet vs Boss
        if self.boss and self.boss.alive:
            for bullet in self.bullets[:]:
                if not bullet.alive:
                    continue

                if bullet.collides_with(self.boss):
                    # Damage boss
                    damage = self.ship.damage if self.ship else 1
                    self.boss.take_damage(damage)

                    # Destroy bullet
                    bullet.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

                    # Check if boss dead
                    if not self.boss.alive:
                        self.bosses_defeated += 1
                        self.score += 1000
                        self.achievement_manager.check_achievement('boss', self.bosses_defeated)

                        # Create explosion
                        self.particle_system.create_asteroid_explosion(
                            self.boss.position.x, self.boss.position.y, 4
                        )
                        self.sound_manager.play_explosion(True)

                        # Drop lots of coins
                        for _ in range(random.randint(10, 20)):
                            angle = random.uniform(0, 2 * math.pi)
                            distance = random.uniform(20, 80)
                            x = self.boss.position.x + math.cos(angle) * distance
                            y = self.boss.position.y + math.sin(angle) * distance
                            value = random.choice([COIN_VALUE_MEDIUM, COIN_VALUE_LARGE])
                            coin = Coin(x, y, value)
                            self.coins.append(coin)

                    break

        # Boss Projectile vs Ship
        if self.ship and self.ship.alive and self.ship.can_be_hit():
            for projectile in self.boss_projectiles[:]:
                if self.ship.collides_with(projectile):
                    self._ship_hit(projectile.damage)
                    projectile.alive = False
                    if projectile in self.boss_projectiles:
                        self.boss_projectiles.remove(projectile)
                    break

        # Ship vs PowerUp
        if self.ship and self.ship.alive:
            for powerup in self.powerups[:]:
                if self.ship.collides_with(powerup):
                    self._collect_powerup(powerup)
                    if powerup in self.powerups:
                        self.powerups.remove(powerup)

        # Ship vs Coin
        if self.ship and self.ship.alive:
            for coin in self.coins[:]:
                if self.ship.collides_with(coin):
                    value = coin.get_value()
                    multiplier = self.progress_manager.get_coin_multiplier()
                    self.player_coins += int(value * multiplier)
                    coin.alive = False
                    if coin in self.coins:
                        self.coins.remove(coin)
                    self.sound_manager.play_powerup()

    def _ship_hit(self, damage: int = 1):
        """
        Handle ship being hit.

        Args:
            damage: Damage amount (in half-hearts)
        """
        if not self.ship:
            return

        # Take damage
        self.ship.take_damage(damage)

        # Sound effect
        self.sound_manager.play_ship_hit()

        # Check if dead
        if not self.ship.is_alive():
            # Create explosion
            self.particle_system.create_ship_explosion(
                self.ship.position.x, self.ship.position.y
            )

            # Game over
            self._game_over()

    def _respawn_ship(self):
        """Respawn the ship (not used in roguelike mode)."""
        pass

    def _collect_powerup(self, powerup: PowerUp):
        """
        Collect a power-up.

        Args:
            powerup: PowerUp object
        """
        powerup_type = powerup.get_type()

        if powerup_type == POWERUP_EXTRA_LIFE:
            # Heal 2 half-hearts (1 full heart)
            if self.ship:
                self.ship.heal(2)
        else:
            self.ship.activate_powerup(powerup_type, POWERUP_DURATION)

        self.powerups_collected += 1
        self.achievement_manager.check_achievement('powerups', self.powerups_collected)

        self.sound_manager.play_powerup()

    def _game_over(self):
        """Handle game over."""
        # Record run in meta-progression
        self.progress_manager.record_run_completion(
            level_reached=self.current_level_number,
            bosses_defeated=self.bosses_defeated,
            coins_collected=self.player_coins,
            rooms_cleared=self.rooms_cleared
        )

        # Give currency for meta-progression
        currency_earned = self.player_coins // 2  # 50% conversion
        self.progress_manager.add_currency(currency_earned)

        # Save high score
        position = self.highscore_manager.add_score(
            self.score, self.current_level_number, self.settings.difficulty
        )

        # Save achievements
        self.achievement_manager.save_achievements()

        # Save progress
        self.progress_manager.save_progress()

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
        elif self.state == STATE_SHOP:
            self._draw_shop()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over()
        elif self.state == STATE_HIGHSCORES:
            self._draw_highscores()
        elif self.state == STATE_ACHIEVEMENTS:
            self._draw_achievements()
        elif self.state == STATE_META_PROGRESSION:
            self._draw_meta_progression()

        # Always draw particles on top
        self.particle_system.draw(self.screen)

        # Draw achievement notifications
        self._draw_achievement_notifications()

        pygame.display.flip()

    def _draw_menu(self):
        """Draw main menu."""
        # Title
        title = self.font_large.render(t('menu.title'), True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 120))
        self.screen.blit(title, title_rect)

        # Version
        version = self.font_small.render("v4.0 Roguelike", True, GRAY)
        self.screen.blit(version, (WIDTH - 120, HEIGHT - 30))

        # Decorative asteroids
        for i in range(8):
            angle = i * math.pi / 4 + pygame.time.get_ticks() / 1000
            x = WIDTH//2 + math.cos(angle) * 150
            y = 120 + math.sin(angle) * 60
            size = 3 + int(2 * math.sin(pygame.time.get_ticks() / 500 + i))
            pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), size, 1)

        # High score
        high_score = self.highscore_manager.get_highest_score()
        hs_text = self.font_small.render(f"{t('menu.high_score')}: {high_score}", True, YELLOW)
        self.screen.blit(hs_text, (10, HEIGHT - 30))

        # Buttons
        for button in self.menu_buttons:
            button.draw(self.screen)

    def _draw_settings(self):
        """Draw settings menu."""
        # Title
        title = self.font_large.render(t('menu.settings'), True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        self.screen.blit(title, title_rect)

        # Sliders
        for slider in self.settings_sliders:
            slider.draw(self.screen)

        # Difficulty label
        diff_label = self.font_medium.render(f"{t('settings.difficulty')}:", True, WHITE)
        self.screen.blit(diff_label, (WIDTH//2 - 210, 340))

        # Difficulty buttons (highlight selected)
        for i, button in enumerate(self.difficulty_buttons):
            if i == self.settings.difficulty:
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
            button.draw(self.screen)

        # Language label
        lang_label = self.font_medium.render(f"{t('settings.language')}:", True, WHITE)
        self.screen.blit(lang_label, (WIDTH//2 - 210, 420))

        # Language buttons (highlight selected)
        for button in self.language_buttons:
            if (button.text == "RU" and self.settings.language == 'ru') or \
               (button.text == "EN" and self.settings.language == 'en'):
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
            button.draw(self.screen)

        # Fullscreen button (highlight if on)
        if self.settings.fullscreen:
            pygame.draw.rect(self.screen, GREEN, self.fullscreen_button.rect, 3)
        self.fullscreen_button.draw(self.screen)

        # Back button
        for button in self.settings_buttons:
            button.draw(self.screen)

    def _draw_game(self):
        """Draw game screen."""
        # Draw game objects
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        for coin in self.coins:
            coin.draw(self.screen)

        if self.boss:
            self.boss.draw(self.screen)

        for projectile in self.boss_projectiles:
            projectile.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        if self.ship:
            self.ship.draw(self.screen)

        # Draw doors
        self._draw_doors()

        # Draw HUD
        self._draw_hud()

        # Draw minimap
        if self.minimap:
            self.minimap.draw(self.screen)

    def _draw_doors(self):
        """Draw visible doors."""
        if not self.level or not self.level.current_room:
            return

        room = self.level.current_room
        door_color = GREEN if room.cleared or room.room_type in [ROOM_TYPE_START, ROOM_TYPE_SHOP, ROOM_TYPE_TREASURE] else RED

        # Draw door indicators
        if room.has_door(DOOR_TOP):
            pygame.draw.rect(self.screen, door_color, (WIDTH // 2 - 30, 10, 60, 20))
        if room.has_door(DOOR_BOTTOM):
            pygame.draw.rect(self.screen, door_color, (WIDTH // 2 - 30, HEIGHT - 30, 60, 20))
        if room.has_door(DOOR_LEFT):
            pygame.draw.rect(self.screen, door_color, (10, HEIGHT // 2 - 30, 20, 60))
        if room.has_door(DOOR_RIGHT):
            pygame.draw.rect(self.screen, door_color, (WIDTH - 30, HEIGHT // 2 - 30, 20, 60))

    def _draw_hud(self):
        """Draw heads-up display."""
        # Score
        score_text = self.font_medium.render(f"{t('hud.score')}: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Hearts
        if self.ship:
            heart_x = 10
            heart_y = 50
            full_hearts = self.ship.health // 2
            half_heart = self.ship.health % 2

            for i in range(self.ship.max_health // 2):
                if i < full_hearts:
                    # Full heart
                    pygame.draw.circle(self.screen, RED, (heart_x + i * 25, heart_y), 8)
                    pygame.draw.circle(self.screen, RED, (heart_x + i * 25 + 10, heart_y), 8)
                elif i == full_hearts and half_heart:
                    # Half heart
                    pygame.draw.circle(self.screen, RED, (heart_x + i * 25, heart_y), 8)
                    pygame.draw.circle(self.screen, GRAY, (heart_x + i * 25 + 10, heart_y), 8, 2)
                else:
                    # Empty heart
                    pygame.draw.circle(self.screen, GRAY, (heart_x + i * 25, heart_y), 8, 2)
                    pygame.draw.circle(self.screen, GRAY, (heart_x + i * 25 + 10, heart_y), 8, 2)

        # Coins
        coin_text = self.font_small.render(f"{t('hud.coins')}: {self.player_coins}", True, YELLOW)
        self.screen.blit(coin_text, (10, 80))

        # Level
        level_text = self.font_small.render(f"{t('hud.level')}: {self.current_level_number}", True, WHITE)
        self.screen.blit(level_text, (10, 105))

        # Room info
        if self.level and self.level.current_room:
            room_text = f"{t('hud.room')}: {self.level.get_visited_count()}/{self.level.get_room_count()}"
            room_display = self.font_small.render(room_text, True, WHITE)
            self.screen.blit(room_display, (10, 130))

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
        pause_text = self.font_large.render(t('game.paused'), True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)

        # Instructions
        inst_text = self.font_medium.render(f"{t('game.continue')} | M - {t('menu.title')}", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        self.screen.blit(inst_text, inst_rect)

    def _draw_game_over(self):
        """Draw game over screen."""
        self.screen.fill(BLACK)

        # Game Over
        go_text = self.font_large.render(t('game.game_over'), True, RED)
        go_rect = go_text.get_rect(center=(WIDTH//2, 150))
        self.screen.blit(go_text, go_rect)

        # Stats
        stats_y = 250
        stats = [
            f"{t('game.final_score')}: {self.score}",
            f"{t('hud.level')}: {self.current_level_number}",
            f"{t('game.bosses_defeated')}: {self.bosses_defeated}",
            f"{t('game.rooms_cleared')}: {self.rooms_cleared}",
            f"{t('game.coins_collected')}: {self.player_coins}",
            f"{t('game.time')}: {int(self.game_time)}s"
        ]

        for stat in stats:
            stat_text = self.font_small.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WIDTH//2, stats_y))
            self.screen.blit(stat_text, stat_rect)
            stats_y += 30

        # Currency earned
        currency_earned = self.player_coins // 2
        currency_text = self.font_medium.render(
            f"{t('game.currency_earned')}: {currency_earned}",
            True, CYAN
        )
        currency_rect = currency_text.get_rect(center=(WIDTH//2, stats_y + 20))
        self.screen.blit(currency_text, currency_rect)

        # New high score?
        if self.score == self.highscore_manager.get_highest_score() and self.score > 0:
            new_record = self.font_medium.render(t('game.new_record'), True, YELLOW)
            new_record_rect = new_record.get_rect(center=(WIDTH//2, stats_y + 60))
            self.screen.blit(new_record, new_record_rect)

        # Instructions
        inst_text = self.font_medium.render(f"R - {t('game.retry')}  |  M - {t('menu.title')}", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        self.screen.blit(inst_text, inst_rect)

    def _draw_highscores(self):
        """Draw high scores screen."""
        # Title
        title = self.font_large.render(t('menu.highscores'), True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 60))
        self.screen.blit(title, title_rect)

        # Scores
        scores = self.highscore_manager.get_top_scores(10)
        y_offset = 130

        for i, entry in enumerate(scores):
            rank = i + 1
            color = YELLOW if rank <= 3 else WHITE

            # Rank and score
            difficulty_name = self.highscore_manager.get_difficulty_name(entry.difficulty)
            rank_text = self.font_medium.render(
                f"{rank}. {entry.score:6d}  {t('hud.level')} {entry.wave:2d}  {difficulty_name}",
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
        title = self.font_large.render(t('menu.achievements'), True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 40))
        self.screen.blit(title, title_rect)

        # Progress
        progress = self.achievement_manager.get_completion_percentage()
        progress_text = self.font_small.render(
            f"{t('achievements.progress')}: {self.achievement_manager.get_unlocked_count()}/{self.achievement_manager.get_total_count()} ({progress:.0f}%)",
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

    def _draw_shop(self):
        """Draw shop interface."""
        if not self.shop:
            return

        # Title
        title = self.font_large.render(t('shop.title'), True, GREEN)
        title_rect = title.get_rect(center=(WIDTH//2, 60))
        self.screen.blit(title, title_rect)

        # Coins
        coins_text = self.font_medium.render(f"{t('hud.coins')}: {self.player_coins}", True, YELLOW)
        self.screen.blit(coins_text, (WIDTH//2 - 100, 120))

        # Items
        items = self.shop.get_all_items()
        y_offset = 180
        for i, item in enumerate(items):
            if item.purchased:
                color = GRAY
                status = t('shop.sold_out')
            elif self.shop.can_purchase(i, self.player_coins):
                color = WHITE
                status = f"{item.price} {t('hud.coins')}"
            else:
                color = RED
                status = f"{item.price} {t('hud.coins')}"

            # Item name
            name_text = self.font_medium.render(f"{i+1}. {t(item.name)}", True, color)
            self.screen.blit(name_text, (WIDTH//2 - 200, y_offset))

            # Price/status
            price_text = self.font_small.render(status, True, color)
            self.screen.blit(price_text, (WIDTH//2 + 100, y_offset + 5))

            # Description
            desc_text = self.font_small.render(t(item.description), True, color)
            self.screen.blit(desc_text, (WIDTH//2 - 180, y_offset + 30))

            y_offset += 70

        # Instructions
        inst = self.font_small.render(t('shop.instructions'), True, WHITE)
        inst_rect = inst.get_rect(center=(WIDTH//2, HEIGHT - 80))
        self.screen.blit(inst, inst_rect)

        leave = self.font_small.render(t('shop.leave'), True, WHITE)
        leave_rect = leave.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(leave, leave_rect)

    def _draw_meta_progression(self):
        """Draw meta-progression menu."""
        # Title
        title = self.font_large.render(t('meta.title'), True, CYAN)
        title_rect = title.get_rect(center=(WIDTH//2, 40))
        self.screen.blit(title, title_rect)

        # Currency
        currency_text = self.font_medium.render(
            f"{t('meta.currency')}: {self.progress_manager.permanent_currency}",
            True, YELLOW
        )
        self.screen.blit(currency_text, (WIDTH//2 - 150, 100))

        # Upgrades
        upgrades = [
            (UPGRADE_MAX_HEALTH, 'meta.upgrade_health'),
            (UPGRADE_BASE_DAMAGE, 'meta.upgrade_damage'),
            (UPGRADE_FIRE_RATE, 'meta.upgrade_fire_rate'),
            (UPGRADE_MOVE_SPEED, 'meta.upgrade_speed'),
            (UPGRADE_STARTING_COINS, 'meta.upgrade_coins'),
            (UPGRADE_COIN_MULTIPLIER, 'meta.upgrade_multiplier')
        ]

        y_offset = 160
        for upgrade_type, name_key in upgrades:
            level = self.progress_manager.upgrades.get(upgrade_type, 0)
            cost = self.progress_manager.get_upgrade_cost(upgrade_type)
            max_level = self.progress_manager.get_max_upgrade_level(upgrade_type)

            if level >= max_level:
                color = GREEN
                status = t('meta.max_level')
            elif self.progress_manager.can_afford_upgrade(upgrade_type):
                color = WHITE
                status = f"{t('meta.cost')}: {cost}"
            else:
                color = RED
                status = f"{t('meta.cost')}: {cost}"

            # Upgrade name and level
            text = f"{t(name_key)} [{level}/{max_level}]"
            upgrade_text = self.font_small.render(text, True, color)
            self.screen.blit(upgrade_text, (100, y_offset))

            # Cost/status
            status_text = self.font_small.render(status, True, color)
            self.screen.blit(status_text, (500, y_offset))

            y_offset += 40

        # Stats
        stats_y = y_offset + 20
        stats = [
            f"{t('meta.total_runs')}: {self.progress_manager.total_runs}",
            f"{t('meta.total_bosses')}: {self.progress_manager.total_bosses_defeated}",
            f"{t('meta.best_level')}: {self.progress_manager.best_level_reached}"
        ]

        for stat in stats:
            stat_text = self.font_small.render(stat, True, GRAY)
            self.screen.blit(stat_text, (100, stats_y))
            stats_y += 25

        # Back button
        for button in self.meta_buttons:
            button.draw(self.screen)

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
