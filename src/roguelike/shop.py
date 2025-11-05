#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shop system for buying upgrades.
"""

import random
from typing import List, Dict, Callable, Optional
from ..constants import (
    SHOP_ITEM_COUNT,
    SHOP_REROLL_COST,
    SHOP_PRICE_HEALTH,
    SHOP_PRICE_MAX_HEALTH,
    SHOP_PRICE_DAMAGE,
    SHOP_PRICE_FIRE_RATE,
    SHOP_PRICE_SPEED,
    SHOP_PRICE_SHIELD,
    SHOP_PRICE_TRIPLE_SHOT
)


class ShopItem:
    """
    Item available in shop.

    Attributes:
        name (str): Item name
        description (str): Item description
        price (int): Cost in coins
        effect (Callable): Function to apply effect
        purchased (bool): Whether item has been purchased
    """

    def __init__(self, name: str, description: str, price: int,
                 effect: Callable = None):
        """
        Initialize shop item.

        Args:
            name: Item name
            description: Item description
            price: Price in coins
            effect: Function to call when purchased
        """
        self.name = name
        self.description = description
        self.price = price
        self.effect = effect
        self.purchased = False

    def purchase(self) -> bool:
        """
        Purchase the item.

        Returns:
            True if successful
        """
        if self.purchased:
            return False

        if self.effect:
            self.effect()

        self.purchased = True
        return True


class Shop:
    """
    Shop with random items.

    Attributes:
        items (List[ShopItem]): Available items
    """

    def __init__(self):
        """Initialize shop with random items."""
        self.items: List[ShopItem] = []
        self.generate_items()

    def generate_items(self):
        """Generate random shop items."""
        self.items = []

        # All possible items
        item_pool = [
            ('shop.health_restore', 'Restore 2 hearts', SHOP_PRICE_HEALTH, 'restore_health'),
            ('shop.max_health', '+1 max health', SHOP_PRICE_MAX_HEALTH, 'max_health'),
            ('shop.damage_up', '+1 damage', SHOP_PRICE_DAMAGE, 'damage'),
            ('shop.fire_rate', 'Fire rate +1', SHOP_PRICE_FIRE_RATE, 'fire_rate'),
            ('shop.speed_up', 'Speed +1', SHOP_PRICE_SPEED, 'speed'),
            ('shop.shield', 'Shield power-up', SHOP_PRICE_SHIELD, 'shield'),
            ('shop.triple_shot', 'Triple shot power-up', SHOP_PRICE_TRIPLE_SHOT, 'triple_shot')
        ]

        # Select random items
        selected = random.sample(item_pool, min(SHOP_ITEM_COUNT, len(item_pool)))

        for name, desc, price, effect_type in selected:
            item = ShopItem(name, desc, price)
            item.effect_type = effect_type  # Store for later use
            self.items.append(item)

    def reroll(self):
        """Reroll shop items."""
        self.generate_items()

    def can_purchase(self, item_index: int, player_coins: int) -> bool:
        """
        Check if player can afford item.

        Args:
            item_index: Item index
            player_coins: Player's coins

        Returns:
            True if affordable
        """
        if item_index < 0 or item_index >= len(self.items):
            return False

        item = self.items[item_index]
        return not item.purchased and player_coins >= item.price

    def purchase_item(self, item_index: int) -> Optional[ShopItem]:
        """
        Purchase an item.

        Args:
            item_index: Item index

        Returns:
            Purchased item or None
        """
        if item_index < 0 or item_index >= len(self.items):
            return None

        item = self.items[item_index]
        if item.purchased:
            return None

        item.purchased = True
        return item

    def get_item(self, index: int) -> Optional[ShopItem]:
        """
        Get item by index.

        Args:
            index: Item index

        Returns:
            Shop item or None
        """
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def get_all_items(self) -> List[ShopItem]:
        """Get all shop items."""
        return self.items.copy()
