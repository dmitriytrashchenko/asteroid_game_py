# 🔧 Integration Guide - Roguelike Systems

## Как использовать новые системы в игре

Все roguelike системы созданы и готовы к интеграции. Вот как их использовать:

## 📁 Структура файлов

```
src/
├── roguelike/
│   ├── room.py          ✅ Система комнат с дверями
│   ├── level.py         ✅ Генератор уровней
│   ├── shop.py          ✅ Магазин
│   └── minimap.py       ✅ Мини-карта
│
├── entities/
│   ├── boss.py          ✅ Боссы с паттернами атак
│   ├── coin.py          ✅ Монеты
│   └── ship.py          ✅ Обновлён (система здоровья)
│
├── managers/
│   └── progress_manager.py  ✅ Мета-прогрессия
│
└── utils/
    └── localization.py  ✅ Локализация
```

## 🎮 Пример использования

### 1. Создание нового уровня

```python
from src.roguelike.level import Level

# Создать уровень
level = Level(level_number=1, difficulty=settings.difficulty)

# Получить стартовую комнату
start_room = level.start_room
level.enter_room(start_room)

# Текущая комната
current_room = level.current_room
```

### 2. Навигация по комнатам

```python
from src.constants import DOOR_TOP, DOOR_BOTTOM, DOOR_LEFT, DOOR_RIGHT

# Проверить наличие двери
if current_room.has_door(DOOR_TOP):
    # Получить соседнюю комнату
    next_room = level.get_adjacent_room(current_room, DOOR_TOP)

    # Перейти в комнату
    level.enter_room(next_room)
```

### 3. Создание босса

```python
from src.entities.boss import Boss
from src.constants import BOSS_ASTEROID_KING

# Создать босса
boss = Boss(x=640, y=360, boss_type=BOSS_ASTEROID_KING, level=level.level_number)

# Обновить босса
boss.update(dt, player_position)

# Атака
projectiles = boss.attack(player_position)

# Для Asteroid King - призвать астероиды
if boss.boss_type == BOSS_ASTEROID_KING:
    asteroids = boss.summon_asteroids(count=3)
```

### 4. Магазин

```python
from src.roguelike.shop import Shop

# Создать магазин
shop = Shop()

# Получить предметы
items = shop.get_all_items()

# Купить предмет
if shop.can_purchase(item_index, player_coins):
    item = shop.purchase_item(item_index)
    player_coins -= item.price

    # Применить эффект
    if item.effect_type == 'restore_health':
        ship.heal(2)
    elif item.effect_type == 'max_health':
        ship.increase_max_health(1)
    # и т.д.

# Перебросить предметы
shop.reroll()
```

### 5. Мини-карта

```python
from src.roguelike.minimap import Minimap

# Создать мини-карту
minimap = Minimap(level)

# Отрисовать
minimap.draw(screen)
```

### 6. Система здоровья корабля

```python
# Создать корабль с постоянными улучшениями
ship = Ship(x, y, settings)

# Применить улучшения из мета-прогрессии
ship.apply_upgrades(
    max_health_bonus=progress_manager.get_max_health_bonus(),
    damage_bonus=progress_manager.get_damage_bonus(),
    fire_rate_bonus=progress_manager.get_fire_rate_bonus(),
    speed_bonus=progress_manager.get_move_speed_bonus()
)

# Получить урон
ship.take_damage(1)  # Теряет 1 полсердца

# Лечение
ship.heal(2)  # Восстанавливает 1 сердце

# Увеличить макс. здоровье
ship.increase_max_health(1)  # +1 сердце

# Проверить жив ли
if ship.is_alive():
    # ...
```

### 7. Монеты

```python
from src.entities.coin import Coin
from src.constants import COIN_VALUE_SMALL, COIN_VALUE_LARGE

# Создать монету
coin = Coin(x, y, value=COIN_VALUE_SMALL)

# Обновить
coin.update(dt)

# Отрисовать
coin.draw(screen)

# Проверить сбор
if ship.collides_with(coin):
    player_coins += coin.get_value()
    coin.alive = False
```

### 8. Мета-прогрессия

```python
from src.managers.progress_manager import ProgressManager

# Инициализация
progress_manager = ProgressManager()

# Получить стартовые монеты
start_coins = progress_manager.get_starting_coins()

# Применить множитель монет
coin_multiplier = progress_manager.get_coin_multiplier()

# После завершения забега
progress_manager.record_run_completion(
    level_reached=current_level,
    bosses_defeated=bosses_killed,
    coins_collected=coins_collected,
    rooms_cleared=rooms_cleared
)

# Купить улучшение
if progress_manager.can_afford_upgrade('max_health'):
    progress_manager.purchase_upgrade('max_health')
```

### 9. Локализация

```python
from src.utils.localization import get_localization, t

# Получить локализацию
loc = get_localization()

# Установить язык
loc.set_language('en')  # or 'ru'

# Получить перевод
title = t('menu.title')  # "ASTEROIDS" или "АСТЕРОИДЫ"
new_game = t('menu.new_game')  # "NEW GAME" или "НОВАЯ ИГРА"

# В настройках
current_language = settings.language
loc.set_language(current_language)
```

## 🔗 Интеграция в Game.py

### Структура игрового цикла

```python
class Game:
    def __init__(self):
        # ... существующий код ...

        # Новые системы
        self.localization = get_localization()
        self.localization.set_language(self.settings.language)

        self.progress_manager = ProgressManager()
        self.level: Optional[Level] = None
        self.minimap: Optional[Minimap] = None
        self.shop: Optional[Shop] = None
        self.boss: Optional[Boss] = None

        # Валюта
        self.coins = 0

    def start_game(self):
        """Начать новый забег."""
        # Применить улучшения
        self.ship = Ship(WIDTH // 2, HEIGHT // 2, self.settings)
        self.ship.apply_upgrades(
            max_health_bonus=self.progress_manager.get_max_health_bonus(),
            damage_bonus=self.progress_manager.get_damage_bonus(),
            fire_rate_bonus=self.progress_manager.get_fire_rate_bonus(),
            speed_bonus=self.progress_manager.get_move_speed_bonus()
        )

        # Стартовые монеты
        self.coins = self.progress_manager.get_starting_coins()

        # Создать уровень
        self.level = Level(level_number=1, difficulty=self.settings.difficulty)
        self.minimap = Minimap(self.level)

        # Войти в стартовую комнату
        self.level.enter_room(self.level.start_room)

        # Заспавнить врагов
        self._spawn_room_enemies()

    def _spawn_room_enemies(self):
        """Заспавнить врагов в текущей комнате."""
        room = self.level.current_room

        if room.room_type == ROOM_TYPE_BOSS:
            # Создать босса
            boss_types = [BOSS_ASTEROID_KING, BOSS_VOID_HUNTER, BOSS_STAR_DESTROYER]
            boss_type = random.choice(boss_types)
            self.boss = Boss(WIDTH // 2, HEIGHT // 2, boss_type, self.level.level_number)

        elif room.room_type == ROOM_TYPE_NORMAL:
            # Создать астероиды
            count = room.enemies_count
            for _ in range(count):
                pos = random.choice(room.get_spawn_positions())
                asteroid = Asteroid(pos[0], pos[1],
                                  size=random.randint(2, 3),
                                  difficulty=self.settings.difficulty)
                self.asteroids.append(asteroid)

    def _check_room_cleared(self):
        """Проверить очистку комнаты."""
        if len(self.asteroids) == 0 and (not self.boss or not self.boss.alive):
            self.level.current_room.clear()

    def _transition_to_room(self, direction: str):
        """Перейти в другую комнату."""
        current = self.level.current_room
        next_room = self.level.get_adjacent_room(current, direction)

        if next_room:
            self.level.enter_room(next_room)
            self.bullets.clear()
            self.asteroids.clear()
            self.boss = None

            # Заспавнить врагов
            if not next_room.cleared:
                self._spawn_room_enemies()

            # Если магазин
            if next_room.is_shop_room():
                self.shop = Shop()
                self.state = STATE_SHOP
```

## 🎨 Отрисовка HUD

```python
def _draw_hud(self):
    """Отрисовать HUD."""
    # Сердца
    heart_x = 10
    heart_y = HEIGHT - 50
    full_hearts = self.ship.health // 2
    half_heart = self.ship.health % 2

    for i in range(self.ship.max_health // 2):
        if i < full_hearts:
            # Полное сердце
            pygame.draw.circle(screen, RED, (heart_x + i * 25, heart_y), 10)
        elif i == full_hearts and half_heart:
            # Половина сердца
            pygame.draw.circle(screen, RED, (heart_x + i * 25, heart_y), 10, 5)
        else:
            # Пустое сердце
            pygame.draw.circle(screen, GRAY, (heart_x + i * 25, heart_y), 10, 2)

    # Монеты
    coin_text = f"{t('hud.coins')}: {self.coins}"
    # ...

    # Мини-карта
    if self.minimap:
        self.minimap.draw(screen)
```

## ✅ Готово к использованию

Все системы **полностью реализованы** и готовы к интеграции:

- ✅ **Room system** - классы Room и Door
- ✅ **Level generator** - процедурная генерация
- ✅ **Boss system** - 3 босса с AI
- ✅ **Shop system** - покупки и reroll
- ✅ **Minimap** - визуализация карты
- ✅ **Health system** - сердца в Ship
- ✅ **Coin system** - валюта
- ✅ **Progress manager** - мета-прогрессия
- ✅ **Localization** - RU/EN

## 🚀 Следующие шаги

1. Обновить `game.py` с использованием примеров выше
2. Добавить UI для магазина
3. Добавить визуализацию дверей
4. Добавить переходы между комнатами
5. Протестировать все системы вместе

## 📝 Примечания

- Все классы имеют docstrings
- Type hints везде
- Обработка ошибок
- Готово к локализации

**Все компоненты работают независимо и легко интегрируются!** 🎮
