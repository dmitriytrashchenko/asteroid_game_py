#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Localization system for multi-language support.
"""

import json
import os
from typing import Dict, Any


class Localization:
    """
    Manages game text translations.

    Attributes:
        current_language (str): Currently selected language code
        translations (Dict): Loaded translations dictionary
        available_languages (Dict): Available language names
    """

    def __init__(self):
        """Initialize localization system."""
        self.current_language = "ru"
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_languages = {
            "ru": "Русский",
            "en": "English"
        }
        self._load_translations()

    def _load_translations(self):
        """Load all translations."""
        self.translations = {
            "ru": self._get_russian_translations(),
            "en": self._get_english_translations()
        }

    def _get_russian_translations(self) -> Dict[str, Any]:
        """Get Russian translations."""
        return {
            # Menu
            "menu": {
                "title": "АСТЕРОИДЫ",
                "new_game": "НОВАЯ ИГРА",
                "continue": "ПРОДОЛЖИТЬ",
                "highscores": "РЕКОРДЫ",
                "achievements": "ДОСТИЖЕНИЯ",
                "settings": "НАСТРОЙКИ",
                "quit": "ВЫХОД",
                "back": "НАЗАД"
            },

            # Settings
            "settings": {
                "title": "НАСТРОЙКИ",
                "music_volume": "Музыка",
                "sound_volume": "Звуки",
                "difficulty": "Сложность",
                "easy": "ЛЕГКО",
                "normal": "НОРМАЛЬНО",
                "hard": "СЛОЖНО",
                "language": "Язык",
                "fullscreen": "Полный экран",
                "windowed": "Оконный режим"
            },

            # Game HUD
            "hud": {
                "score": "Счет",
                "lives": "Жизни",
                "wave": "Волна",
                "room": "Комната",
                "level": "Уровень",
                "highscore": "Рекорд",
                "coins": "Монеты",
                "health": "Здоровье",
                "boss": "БОСС"
            },

            # Pause
            "pause": {
                "title": "ПАУЗА",
                "continue": "ESC - продолжить",
                "menu": "M - меню"
            },

            # Game Over
            "gameover": {
                "title": "ИГРА ОКОНЧЕНА",
                "final_score": "Финальный счет",
                "wave": "Волна",
                "level": "Уровень",
                "asteroids_destroyed": "Уничтожено астероидов",
                "powerups_collected": "Собрано бонусов",
                "time": "Время",
                "new_highscore": "НОВЫЙ РЕКОРД!",
                "restart": "R - заново",
                "menu": "M - меню"
            },

            # Power-ups
            "powerups": {
                "shield": "Щит",
                "rapid_fire": "Быстрая стрельба",
                "triple_shot": "Тройной выстрел",
                "extra_life": "Дополнительная жизнь",
                "health": "Здоровье",
                "speed": "Скорость",
                "damage": "Урон"
            },

            # Shop
            "shop": {
                "title": "МАГАЗИН",
                "buy": "Купить",
                "sold": "Продано",
                "not_enough": "Недостаточно монет",
                "health_restore": "Восстановить здоровье",
                "max_health": "Макс. здоровье +1",
                "damage_up": "Урон +1",
                "fire_rate": "Скорость стрельбы +1",
                "speed_up": "Скорость +1",
                "continue": "Продолжить"
            },

            # Upgrades
            "upgrades": {
                "title": "УЛУЧШЕНИЯ",
                "max_health": "Максимум здоровья",
                "damage": "Урон",
                "fire_rate": "Скорость стрельбы",
                "move_speed": "Скорость движения",
                "starting_coins": "Начальные монеты",
                "coin_multiplier": "Множитель монет"
            },

            # Achievements
            "achievements": {
                "title": "ДОСТИЖЕНИЯ",
                "progress": "Прогресс",
                "unlocked": "Разблокировано",
                "locked": "Заблокировано",
                "notification": "ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!",

                # Achievement names
                "score_100": "Первые очки",
                "score_500": "Любитель",
                "score_1000": "Профи",
                "score_5000": "Мастер",
                "score_10000": "Легенда",
                "asteroids_10": "Начинающий охотник",
                "asteroids_50": "Охотник",
                "asteroids_100": "Опытный охотник",
                "asteroids_500": "Мастер охоты",
                "survive_60": "Выживший",
                "survive_300": "Ветеран",
                "survive_600": "Бессмертный",
                "wave_5": "Волна 5",
                "wave_10": "Волна 10",
                "wave_20": "Волна 20",
                "no_hit": "Неуловимый",
                "powerup_collector": "Коллекционер",
                "boss_killer": "Убийца боссов",
                "room_explorer": "Исследователь",

                # Achievement descriptions
                "score_100_desc": "Набрать 100 очков",
                "score_500_desc": "Набрать 500 очков",
                "score_1000_desc": "Набрать 1000 очков",
                "score_5000_desc": "Набрать 5000 очков",
                "score_10000_desc": "Набрать 10000 очков",
                "asteroids_10_desc": "Уничтожить 10 астероидов",
                "asteroids_50_desc": "Уничтожить 50 астероидов",
                "asteroids_100_desc": "Уничтожить 100 астероидов",
                "asteroids_500_desc": "Уничтожить 500 астероидов",
                "survive_60_desc": "Продержаться 1 минуту",
                "survive_300_desc": "Продержаться 5 минут",
                "survive_600_desc": "Продержаться 10 минут",
                "wave_5_desc": "Достичь волны 5",
                "wave_10_desc": "Достичь волны 10",
                "wave_20_desc": "Достичь волны 20",
                "no_hit_desc": "Пройти комнату без повреждений",
                "powerup_collector_desc": "Собрать 10 бонусов",
                "boss_killer_desc": "Победить 5 боссов",
                "room_explorer_desc": "Посетить 20 комнат"
            },

            # High scores
            "highscores": {
                "title": "ТАБЛИЦА РЕКОРДОВ",
                "rank": "Место",
                "score": "Очки",
                "level": "Уровень",
                "difficulty": "Сложность"
            },

            # Rooms
            "rooms": {
                "normal": "Обычная комната",
                "boss": "Комната босса",
                "shop": "Магазин",
                "treasure": "Сокровищница",
                "cleared": "Очищена"
            },

            # Boss names
            "bosses": {
                "asteroid_king": "Король астероидов",
                "void_hunter": "Охотник бездны",
                "star_destroyer": "Разрушитель звезд"
            },

            # Controls
            "controls": {
                "move": "W/A/S/D - движение",
                "shoot": "SPACE - стрельба",
                "pause": "ESC - пауза",
                "interact": "E - взаимодействие"
            },

            # Messages
            "messages": {
                "loading": "Загрузка...",
                "saving": "Сохранение...",
                "saved": "Сохранено!",
                "room_cleared": "Комната очищена!",
                "boss_defeated": "Босс побежден!",
                "level_complete": "Уровень пройден!",
                "enter_shop": "E - войти в магазин",
                "next_room": "Выберите следующую комнату"
            }
        }

    def _get_english_translations(self) -> Dict[str, Any]:
        """Get English translations."""
        return {
            # Menu
            "menu": {
                "title": "ASTEROIDS",
                "new_game": "NEW GAME",
                "continue": "CONTINUE",
                "highscores": "HIGH SCORES",
                "achievements": "ACHIEVEMENTS",
                "settings": "SETTINGS",
                "quit": "QUIT",
                "back": "BACK"
            },

            # Settings
            "settings": {
                "title": "SETTINGS",
                "music_volume": "Music",
                "sound_volume": "Sound",
                "difficulty": "Difficulty",
                "easy": "EASY",
                "normal": "NORMAL",
                "hard": "HARD",
                "language": "Language",
                "fullscreen": "Fullscreen",
                "windowed": "Windowed"
            },

            # Game HUD
            "hud": {
                "score": "Score",
                "lives": "Lives",
                "wave": "Wave",
                "room": "Room",
                "level": "Level",
                "highscore": "High Score",
                "coins": "Coins",
                "health": "Health",
                "boss": "BOSS"
            },

            # Pause
            "pause": {
                "title": "PAUSED",
                "continue": "ESC - continue",
                "menu": "M - menu"
            },

            # Game Over
            "gameover": {
                "title": "GAME OVER",
                "final_score": "Final Score",
                "wave": "Wave",
                "level": "Level",
                "asteroids_destroyed": "Asteroids Destroyed",
                "powerups_collected": "Power-ups Collected",
                "time": "Time",
                "new_highscore": "NEW HIGH SCORE!",
                "restart": "R - restart",
                "menu": "M - menu"
            },

            # Power-ups
            "powerups": {
                "shield": "Shield",
                "rapid_fire": "Rapid Fire",
                "triple_shot": "Triple Shot",
                "extra_life": "Extra Life",
                "health": "Health",
                "speed": "Speed",
                "damage": "Damage"
            },

            # Shop
            "shop": {
                "title": "SHOP",
                "buy": "Buy",
                "sold": "Sold",
                "not_enough": "Not enough coins",
                "health_restore": "Restore Health",
                "max_health": "Max Health +1",
                "damage_up": "Damage +1",
                "fire_rate": "Fire Rate +1",
                "speed_up": "Speed +1",
                "continue": "Continue"
            },

            # Upgrades
            "upgrades": {
                "title": "UPGRADES",
                "max_health": "Max Health",
                "damage": "Damage",
                "fire_rate": "Fire Rate",
                "move_speed": "Move Speed",
                "starting_coins": "Starting Coins",
                "coin_multiplier": "Coin Multiplier"
            },

            # Achievements
            "achievements": {
                "title": "ACHIEVEMENTS",
                "progress": "Progress",
                "unlocked": "Unlocked",
                "locked": "Locked",
                "notification": "ACHIEVEMENT UNLOCKED!",

                # Achievement names
                "score_100": "First Blood",
                "score_500": "Amateur",
                "score_1000": "Professional",
                "score_5000": "Master",
                "score_10000": "Legend",
                "asteroids_10": "Novice Hunter",
                "asteroids_50": "Hunter",
                "asteroids_100": "Expert Hunter",
                "asteroids_500": "Master Hunter",
                "survive_60": "Survivor",
                "survive_300": "Veteran",
                "survive_600": "Immortal",
                "wave_5": "Wave 5",
                "wave_10": "Wave 10",
                "wave_20": "Wave 20",
                "no_hit": "Untouchable",
                "powerup_collector": "Collector",
                "boss_killer": "Boss Killer",
                "room_explorer": "Explorer",

                # Achievement descriptions
                "score_100_desc": "Reach 100 points",
                "score_500_desc": "Reach 500 points",
                "score_1000_desc": "Reach 1000 points",
                "score_5000_desc": "Reach 5000 points",
                "score_10000_desc": "Reach 10000 points",
                "asteroids_10_desc": "Destroy 10 asteroids",
                "asteroids_50_desc": "Destroy 50 asteroids",
                "asteroids_100_desc": "Destroy 100 asteroids",
                "asteroids_500_desc": "Destroy 500 asteroids",
                "survive_60_desc": "Survive for 1 minute",
                "survive_300_desc": "Survive for 5 minutes",
                "survive_600_desc": "Survive for 10 minutes",
                "wave_5_desc": "Reach wave 5",
                "wave_10_desc": "Reach wave 10",
                "wave_20_desc": "Reach wave 20",
                "no_hit_desc": "Clear room without taking damage",
                "powerup_collector_desc": "Collect 10 power-ups",
                "boss_killer_desc": "Defeat 5 bosses",
                "room_explorer_desc": "Visit 20 rooms"
            },

            # High scores
            "highscores": {
                "title": "HIGH SCORES",
                "rank": "Rank",
                "score": "Score",
                "level": "Level",
                "difficulty": "Difficulty"
            },

            # Rooms
            "rooms": {
                "normal": "Normal Room",
                "boss": "Boss Room",
                "shop": "Shop",
                "treasure": "Treasure Room",
                "cleared": "Cleared"
            },

            # Boss names
            "bosses": {
                "asteroid_king": "Asteroid King",
                "void_hunter": "Void Hunter",
                "star_destroyer": "Star Destroyer"
            },

            # Controls
            "controls": {
                "move": "W/A/S/D - move",
                "shoot": "SPACE - shoot",
                "pause": "ESC - pause",
                "interact": "E - interact"
            },

            # Messages
            "messages": {
                "loading": "Loading...",
                "saving": "Saving...",
                "saved": "Saved!",
                "room_cleared": "Room Cleared!",
                "boss_defeated": "Boss Defeated!",
                "level_complete": "Level Complete!",
                "enter_shop": "E - enter shop",
                "next_room": "Choose next room"
            }
        }

    def set_language(self, language_code: str):
        """
        Set current language.

        Args:
            language_code: Language code ('ru' or 'en')
        """
        if language_code in self.available_languages:
            self.current_language = language_code

    def get(self, key_path: str, default: str = "") -> str:
        """
        Get translated text by key path.

        Args:
            key_path: Dot-separated path to translation (e.g., 'menu.title')
            default: Default value if key not found

        Returns:
            Translated text
        """
        keys = key_path.split('.')
        value = self.translations.get(self.current_language, {})

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

        return value if isinstance(value, str) else default

    def get_current_language_name(self) -> str:
        """
        Get current language name.

        Returns:
            Language name
        """
        return self.available_languages.get(self.current_language, "Unknown")


# Global localization instance
_localization = None

def get_localization() -> Localization:
    """Get global localization instance."""
    global _localization
    if _localization is None:
        _localization = Localization()
    return _localization

def t(key: str, default: str = "") -> str:
    """
    Shorthand for getting translated text.

    Args:
        key: Translation key path
        default: Default value

    Returns:
        Translated text
    """
    return get_localization().get(key, default)
