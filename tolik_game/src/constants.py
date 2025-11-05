#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game constants for Tolik: Escape from the Basement
Isaac-like roguelike game
"""

import pygame

# Screen settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
GAME_WIDTH = 1280
GAME_HEIGHT = 720
FPS = 60

# Room dimensions (like Isaac)
ROOM_WIDTH = 1040  # Playable area width
ROOM_HEIGHT = 560  # Playable area height
ROOM_OFFSET_X = 120  # Left offset for UI
ROOM_OFFSET_Y = 80   # Top offset

# Grid for room layout (13x7 tiles)
TILE_SIZE = 80
GRID_WIDTH = 13
GRID_HEIGHT = 7

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
DARK_RED = (150, 20, 20)
GREEN = (50, 220, 50)
BLUE = (50, 50, 220)
YELLOW = (255, 220, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 90, 60)
PURPLE = (180, 50, 180)
ORANGE = (255, 165, 0)

# Background colors for floors
FLOOR_COLORS = {
    'basement': (80, 60, 50),      # Dark brown
    'caves': (40, 35, 35),         # Dark gray
    'depths': (30, 25, 30),        # Very dark purple
    'womb': (80, 30, 30),          # Dark red
}

# Wall colors for floors
WALL_COLORS = {
    'basement': (60, 45, 35),
    'caves': (30, 25, 25),
    'depths': (20, 15, 20),
    'womb': (60, 20, 20),
}

# Player (Tolik) constants
TOLIK_SIZE = 32
TOLIK_SPEED = 200  # pixels per second
TOLIK_MAX_HEALTH = 6  # 3 full hearts
TOLIK_BASE_DAMAGE = 1.0
TOLIK_BASE_TEARS = 1.0  # Tears per second
TOLIK_BASE_RANGE = 300  # Tear range in pixels
TOLIK_BASE_SHOT_SPEED = 400  # Tear speed

# Tolik starting stats
TOLIK_START_SPEED = 200
TOLIK_START_TEARS = 1.0
TOLIK_START_DAMAGE = 1.0
TOLIK_START_RANGE = 300
TOLIK_START_SHOT_SPEED = 400

# Tear constants
TEAR_SIZE = 8
TEAR_COLOR = (100, 150, 255)  # Blue tears
TEAR_GRAVITY = 0  # No gravity for top-down
TEAR_KNOCKBACK = 50

# Enemy types
ENEMY_FLY = 'fly'
ENEMY_SPIDER = 'spider'
ENEMY_BLOB = 'blob'
ENEMY_HOPPER = 'hopper'
ENEMY_SHOOTER = 'shooter'
ENEMY_CHARGER = 'charger'

# Enemy stats
ENEMY_STATS = {
    ENEMY_FLY: {
        'health': 2,
        'speed': 150,
        'damage': 1,
        'size': 24,
        'color': (100, 80, 60),
        'behavior': 'fly_random',
        'score': 10
    },
    ENEMY_SPIDER: {
        'health': 4,
        'speed': 80,
        'damage': 1,
        'size': 32,
        'color': (60, 40, 40),
        'behavior': 'chase',
        'score': 20
    },
    ENEMY_BLOB: {
        'health': 6,
        'speed': 40,
        'damage': 1,
        'size': 40,
        'color': (80, 150, 80),
        'behavior': 'wander',
        'score': 30
    },
    ENEMY_HOPPER: {
        'health': 3,
        'speed': 200,
        'damage': 1,
        'size': 28,
        'color': (150, 100, 150),
        'behavior': 'hop',
        'score': 25
    },
    ENEMY_SHOOTER: {
        'health': 5,
        'speed': 60,
        'damage': 1,
        'size': 36,
        'color': (180, 60, 60),
        'behavior': 'shoot',
        'score': 40
    },
    ENEMY_CHARGER: {
        'health': 8,
        'speed': 250,
        'damage': 2,
        'size': 44,
        'color': (200, 100, 50),
        'behavior': 'charge',
        'score': 50
    }
}

# Boss types
BOSS_MONSTRO = 'monstro'
BOSS_GEMINI = 'gemini'
BOSS_FAMINE = 'famine'
BOSS_MOM = 'mom'

# Boss stats
BOSS_STATS = {
    BOSS_MONSTRO: {
        'health': 200,
        'speed': 100,
        'damage': 2,
        'size': 80,
        'color': ORANGE,
        'attacks': ['jump', 'shoot_burst'],
        'score': 500
    },
    BOSS_GEMINI: {
        'health': 120,  # Split into two parts
        'speed': 150,
        'damage': 1,
        'size': 60,
        'color': PURPLE,
        'attacks': ['charge', 'split'],
        'score': 600
    },
    BOSS_FAMINE: {
        'health': 300,
        'speed': 120,
        'damage': 2,
        'size': 100,
        'color': DARK_GRAY,
        'attacks': ['horse_charge', 'summon'],
        'score': 800
    },
    BOSS_MOM: {
        'health': 500,
        'speed': 80,
        'damage': 3,
        'size': 120,
        'color': (255, 200, 200),
        'attacks': ['stomp', 'hand', 'summon'],
        'score': 1000
    }
}

# Item types
ITEM_HEALTH = 'health'
ITEM_DAMAGE_UP = 'damage_up'
ITEM_SPEED_UP = 'speed_up'
ITEM_TEARS_UP = 'tears_up'
ITEM_RANGE_UP = 'range_up'
ITEM_TRIPLE_SHOT = 'triple_shot'
ITEM_HOMING = 'homing'
ITEM_PIERCING = 'piercing'
ITEM_BOMB = 'bomb'
ITEM_KEY = 'key'
ITEM_COIN = 'coin'

# Pickup types
PICKUP_HEART = 'heart'
PICKUP_HALF_HEART = 'half_heart'
PICKUP_SOUL_HEART = 'soul_heart'
PICKUP_COIN = 'coin'
PICKUP_BOMB = 'bomb'
PICKUP_KEY = 'key'

# Room types
ROOM_TYPE_NORMAL = 'normal'
ROOM_TYPE_BOSS = 'boss'
ROOM_TYPE_TREASURE = 'treasure'
ROOM_TYPE_SHOP = 'shop'
ROOM_TYPE_SECRET = 'secret'
ROOM_TYPE_START = 'start'
ROOM_TYPE_SACRIFICE = 'sacrifice'

# Door directions
DOOR_TOP = 'top'
DOOR_BOTTOM = 'bottom'
DOOR_LEFT = 'left'
DOOR_RIGHT = 'right'

# Door positions
DOOR_POSITIONS = {
    DOOR_TOP: (ROOM_OFFSET_X + ROOM_WIDTH // 2, ROOM_OFFSET_Y),
    DOOR_BOTTOM: (ROOM_OFFSET_X + ROOM_WIDTH // 2, ROOM_OFFSET_Y + ROOM_HEIGHT),
    DOOR_LEFT: (ROOM_OFFSET_X, ROOM_OFFSET_Y + ROOM_HEIGHT // 2),
    DOOR_RIGHT: (ROOM_OFFSET_X + ROOM_WIDTH, ROOM_OFFSET_Y + ROOM_HEIGHT // 2)
}

# Door size
DOOR_WIDTH = 80
DOOR_HEIGHT = 60

# Level generation
LEVEL_MIN_ROOMS = 8
LEVEL_MAX_ROOMS = 15
LEVEL_BOSS_DISTANCE_MIN = 5  # Minimum rooms from start to boss

# Floor names
FLOOR_BASEMENT = 'basement'
FLOOR_CAVES = 'caves'
FLOOR_DEPTHS = 'depths'
FLOOR_WOMB = 'womb'

# Floor progression
FLOORS = [FLOOR_BASEMENT, FLOOR_CAVES, FLOOR_DEPTHS, FLOOR_WOMB]

# Difficulty scaling per floor
FLOOR_DIFFICULTY = {
    FLOOR_BASEMENT: 1.0,
    FLOOR_CAVES: 1.3,
    FLOOR_DEPTHS: 1.6,
    FLOOR_WOMB: 2.0
}

# Enemy spawn counts per room type
ROOM_ENEMY_COUNT = {
    ROOM_TYPE_NORMAL: (3, 8),
    ROOM_TYPE_BOSS: (0, 0),  # Boss only
    ROOM_TYPE_TREASURE: (0, 0),
    ROOM_TYPE_SHOP: (0, 0),
    ROOM_TYPE_SECRET: (0, 0),
    ROOM_TYPE_START: (0, 0),
    ROOM_TYPE_SACRIFICE: (4, 6)
}

# Shop prices
SHOP_HEART_PRICE = 3
SHOP_ITEM_PRICE = 15
SHOP_BOMB_PRICE = 5
SHOP_KEY_PRICE = 5

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3
STATE_WIN = 4
STATE_ROOM_TRANSITION = 5

# Damage numbers
DAMAGE_DISPLAY_TIME = 1.0  # seconds

# Particle effects
PARTICLE_BLOOD = 'blood'
PARTICLE_TEARS = 'tears'
PARTICLE_EXPLOSION = 'explosion'

# Sound effects (placeholders)
SOUND_TEAR = 'tear'
SOUND_HIT = 'hit'
SOUND_DEATH = 'death'
SOUND_PICKUP = 'pickup'
SOUND_DOOR = 'door'

# Animation frames
ANIMATION_IDLE_DOWN = 'idle_down'
ANIMATION_IDLE_UP = 'idle_up'
ANIMATION_IDLE_LEFT = 'idle_left'
ANIMATION_IDLE_RIGHT = 'idle_right'
ANIMATION_WALK_DOWN = 'walk_down'
ANIMATION_WALK_UP = 'walk_up'
ANIMATION_WALK_LEFT = 'walk_left'
ANIMATION_WALK_RIGHT = 'walk_right'

# Invincibility
INVINCIBILITY_TIME = 1.0  # seconds after hit

# Score multipliers
SCORE_MULTIPLIER_NO_DAMAGE = 2.0
SCORE_MULTIPLIER_FAST_CLEAR = 1.5

# Achievement IDs
ACHIEVEMENT_BEAT_BASEMENT = 'beat_basement'
ACHIEVEMENT_BEAT_CAVES = 'beat_caves'
ACHIEVEMENT_BEAT_DEPTHS = 'beat_depths'
ACHIEVEMENT_BEAT_WOMB = 'beat_womb'
ACHIEVEMENT_NO_DAMAGE = 'no_damage'
ACHIEVEMENT_100_ENEMIES = '100_enemies'
ACHIEVEMENT_ALL_ITEMS = 'all_items'

# File paths
SAVE_FILE = 'data/save.json'
CONFIG_FILE = 'data/config.json'
HIGHSCORE_FILE = 'data/highscores.json'
