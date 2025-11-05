#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High score management system.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from ..constants import HIGHSCORE_FILE


class HighScoreEntry:
    """
    Single high score entry.

    Attributes:
        score (int): Score value
        wave (int): Wave reached
        date (str): Date achieved
        difficulty (int): Difficulty level
    """

    def __init__(self, score: int, wave: int = 0, date: str = None, difficulty: int = 1):
        """
        Initialize high score entry.

        Args:
            score: Score value
            wave: Wave number reached
            date: Date string (ISO format, uses current time if None)
            difficulty: Difficulty level
        """
        self.score = score
        self.wave = wave
        self.date = date if date else datetime.now().isoformat()
        self.difficulty = difficulty

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'score': self.score,
            'wave': self.wave,
            'date': self.date,
            'difficulty': self.difficulty
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HighScoreEntry':
        """
        Create entry from dictionary.

        Args:
            data: Dictionary with score data

        Returns:
            HighScoreEntry instance
        """
        return HighScoreEntry(
            score=data.get('score', 0),
            wave=data.get('wave', 0),
            date=data.get('date', ''),
            difficulty=data.get('difficulty', 1)
        )

    def get_formatted_date(self) -> str:
        """
        Get formatted date string.

        Returns:
            Formatted date (DD.MM.YYYY)
        """
        try:
            dt = datetime.fromisoformat(self.date)
            return dt.strftime('%d.%m.%Y')
        except (ValueError, AttributeError):
            return "???"


class HighScoreManager:
    """
    Manages top 10 high scores.

    Attributes:
        scores (List[HighScoreEntry]): List of high score entries
        max_scores (int): Maximum number of scores to keep
    """

    def __init__(self, max_scores: int = 10):
        """
        Initialize high score manager.

        Args:
            max_scores: Maximum number of scores to keep (default: 10)
        """
        self.max_scores = max_scores
        self.scores: List[HighScoreEntry] = []
        self.load_scores()

    def load_scores(self) -> bool:
        """
        Load high scores from file.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(HIGHSCORE_FILE):
            self._create_default_scores()
            return False

        try:
            with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.scores = []
            for entry_data in data.get('scores', []):
                entry = HighScoreEntry.from_dict(entry_data)
                self.scores.append(entry)

            # Sort by score descending
            self.scores.sort(key=lambda x: x.score, reverse=True)

            # Keep only top scores
            self.scores = self.scores[:self.max_scores]

            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки рекордов: {e}")
            self._create_default_scores()
            return False

    def save_scores(self) -> bool:
        """
        Save high scores to file.

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'scores': [entry.to_dict() for entry in self.scores],
                'last_updated': datetime.now().isoformat()
            }

            with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except (IOError, OSError) as e:
            print(f"Ошибка сохранения рекордов: {e}")
            return False

    def add_score(self, score: int, wave: int = 0, difficulty: int = 1) -> int:
        """
        Add a new score to the leaderboard.

        Args:
            score: Score value
            wave: Wave number reached
            difficulty: Difficulty level

        Returns:
            Position in leaderboard (1-based), or 0 if not in top scores
        """
        # Create new entry
        new_entry = HighScoreEntry(score, wave, difficulty=difficulty)

        # Add to list
        self.scores.append(new_entry)

        # Sort by score descending
        self.scores.sort(key=lambda x: x.score, reverse=True)

        # Find position
        position = 0
        for i, entry in enumerate(self.scores):
            if entry == new_entry:
                position = i + 1
                break

        # Keep only top scores
        self.scores = self.scores[:self.max_scores]

        # Save if in top 10
        if position > 0 and position <= self.max_scores:
            self.save_scores()
            return position

        return 0

    def is_high_score(self, score: int) -> bool:
        """
        Check if score would make it to the leaderboard.

        Args:
            score: Score to check

        Returns:
            True if score would be in top scores
        """
        if len(self.scores) < self.max_scores:
            return True

        return score > self.scores[-1].score

    def get_highest_score(self) -> int:
        """
        Get the highest score.

        Returns:
            Highest score value, or 0 if no scores
        """
        if self.scores:
            return self.scores[0].score
        return 0

    def get_top_scores(self, count: int = 10) -> List[HighScoreEntry]:
        """
        Get top N scores.

        Args:
            count: Number of scores to return

        Returns:
            List of top score entries
        """
        return self.scores[:min(count, len(self.scores))]

    def clear_scores(self):
        """Clear all high scores."""
        self.scores = []
        self._create_default_scores()
        self.save_scores()

    def _create_default_scores(self):
        """Create default placeholder scores."""
        self.scores = []
        # No default scores - start fresh

    def get_rank_suffix(self, rank: int) -> str:
        """
        Get suffix for rank number (1st, 2nd, etc).

        Args:
            rank: Rank number (1-based)

        Returns:
            Rank with suffix
        """
        if rank == 1:
            return f"{rank}-е место"
        elif rank == 2:
            return f"{rank}-е место"
        elif rank == 3:
            return f"{rank}-е место"
        else:
            return f"{rank}-е место"

    def get_difficulty_name(self, difficulty: int) -> str:
        """
        Get difficulty name.

        Args:
            difficulty: Difficulty level

        Returns:
            Difficulty name in Russian
        """
        names = {0: "Легко", 1: "Нормально", 2: "Сложно"}
        return names.get(difficulty, "?")
