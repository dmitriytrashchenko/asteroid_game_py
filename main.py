#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Векторная игра "Астероиды" v3.0

Полностью переработанная версия с улучшенной архитектурой,
системой достижений, таблицей рекордов, power-up'ами,
процедурной генерацией звуков и визуальными эффектами.

Автор: Claude AI
Версия: 3.0
Дата: 2025-11-05

Требования:
- Python 3.6+
- pygame
- numpy (для генерации звуков)

Установка зависимостей:
    pip install pygame numpy

Запуск:
    python main.py

Управление:
    W - тяга
    A - поворот влево
    D - поворот вправо
    SPACE - стрельба
    ESC - пауза

Особенности:
    ✓ Модульная архитектура
    ✓ Type hints и документация
    ✓ Система жизней (3 жизни)
    ✓ Неуязвимость после возрождения
    ✓ Power-up'ы (щит, быстрая стрельба, тройной выстрел, жизнь)
    ✓ Система достижений (17 достижений)
    ✓ Таблица рекордов (топ-10)
    ✓ Эффекты частиц
    ✓ Процедурная генерация звуков
    ✓ Прогрессивная сложность (волны)
    ✓ 3 уровня сложности
    ✓ Настройки с сохранением
    ✓ Оптимизированная система коллизий
"""

import sys
import traceback

try:
    from src.game import Game

    def main():
        """Entry point for the game."""
        print("=" * 60)
        print("Векторная игра 'Астероиды' v3.0")
        print("=" * 60)
        print()
        print("Запуск игры...")
        print()
        print("Управление:")
        print("  W - тяга вперед")
        print("  A/D - поворот влево/вправо")
        print("  SPACE - стрельба")
        print("  ESC - пауза")
        print()
        print("Новые возможности v3.0:")
        print("  ✓ Система жизней")
        print("  ✓ Power-up'ы (щит, быстрая стрельба, тройной выстрел)")
        print("  ✓ Достижения")
        print("  ✓ Таблица рекордов")
        print("  ✓ Визуальные эффекты")
        print("  ✓ Звуковые эффекты")
        print("  ✓ Прогрессивная сложность")
        print()
        print("-" * 60)

        try:
            game = Game()
            game.run()
        except KeyboardInterrupt:
            print("\n\nИгра прервана пользователем")
            sys.exit(0)
        except Exception as e:
            print("\n\nКритическая ошибка при запуске игры:")
            print(f"  {type(e).__name__}: {e}")
            print("\nПолная трассировка:")
            traceback.print_exc()
            print("\nПроверьте установку зависимостей:")
            print("  pip install pygame numpy")
            sys.exit(1)

    if __name__ == "__main__":
        main()

except ImportError as e:
    print("=" * 60)
    print("ОШИБКА: Не удалось импортировать модули игры")
    print("=" * 60)
    print()
    print(f"Детали ошибки: {e}")
    print()
    print("Убедитесь, что все зависимости установлены:")
    print("  pip install pygame numpy")
    print()
    print("Если используется виртуальное окружение, активируйте его:")
    print("  source env/bin/activate  # Linux/Mac")
    print("  env\\Scripts\\activate     # Windows")
    print()
    sys.exit(1)
