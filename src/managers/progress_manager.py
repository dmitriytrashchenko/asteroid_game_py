#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta-progression and permanent upgrades manager.
"""

import json
import os
from typing import Dict
from ..constants import (
    PROGRESS_FILE,
    UPGRADE_MAX_HEALTH,
    UPGRADE_BASE_DAMAGE,
    UPGRADE_FIRE_RATE,
    UPGRADE_MOVE_SPEED,
    UPGRADE_STARTING_COINS,
    UPGRADE_COIN_MULTIPLIER,
    UPGRADE_COSTS,
    UPGRADE_MAX_LEVEL
)


class ProgressManager:
    """
    Manages meta-progression and permanent upgrades.

    Attributes:
        permanent_currency (int): Currency for buying permanent upgrades
        upgrades (Dict[str, int]): Current upgrade levels
        total_runs (int): Total number of runs
        total_bosses_defeated (int): Bosses defeated across all runs
        total_coins_collected (int): Coins collected across all runs
    """

    def __init__(self):
        """Initialize progress manager."""
        self.permanent_currency = 0
        self.upgrades: Dict[str, int] = {
            UPGRADE_MAX_HEALTH: 0,
            UPGRADE_BASE_DAMAGE: 0,
            UPGRADE_FIRE_RATE: 0,
            UPGRADE_MOVE_SPEED: 0,
            UPGRADE_STARTING_COINS: 0,
            UPGRADE_COIN_MULTIPLIER: 0
        }

        # Statistics
        self.total_runs = 0
        self.total_bosses_defeated = 0
        self.total_coins_collected = 0
        self.highest_level_reached = 0
        self.total_rooms_cleared = 0

        self.load_progress()

    def load_progress(self) -> bool:
        """
        Load progress from file.

        Returns:
            True if successful
        """
        if not os.path.exists(PROGRESS_FILE):
            return False

        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.permanent_currency = data.get('permanent_currency', 0)

            # Load upgrades
            upgrades_data = data.get('upgrades', {})
            for upgrade_type in self.upgrades.keys():
                self.upgrades[upgrade_type] = upgrades_data.get(upgrade_type, 0)

            # Load statistics
            self.total_runs = data.get('total_runs', 0)
            self.total_bosses_defeated = data.get('total_bosses_defeated', 0)
            self.total_coins_collected = data.get('total_coins_collected', 0)
            self.highest_level_reached = data.get('highest_level_reached', 0)
            self.total_rooms_cleared = data.get('total_rooms_cleared', 0)

            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Error loading progress: {e}")
            return False

    def save_progress(self) -> bool:
        """
        Save progress to file.

        Returns:
            True if successful
        """
        try:
            data = {
                'permanent_currency': self.permanent_currency,
                'upgrades': self.upgrades.copy(),
                'total_runs': self.total_runs,
                'total_bosses_defeated': self.total_bosses_defeated,
                'total_coins_collected': self.total_coins_collected,
                'highest_level_reached': self.highest_level_reached,
                'total_rooms_cleared': self.total_rooms_cleared
            }

            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True

        except (IOError, OSError) as e:
            print(f"Error saving progress: {e}")
            return False

    def can_afford_upgrade(self, upgrade_type: str) -> bool:
        """
        Check if player can afford an upgrade.

        Args:
            upgrade_type: Type of upgrade

        Returns:
            True if affordable
        """
        if upgrade_type not in self.upgrades:
            return False

        current_level = self.upgrades[upgrade_type]
        if current_level >= UPGRADE_MAX_LEVEL:
            return False

        cost = self.get_upgrade_cost(upgrade_type)
        return self.permanent_currency >= cost

    def get_upgrade_cost(self, upgrade_type: str) -> int:
        """
        Get cost of next upgrade level.

        Args:
            upgrade_type: Type of upgrade

        Returns:
            Cost in permanent currency
        """
        if upgrade_type not in self.upgrades:
            return 999999

        current_level = self.upgrades[upgrade_type]
        if current_level >= UPGRADE_MAX_LEVEL:
            return 999999

        costs = UPGRADE_COSTS.get(upgrade_type, [])
        if current_level < len(costs):
            return costs[current_level]

        return 999999

    def purchase_upgrade(self, upgrade_type: str) -> bool:
        """
        Purchase an upgrade.

        Args:
            upgrade_type: Type of upgrade

        Returns:
            True if successful
        """
        if not self.can_afford_upgrade(upgrade_type):
            return False

        cost = self.get_upgrade_cost(upgrade_type)
        self.permanent_currency -= cost
        self.upgrades[upgrade_type] += 1
        self.save_progress()

        return True

    def get_upgrade_level(self, upgrade_type: str) -> int:
        """
        Get current upgrade level.

        Args:
            upgrade_type: Type of upgrade

        Returns:
            Current level (0-5)
        """
        return self.upgrades.get(upgrade_type, 0)

    def add_permanent_currency(self, amount: int):
        """
        Add permanent currency (earned after runs).

        Args:
            amount: Currency to add
        """
        self.permanent_currency += amount
        self.save_progress()

    def record_run_completion(self, level_reached: int, bosses_defeated: int,
                             coins_collected: int, rooms_cleared: int):
        """
        Record statistics from a completed run.

        Args:
            level_reached: Highest level reached
            bosses_defeated: Number of bosses defeated
            coins_collected: Coins collected in run
            rooms_cleared: Rooms cleared in run
        """
        self.total_runs += 1
        self.total_bosses_defeated += bosses_defeated
        self.total_coins_collected += coins_collected
        self.total_rooms_cleared += rooms_cleared

        if level_reached > self.highest_level_reached:
            self.highest_level_reached = level_reached

        # Award permanent currency based on performance
        earned = level_reached * 2 + bosses_defeated * 5
        self.add_permanent_currency(earned)

    def get_starting_coins(self) -> int:
        """
        Get starting coins based on upgrade level.

        Returns:
            Starting coins for new run
        """
        base = 0
        upgrade_level = self.get_upgrade_level(UPGRADE_STARTING_COINS)
        return base + upgrade_level * 10

    def get_coin_multiplier(self) -> float:
        """
        Get coin drop multiplier based on upgrade level.

        Returns:
            Multiplier (1.0 - 3.0)
        """
        upgrade_level = self.get_upgrade_level(UPGRADE_COIN_MULTIPLIER)
        return 1.0 + upgrade_level * 0.4

    def get_max_health_bonus(self) -> int:
        """
        Get max health bonus from upgrades.

        Returns:
            Additional max health
        """
        return self.get_upgrade_level(UPGRADE_MAX_HEALTH)

    def get_damage_bonus(self) -> int:
        """
        Get damage bonus from upgrades.

        Returns:
            Additional damage
        """
        return self.get_upgrade_level(UPGRADE_BASE_DAMAGE)

    def get_fire_rate_bonus(self) -> float:
        """
        Get fire rate bonus from upgrades.

        Returns:
            Fire rate multiplier (0.8 - 0.5)
        """
        upgrade_level = self.get_upgrade_level(UPGRADE_FIRE_RATE)
        return 1.0 - upgrade_level * 0.1  # Reduces cooldown

    def get_move_speed_bonus(self) -> float:
        """
        Get movement speed bonus from upgrades.

        Returns:
            Speed multiplier (1.0 - 1.5)
        """
        upgrade_level = self.get_upgrade_level(UPGRADE_MOVE_SPEED)
        return 1.0 + upgrade_level * 0.1
