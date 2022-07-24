import pygame
from random import randrange
from sqlite3 import *
from datetime import datetime

# меню игры
import pygame_menu
from pygame_menu.examples import create_example_window
from functools import partial

# натройка идеального звука
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()


class Snake():
    def __init__(self):
        # цвета в RGB
        self.red = (255, 0, 0)
        self.background = (122, 245, 196)

        # размеры экрана
        self.dis_width = 800
        self.dis_height = 600

        # загрузка файла музыки
        pygame.mixer.music.load("sounds/back.mp3")
        pygame.mixer.music.play(-1)
        self.s_cath = pygame.mixer.Sound("sounds/catch.ogg")
        self.over = pygame.mixer.Sound("sounds/over.ogg")

        self.dis = pygame.display.set_mode((self.dis_width, self.dis_height))
        self.clock = pygame.time.Clock()
        self.snake_block = 10

        # шрифты
        self.font_style = pygame.font.Font("fonts/Lobster-Regular.ttf", 30)
        self.score_font = pygame.font.Font("fonts/Lobster-Regular.ttf", 35)

    # функция вывода результата очков
    def yourScore(self, score):
        self.value_e = self.score_font.render("Your Score: " + str(score), True, self.red)
        self.dis.blit(self.value_e, [10, 5])

    def our_snake(self, snake_block, snake_list):
        for x in snake_list:
            pygame.draw.rect(self.dis, self.col, [x[0], x[1], snake_block, snake_block])

    def message(self, msg, color):
        mesg = self.font_style.render(msg, True, color)
        self.dis.blit(mesg, [180, 200])

    # вывод текста "Game over"
    def mes_res(self):
        self.dis.blit(self.font_style.render("Game Over", True, self.red), [350, 250])

    # функция которая выполняется при проигрыше
    def finish(self):
        self.over.play()  # выводим звук проигрыша
        # записуем в дб NickName и результат игры
        conn = connect("game.db")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS Game_table
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    dataFind DATATIME UNIQUE,
                                    nickName TEXT,
                                    score INTEGER
                                    )""")
        d_n = datetime.now()
        dat = [
            (d_n, self.name.get_value(), self.score)
        ]
        cur.executemany("INSERT INTO Game_table VALUES(NULL, ?, ?, ?)", dat)
        conn.commit()
        conn.close()

    def gameLoop(self, name, col, hard):
        # устанавливаем название игры
        pygame.display.set_caption('Snake Game')
        # устанавливаем иконку игры
        pygame.display.set_icon(pygame.image.load("images/snake_icon.png"))

        self.name = name  # получаем NickName игрока
        self.col = col.get_value()  # получаем цвет змейки
        self.hard = hard.get_value()[1]  # получаем уровень сложности игры

        self.x1 = self.dis_width / 2
        self.y1 = self.dis_height / 2

        self.x1_change = 0
        self.y1_change = 0

        self.snake_List = []
        self.Length_of_snake = 1
        self.score = 0

        # рандомим еду
        self.foodx = round(randrange(0, self.dis_width - self.snake_block) / 10.0) * 10.0
        self.foody = round(randrange(0, self.dis_height - self.snake_block) / 10.0) * 10.0

        self.game_over = False
        self.game_close = False

        # главный цикл игры
        while not self.game_over:
            # что отображать если проиграл
            while self.game_close == True:
                self.dis.fill(self.background)
                self.mes_res()
                self.yourScore(self.Length_of_snake - 1)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()

            # основной цикл игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

                # логика движение змейки
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.x1_change = -self.snake_block
                        self.y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        self.x1_change = self.snake_block
                        self.y1_change = 0
                    elif event.key == pygame.K_UP:
                        self.y1_change = -self.snake_block
                        self.x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        self.y1_change = self.snake_block
                        self.x1_change = 0

            # если змейка вышла за границу поля
            if self.x1 >= self.dis_width or self.x1 < 0 or self.y1 >= self.dis_height or self.y1 < 0:
                self.finish()
                self.game_close = True

            self.x1 += self.x1_change
            self.y1 += self.y1_change
            self.dis.fill(self.background)
            pygame.draw.rect(self.dis, self.red, [self.foodx, self.foody, self.snake_block, self.snake_block])

            self.head = []
            self.head.append(self.x1)
            self.head.append(self.y1)
            self.snake_List.append(self.head)

            if len(self.snake_List) > self.Length_of_snake:
                del self.snake_List[0]

            # если змейка съела саму себя
            for x in self.snake_List[:-1]:
                if x == self.head:
                    self.game_close = True
                    self.finish()

            self.our_snake(self.snake_block, self.snake_List)
            self.yourScore(self.Length_of_snake - 1)

            # когда змейка съела еду
            if self.x1 == self.foodx and self.y1 == self.foody:
                self.s_cath.play()  # воспроизводим звук при съедании еды
                self.foodx = round(randrange(0, self.dis_width - self.snake_block) / 10.0) * 10.0
                self.foody = round(randrange(0, self.dis_height - self.snake_block) / 10.0) * 10.0
                self.Length_of_snake += 1
                self.score += 1

            # выбираем разный FPS при выборе разного уровня сложности
            if self.hard == 0:
                self.clock.tick(10)
            elif self.hard == 1:
                self.clock.tick(20)
            elif self.hard == 2:
                self.clock.tick(30)

            pygame.display.update()

        pygame.quit()
        quit()


snake = Snake()


def start_the_game():
    snake.gameLoop(t, col, hard)


# закрашиваем цвет поля когда открыто меню
def paint_background(surface):
    surface.fill(snake.background)


def make_long_menu():
    global t, col, hard, n
    theme_menu = pygame_menu.themes.THEME_BLUE.copy()  # тематика меню (цвет)
    theme_menu.scrollbar_cursor = pygame_menu.locals.CURSOR_HAND
    menu = pygame_menu.Menu(
        height=400,
        onclose=pygame_menu.events.EXIT,
        theme=theme_menu,
        title='Snake Game',
        width=600
    )
    """настройка окон разных кнопок"""
    # настройка окна rules
    menu_text = pygame_menu.Menu(
        height=400,
        onclose=pygame_menu.events.EXIT,
        theme=pygame_menu.themes.THEME_BLUE,
        title='Rules of the game',
        width=600
    )
    # настройка окна about
    about = pygame_menu.Menu(
        height=400,
        onclose=pygame_menu.events.EXIT,
        theme=pygame_menu.themes.THEME_BLUE,
        title='About',
        width=600
    )
    # настройка окна settings
    settings = pygame_menu.Menu(
        height=400,
        onclose=pygame_menu.events.EXIT,
        theme=pygame_menu.themes.THEME_BLUE,
        title='Settings',
        width=600
    )

    """начало наполнения окна settings"""
    settings.add.label("You can choose the snake color")
    settings.add.vertical_margin(10)
    col = settings.add.color_input('Snake color: ',
                                   color_type=pygame_menu.widgets.COLORINPUT_TYPE_RGB,
                                   default=(0, 0, 0), font_size=18)
    settings.add.vertical_margin(10)
    items = [('Easy', 'EASY'),
             ('Medium', 'MEDIUM'),
             ('Hard', 'HARD')]
    settings.add.vertical_margin(10)
    hard = settings.add.selector(
        'Set difficulty:\t',
        items,
        selector_id='difficulty',
        default=0
    )
    settings.add.vertical_margin(100)
    settings.add.button(
        'Return to main menu',
        pygame_menu.events.BACK,
        align=pygame_menu.locals.ALIGN_CENTER
    )
    settings.add.vertical_margin(30)
    """конец наполнения окна settings"""

    """Главная страница меню"""
    t = menu.add.text_input('NickName: ', default='player')
    menu.add.button('Play', start_the_game)
    menu.add.button('Rules', menu_text)
    menu.add.button("Settings", settings)
    menu.add.button("About", about)
    menu.add.button('Exit', pygame_menu.events.EXIT)

    """начало наполнения окна about"""
    about.add.label("""Author
    Telegram: @antonSkazko
    Phone: +380682505442
    E-mail: sk.anton06@gmail.com
    """)
    about.add.button(
        'Return to main menu',
        pygame_menu.events.BACK,
        align=pygame_menu.locals.ALIGN_CENTER
    )
    """конец наполнения окна about"""

    """начало наполнения окна rules"""
    menu_text.add.label("""The goal of the game is to increase your length and size in order to become the biggest snake and get on the leaderboard. You can play this game for a very long time, being carried away by a simple, but very addictive game plot and easy controls. You can play as an ordinary snake eating fruits and sweets.
    """,
                        max_char=33,
                        align=pygame_menu.locals.ALIGN_CENTER,
                        margin=(0, -1)
                        )
    menu_text.add.button(
        'Return to main menu',
        pygame_menu.events.BACK,
        align=pygame_menu.locals.ALIGN_CENTER
    )
    menu_text.add.vertical_margin(30)
    """конец наполнения окна rules"""
    return menu


def main(test: bool = False):
    screen = create_example_window('Snake Game', (800, 600))
    menu = make_long_menu()
    while True:
        paint_background(screen)
        menu.mainloop(
            surface=screen,
            bgfun=partial(paint_background, screen),
            disable_loop=test,
        )
        pygame.display.update()


if __name__ == '__main__':
    main()
