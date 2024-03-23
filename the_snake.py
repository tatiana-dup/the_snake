from random import choice, randint

import pygame


pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (229, 43, 80)

# Цвет змейки:
SNAKE_COLOR = (71, 167, 106)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Метод определяет, как объект будет отрисовываться на экране."""
        pass


class Apple(GameObject):
    """Дочерний класс, описывающий яблоко и действия с ним."""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(self.position)

    def randomize_position(self, list_exception_pos):
        """Устанавливает случайное положение яблока на игровом поле.

        Аргументы:
        - list_exception_pos: список с координатами каждого сегмента змейки.
        """
        # Задаем случайные координаты, но так, чтобы
        # яблоко не появилось под телом змейки.
        while True:
            x_pos = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y_pos = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x_pos, y_pos)
            if self.position not in list_exception_pos:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Дочерний класс, описывающий змейку и ее поведение."""

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Обновляет направления змейки после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждого сегмента)
        и проверяем, не столкнулась ли она с собой.
        """
        current_head_x_pos, current_head_y_pos = self.get_head_position()

        # В зависимости от направления движения, задаем изменение координат.
        dx, dy = {
            RIGHT: (GRID_SIZE, 0),
            UP: (0, -GRID_SIZE),
            LEFT: (-GRID_SIZE, 0),
            DOWN: (0, GRID_SIZE)
        }[self.direction]

        # Задаем новые координаты для головы змейки.
        new_head_x_pos = (current_head_x_pos + dx) % SCREEN_WIDTH
        new_head_y_pos = (current_head_y_pos + dy) % SCREEN_HEIGHT
        new_head_position = (new_head_x_pos, new_head_y_pos)

        # Проверяем, не столкнулась ли змейка с собой.
        if new_head_position in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, (new_head_position))

        # Проверяем, съела ли змейка яблоко.
        if len(self.positions) > self.length:
            self.last = self.positions.pop(-1)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние после
        столкновения с собой.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, UP, LEFT, DOWN])
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает действия пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает основной цикл игры."""
    the_apple = Apple()
    my_snake = Snake()

    while True:
        clock.tick(SPEED)

        handle_keys(my_snake)
        my_snake.update_direction()
        my_snake.move()

        if the_apple.position == my_snake.get_head_position():
            my_snake.length += 1
            the_apple.randomize_position(my_snake.positions)

        the_apple.draw()
        my_snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
