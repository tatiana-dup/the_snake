from random import choice, randint

import pygame as pg


pg.init()

# Константы для размеров экрана, информационной панели, игрового поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 500
PANEL_WIDTH, PANEL_HIGHT = SCREEN_WIDTH, 20
GAME_WINDOW_WIDTH, GAME_WINDOW_HIGHT = SCREEN_WIDTH, (
    SCREEN_HEIGHT - PANEL_HIGHT)
PANEL_POSITION = (0, GAME_WINDOW_HIGHT)
SCREEN_CENTER = (SCREEN_WIDTH // 2, GAME_WINDOW_HIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_WINDOW_HIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет информационной панели:
PANEL_COLOR = (95, 158, 160)

# Цвет информационной панели:
PANEL_COLOR = (95, 158, 160)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Базовый цвет объекта:
OBJECT_COLOR_WHITE = (255, 255, 255)

# Цвет яблока:
APPLE_COLOR = (229, 43, 80)

# Цвет несъедобного мусора:
GARBAGE_COLOR = (189, 183, 107)

# Цвет змейки:
SNAKE_COLOR = (71, 167, 106)

# Шрифт для информационной панели:
INFO_FONT = pg.font.Font(None, 16)

# Шрифт для информационной панели:
INFO_FONT = pg.font.Font(None, 16)

# В словаре реализована логика, какое новое направление должен
# принять игровой объект в зависимости от его текущего направления
# и нажатой кнопокой.
OBJECT_DIRECTION_LOGIC = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}

# Скорость движения змейки:
SPEED = 13

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, object_color=OBJECT_COLOR_WHITE):
        self.position = SCREEN_CENTER
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
                           list_exception_pos=[SCREEN_CENTER]):
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


class Garbage(GameObject):
    """Дочерний класс, описывающий несъедобный мусор и действия с ним"""

    def __init__(self, list_exception_pos, object_color=GARBAGE_COLOR):
        super().__init__(object_color)
        self.randomize_position(list_exception_pos)

    def randomize_position(self, list_exception_pos):
        """Устанавливает случайное положение мусора на игровом поле.

        Аргументы:
        - list_exception_pos: список с координатами, которые нужно исключить
        из возможных координат появления.
        """
        # Задаем случайные координаты, но так, чтобы
        # мусор не появилось под телом змейки или под яблоком.
        while True:
            x_pos = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y_pos = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x_pos, y_pos)
            if self.position not in list_exception_pos:
                break

    def draw(self):
        """Отрисовывает мусор на игровой поверхности."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Дочерний класс, описывающий змейку и ее поведение."""

    def __init__(self, object_color=SNAKE_COLOR):
        super().__init__(object_color)
        self.reset(RIGHT)
        self.next_direction = None
        self.last = []

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        # Затирание последнего сегмента
        if len(self.last) > 0:
            for cell in self.last:
                self.draw_cell(cell, BOARD_BACKGROUND_COLOR,
                               BOARD_BACKGROUND_COLOR)
            self.last.clear()

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
        new_head_x_pos = (current_head_x_pos + dx) % GAME_WINDOW_WIDTH
        new_head_y_pos = (current_head_y_pos + dy) % GAME_WINDOW_HIGHT
        new_head_position = (new_head_x_pos, new_head_y_pos)
        self.positions.insert(0, (new_head_position))

        # Проверяем, съела ли змейка яблоко.
        if len(self.positions) > self.length:
            count_extra_cell = len(self.positions) - self.length
            for _ in range(count_extra_cell):
                self.last.append(self.positions.pop(-1))

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def change_speed(self, selector):
        """Изменяет скорость движения змейки."""
        if selector == 1:
            self.speed -= 1
        else:
            self.speed += 1

    def reset(self, direction=None):
        """Сбрасывает змейку в начальное состояние после
        столкновения с собой.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice([RIGHT, UP, LEFT, DOWN])
        self.speed = SPEED


def handle_keys(game_object):
    """Обрабатывает действия пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pg.K_1:
                game_object.change_speed(1)
            elif event.key == pg.K_2:
                game_object.change_speed(2)
            else:
                game_object.next_direction = OBJECT_DIRECTION_LOGIC.get(
                    (game_object.direction, event.key),
                    game_object.direction)


class InfoPanel():
    """Информационная панель на игровом поле"""

    def __init__(self):
        """Инициализация панели"""
        self.position = PANEL_POSITION
        self.color = PANEL_COLOR

    def draw_panel(self):
        """Отрисовывает информационную панель снизу экрана"""
        rect = pg.Rect(self.position, (PANEL_WIDTH, PANEL_HIGHT))
        pg.draw.rect(screen, self.color, rect)

    def draw_score(self, score):
        """Отображает счет"""
        score_text = INFO_FONT.render(f'Length: {score}',
                                      True,
                                      OBJECT_COLOR_WHITE)
        screen.blit(score_text, (self.position[0] + 5, self.position[1] + 5))

    def draw_speed(self, speed):
        """Отображает скорость змейки"""
        speed_text = INFO_FONT.render(f'Speed: {speed}',
                                      True,
                                      OBJECT_COLOR_WHITE)
        screen.blit(speed_text, (self.position[0] + 100, self.position[1] + 5))

    def update_panel(self, score, speed):
        """Обновляем информационную панель"""
        self.draw_panel()
        self.draw_score(score)
        self.draw_speed(speed)


def main():
    """Запускает основной цикл игры."""
    the_apple = Apple()
    my_snake = Snake()
    some_garbage = Garbage(my_snake.positions + [the_apple.position])
    info_panel = InfoPanel()

    def start_over():
        my_snake.reset()
        the_apple.randomize_position(my_snake.positions)
        some_garbage.randomize_position(
            my_snake.positions + [the_apple.position]
        )
        screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(my_snake.speed)

        handle_keys(my_snake)
        my_snake.update_direction()
        my_snake.move()

        if the_apple.position == my_snake.get_head_position():
            my_snake.length += 1
            the_apple.randomize_position(my_snake.positions)

        if some_garbage.position == my_snake.get_head_position():
            if my_snake.length > 1:
                my_snake.length -= 1
                some_garbage.randomize_position(
                    my_snake.positions + [the_apple.position]
                )
            else:
                start_over()

        if my_snake.get_head_position() in my_snake.positions[2:]:
            start_over()

        my_snake.draw()
        the_apple.draw()
        some_garbage.draw()
        info_panel.update_panel(my_snake.length, my_snake.speed)
        pg.display.update()


if __name__ == '__main__':
    main()
