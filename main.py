import pygame
import math
import random
import sys

pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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
    def __init__(self, x, y):
        super().__init__(x, y)
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
    def __init__(self, x, y, size=3):
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
        
        # Случайная скорость
        speed = random.uniform(20, 80)
        direction = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2D(speed * math.cos(direction), speed * math.sin(direction))
    
    def update(self, dt):
        super().update(dt)
        self.angle += self.rotation_speed * dt
    
    def split(self):
        if self.size > 1:
            new_asteroids = []
            for _ in range(2):
                new_asteroid = Asteroid(self.position.x, self.position.y, self.size - 1)
                new_asteroids.append(new_asteroid)
            return new_asteroids
        return []

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Векторные Астероиды")
        self.clock = pygame.time.Clock()
        
        self.ship = Ship(WIDTH // 2, HEIGHT // 2)
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
        # Создаем начальные астероиды
        for _ in range(5):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            # Убеждаемся, что астероид не появляется рядом с кораблем
            while math.sqrt((x - self.ship.position.x)**2 + (y - self.ship.position.y)**2) < 100:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
            self.asteroids.append(Asteroid(x, y))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.ship.thrust = 0
        self.ship.rotation_speed = 0
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.ship.thrust = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship.rotation_speed = -3
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship.rotation_speed = 3
        if keys[pygame.K_SPACE]:
            self.shoot()
    
    def shoot(self):
        # Ограничиваем частоту стрельбы
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_shot') or current_time - self.last_shot > 200:
            bullet = Bullet(self.ship.position.x, self.ship.position.y, self.ship.angle)
            self.bullets.append(bullet)
            self.last_shot = current_time
    
    def update(self, dt):
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
                    self.score += 10 * (4 - asteroid.size)
                    
                    # Разбиваем астероид
                    new_asteroids = asteroid.split()
                    self.asteroids.extend(new_asteroids)
                    break
        
        # Проверяем столкновение корабля с астероидами
        for asteroid in self.asteroids:
            if self.ship.collides_with(asteroid):
                self.ship.alive = False
        
        # Добавляем новые астероиды если все уничтожены
        if len(self.asteroids) == 0:
            for _ in range(5):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                while math.sqrt((x - self.ship.position.x)**2 + (y - self.ship.position.y)**2) < 150:
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                self.asteroids.append(Asteroid(x, y, random.randint(2, 3)))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.ship.alive:
            self.ship.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Отображаем счет
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if not self.ship.alive:
            game_over_text = self.font.render("ИГРА ОКОНЧЕНА! Нажмите R для перезапуска", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        # Инструкции
        instructions = [
            "W/↑ - тяга",
            "A/← D/→ - поворот", 
            "ПРОБЕЛ - стрельба"
        ]
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, WHITE)
            self.screen.blit(text, (WIDTH - 200, 10 + i * 25))
        
        pygame.display.flip()
    
    def restart(self):
        self.ship = Ship(WIDTH // 2, HEIGHT // 2)
        self.bullets = []
        self.asteroids = []
        self.score = 0
        
        for _ in range(5):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            while math.sqrt((x - self.ship.position.x)**2 + (y - self.ship.position.y)**2) < 100:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
            self.asteroids.append(Asteroid(x, y))
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and not self.ship.alive:
                        self.restart()
            
            if self.ship.alive:
                self.handle_input()
            
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()