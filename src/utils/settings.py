#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game settings manager with persistence.
"""

import json
import os
import pygame
from typing import Dict, Any
from ..constants import (
    SETTINGS_FILE,
    DIFFICULTY_NORMAL,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD
)


class Settings:
    """
    Manages game settings with save/load functionality.

    Attributes:
        music_volume (float): Music volume (0.0-1.0)
        sound_volume (float): Sound effects volume (0.0-1.0)
        difficulty (int): Game difficulty level
        controls (Dict[str, int]): Keyboard controls mapping
    """

    def __init__(self):
        """Initialize settings with default values."""
        self.music_volume: float = 0.5
        self.sound_volume: float = 0.7
        self.difficulty: int = DIFFICULTY_NORMAL
        self.controls: Dict[str, int] = {
            'thrust': pygame.K_w,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'shoot': pygame.K_SPACE
        }
        self.load_settings()

    def save_settings(self) -> bool:
        """
        Save settings to file.

        Returns:
            True if successful, False otherwise
        """
        try:
            settings_data = {
                'music_volume': self.music_volume,
                'sound_volume': self.sound_volume,
                'difficulty': self.difficulty,
                'controls': {k: v for k, v in self.controls.items()}
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
        except (TypeError, ValueError) as e:
            print(f"Ошибка кодирования настроек: {e}")
            return False

    def load_settings(self) -> bool:
        """
        Load settings from file.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(SETTINGS_FILE):
            return False

        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate and load music volume
            music_vol = data.get('music_volume', 0.5)
            self.music_volume = max(0.0, min(1.0, float(music_vol)))

            # Validate and load sound volume
            sound_vol = data.get('sound_volume', 0.7)
            self.sound_volume = max(0.0, min(1.0, float(sound_vol)))

            # Validate and load difficulty
            difficulty = data.get('difficulty', DIFFICULTY_NORMAL)
            if difficulty in [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]:
                self.difficulty = difficulty
            else:
                self.difficulty = DIFFICULTY_NORMAL

            # Validate and load controls
            if 'controls' in data and isinstance(data['controls'], dict):
                for key, value in data['controls'].items():
                    if key in self.controls and isinstance(value, int):
                        # Validate pygame key code range
                        if 0 <= value <= 1000:
                            self.controls[key] = value

            return True

        except (IOError, OSError) as e:
            print(f"Ошибка загрузки настроек: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON настроек: {e}")
            # Backup corrupted file
            try:
                backup_path = f"{SETTINGS_FILE}.backup"
                if os.path.exists(SETTINGS_FILE):
                    os.rename(SETTINGS_FILE, backup_path)
                    print(f"Поврежденный файл сохранен как {backup_path}")
            except OSError:
                pass
            return False
        except (TypeError, ValueError) as e:
            print(f"Ошибка валидации настроек: {e}")
            return False

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.difficulty = DIFFICULTY_NORMAL
        self.controls = {
            'thrust': pygame.K_w,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'shoot': pygame.K_SPACE
        }
        self.save_settings()

    def get_difficulty_name(self) -> str:
        """
        Get human-readable difficulty name.

        Returns:
            Difficulty name in Russian
        """
        names = {
            DIFFICULTY_EASY: "Легко",
            DIFFICULTY_NORMAL: "Нормально",
            DIFFICULTY_HARD: "Сложно"
        }
        return names.get(self.difficulty, "Неизвестно")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return {
            'music_volume': self.music_volume,
            'sound_volume': self.sound_volume,
            'difficulty': self.difficulty,
            'difficulty_name': self.get_difficulty_name(),
            'controls': self.controls.copy()
        }
