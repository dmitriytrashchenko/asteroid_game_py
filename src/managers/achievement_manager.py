#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Achievement tracking system.
"""

import json
import os
from typing import Dict, List, Set
from datetime import datetime
from ..constants import ACHIEVEMENTS_FILE


class Achievement:
    """
    Single achievement definition.

    Attributes:
        id (str): Unique achievement identifier
        name (str): Achievement name
        description (str): Achievement description
        condition_type (str): Type of condition (score, asteroids, time, wave)
        threshold (int): Value needed to unlock
        unlocked (bool): Whether achievement is unlocked
        unlock_date (str): Date when unlocked
    """

    def __init__(self, id: str, name: str, description: str,
                 condition_type: str, threshold: int):
        """
        Initialize achievement.

        Args:
            id: Unique identifier
            name: Achievement name
            description: Achievement description
            condition_type: Type of condition
            threshold: Value needed to unlock
        """
        self.id = id
        self.name = name
        self.description = description
        self.condition_type = condition_type
        self.threshold = threshold
        self.unlocked = False
        self.unlock_date = ""

    def unlock(self):
        """Mark achievement as unlocked."""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'condition_type': self.condition_type,
            'threshold': self.threshold,
            'unlocked': self.unlocked,
            'unlock_date': self.unlock_date
        }

    @staticmethod
    def from_dict(data: dict) -> 'Achievement':
        """Create achievement from dictionary."""
        ach = Achievement(
            data['id'],
            data['name'],
            data['description'],
            data['condition_type'],
            data['threshold']
        )
        ach.unlocked = data.get('unlocked', False)
        ach.unlock_date = data.get('unlock_date', '')
        return ach


class AchievementManager:
    """
    Manages game achievements.

    Attributes:
        achievements (Dict[str, Achievement]): All achievements
        newly_unlocked (Set[str]): Recently unlocked achievement IDs
    """

    def __init__(self):
        """Initialize achievement manager."""
        self.achievements: Dict[str, Achievement] = {}
        self.newly_unlocked: Set[str] = set()
        self._create_achievements()
        self.load_achievements()

    def _create_achievements(self):
        """Create all achievement definitions."""
        achievement_defs = [
            # Score achievements
            ('score_100', 'Первые очки', 'Набрать 100 очков', 'score', 100),
            ('score_500', 'Любитель', 'Набрать 500 очков', 'score', 500),
            ('score_1000', 'Профи', 'Набрать 1000 очков', 'score', 1000),
            ('score_5000', 'Мастер', 'Набрать 5000 очков', 'score', 5000),
            ('score_10000', 'Легенда', 'Набрать 10000 очков', 'score', 10000),

            # Asteroid achievements
            ('asteroids_10', 'Начинающий охотник', 'Уничтожить 10 астероидов', 'asteroids', 10),
            ('asteroids_50', 'Охотник', 'Уничтожить 50 астероидов', 'asteroids', 50),
            ('asteroids_100', 'Опытный охотник', 'Уничтожить 100 астероидов', 'asteroids', 100),
            ('asteroids_500', 'Мастер охоты', 'Уничтожить 500 астероидов', 'asteroids', 500),

            # Survival achievements
            ('survive_60', 'Выживший', 'Продержаться 1 минуту', 'time', 60),
            ('survive_300', 'Ветеран', 'Продержаться 5 минут', 'time', 300),
            ('survive_600', 'Бессмертный', 'Продержаться 10 минут', 'time', 600),

            # Wave achievements
            ('wave_5', 'Волна 5', 'Достичь волны 5', 'wave', 5),
            ('wave_10', 'Волна 10', 'Достичь волны 10', 'wave', 10),
            ('wave_20', 'Волна 20', 'Достичь волны 20', 'wave', 20),

            # Special achievements
            ('no_hit', 'Неуловимый', 'Пройти волну без повреждений', 'no_hit', 1),
            ('powerup_collector', 'Коллекционер', 'Собрать 10 бонусов', 'powerups', 10),
        ]

        for ach_def in achievement_defs:
            achievement = Achievement(*ach_def)
            self.achievements[achievement.id] = achievement

    def load_achievements(self) -> bool:
        """
        Load achievement progress from file.

        Returns:
            True if successful
        """
        if not os.path.exists(ACHIEVEMENTS_FILE):
            return False

        try:
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for ach_id, ach_data in data.get('achievements', {}).items():
                if ach_id in self.achievements:
                    if ach_data.get('unlocked', False):
                        self.achievements[ach_id].unlocked = True
                        self.achievements[ach_id].unlock_date = ach_data.get('unlock_date', '')

            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки достижений: {e}")
            return False

    def save_achievements(self) -> bool:
        """
        Save achievement progress to file.

        Returns:
            True if successful
        """
        try:
            data = {
                'achievements': {
                    ach_id: ach.to_dict()
                    for ach_id, ach in self.achievements.items()
                },
                'last_updated': datetime.now().isoformat()
            }

            with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except (IOError, OSError) as e:
            print(f"Ошибка сохранения достижений: {e}")
            return False

    def check_achievement(self, condition_type: str, value: int):
        """
        Check and unlock achievements based on condition.

        Args:
            condition_type: Type of condition to check
            value: Current value to check against
        """
        for achievement in self.achievements.values():
            if not achievement.unlocked:
                if achievement.condition_type == condition_type:
                    if value >= achievement.threshold:
                        achievement.unlock()
                        self.newly_unlocked.add(achievement.id)

    def get_newly_unlocked(self) -> List[Achievement]:
        """
        Get and clear newly unlocked achievements.

        Returns:
            List of newly unlocked achievements
        """
        unlocked = [
            self.achievements[ach_id]
            for ach_id in self.newly_unlocked
        ]
        self.newly_unlocked.clear()
        return unlocked

    def get_all_achievements(self) -> List[Achievement]:
        """
        Get all achievements sorted by unlock status.

        Returns:
            List of all achievements
        """
        return sorted(
            self.achievements.values(),
            key=lambda x: (not x.unlocked, x.id)
        )

    def get_unlocked_count(self) -> int:
        """
        Get number of unlocked achievements.

        Returns:
            Count of unlocked achievements
        """
        return sum(1 for ach in self.achievements.values() if ach.unlocked)

    def get_total_count(self) -> int:
        """
        Get total number of achievements.

        Returns:
            Total achievement count
        """
        return len(self.achievements)

    def get_completion_percentage(self) -> float:
        """
        Get achievement completion percentage.

        Returns:
            Completion percentage (0-100)
        """
        if not self.achievements:
            return 0.0
        return (self.get_unlocked_count() / self.get_total_count()) * 100

    def reset_achievements(self):
        """Reset all achievements to locked state."""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_date = ""
        self.newly_unlocked.clear()
        self.save_achievements()
