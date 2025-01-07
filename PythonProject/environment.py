import os
import pygame
import random
from agents import EnemyAgent

class GameEnvironment:
    MAX_LEVELS = 5

    def __init__(self, screen, level):
        self.screen = screen
        self.level = level
        self.grid_size = min(screen.get_width(), screen.get_height()) // 20
        self.start = None
        self.finish = None
        self.enemies = []
        self.lives = 3  # Начальное количество жизней
        self.passes = 0  # Начальное количество pass
        self.load_assets()
        self.generate_maze()

    def load_assets(self):
        self.player_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'player.png')), (self.grid_size, self.grid_size))
        self.enemy_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'enemy.png')), (self.grid_size, self.grid_size))
        self.coin_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'coin.png')), (self.grid_size // 2, self.grid_size // 2))
        self.wall_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'wall.png')), (self.grid_size, self.grid_size))
        self.background_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'background.jpeg')), self.screen.get_size())
        self.pass_image = pygame.transform.scale(
            pygame.image.load(os.path.join('assets', 'pass.png')), size=(self.grid_size // 2, self.grid_size // 2))

    def add_pass(self):
        for _ in range(5):
            while True:
                cx, cy = random.randint(1, len(self.maze) - 2), random.randint(1, len(self.maze[0]) - 2)
                if self.maze[cx][cy] == 0:
                    self.maze[cx][cy] = "P"
                    break

    def generate_maze(self):
        # Увеличиваем размеры лабиринта на 1 клетку
        rows = (self.screen.get_height() // self.grid_size) + 1
        cols = (self.screen.get_width() // self.grid_size) + 1
        self.maze = [[1 for _ in range(cols)] for _ in range(rows)]

        # Начинаем генерацию с клетки (1, 1), чтобы не было стен справа и снизу
        stack = [(1, 1)]
        self.maze[1][1] = -1  # Starting point

        while stack:
            x, y = stack[-1]
            neighbors = [(x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)]
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if 1 <= nx < rows - 1 and 1 <= ny < cols - 1 and self.maze[nx][ny] == 1:
                    self.maze[nx][ny] = 0
                    self.maze[(x + nx) // 2][(y + ny) // 2] = 0
                    stack.append((nx, ny))
                    break
            else:
                stack.pop()

        self.generate_start_and_finish(rows, cols)
        self.add_coins(self.level * 8)
        self.add_pass()  # Добавляем pass в лабиринт


    def generate_start_and_finish(self, rows, cols):
        while True:
            start = (random.randint(1, rows - 2), random.randint(1, cols - 2))
            finish = (random.randint(1, rows - 2), random.randint(1, cols - 2))
            if start != finish and self.maze[start[0]][start[1]] == 0 and self.maze[finish[0]][finish[1]] == 0:
                self.start = start
                self.finish = finish
                self.maze[self.start[0]][self.start[1]] = "S"
                self.maze[self.finish[0]][self.finish[1]] = "F"
                break

    def add_coins(self, count):
        for _ in range(count):
            while True:
                cx, cy = random.randint(1, len(self.maze) - 2), random.randint(1, len(self.maze[0]) - 2)
                if self.maze[cx][cy] == 0:
                    self.maze[cx][cy] = "C"
                    break

    def coins_remaining(self):
        return sum(row.count("C") for row in self.maze)

    def on_finish(self):
        """Проверка завершения уровня."""
        if self.coins_remaining() == 0:  # Все монеты собраны
            self.level += 1
            if self.level > self.MAX_LEVELS:
                print("Game Complete!")
                self.level = self.MAX_LEVELS
                return True

            self.generate_maze()  # Генерация нового уровня
            self.enemies = []  # Очистить список врагов
            self.lives = 3  # Сбрасываем жизни на начальное значение
            return False
        return False

    def check_finish(self, player):
        """Проверка достижения финиша игроком."""
        col, row = player.x // self.grid_size, player.y // self.grid_size
        if (row, col) == self.finish and self.coins_remaining() == 0:  # Игрок на финише и монеты собраны
            return self.on_finish()
        return False

    def lose_life(self):
        """Уменьшаем количество жизней на 1."""
        self.lives -= 1
        if self.lives <= 0:
            print("Game Over!")
            return True  # Игра закончена, если жизней больше нет
        return False

    def render(self):
        self.screen.blit(self.background_image, (0, 0))
        for row_idx, row in enumerate(self.maze):
            for col_idx, cell in enumerate(row):
                x, y = col_idx * self.grid_size, row_idx * self.grid_size
                if cell == 1:
                    self.screen.blit(self.wall_image, (x, y))
                elif cell == "S":
                    pygame.draw.rect(self.screen, (0, 255, 0), (x, y, self.grid_size, self.grid_size))
                elif cell == "F":
                    pygame.draw.rect(self.screen, (255, 0, 0), (x, y, self.grid_size, self.grid_size))
                elif cell == "C":
                    self.screen.blit(self.coin_image, (x + self.grid_size // 4, y + self.grid_size // 4))
                elif cell == "P":  # Отображение pass
                    self.screen.blit(self.pass_image, (x + self.grid_size // 4, y + self.grid_size // 4))

        for enemy in self.enemies:
            enemy.draw()

        # Отображение количества жизней и pass
        font = pygame.font.Font(None, 36)
        #lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        #self.screen.blit(lives_text, (10, 10))

        pass_text = font.render(f"Passes: {self.passes}", True, (255, 255, 255))
        self.screen.blit(pass_text, (10, 50))

    def is_within_bounds(self, x, y):
        return 0 <= x < len(self.maze) and 0 <= y < len(self.maze[0])
