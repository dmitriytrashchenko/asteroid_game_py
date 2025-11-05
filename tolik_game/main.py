#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tolik: Escape from the Basement
A roguelike game inspired by The Binding of Isaac

Controls:
- WASD: Move Tolik
- Arrow Keys: Shoot tears
- ESC: Pause

Created as a complete Isaac-like roguelike!
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game


def main():
    """Main entry point."""
    print("=" * 60)
    print("TOLIK: ESCAPE FROM THE BASEMENT".center(60))
    print("=" * 60)
    print()
    print("Толик заперт в подвале своего дома...")
    print("Помоги ему сбежать, сражаясь с монстрами из кошмаров!")
    print()
    print("УПРАВЛЕНИЕ:".center(60))
    print("  WASD - Движение")
    print("  Стрелки - Стрельба слезами")
    print("  ESC - Пауза")
    print()
    print("=" * 60)
    print()

    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nИгра прервана пользователем.")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nСпасибо за игру!")


if __name__ == "__main__":
    main()
