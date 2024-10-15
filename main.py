import os
from pygame import Surface, SurfaceType
from extra_functions import schedule_table_load
import pygame

parent_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(parent_dir, 'resources')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
YELLOW = (255, 195, 63)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
BLUE = (0, 0, 255)

screen_size = (1280, 720)
new_size = (1136, 640)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(new_size)
pygame.display.set_caption("Расписание")
pygame.mouse.set_visible(True)

pre_screen = pygame.Surface(screen_size)

fps = 60
block = False

imgs = {}
fonts = {}
sheets = {}


def preload_resources():
    global imgs, fonts, sheets
    full_path = data_dir
    files = os.listdir(full_path)
    for file in files:
        if file.endswith('.png'):
            im = pygame.image.load(os.path.join(full_path, file)).convert_alpha()
            im.set_colorkey(BLACK)
            imgs.update({file[0:-4]: im})
        elif file.endswith('.jpg'):
            im = pygame.image.load(os.path.join(full_path, file))
            imgs.update({file[0:-4]: im})
        elif file.endswith('.ttf'):
            fonts.update({file[0:-4]: os.path.join(full_path, file)})
        elif file.endswith('.xlsx'):
            sheets.update({file[0:-5]: os.path.join(full_path, file)})
    print(imgs, fonts, sheets)

class Button:
    def __init__(self, mode: str, im_on: Surface | SurfaceType | None = None,
                 im_off: Surface | SurfaceType | None = None, non_blocking_mode: bool = False):
        """
        Класс для создания кнопок
        :param mode: режим кнопки push | toggle
        :param im_on: картинка для нажатой кнопки
        :param im_off: картинка для не нажатой кнопки
        :param non_blocking_mode: отключение блокировки (приминимо только к push) возвращает true пока кнопка нажата
        """
        self.block = False
        self.mode = mode
        self.pushed = False
        self.coords = None
        self.new_size = None
        self.native_size = screen_size
        self.im_on = im_on
        self.im_off = im_off
        self.non_block = non_blocking_mode

    def set_ims(self, im_on: Surface | SurfaceType | None = None, im_off: Surface | SurfaceType | None = None):
        """
        Метод для добавления/изменения картинок уже существующих кнопок
        :param im_on: картинка для нажатой кнопки
        :param im_off: картинка для не нажатой кнопки
        """
        self.im_on = im_on
        self.im_off = im_off

    def get_coords(self, x: float = 0, y: float = 0, default=None) -> tuple:
        """
        Метод получения позиции относительно позиции кнопки
        :param x: относительный х
        :param y: относительный у
        :param default: значение по умолчанию для тех случаев, когда у кнопки нет позиции
        :return:
        """
        if self.coords:
            return self.coords[0]+x, self.coords[1]+y
        else:
            return default

    def draw(self, text: str, coords: list, text_coords: tuple = (0, 0), color: list = BLACK, size: int = 20,
             new_size: tuple | str = 'native', box: bool = False, smooth: bool = False):
        """
        Метод для отрисовки кнопки. Только после отрисовки кнопка получает координаты!
        :param text: текст для отображения на кнопке
        :param coords: позиция кнопки
        :param text_coords: относительное положение текста на кнопке
        :param color: цвет обводки кнопки и текста
        :param size: размер текста
        :param new_size: размер экрана для маштабирования
        :param box: включает обводку кнопки
        :param smooth: включает "мягкое" маштабирование
        """
        self.new_size = new_size
        self.coords = coords

        if self.im_on and self.pushed:
            images(self.im_on, [self.coords[0], self.coords[1]], [self.coords[2], self.coords[3]], smooth=smooth)
        elif self.im_off and not self.pushed:
            images(self.im_off, [self.coords[0], self.coords[1]], [self.coords[2], self.coords[3]], smooth=smooth)

        if box:
            pygame.draw.rect(pre_screen, color, (coords[0], coords[1], coords[2], coords[3]), 5)
        if text:
            write(text, [coords[0] + text_coords[0], coords[1] + text_coords[1]], color, size=size)

    def check(self, global_block: bool = False) -> bool:
        """
        Метод для проверки состояния кнопки (требуется предварительно отрисовать кнопку!)
        :param global_block: включение глобальной блокировки (при нажатии блокируется нажатие ВСЕХ остальных кнопок)
        :return: bool состояния кнопки
        """
        global block
        pos = pygame.mouse.get_pos()
        if self.native_size == 'native':
            if (self.coords[0] < pos[0] < (self.coords[0] + self.coords[2])) and (
                    self.coords[1] < pos[1] < (self.coords[1] + self.coords[3])):
                if pygame.mouse.get_pressed(3)[0] and (not self.block or self.non_block):
                    if global_block and not block:
                        self.block = True
                        block = True
                        if self.mode == 'push':
                            self.pushed = True
                        elif self.mode == 'toggle':
                            self.pushed = not self.pushed
                    elif not global_block:
                        self.block = True
                        if self.mode == 'push':
                            self.pushed = True
                        elif self.mode == 'toggle':
                            self.pushed = not self.pushed
                elif not pygame.mouse.get_pressed(3)[0] and self.block:
                    if global_block:
                        block = False
                    self.block = False
                else:
                    if self.mode == 'push':
                        self.pushed = False
            elif self.mode == 'push':
                self.pushed = False

        else:
            y_div = self.native_size[1] / new_size[1]
            x_div = self.native_size[0] / new_size[0]
            if (self.coords[0] / x_div < pos[0] < (self.coords[0] / x_div + self.coords[2] / x_div)) and (
                    self.coords[1] / y_div < pos[1] < (self.coords[1] / y_div + self.coords[3] / y_div)):
                if pygame.mouse.get_pressed(3)[0] and (not self.block or self.non_block):
                    if global_block and not block:
                        block = True
                        self.block = True
                        if self.mode == 'push':
                            self.pushed = True
                        elif self.mode == 'toggle':
                            self.pushed = not self.pushed
                    elif not global_block:
                        self.block = True
                        if self.mode == 'push':
                            self.pushed = True
                        elif self.mode == 'toggle':
                            self.pushed = not self.pushed
                elif not pygame.mouse.get_pressed(3)[0] and self.block:
                    self.block = False
                    if global_block:
                        block = False
                else:
                    if self.mode == 'push':
                        self.pushed = False
            elif self.mode == 'push':
                self.pushed = False

        return self.pushed


def images(filename: Surface | SurfaceType, coords: list = (0, 0), size: str | list = 'native', rotation: float = 0,
           anchor: str | None = None, smooth: bool = False):
    """
    Функция для отрисовки картинок на экране
    :param filename: предварительно подгруженная картинка (или любая другая поверхность)
    :param coords: положение якоря картинки
    :param size: размер картинки после маштабирования (при list[высота] сохраняет соотношение сторон,
    при list[длина, высота] - нет)
    :param rotation: вращение картинки относительно геометрического центра ограничивающего прямоугольника
    :param anchor: якорь картинки (при None левый верхний угол,
     при 'mid' - геометрический центр ограничивающего прямоугольника)
    :param smooth: включает "мягкое" маштабирование
    """
    back = filename
    rect = None
    if size != 'native':
        if len(size) == 2:
            back = pygame.transform.scale(back, size)
        else:
            old_size = back.get_size()
            size_y = size[0]
            size_x = int((old_size[0] * size_y) / old_size[1])
            if not smooth:
                back = pygame.transform.scale(back, [size_x, size_y])
            else:
                back = pygame.transform.smoothscale(back, [size_x, size_y])
    if anchor == 'mid':
        t_size = back.get_size()
        div_x = int(t_size[0] / 2)
        div_y = int(t_size[1] / 2)
        if len(coords) > 2:
            rotation = coords[2]
        if rotation != 0:
            back = pygame.transform.rotozoom(back, rotation, 1)
            rect = back.get_rect(center=[coords[0], coords[1]])

    else:
        div_x = 0
        div_y = 0

    if not rect:
        pre_screen.blit(back, [coords[0] - div_x, coords[1] - div_y])
    else:
        pre_screen.blit(back, rect)


def write(text: str, coords: list, main_color: list, style: str = 'standard', size: int = 20,
          anchor: str | None = None):
    """
    Функция для отрисовки текста на экране
    :param text: текст для отрисовки
    :param coords: положение якоря текста
    :param main_color: цвет текста
    :param style: шрифт
    :param size: размер
    :param anchor: якорь картинки (при None левый верхний угол,
     при 'mid' - геометрический центр ограничивающего прямоугольника)
    """
    if style == 'standard':
        font = pygame.font.SysFont('arial', size)
    elif style == 'bold':
        font = pygame.font.SysFont('arialполужирный', size)
    elif style == 'italic':
        font = pygame.font.SysFont('arialкурсив', size)
    elif style == 'bold-italic':
        font = pygame.font.SysFont('arialполужирныйкурсив', size)
    else:
        font = pygame.font.Font(style, size)
    #     sys.exit(('Неверные параметры шрифта!', style))

    text = font.render(str(text), True, main_color)
    if not anchor:
        pre_screen.blit(text, (coords[0], coords[1]))
    elif anchor == 'mid':
        sz = text.get_size()
        pre_screen.blit(text, (coords[0] - (sz[0] / 2), coords[1] - (sz[1] / 2)))


def render(surface: Surface | SurfaceType, size: list | tuple | None = None, default_color: list | tuple = BLACK):
    """
    Функция для рендера поверхности на экране
    :param surface: поверхность для отрисовки на экране
    :param size: размер поверхности после маштабирования
    :param default_color: цвет заливки поверхности после отрисовки
    """
    screen.fill(default_color)
    if size and size != screen_size:
        new_surface = pygame.transform.smoothscale(surface, size)
    else:
        new_surface = surface
    screen.blit(new_surface, [0, 0])
    pre_screen.fill(default_color)


def get_mouse() -> tuple:
    """
    Функция для получения положения курсора на маштабированом экране
    :return: tuple(x, y) положения курсора
    """
    y_div = screen_size[1] / new_size[1]
    x_div = screen_size[0] / new_size[0]
    native = pygame.mouse.get_pos()
    return native[0] * x_div, native[1] * y_div


def buttons_supply(names: list, modes: list) -> dict:
    """
    Функция для быстрого создания произвольных словарей кнопок
    :param names: массив имён кнопок
    :param modes: массив режимов кнопок
    :return: dict{keys=names: items=buttons}
    """
    out = {}
    for i in range(len(names)):
        out.update({names[i]: Button(modes[i])})

    return out


class Main:
    def __init__(self):
        pass

    def draw(self):
        pass


preload_resources()

interface = Main()

done = False

while not done:

    pg_events = pygame.event.get()

    for event in pg_events:  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True

    interface.draw()

    render(pre_screen, new_size, LIGHT_GRAY)

    pygame.display.flip()
    pygame.display.update()
    clock.tick(fps)

pygame.display.quit()
