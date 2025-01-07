import pygame
import random


class PlayerAgent:
    def __init__(self, env):
        self.env = env
        self.x, self.y = env.start[1] * env.grid_size, env.start[0] * env.grid_size
        self.speed = env.grid_size
        self.image = env.player_image
        self.coins_collected = 0
        self.passes_collected = 0  # Новый атрибут для подсчета pass
        self.start_position = (env.start[0], env.start[1])  # Сохраняем начальную позицию

    def collect_pass(self):
        """Метод для сбора pass."""
        col, row = self.x // self.env.grid_size, self.y // self.env.grid_size
        if self.env.is_within_bounds(row, col) and self.env.maze[row][col] == "P":  # Если на клетке pass
            self.passes_collected += 1  # Увеличиваем счетчик pass
            self.env.maze[row][col] = 0  # Убираем pass с лабиринта
            self.env.passes += 1  # Обновляем отображаемое число pass


    def attempt_pass_through_wall(self, col, row):
        """Проверка на возможность пройти через стену, используя pass."""
        if self.env.maze[row][col] == 1:  # Если это стена
            if self.passes_collected > 0:
                self.passes_collected -= 1  # Используем один pass
                self.env.passes -= 1
                self.env.maze[row][col] = 0  # Убираем стену из лабиринта
                return True  # Проходить можно
        return False  # Если pass нет, проходить нельзя

    def collect_coin(self):
        """Метод для сбора монеты"""
        col, row = self.x // self.env.grid_size, self.y // self.env.grid_size

        if self.env.is_within_bounds(row,col) and self.env.maze[row][col] == "C":  # Если на клетке монета
            self.coins_collected += 1  # Увеличиваем счетчик монет
            self.env.maze[row][col] = 0  # Убираем монету с лабиринта

    def update(self):
        keys = pygame.key.get_pressed()
        nx, ny = self.x, self.y
        if keys[pygame.K_LEFT]:
            nx -= self.speed
        if keys[pygame.K_RIGHT]:
            nx += self.speed
        if keys[pygame.K_UP]:
            ny -= self.speed
        if keys[pygame.K_DOWN]:
            ny += self.speed

        if 0 <= nx < self.env.screen.get_width() and 0 <= ny < self.env.screen.get_height():
            col, row = nx // self.env.grid_size, ny // self.env.grid_size
            if self.env.maze[row][col] in (0, "C", "F", "S", "P"):  # Разрешенные клетки
                self.x, self.y = nx, ny
            elif self.env.maze[row][col] == 1:  # Если это стена
                if keys[pygame.K_SPACE]:  # Условие для использования pass
                    if self.attempt_pass_through_wall(col, row):
                        self.x, self.y = nx, ny

        self.collect_coin()  # Проверка сбора монеты
        self.collect_pass()  # Проверка сбора pass

    def draw(self):
        self.env.screen.blit(self.image, (self.x, self.y))




class EnemyAgent:
    def __init__(self, env):
        self.env = env
        self.x, self.y = random.randint(1, len(env.maze) - 2), random.randint(1, len(env.maze) - 2)
        self.x *= env.grid_size
        self.y *= env.grid_size
        self.speed = env.grid_size  # Сохраняем скорость
        self.image = env.enemy_image
        self.move_delay = 3  # Увеличим задержку для плавного движения
        self.frame_count = 0
        self.q_table = {}  # Таблица Q для обучения

    def update(self):
        self.frame_count += 1
        if self.frame_count >= self.move_delay:
            self.frame_count = 0
            current_state = (self.x, self.y)

            # Возможные действия врага (вверх, вниз, влево, вправо)
            actions = [(0, -self.speed), (0, self.speed), (-self.speed, 0), (self.speed, 0)]
            best_action = self.choose_action(current_state, actions)

            # Новая позиция после выбранного действия
            new_x = self.x + best_action[0]
            new_y = self.y + best_action[1]

            # Проверка, не выходит ли противник за пределы экрана
            if self.is_valid_move(new_x, new_y):
                self.x = new_x
                self.y = new_y

            # Обучение с новым состоянием
            self.learn(current_state, best_action)

    def choose_action(self, state, actions):
        """Выбор действия на основе таблицы Q."""
        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in actions}

        return max(actions, key=lambda action: self.q_table[state][action])

    def learn(self, state, action):
        """Обучение на основе вознаграждения."""
        reward = -1  # Для примера, можно изменить на более сложную систему вознаграждений
        next_state = (self.x + action[0], self.y + action[1])
        if next_state not in self.q_table:
            self.q_table[next_state] = {action: 0 for action in
                                        [(0, -self.speed), (0, self.speed), (-self.speed, 0), (self.speed, 0)]}

        # Обновление значения Q
        self.q_table[state][action] += 0.1 * (
                reward + 0.9 * max(self.q_table[next_state].values()) - self.q_table[state][action])

    def is_valid_move(self, new_x, new_y):
        """Проверка, можно ли сделать ход в новую позицию (не выходя за пределы экрана и не сталкиваясь с препятствиями)."""
        # Проверка, не выходит ли противник за пределы экрана
        if not (0 <= new_x < self.env.screen.get_width() and 0 <= new_y < self.env.screen.get_height()):
            return False

        # Проверка на столкновение с стенами
        col, row = new_x // self.env.grid_size, new_y // self.env.grid_size

        # Враги могут двигаться только на пустые клетки или клетки с монетами
        if self.env.is_within_bounds(row,col) and self.env.maze[row][col] in (0, "C", "P"):
            return True

        return False

    def draw(self):
        """Отображение врага на экране."""
        self.env.screen.blit(self.image, (self.x, self.y))
