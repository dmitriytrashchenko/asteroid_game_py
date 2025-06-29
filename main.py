import pygame
import math
import random
import sys
import json
import os

pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Settings:
    def __init__(self):
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.difficulty = 1  # 0=легко, 1=нормально, 2=сложно
        self.controls = {
            'thrust': pygame.K_w,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'shoot': pygame.K_SPACE
        }
        self.load_settings()
    
    def save_settings(self):
        try:
            settings_data = {
                'music_volume': self.music_volume,
                'sound_volume': self.sound_volume,
                'difficulty': self.difficulty,
                'controls': {k: v for k, v in self.controls.items()}
            }
            with open('settings.json', 'w') as f:
                json.dump(settings_data, f)
        except:
            pass
    
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    data = json.load(f)
                    self.music_volume = data.get('music_volume', 0.5)
                    self.sound_volume = data.get('sound_volume', 0.7)
                    self.difficulty = data.get('difficulty', 1)
                    if 'controls' in data:
                        self.controls.update(data['controls'])
        except:
            pass

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def rotate(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.font = pygame.font.Font(None, 32)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
                return True
        return False
    
    def draw(self, screen):
        color = YELLOW if self.hovered else WHITE
        # Рисуем векторную рамку
        pygame.draw.rect(screen, color, self.rect, 2)
        
        # Текст
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 28)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
    
    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))
        self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
    
    def draw(self, screen):
        # Слайдер трек
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Ползунок
        slider_pos = (self.val - self.min_val) / (self.max_val - self.min_val)
        slider_x = self.rect.x + slider_pos * self.rect.width
        pygame.draw.circle(screen, YELLOW, (int(slider_x), self.rect.centery), 8)
        
        # Лейбл и значение
        label_text = f"{self.label}: {self.val:.1f}"
        text_surface = self.font.render(label_text, True, WHITE)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 30))

class GameObject:
    def __init__(self, x, y):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.angle = 0
        self.vertices = []
        self.alive = True
    
    def update(self, dt):
        self.position = self.position + self.velocity * dt
        # Оборачивание экрана
        self.position.x = self.position.x % WIDTH
        self.position.y = self.position.y % HEIGHT
    
    def draw(self, screen):
        if not self.alive:
            return
        
        transformed_vertices = []
        for vertex in self.vertices:
            rotated = vertex.rotate(self.angle)
            world_pos = rotated + self.position
            transformed_vertices.append((world_pos.x, world_pos.y))
        
        if len(transformed_vertices) > 2:
            pygame.draw.polygon(screen, WHITE, transformed_vertices, 2)
        elif len(transformed_vertices) == 2:
            pygame.draw.line(screen, WHITE, transformed_vertices[0], transformed_vertices[1], 2)
    
    def get_radius(self):
        max_dist = 0
        for vertex in self.vertices:
            dist = vertex.magnitude()
            if dist > max_dist:
                max_dist = dist
        return max_dist
    
    def collides_with(self, other):
        distance = math.sqrt((self.position.x - other.position.x)**2 + 
                           (self.position.y - other.position.y)**2)
        return distance < (self.get_radius() + other.get_radius())

class Ship(GameObject):
    def __init__(self, x, y, settings):
        super().__init__(x, y)
        self.settings = settings
        self.thrust = 0
        self.rotation_speed = 0
        self.vertices = [
            Vector2D(15, 0),    # нос
            Vector2D(-10, -8),  # левое крыло
            Vector2D(-5, 0),    # центр сзади
            Vector2D(-10, 8)    # правое крыло
        ]
        self.max_speed = 300
        self.thrust_power = 200
        self.friction = 0.98
    
    def update(self, dt):
        # Поворот
        self.angle += self.rotation_speed * dt
        
        # Тяга
        if self.thrust > 0:
            thrust_vector = Vector2D(self.thrust_power * self.thrust, 0).rotate(self.angle)
            self.velocity = self.velocity + thrust_vector * dt
        
        # Ограничение скорости
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
        
        # Трение
        self.velocity = self.velocity * self.friction
        
        super().update(dt)
    
    def draw(self, screen):
        super().draw(screen)
        
        # Рисуем пламя двигателя
        if self.thrust > 0:
            flame_vertices = [
                Vector2D(-5, 0),
                Vector2D(-15 - random.randint(0, 5), -3),
                Vector2D(-15 - random.randint(0, 5), 3)
            ]
            transformed_flame = []
            for vertex in flame_vertices:
                rotated = vertex.rotate(self.angle)
                world_pos = rotated + self.position
                transformed_flame.append((world_pos.x, world_pos.y))
            pygame.draw.polygon(screen, RED, transformed_flame)

class Bullet(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(x, y)
        self.angle = angle
        self.velocity = Vector2D(400, 0).rotate(angle)
        self.lifetime = 2.0
        self.vertices = [Vector2D(2, 0), Vector2D(-2, 0)]
    
    def update(self, dt):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, GREEN, (int(self.position.x), int(self.position.y)), 3)

class Asteroid(GameObject):
    def __init__(self, x, y, size=3, difficulty=1):
        super().__init__(x, y)
        self.size = size
        self.rotation_speed = random.uniform(-2, 2)
        
        # Генерируем случайную форму астероида
        num_vertices = random.randint(6, 10)
        radius = 15 * size
        self.vertices = []
        
        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            r = radius + random.randint(-radius//3, radius//3)
            self.vertices.append(Vector2D(r * math.cos(angle), r * math.sin(angle)))
        
        # Скорость зависит от сложности
        base_speed = 20 + difficulty * 20
        speed = random.uniform(base_speed, base_speed + 60)
        direction = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2D(speed * math.cos(direction), speed * math.sin(direction))
    
    def update(self, dt):
        super().update(dt)
        self.angle += self.rotation_speed * dt
    
    def split(self, difficulty):
        if self.size > 1:
            new_asteroids = []
            for _ in range(2):
                new_asteroid = Asteroid(self.position.x, self.position.y, self.size - 1, difficulty)
                new_asteroids.append(new_asteroid)
            return new_asteroids
        return []

class GameState:
    MENU = 0
    SETTINGS = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Векторные Астероиды")
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        
        self.state = GameState.MENU
        self.ship = None
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.high_score = self.load_high_score()
        
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.setup_menu()
        self.setup_settings()
    
    def setup_menu(self):
        self.menu_buttons = [
            Button(WIDTH//2 - 100, 250, 200, 50, "НОВАЯ ИГРА", self.start_game),
            Button(WIDTH//2 - 100, 320, 200, 50, "НАСТРОЙКИ", lambda: self.set_state(GameState.SETTINGS)),
            Button(WIDTH//2 - 100, 390, 200, 50, "ВЫХОД", self.quit_game)
        ]
    
    def setup_settings(self):
        self.settings_sliders = [
            Slider(WIDTH//2 - 150, 200, 300, 0.0, 1.0, self.settings.music_volume, "Музыка"),
            Slider(WIDTH//2 - 150, 280, 300, 0.0, 1.0, self.settings.sound_volume, "Звуки")
        ]
        
        self.difficulty_buttons = [
            Button(WIDTH//2 - 200, 360, 120, 40, "ЛЕГКО", lambda: self.set_difficulty(0)),
            Button(WIDTH//2 - 40, 360, 120, 40, "НОРМАЛЬНО", lambda: self.set_difficulty(1)),
            Button(WIDTH//2 + 120, 360, 120, 40, "СЛОЖНО", lambda: self.set_difficulty(2))
        ]
        
        self.settings_buttons = [
            Button(WIDTH//2 - 100, 480, 200, 50, "НАЗАД", lambda: self.set_state(GameState.MENU))
        ]
    
    def set_difficulty(self, difficulty):
        self.settings.difficulty = difficulty
        self.settings.save_settings()
    
    def set_state(self, state):
        self.state = state
    
    def start_game(self):
        self.ship = Ship(WIDTH // 2, HEIGHT // 2, self.settings)
        self.bullets = []
        self.asteroids = []
        self.score = 0
        
        # Создаем начальные астероиды
        asteroid_count = 3 + self.settings.difficulty * 2
        for _ in range(asteroid_count):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            # Убеждаемся, что астероид не появляется рядом с кораблем
            while math.sqrt((x - self.ship.position.x)**2 + (y - self.ship.position.y)**2) < 100:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
            self.asteroids.append(Asteroid(x, y, 3, self.settings.difficulty))
        
        self.state = GameState.PLAYING
    
    def quit_game(self):
        self.settings.save_settings()
        pygame.quit()
        sys.exit()
    
    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def handle_menu_events(self, event):
        for button in self.menu_buttons:
            if button.handle_event(event):
                break
    
    def handle_settings_events(self, event):
        for slider in self.settings_sliders:
            slider.handle_event(event)
        
        for button in self.difficulty_buttons:
            if button.handle_event(event):
                break
        
        for button in self.settings_buttons:
            if button.handle_event(event):
                break
        
        # Обновляем настройки из слайдеров
        self.settings.music_volume = self.settings_sliders[0].val
        self.settings.sound_volume = self.settings_sliders[1].val
        self.settings.save_settings()
    
    def handle_game_input(self):
        keys = pygame.key.get_pressed()
        
        self.ship.thrust = 0
        self.ship.rotation_speed = 0
        
        if keys[self.settings.controls['thrust']]:
            self.ship.thrust = 1
        if keys[self.settings.controls['left']]:
            self.ship.rotation_speed = -3
        if keys[self.settings.controls['right']]:
            self.ship.rotation_speed = 3
        if keys[self.settings.controls['shoot']]:
            self.shoot()
    
    def shoot(self):
        # Ограничиваем частоту стрельбы
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_shot') or current_time - self.last_shot > 200:
            bullet = Bullet(self.ship.position.x, self.ship.position.y, self.ship.angle)
            self.bullets.append(bullet)
            self.last_shot = current_time
    
    def update_game(self, dt):
        if not self.ship.alive:
            return
        
        self.ship.update(dt)
        
        # Обновляем пули
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.alive:
                self.bullets.remove(bullet)
        
        # Обновляем астероиды
        for asteroid in self.asteroids:
            asteroid.update(dt)
        
        # Проверяем столкновения пуль с астероидами
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if bullet.collides_with(asteroid):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 10 * (4 - asteroid.size) * (self.settings.difficulty + 1)
                    
                    # Разбиваем астероид
                    new_asteroids = asteroid.split(self.settings.difficulty)
                    self.asteroids.extend(new_asteroids)
                    break
        
        # Проверяем столкновение корабля с астероидами
        for asteroid in self.asteroids:
            if self.ship.collides_with(asteroid):
                self.ship.alive = False
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                self.state = GameState.GAME_OVER
        
        # Добавляем новые астероиды если все уничтожены
        if len(self.asteroids) == 0:
            asteroid_count = 4 + self.settings.difficulty * 2
            for _ in range(asteroid_count):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                while math.sqrt((x - self.ship.position.x)**2 + (y - self.ship.position.y)**2) < 150:
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                self.asteroids.append(Asteroid(x, y, random.randint(2, 3), self.settings.difficulty))
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Заголовок
        title = self.font_large.render("АСТЕРОИДЫ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Векторный декор вокруг заголовка
        for i in range(8):
            angle = i * math.pi / 4
            start_x = WIDTH//2 + math.cos(angle) * 120
            start_y = 150 + math.sin(angle) * 40
            end_x = WIDTH//2 + math.cos(angle) * 140
            end_y = 150 + math.sin(angle) * 50
            pygame.draw.line(self.screen, WHITE, (start_x, start_y), (end_x, end_y), 2)
        
        # Рекорд
        high_score_text = self.font_small.render(f"Рекорд: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10, HEIGHT - 30))
        
        for button in self.menu_buttons:
            button.draw(self.screen)
    
    def draw_settings(self):
        self.screen.fill(BLACK)
        
        # Заголовок
        title = self.font_large.render("НАСТРОЙКИ", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Слайдеры
        for slider in self.settings_sliders:
            slider.draw(self.screen)
        
        # Сложность
        difficulty_text = self.font_medium.render("Сложность:", True, WHITE)
        self.screen.blit(difficulty_text, (WIDTH//2 - 200, 320))
        
        for i, button in enumerate(self.difficulty_buttons):
            if i == self.settings.difficulty:
                # Подсветка выбранной сложности
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
            button.draw(self.screen)
        
        for button in self.settings_buttons:
            button.draw(self.screen)
    
    def draw_game(self):
        self.screen.fill(BLACK)
        
        if self.ship and self.ship.alive:
            self.ship.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # HUD
        score_text = self.font_medium.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.font_small.render(f"Рекорд: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10, 50))
        
        difficulty_names = ["ЛЕГКО", "НОРМАЛЬНО", "СЛОЖНО"]
        diff_text = self.font_small.render(f"Сложность: {difficulty_names[self.settings.difficulty]}", True, WHITE)
        self.screen.blit(diff_text, (WIDTH - 200, 10))
        
        # Инструкции
        pause_text = self.font_small.render("ESC - пауза", True, GRAY)
        self.screen.blit(pause_text, (WIDTH - 100, HEIGHT - 30))
    
    def draw_pause(self):
        # Затемнение
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Текст паузы
        pause_text = self.font_large.render("ПАУЗА", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        continue_text = self.font_medium.render("ESC - продолжить  |  M - в меню", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Game Over
        game_over_text = self.font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Финальный счет
        final_score_text = self.font_medium.render(f"Финальный счет: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        self.screen.blit(final_score_text, final_score_rect)
        
        # Новый рекорд?
        if self.score == self.high_score and self.score > 0:
            new_record_text = self.font_medium.render("НОВЫЙ РЕКОРД!", True, YELLOW)
            new_record_rect = new_record_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(new_record_text, new_record_rect)
        
        # Инструкции
        restart_text = self.font_medium.render("R - заново  |  M - в меню", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.PLAYING:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.PLAYING
                        elif event.key == pygame.K_m:
                            self.state = GameState.MENU
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_r:
                            self.start_game()
                        elif event.key == pygame.K_m:
                            self.state = GameState.MENU
                
                # Обработка событий интерфейса
                if self.state == GameState.MENU:
                    self.handle_menu_events(event)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_events(event)
            
            # Обновление игры
            if self.state == GameState.PLAYING:
                self.handle_game_input()
                self.update_game(dt)
            
            # Отрисовка
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.SETTINGS:
                self.draw_settings()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_game()
                self.draw_pause()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            
            pygame.display.flip()
        
        self.settings.save_settings()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()