#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for AchievementManager.
"""

import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.managers.achievement_manager import AchievementManager, Achievement


class TestAchievement(unittest.TestCase):
    """Test cases for Achievement class."""

    def test_unlock(self):
        """Test unlocking achievement."""
        ach = Achievement('test_id', 'Test', 'Test description', 'score', 100)
        self.assertFalse(ach.unlocked)
        self.assertEqual(ach.unlock_date, "")

        ach.unlock()
        self.assertTrue(ach.unlocked)
        self.assertNotEqual(ach.unlock_date, "")

    def test_to_dict(self):
        """Test dictionary conversion."""
        ach = Achievement('test_id', 'Test', 'Test description', 'score', 100)
        data = ach.to_dict()

        self.assertEqual(data['id'], 'test_id')
        self.assertEqual(data['name'], 'Test')
        self.assertEqual(data['threshold'], 100)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'id': 'test_id',
            'name': 'Test',
            'description': 'Test description',
            'condition_type': 'score',
            'threshold': 100,
            'unlocked': True,
            'unlock_date': '2025-01-01'
        }
        ach = Achievement.from_dict(data)

        self.assertEqual(ach.id, 'test_id')
        self.assertTrue(ach.unlocked)


class TestAchievementManager(unittest.TestCase):
    """Test cases for AchievementManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AchievementManager()

    def test_check_achievement_score(self):
        """Test checking score achievements."""
        self.manager.check_achievement('score', 150)

        # Should unlock 100 score achievement
        unlocked = self.manager.get_newly_unlocked()
        unlocked_ids = [ach.id for ach in unlocked]
        self.assertIn('score_100', unlocked_ids)

    def test_check_achievement_multiple(self):
        """Test checking multiple achievements at once."""
        self.manager.check_achievement('score', 600)

        unlocked = self.manager.get_newly_unlocked()
        unlocked_ids = [ach.id for ach in unlocked]

        # Should unlock 100 and 500
        self.assertIn('score_100', unlocked_ids)
        self.assertIn('score_500', unlocked_ids)

    def test_get_unlocked_count(self):
        """Test getting count of unlocked achievements."""
        initial_count = self.manager.get_unlocked_count()

        self.manager.check_achievement('score', 100)
        self.manager.get_newly_unlocked()  # Clear newly unlocked

        new_count = self.manager.get_unlocked_count()
        self.assertGreater(new_count, initial_count)

    def test_get_completion_percentage(self):
        """Test completion percentage calculation."""
        total = self.manager.get_total_count()
        self.assertGreater(total, 0)

        percentage = self.manager.get_completion_percentage()
        self.assertGreaterEqual(percentage, 0)
        self.assertLessEqual(percentage, 100)

    def test_reset_achievements(self):
        """Test resetting all achievements."""
        self.manager.check_achievement('score', 1000)
        self.manager.get_newly_unlocked()

        self.manager.reset_achievements()

        # All should be locked
        for achievement in self.manager.achievements.values():
            self.assertFalse(achievement.unlocked)

    def test_get_all_achievements(self):
        """Test getting all achievements."""
        all_achievements = self.manager.get_all_achievements()

        self.assertGreater(len(all_achievements), 0)
        # Should be sorted (unlocked first)
        # For new manager, all should be locked


if __name__ == '__main__':
    unittest.main()
