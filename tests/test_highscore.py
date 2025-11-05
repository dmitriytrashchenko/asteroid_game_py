#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for HighScoreManager.
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.managers.highscore_manager import HighScoreManager, HighScoreEntry
from src.constants import DIFFICULTY_NORMAL


class TestHighScoreManager(unittest.TestCase):
    """Test cases for HighScoreManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = HighScoreManager()
        self.manager.scores = []  # Clear any existing scores

    def test_add_score(self):
        """Test adding a score."""
        position = self.manager.add_score(1000, 5, DIFFICULTY_NORMAL)
        self.assertEqual(position, 1)
        self.assertEqual(len(self.manager.scores), 1)
        self.assertEqual(self.manager.scores[0].score, 1000)

    def test_score_ordering(self):
        """Test that scores are ordered correctly."""
        self.manager.add_score(500, 3, DIFFICULTY_NORMAL)
        self.manager.add_score(1000, 5, DIFFICULTY_NORMAL)
        self.manager.add_score(750, 4, DIFFICULTY_NORMAL)

        self.assertEqual(self.manager.scores[0].score, 1000)
        self.assertEqual(self.manager.scores[1].score, 750)
        self.assertEqual(self.manager.scores[2].score, 500)

    def test_max_scores_limit(self):
        """Test that only top 10 scores are kept."""
        for i in range(15):
            self.manager.add_score(i * 100, i, DIFFICULTY_NORMAL)

        self.assertEqual(len(self.manager.scores), 10)
        self.assertEqual(self.manager.scores[0].score, 1400)
        self.assertEqual(self.manager.scores[-1].score, 500)

    def test_is_high_score(self):
        """Test high score detection."""
        # Empty list - any score is high score
        self.assertTrue(self.manager.is_high_score(100))

        # Add 10 scores
        for i in range(10):
            self.manager.add_score(i * 100, i, DIFFICULTY_NORMAL)

        # Score higher than lowest
        self.assertTrue(self.manager.is_high_score(150))

        # Score lower than lowest
        self.assertFalse(self.manager.is_high_score(50))

    def test_get_highest_score(self):
        """Test getting highest score."""
        self.assertEqual(self.manager.get_highest_score(), 0)

        self.manager.add_score(500, 3, DIFFICULTY_NORMAL)
        self.manager.add_score(1000, 5, DIFFICULTY_NORMAL)

        self.assertEqual(self.manager.get_highest_score(), 1000)

    def test_get_top_scores(self):
        """Test getting top N scores."""
        for i in range(15):
            self.manager.add_score(i * 100, i, DIFFICULTY_NORMAL)

        top_5 = self.manager.get_top_scores(5)
        self.assertEqual(len(top_5), 5)
        self.assertEqual(top_5[0].score, 1400)

    def test_clear_scores(self):
        """Test clearing all scores."""
        self.manager.add_score(1000, 5, DIFFICULTY_NORMAL)
        self.manager.clear_scores()
        self.assertEqual(len(self.manager.scores), 0)


class TestHighScoreEntry(unittest.TestCase):
    """Test cases for HighScoreEntry."""

    def test_to_dict(self):
        """Test dictionary conversion."""
        entry = HighScoreEntry(1000, 5, "2025-01-01", DIFFICULTY_NORMAL)
        data = entry.to_dict()

        self.assertEqual(data['score'], 1000)
        self.assertEqual(data['wave'], 5)
        self.assertEqual(data['date'], "2025-01-01")
        self.assertEqual(data['difficulty'], DIFFICULTY_NORMAL)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'score': 1000,
            'wave': 5,
            'date': "2025-01-01",
            'difficulty': DIFFICULTY_NORMAL
        }
        entry = HighScoreEntry.from_dict(data)

        self.assertEqual(entry.score, 1000)
        self.assertEqual(entry.wave, 5)
        self.assertEqual(entry.date, "2025-01-01")
        self.assertEqual(entry.difficulty, DIFFICULTY_NORMAL)


if __name__ == '__main__':
    unittest.main()
