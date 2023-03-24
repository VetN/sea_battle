from random import randint
import time


class GeneralException(Exception):
    pass


class SeadOutException(GeneralException):
    def __str__(self):
        return "Вы стреляете за пределы поля!"


class BoardUsedException(GeneralException):
    def __str__(self):
        return "Этот ход уже был"


class CoordUsedException(GeneralException):
    def __str__(self):
        return "Неправильный ввод"


class BoardWrongShipException(GeneralException):
    pass


class A:
    
    ''' На вход получает координаты, сравнивает их и выводит список. '''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        a = (self.x, self.y)
        return "A" + str(a)
        # return f"A({self.x}, {self.y})"  можно  использовать, если работает f-функция


class Ship:
    
    ''' Создает корабль:
    на входе: nos(координаты(x,y) носа корабля),
              pipe - кол-во труб,
              course - расположение,
              кол-во жизней равно кол-ву труб.
    Проверяет были ли эти координаты ранее (class A)
    на выходе: список координат корабля '''

    def __init__(self, nos, pipe, course):
        self.nos = nos
        self.pipe = pipe
        self.course = course
        self.lives = pipe

    @property
    def fun_makeship(self):
        form_ship = []
        for i in range(self.pipe):
            cur_x = self.nos.x
            cur_y = self.nos.y

            if self.course == 0:
                cur_x += i
            elif self.course == 1:
                cur_y += i

            form_ship.append(A(cur_x, cur_y))

        return form_ship  # список координат корабля

    # Проверка координат выстрела
    def fun_shoot(self, shoot):
        return shoot in self.fun_makeship


class Sea:
    '''Создает поле игры'''

    def __init__(self, hide=False):

        self.hide = hide  # скрывает клетки с кораблем
        self.count = 0  # кол-во пораженных кораблей

        self.sea_cage = [["| O"] * 9 for _ in range(9)]

        self.used_cage = []  # список занятых клеток любых
        self.map_ship = []  # список кораблей всех

    # создание клеток моря
    def __str__(self):
        print('    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |')
        print("-" * 42)
        res = ""

        for r, row in enumerate(self.sea_cage):
            print(r, ' ', *row, '|')
            # res += f"\n{i} | " + " | ".join(row) + " |" если есть f-функция

        # cкрывает корабли
        if self.hide:
            res = res.replace("| ▉", "| O")
        return res

    # cтавит корабль на море
    def fun_addshipsea(self, ship):

        for d in ship.fun_makeship:
            if self.fun_out(d) or d in self.used_cage:
                raise BoardWrongShipException(GeneralException)

        for d in ship.fun_makeship:
            self.sea_cage[d.x][d.y] = "| ▉"
            self.used_cage.append(d)

        self.map_ship.append(ship)
        self.fun_perimetr(ship)

    def fun_perimetr(self, ship, view=True):
        perimetr = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (1, -1), (1, 0), (1, 1)]

        for d in ship.fun_makeship:
            for dx, dy in perimetr:
                zon = A(d.x + dx, d.y + dy)
                if not (self.fun_out(zon)) and zon not in self.used_cage:
                    if view:
                        self.sea_cage[zon.x][zon.y] = "| •"
                    self.used_cage.append(zon)
        return self.used_cage

    # определение точки за пределами поля игры
    @staticmethod
    def fun_out(d):
        return not ((0 <= d.x < 9) and (0 <= d.y < 9))

    # ход
    def fun_hod(self, d):

        if self.fun_out(d):  # если координаты хода  выходят за пределы поля
            raise SeadOutException(GeneralException)

        if d in self.used_cage:  # если координаты занятой клетки
            raise BoardUsedException(GeneralException)

        self.used_cage.append(d)  # добавление координат в список занятых клеток
        print("список клеток", self.used_cage)
        for ship in self.map_ship:
            if d in ship.fun_makeship:  # если d есть в списке координат корабля, то
                ship.lives -= 1  # уменьшает жизнь
                self.sea_cage[d.x][d.y] = "| X"  # отмечает ход в клетке

                if ship.lives == 0:
                    self.count += 1  # добавляет в список убитых
                    self.fun_perimetr(ship, view=True)
                    print("\033[31m", "Корабль уничтожен!", "\033[0m")
                    time.sleep(2)
                    return True  # добавляет ход
                else:
                    print("\033[31m", "Корабль ранен!", "\033[0m")
                    time.sleep(1)
                    return True  # добавляет ход

        self.sea_cage[d.x][d.y] = "| •"

        print("\033[32m", "Мимо!", "\033[0m")
        time.sleep(1)
        return False  # переход хода

    # обнуление списка занятых точек перед началом игры
    def fun_newlist(self):
        self.used_cage = []


class Player:

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def fun_ask(self):
        raise NotImplementedError()

    # бесконечный цикл выстрелов
    def fun_move(self):
        while True:
            try:
                target = self.fun_ask()
                repeat = self.enemy.fun_hod(target)
                return repeat
            except GeneralException as e:
                print(e)


class Kom(Player):

    # координаты хода компьютера
    def fun_ask(self):
        d = A(randint(0, 8), randint(0, 8))
        # print(f" Ход компьютера: {d.x} {d.y}")
        fx = d.x
        fy = d.y
        print("Координаты хода компьютера:", fx, fy)
        time.sleep(2)
        return d


class User(Player):

    def fun_ask(self):
        while True:
            coord = input('введите два числа через пробел:').split()
            if len(coord) != 2:
                raise CoordUsedException(GeneralException)

            if not (coord[0].isdigit() and coord[1].isdigit()):
                raise CoordUsedException(GeneralException)

            x, y = map(int, coord)
            if x < 0 or y < 0 or x > 8 or y > 8:
                raise SeadOutException(GeneralException)

            print("Координаты вашего хода:", x, y)  
            return A(x, y)


class Game:
    
    '''  Создание карты расстановки всех кораблей.  '''

    def __init__(self):
        # plaboard = self.fun_randboa()
        if choice == 0:
            plaboard = self.fun_randboa()
        else:
            plaboard = boards
        comboard = self.fun_randboa()
        comboard.hide = True

        self.kom = Kom(comboard, plaboard)
        self.user = User(plaboard, comboard)

    # создание поля
    def fun_randboa(self):
        board = None
        while board is None:
            board = self.fun_makeboard()
        return board

    # расстановка кораблей на поле
    @staticmethod
    def fun_makeboard():
        lens = [4, 3, 3, 2, 2, 1, 1, 1]
        board = Sea()
        addmakeboard = 0
        for pipe in lens:
            while True:
                addmakeboard += 1
                if addmakeboard > 2000:
                    return None
                ship = Ship(A(randint(0, 8), randint(0, 8)), pipe, randint(0, 1))
                try:
                    board.fun_addshipsea(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.fun_newlist()  # подготовка к игре
        return board

    def fun_cyclegame(self):
        num = 0
        while True:
            print("\033[35m", "Игровое поле игрока\n", self.user.board, "\033[0m")
            print("Игровое поле компьютера\n", self.kom.board)
            if num % 2 == 0:
                print("Ваш ход! Ход №", num)
                repeat = self.user.fun_move()
            else:
                print("Ход компьютера! Ход №", num)
                repeat = self.kom.fun_move()
            if repeat:
                num -= 1
            if self.kom.board.count == 2:
                print("\033[35m", "Поздравляем! Вы победили!", "\033[0m")
                print(self.kom.board)
                break

            if self.user.board.count == 2:
                print("Упс! Победил компьютер!")
                print(self.user.board)
                break
            num += 1


#  определяем координаты носа корабля
def fun_coords():
    while True:
        coord = input("введите 2 числа").split()
        if len(coord) != 2:
            raise CoordUsedException(GeneralException)
        if not (coord[0].isdigit() and coord[1].isdigit()):
            raise CoordUsedException(GeneralException)

        x, y = map(int, coord)
        if x < 0 or y < 0 or x > 8 or y > 8:
            print('число вне диапазона')
            continue
        nos = (x, y)
        return nos


#  определяем расположение корабля
def fun_cour():
    while True:
        cour = input("Введите расположение корабля\n0 - вертикальное\n1-горизонтальное")
        if not cour.isdigit():
            print("введите число")
            continue
        cour = int(cour)
        if 0 != cour != 1:
            print('неправильный ввод, введите 0 или 1')
            continue
        return cour


# форма корабля(координаты носа и расположение)
def loop():
    nos = fun_coords()
    cour = fun_cour()
    return nos, cour


# определяем  возможность установки корабля на море
def fun_maps(x, y, pipe, cour, board):
    ship = Ship(A(x, y), pipe, cour)
    try:
        board.fun_addshipsea(ship)
    except BoardWrongShipException(GeneralException):
        fun_enter(pipe, board)
    boa = board
    print(boa)
    return boa


# ставим корабль на море
def fun_enter(pipe, board):

    if pipe == 1:
        nos = fun_coords()
        x, y = nos
        pipe = 1
        cour = 1
        boa = fun_maps(x, y, pipe, cour, board)

    else:
        nos, cour = loop()
        x, y = nos
        boa = fun_maps(x, y, pipe, cour, board)

    return boa


def fun_hello():
    
    print("\033[33m", "НАЧИНАЕМ ИГРУ", "\033[0m")
    print("\033[34m", "первое число 'Х' -ряд")
    print(" второе число 'Y' - столбец", "\033[0m")


# расставляем корабли
def fun_draw():
    board = Sea()
    print("\033[34m", "Расстановка четырехтрубника\nкоординаты носа корабля", "\033[0m")
    boa = fun_enter(4, board)

    for i in range(2):
        print("\033[34m", "Расстановка трех трубника\nкоординаты носа корабля", "\033[0m")
        fun_enter(3, board)

    for i in range(3):
        print("\033[34m", "Расстановка двух трубника\nкоординаты носа корабля", "\033[0m")
        fun_enter(2, board)

    for i in range(4):
        print("\033[34m", "Расстановка одно трубника\nкоординаты носа корабля", "\033[0m")
        fun_enter(1, board)
    
    return boa


# начало игры здесь
fun_hello()
while True:
    ans_st = input("Вы хотите расставить корабли? Нажмите 1\nЕсли это сделать компьютеру, то любую букву")
    if ans_st != "1":
        choice = 0

    else:
        print("\033[34m", "Расстановка кораблей", "\033[0m")
        b = Sea()
        print(b)
        boards = fun_draw()   # создаем сами карту кораблей
        boards.fun_newlist()  # обнуляем список занятых клеток
    print("\033[33m", "НАЧИНАЕМ ИГРУ", "\033[0m")
    f = Game().fun_cyclegame()   # уходим в цикл игры

    ex = input("Хотите сыграть еще? Нажмите 1.\n Если нет, то любую букву")
    if ex != "1":
        print("\033[34m", "Спасибо за игру!", "\033[0m",)
        break
