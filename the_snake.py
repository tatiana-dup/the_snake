from random import choice, randint

import pygame as pg


pg.init()

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
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, object_color=(255, 255, 255)):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = object_color

    def draw_cell(self, position, body_color=None, border_color=BORDER_COLOR):
        """Метод отрисовывает один сегмент игрового объекта."""
        body_color = body_color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Метод определяет, как объект будет отрисовываться на экране."""
        raise NotImplementedError('Метод draw должен быть реализован'
                                  'в дочерних классах.')


class Apple(GameObject):
    """Дочерний класс, описывающий яблоко и действия с ним."""

    def __init__(self, object_color=APPLE_COLOR):
        super().__init__(object_color)
        self.randomize_position()

    def randomize_position(self,
                           list_exception_pos=[(SCREEN_WIDTH // 2,
                                                SCREEN_HEIGHT // 2)]
                           ):
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
        self.draw_cell(self.position)


class Snake(GameObject):
    """Дочерний класс, описывающий змейку и ее поведение."""

    def __init__(self, object_color=SNAKE_COLOR):
        super().__init__(object_color)
        self.positions = [self.position]
        self.length = None
        self.direction = None
        self.next_direction = None
        self.last = None
        self.reset(RIGHT)

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        # Затирание последнего сегмента
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR,
                           BOARD_BACKGROUND_COLOR)

        # Отрисовка новой головы змейки
        self.draw_cell(self.get_head_position())

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
        self.positions.insert(0, (new_head_position))

        # Проверяем, съела ли змейка яблоко.
        if len(self.positions) > self.length:
            self.last = self.positions.pop(-1)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self, direction=None):
        """Сбрасывает змейку в начальное состояние после
        столкновения с собой.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice([RIGHT, UP, LEFT, DOWN])


def handle_keys(game_object):
    """Обрабатывает действия пользователя"""
    # В словаре реализована логика, какое новое направление должен
    # принять игровой объект в зависимости от его текущего направления
    # и нажатой кнопокой.
    direction_logic = {
        (LEFT, pg.K_UP): UP,
        (RIGHT, pg.K_UP): UP,
        (UP, pg.K_LEFT): LEFT,
        (DOWN, pg.K_LEFT): LEFT,
        (LEFT, pg.K_DOWN): DOWN,
        (RIGHT, pg.K_DOWN): DOWN,
        (UP, pg.K_RIGHT): RIGHT,
        (DOWN, pg.K_RIGHT): RIGHT
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            else:
                game_object.next_direction = direction_logic.get(
                    (game_object.direction, event.key),
                    game_object.direction)


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

        if my_snake.get_head_position() in my_snake.positions[2:]:
            my_snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        my_snake.draw()
        the_apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
