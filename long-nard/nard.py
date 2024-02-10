"""Длинные нарды."""

from __future__ import annotations

import json
import math
import os
import random
import sys
from enum import Enum, unique

import pygame


##
# @mainpage Long Nardy game project
#
# @section description_main Description
# Simple Description
#
# @section notes_main Notes
# Simple notes
##
# @file main.py
#
# @brief Long Nardy game program with Doxygen style comments.
#
# @section description_doxygen_example Description
# Long Nardy game program with Doxygen style comments.


def time_to_text(time: int) -> str:
    """Преобразовать секунды в строку.
    @param time Число секунд
    @return Строковое представление времени
    """
    t_sec = time % 60
    t_min = (time // 60) % 60
    t_hour = time // 3600
    return f"{t_hour:d}:{t_min:02d}:{t_sec:02d}"


class Dice:
    """Класс кубиков."""

    def __init__(self, first: int = 0, second: int = 0):
        """Конструктор.
        @param first Значение первого кубика
        @param second Значение второго кубика
        """
        self.first = first
        self.second = second

    def copy(self, dice: Dice) -> None:
        """Копировать
        @param dice Экземпляр кубиков
        """
        self.first = dice.first
        self.second = dice.second

    def reset(self) -> None:
        """Сбросить состояние кубиков"""
        self.first = 0
        self.second = 0

    def roll_both(self) -> None:
        """Бросить оба кубика"""
        self.first = random.randint(1, 6)
        self.second = random.randint(1, 6)

    def roll(self, number: int) -> None:
        """Бросить кубик.
        @param number Какой кубик бросить
        """
        if number == 0:
            self.first = random.randint(1, 6)
        elif number == 1:
            self.second = random.randint(1, 6)

    def is_doubling(self) -> bool:
        """Проверить, выпал ли дубль.
        @return Выпал ли дубль
        """
        return self.first == self.second


class Record:
    """Класс статистики."""

    def __init__(self) -> None:
        """Конструктор."""
        self.sum: int = 0
        self.underplayed: int = 0
        self.player_one: int = 0
        self.player_two: int = 0
        self.min_party: int = 0
        self.max_party: int = 0
        self.avg_party: int = 0

    def reset(self) -> None:
        """Сбросить статистику."""
        self.sum = 0
        self.underplayed = 0
        self.player_one = 0
        self.player_two = 0
        self.min_party = 0
        self.max_party = 0
        self.avg_party = 0

    def read(self, filename: str) -> Record:
        """Прочитать файл статистики.
        @param filename Имя файла
        @return Экземпляр класса статистики
        """
        data: dict = {}
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        self.sum = int(data.get("sum", 0))
        self.underplayed = int(data.get("underplayed", 0))
        self.player_one = int(data.get("player_one", 0))
        self.player_two = int(data.get("player_two", 0))
        self.min_party = int(data.get("min_party", 0))
        self.max_party = int(data.get("max_party", 0))
        self.avg_party = int(data.get("avg_party", 0))
        return self

    def get_table(self) -> list[int]:
        """Получить таблицу со статистикой.
        @return Табличный вид статистики
        """
        return [
            self.sum,
            self.underplayed,
            self.player_one,
            self.player_two,
            self.min_party,
            self.max_party,
            self.avg_party,
        ]

    def write(self, filename: str) -> None:
        """Записать файл статистики.
        @param filename Имя файла
        """
        data: dict = {
            "sum": self.sum,
            "underplayed": self.underplayed,
            "player_one": self.player_one,
            "player_two": self.player_two,
            "min_party": self.min_party,
            "max_party": self.max_party,
            "avg_party": self.avg_party,
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


class State:
    """Класс состояния игровой доски."""

    def __init__(self, state: State | None = None):
        """Конструктор.
        @param state Состояние доски
        """
        self.checkers = [0] * 26
        self.owner = [-1] * 26
        self.ind = [[-1] for _ in range(26)]
        self.player = 0
        self.dice: Dice = Dice()
        self.step = 0
        self.move = 0
        self.remained_die: list[int] = []
        self.played_head = False
        self.color = 0
        self.amount = 0
        self.left = 0
        if state is not None:
            self.copy(state)
        else:
            self.init()

    def init(self):
        """Инициализировать."""
        for i in range(26):
            self.checkers[i] = 0
            self.owner[i] = -1
        self.checkers[24] = self.checkers[25] = 15
        self.owner[24] = 0
        self.owner[25] = 1
        self.init_ind()
        self.dice.reset()
        self.player = 0
        self.step = 0
        self.move = 0
        self.remained_die = []
        self.played_head = False
        self.color = 0
        self.amount = 30
        self.left = 0

    def copy(self, state: State) -> None:
        """Копировать состояние доски.
        @param state Состояние доски
        """
        self.checkers = state.checkers[:]
        self.owner = state.owner[:]
        for i in range(26):
            self.ind[i].clear()
            for j in range(len(state.ind[i])):
                self.ind[i].append(state.ind[i][j])
        self.player = state.player
        self.dice.copy(state.dice)
        self.remained_die = state.remained_die[:]
        self.step = state.step
        self.move = state.move
        self.color = state.color
        self.played_head = state.played_head
        self.amount = state.amount
        self.left = state.left

    def init_ind(self) -> None:
        """Инициализировать позиции шашек."""
        cnt_w = 0
        cnt_b = 15
        for i in range(26):
            self.ind[i].clear()
            self.ind[i].append(self.owner[i])
            for _ in range(self.checkers[i]):
                if self.owner[i] == 0:
                    self.ind[i].append(cnt_w)
                    cnt_w += 1
                if self.owner[i] == 1:
                    self.ind[i].append(cnt_b)
                    cnt_b += 1

    def __relative_pos(self, pos: int) -> int:
        """Вернуть позицию относительно головы игрока.
        @param pos Абсолютная позиция
        @return Относительная позиция
        """
        return (pos + 12 * self.player) % 24

    def __opponent_pos(self, pos: int) -> int:
        """Вернуть позицию относительно головы оппонента.
        @param pos Абсолютная позиция
        @return Относительная позиция
        """
        return (pos + 12 * (1 - self.player)) % 24

    def __is_player_pos(self, pos: int) -> bool:
        """Проверить, есть ли шашки игрока в лунке.
        @param pos Абсолютная позиция
        @return Флаг наличия шашек игрока в позиции
        """
        return self.owner[pos] == self.player ^ self.color

    def __is_empty_pos(self, pos: int) -> bool:
        """Проверить, свободна ли лунка.
        @param pos Абсолютная позиция
        @return Флаг отсутствия шашек в позиции
        """
        return self.owner[pos] == -1

    def __is_opponent_pos(self, pos: int) -> bool:
        """Проверить, занята ли лунка оппонентом.
        @param pos Абсолютная позиция
        @return Флаг наличия шашек оппонента в позиции
        """
        return not self.__is_empty_pos(pos) and not self.__is_player_pos(pos)

    def __is_home(self) -> bool:
        """Проверить, все ли шашки в доме.
        @return Флаг полноты шашек в доме
        """
        for i in range(18):
            if self.__is_player_pos(self.__relative_pos(i)):
                return False
        return True

    def is_remove_checkers(self, pos: int, number: int) -> bool:
        """Проверить, снятие ли шашки с доски.
        @param pos Абсолютная позиция
        @param number Длина хода
        @return Флаг снятия шашки с доски
        """
        return self.__relative_pos(pos) + number >= 24

    def __is_high_order(self, pos: int, number: int) -> bool:
        """Проверить, снятие ли с доски шашки старшего разряда.
        @param pos Абсолютная позиция
        @param number Длина хода
        @return Флаг снятие старшей шашки с доски
        """
        diff = self.__relative_pos(pos) + number - 24
        for i in range(pos - diff, pos):
            if self.__is_player_pos(i):
                return False
        return True

    def is_one_line(self) -> bool:
        """Проверить законность блока.
        @return Флаг законности блока
        """
        max_count = 0
        count = 0
        for i in range(23, -1, -1):
            if self.__is_player_pos(self.__opponent_pos(i)):
                count += 1
                max_count = max(max_count, count)
            if self.__is_empty_pos(self.__opponent_pos(i)):
                count = 0
            if self.__is_opponent_pos(self.__opponent_pos(i)):
                break
        if max_count > 5:
            return True
        return False

    def get_checkers_pos(self) -> list[int]:
        """Вернуть номера позиций игрока.
        @return Список позиций игрока
        """
        res: list[int] = []
        for i in range(24):
            if self.__is_player_pos(i):
                res.append(i)
        return res

    def fill_dice(self) -> None:
        """Заполнить очки на ход."""
        if not self.remained_die and self.step == 0:
            if self.dice.is_doubling():
                self.remained_die = [self.dice.first] * 4
            else:
                self.remained_die = [self.dice.first, self.dice.second]

    def __play_die(self, number: int) -> None:
        """Убрать кубик.
        @param number Номер кубика выполненного хода
        """
        self.fill_dice()
        del self.remained_die[self.remained_die.index(number)]

    def right_move(self, start: int, number: int) -> bool:
        """Проверить ход и сходить.
        @param start Позиция начала хода
        @param number Длина хода
        @return Флаг правильности хода
        """
        if not self.__is_player_pos(start):
            return False
        if self.step > 0 and not self.remained_die:
            return False
        if number not in self.remained_die:
            return False
        # Ход шашек
        if not self.is_remove_checkers(start, number):
            if not self.__is_opponent_pos((start + number) % 24):
                if self.__relative_pos(start) == 0:
                    if self.played_head:
                        if self.move == 0:
                            if self.dice.is_doubling():
                                if not (
                                    (self.dice.first == 3 and self.step == 3)
                                    or (self.dice.first == 4 and self.step == 2)
                                    or (self.dice.first == 6 and self.step == 1)
                                ):
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        self.played_head = True
                self.ind[(start + number) % 24].append(self.ind[start].pop())
                if len(self.ind[start]) == 1:
                    self.ind[start][0] = -1
                if self.ind[(start + number) % 24][0] == -1:
                    self.ind[(start + number) % 24][0] = self.owner[start]
                self.checkers[(start + number) % 24] += 1
                self.owner[(start + number) % 24] = self.owner[start]
                self.checkers[start] -= 1
                if self.checkers[start] == 0:
                    self.owner[start] = -1
                self.__play_die(number)

                self.step += 1
                return True
            return False
        # Вывод шашек
        if not self.__is_home():
            return False
        # Вывод шашек низшего разряда
        if self.__is_high_order(start, number):
            self.ind[24 + self.player].append(self.ind[start].pop())
            if len(self.ind[start]) == 1:
                self.ind[start][0] = -1
            self.checkers[24 + self.player] += 1
            self.checkers[start] -= 1
            if self.checkers[start] == 0:
                self.owner[start] = -1
            self.__play_die(number)
            self.step += 1
            return True
        return False


class TreeMove:
    """Класс дерева возможных ходов."""

    def __init__(self, state: State, start: int, die: int):
        """Конструктор.
        @param state Состояние доски
        @param start Позиция начала хода
        @param die Длина хода
        @return Дерево возможных ходов
        """
        self.state: State = state
        self.state.left = 0
        self.start = start
        self.die = die
        self.end = (start + die) % 24
        if self.state.is_remove_checkers(start, die):
            self.end = 24 + self.state.player
        self.checkers = self.state.get_checkers_pos()
        self.children: list[list[TreeMove]] = [[], []]
        self.value = [0, 0]
        if start == -1 or die == -1:
            self.state.remained_die = []
            self.state.fill_dice()

    def possible_move(self, start: int, end: int) -> TreeMove | None:
        """Найти возможный ход.
        @param start Начальная позиция
        @param end Конечная позиция
        @return Поддерево возможных ходов
        """
        for item1 in self.children:
            for item2 in item1:
                if start == item2.start:
                    if end == item2.end:
                        return item2
                    else:
                        res = item2.possible_move(item2.end, end)
                        if res is not None:
                            return res
        return None

    def next(self) -> None:
        """Просчитать следующие ходы."""
        self.checkers = self.state.get_checkers_pos()
        self.children = [[], []]
        self.value = [0, 0]
        self.state.left = 0
        if not self.state.remained_die:
            return
        last = 1
        if self.state.step == 0:
            if not self.state.dice.is_doubling():
                last = 2
        for i in range(0, last):
            if i == 0:
                die = max(self.state.remained_die)
            else:
                die = min(self.state.remained_die)
            for start in self.checkers:
                v_state = State(self.state)
                flag = v_state.right_move(start, die)
                if flag:
                    current_tree = TreeMove(v_state, start, die)
                    current_tree.next()
                    if v_state.left != 0 or not v_state.is_one_line():
                        self.children[i].append(current_tree)
                        self.value[i] = max(v_state.left + 1, self.value[i])
            if len(self.children[i]) > 1:
                self.children[i].sort(key=lambda x: x.start)
        if last == 2:
            if self.value[0] == 1 and self.value[1] > 1:
                self.children[0] = []
                self.value[0] = 0
            if self.value[1] == 1 and self.value[0] > 1:
                self.children[1] = []
                self.value[1] = 0
            if self.value[0] == 1 and self.value[1] == 1:
                self.children[1] = []
                self.value[1] = 0
            if not self.children[0] and self.children[1]:
                self.children[0] = self.children[1][:]
                self.value[0] = self.value[1]
                self.children[1] = []
                self.value[1] = 0
        self.state.left = max(self.value[0], self.value[1])


@unique
class Stage(Enum):
    """Перечисление этапов хода игрока."""

    INIT = 0
    BEGIN = 1
    TOSS = 2
    ROLL = 3
    MOVE = 4
    NEXT = 5
    WIN = 6


class Party:
    """Класс игровой доски."""

    def __init__(self):
        """Конструктор."""
        self.stage = Stage.INIT
        self.count = None
        self.color = None
        self.tree: TreeMove | None = None
        self.state = State()
        self.new_party()

    def new_party(self) -> None:
        """Начать новую партию."""
        self.stage = Stage.BEGIN
        self.state.init()
        self.tree = None
        self.count = 0
        self.color = None

    def __init_players(self, dice: Dice) -> None:
        """Начать расстановку шашек.
        @param dice Состояние кубиков
        """
        diff = dice.first - dice.second
        self.state.player = 0
        if diff > 0:
            self.state.color = 0
        else:
            self.state.color = 1
        for i in range(26):
            self.state.checkers[i] = 0
            self.state.owner[i] = -1
        self.state.owner[24] = self.state.color
        self.state.owner[25] = 1 - self.state.color
        self.state.checkers[0] = 15
        self.state.checkers[12] = 15
        self.state.owner[0] = self.state.color
        self.state.owner[12] = 1 - self.state.color
        self.state.init_ind()
        self.state.player = self.state.color
        self.state.move = 0

    # def get_stage(self) -> Stage:
    #     """Вернуть текущий этап хода.
    #     @return Этап хода
    #     """
    #     return self.stage

    def set_dice(self, dice: Dice) -> None:
        """Обработать состояние кубиков.
        @param dice Состояние кубиков
        """
        if self.stage == Stage.TOSS:
            if self.state.player == 0:
                self.state.player = 1
            elif self.state.player == 1:
                if dice.is_doubling():
                    self.state.player = 0
                else:
                    self.__init_players(dice)
                    self.stage = Stage.ROLL
        elif self.stage == Stage.ROLL:
            self.state.dice.copy(dice)
            self.__init_move()

    def start_party(self) -> None:
        """Начать кон."""
        if self.stage == Stage.BEGIN:
            self.state.player = 0
            self.stage = Stage.TOSS

    def next_player(self) -> None:
        """Передать ход."""
        self.stage = Stage.ROLL
        if self.state.player == 1 - self.state.color:
            self.state.move += 1
        self.state.player = 1 - self.state.player
        self.state.step = 0
        self.state.played_head = False

    def __init_move(self) -> None:
        """Начать перемещение шашек."""
        self.stage = Stage.MOVE
        self.tree = TreeMove(self.state, -1, -1)
        self.tree.next()
        if self.state.left == 0:
            self.stage = Stage.NEXT


@unique
class ButtonStatus(Enum):
    """Перечисление состояния кнопок."""

    DISABLED = 0
    ENABLED = 1
    TEXT = 2


class Button(pygame.sprite.Sprite):
    """Класс кнопок."""

    def __init__(self, *groups):
        """!Конструктор.
        @param groups Группы слайда
        """
        super().__init__(*groups)
        self.__idd = -1
        self.__text = ""
        self.x_pos = 0
        self.y_pos = 0
        self.status = ButtonStatus.DISABLED
        self.color = (255, 255, 255)
        self.font = pygame.font.Font("freesansbold.ttf", 22)
        self.image = self.font.render(self.__text, True, self.color)
        self.rect = self.image.get_rect()
        self.command = lambda *args: None

    def init(
        self,
        idd: int,
        text: str,
        x_pos: int,
        y_pos: int,
        status: ButtonStatus = ButtonStatus.TEXT,
    ) -> Button:
        """Инициализировать.
        @param idd Идентификатор кнопки
        @param text Текст кнопки
        @param x_pos Координата X кнопки
        @param y_pos Координата Y кнопки
        @param status Состояние кнопки
        @return Экземпляр класса кнопки
        """
        self.status = status
        if self.status == ButtonStatus.ENABLED:
            self.color = (255, 255, 0)
        elif self.status == ButtonStatus.DISABLED:
            self.color = (100, 100, 100)
        else:
            self.color = (255, 255, 255)
        self.__text = text
        self.font = pygame.font.Font("freesansbold.ttf", 22)
        self.image = self.font.render(self.__text, True, self.color)
        self.rect = self.image.get_rect()
        self.__idd = idd
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos
        self.command = lambda *args: None
        return self

    def change(
        self,
        x_pos: int | None = None,
        y_pos: int | None = None,
        text: str | None = None,
        status: ButtonStatus | None = None,
    ) -> None:
        """Изменить параметры кнопки.
        @param x_pos Координата X кнопки
        @param y_pos Координата Y кнопки
        @param text Текст кнопки
        @param status Состояние кнопки
        """
        if text is not None:
            self.__text = text
        if status is not None:
            self.status = status
        if x_pos is not None:
            self.x_pos = x_pos
        if y_pos is not None:
            self.y_pos = y_pos
        if self.status == ButtonStatus.ENABLED:
            self.color = (255, 255, 0)
        elif self.status == ButtonStatus.DISABLED:
            self.color = (100, 100, 100)
        else:
            self.color = (255, 255, 255)
        self.image = self.font.render(self.__text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos

    def pushable(self, yes: bool) -> None:
        """Переключить состояние кнопки.
        @param yes Флаг нажимаемой кнопки
        """
        if self.status != ButtonStatus.TEXT:
            if yes:
                self.change(status=ButtonStatus.ENABLED)
            else:
                self.change(status=ButtonStatus.DISABLED)


@unique
class Player(Enum):
    """Перечисление типов игрока."""

    HUMAN = 0
    COMPUTER = 1


class Settings:
    """Настройки."""

    def __init__(self, players: list[Player]) -> None:
        """Конструктор.
        @param players Типы игроков
        """
        self.players = players
        self.player_one = players[0]
        self.player_two = players[1]


class Control:
    """Класс контроллера."""

    def __init__(self, party: Party, settings: Settings, record: Record):
        """Конструктор.
        @param party Модель
        @param settings Настройки
        @param record Статистика
        """
        self.party = party  # состояние доски
        self.settings = settings  # настройки
        self.record = record  # таблица рекордов
        self.display: Display | None = None  # Слой отображения
        self.dice: Dice = Dice()
        self.count = 0
        self.editor = False  # Режим редактирования
        self.save = False
        self.time = 0
        self.run = True

    def is_running(self) -> bool:
        """Вернуть статус игры.
        @return Флаг активной игры
        """
        return self.run

    def exit(self) -> None:
        """Выйти."""
        self.run = False

    def timer(self) -> None:
        """Обновить счетчик секунд.
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        if self.party.stage not in [Stage.BEGIN, Stage.WIN]:
            self.time += 1
            self.display.menu.refresh()

    def reset_record(self) -> None:
        """Сбросить таблицу рекордов.
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        self.record = Record()
        self.display.refresh()
        self.display.menu.refresh()

    def set_display(self, display: Display) -> None:
        """Установить представление.
        @param display Экземпляр класса представления
        """
        self.display = display

    def toggle_editor(self) -> None:
        """Переключить режим редактирования.
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        if self.party.stage == Stage.ROLL and self.count == 0:
            self.editor = not self.editor
            self.display.panel.toggle_throw(not self.editor)
            self.display.refresh()
            self.display.menu.refresh()

    def restart(self, change: bool = True) -> None:
        """Перезапустить партию.
        @param change Флаг открытия меню
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        self.editor = False  # Режим редактирования выключен по умолчанию
        self.party.new_party()  # Сбросить состояние партии
        self.party.start_party()  # Начать новую партию
        self.display.resume = True
        self.display.init()  # Инициализация вью
        if change:
            self.display.toggle_menu(False)
        self.dice.reset()
        self.display.refresh()  # Обновление вью
        self.display.menu.refresh()  # Обновление меню
        self.display.panel.refresh()  # Обновление панели
        self.time = 0

    def throw_dice(self) -> None:
        """Бросить кубики.
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        if self.party.stage == Stage.TOSS:
            if self.count == 0:
                self.display.panel.toggle_throw(False)
                if self.party.state.player == 0:
                    self.dice.reset()
            self.dice.roll(self.party.state.player)
        if self.party.stage == Stage.ROLL:
            self.display.panel.toggle_throw(False)
            self.dice.roll_both()
        self.count += 1
        if self.count >= 1:
            self.count = -1

    def process(self) -> None:
        """Обработать этапы хода.
        @throw ValueError Display is None
        @throw ValueError TreeMove is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        if self.party.stage in [Stage.TOSS, Stage.ROLL]:
            if self.count > 0:
                self.throw_dice()
                self.display.panel.refresh()
                self.display.refresh()
            if self.count == -1 and self.display.pieces.stay != "":
                self.count = 0
                self.party.set_dice(self.dice)
                if self.party.stage in [Stage.TOSS, Stage.ROLL, Stage.NEXT]:
                    self.display.panel.toggle_throw(True)
        if self.party.stage == Stage.NEXT and self.display.pieces.stay != "":
            self.display.panel.toggle_throw(True)
            self.party.next_player()
        if self.party.stage == Stage.ROLL:
            self.display.panel.refresh()
        if self.party.stage == Stage.MOVE and self.display.pieces.stay != "":
            self.save = True
            self.display.panel.refresh()
        if self.party.stage == Stage.WIN:
            if self.display.resume:
                self.save = False
                if self.record.min_party == 0:
                    self.record.min_party = self.time
                else:
                    self.record.min_party = min(self.record.min_party, self.time)
                self.record.max_party = max(self.record.max_party, self.time)
                self.record.avg_party = (
                    self.record.avg_party * self.record.sum + self.time
                ) // (self.record.sum + 1)
                self.record.sum += 1
                if self.party.state.player == 0:
                    self.record.player_one += 1
                else:
                    self.record.player_two += 1
                self.display.resume = False
                self.display.panel.refresh()
                self.display.menu.refresh()
            self.display.resume = False
        if (
            self.settings.players[self.party.state.player] == Player.COMPUTER
            and not self.editor
        ):
            if self.display.pieces.stay or 1:
                if (
                    self.party.stage in [Stage.TOSS, Stage.ROLL]
                    and self.display.panel.buttons[2].status == ButtonStatus.ENABLED
                ):
                    self.throw_dice()
                if self.party.stage == Stage.MOVE:
                    if self.party.tree is None:
                        raise ValueError("TreeMove is None")
                    if self.party.state.player == 0:
                        item1 = random.choice(self.party.tree.children)
                    else:
                        item1 = self.party.tree.children[0]
                    if item1:
                        if self.party.state.player == 0:
                            item2 = random.choice(item1)
                        else:
                            if self.party.state.step == 0:
                                item2 = item1[0]
                            else:
                                item2 = item1[-1]
                        flag = self.try_move(
                            self.party.state.player ^ self.party.state.color,
                            item2.start,
                            item2.end,
                        )
                        if flag:
                            self.display.pieces.refresh()
                if self.party.stage == Stage.WIN and not self.display.resume:
                    self.restart(False)

    def change_settings(self, player: int) -> None:
        """Изменить настройки.
        @param player Номер игрока
        @throw ValueError Display is None
        """
        if self.display is None:
            raise ValueError("Display is None")
        if self.settings.players[player] == Player.HUMAN:
            self.settings.players[player] = Player.COMPUTER
        else:
            self.settings.players[player] = Player.HUMAN
        self.display.menu.refresh()

    def try_move(self, color: int, start: int, end: int) -> bool:
        """Попытаться сходить.
        @param color Номер цвета игрока
        @param start Позиция начала хода
        @param end Позиция конца хода
        @return Флаг корректности хода
        @throw ValueError TreeMove is None
        """
        if self.party.state.ind[end][0] == 1 - color:
            return False
        if len(self.party.state.ind[end]) > 15:
            return False
        if not self.editor:
            if self.party.stage != Stage.MOVE:
                return False
            if color != self.party.state.player ^ self.party.state.color:
                return False
            if self.party.tree is None:
                raise ValueError("TreeMove is None")
            tree = self.party.tree.possible_move(start, end)
            if tree is not None:
                self.party.state.copy(tree.state)
                self.party.tree = tree
                self.party.tree.state = self.party.state
                if max(tree.value) == 0:
                    if (
                        len(self.party.state.ind[24]) == 16
                        or len(self.party.state.ind[25]) == 16
                    ):
                        self.party.stage = Stage.WIN
                    else:
                        self.party.stage = Stage.NEXT
                return True
            else:
                return False
        else:
            self.party.state.ind[end].append(self.party.state.ind[start].pop())
            if len(self.party.state.ind[start]) == 1:
                self.party.state.ind[start][0] = -1
            if self.party.state.ind[end][0] == -1:
                self.party.state.ind[end][0] = self.party.state.owner[start]
            self.party.state.checkers[end] += 1
            self.party.state.owner[end] = self.party.state.owner[start]
            self.party.state.checkers[start] -= 1
            if self.party.state.checkers[start] == 0 and start not in [24, 25]:
                self.party.state.owner[start] = -1
            return True


@unique
class PieceStatus(Enum):
    """Перечисление состояния шашки."""

    STAY = 0
    TO_HOME = 1
    CLICKED = 2


class Piece(pygame.sprite.Sprite):
    """Класс элемента шашки."""

    def __init__(self, *groups):
        """Конструктор.
        @param groups Группы слайда
        """
        super().__init__(*groups)
        self.color = 0
        self.image = pygame.image.load("./resources/white.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = 0
        self.hgt = 0

        self.old_x = 0
        self.old_y = 0
        self.home_x = 0
        self.home_y = 0

        self.__idd = -1
        self.status = PieceStatus.STAY

    def init(self, idd: int, pos: int, hgt: int, color: int) -> Piece:
        """Инициализировать.
        @param idd Идентификатор шашки
        @param pos Поле шашки
        @param hgt Номер шашки в поле
        @param color Номер цвета шашки
        @return Экземпляр класса шашки
        """
        self.__idd = idd
        self.color = color
        if self.color == 0:
            self.image = pygame.image.load("./resources/white.png").convert_alpha()
        else:
            self.image = pygame.image.load("./resources/black.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = pos
        self.hgt = hgt
        self.rect.x, self.rect.y = self.pos_to_coord()
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        self.home_x = self.rect.x
        self.home_y = self.rect.y
        self.status = PieceStatus.STAY
        return self

    def pos_to_coord(self) -> tuple[int, int]:
        """Вернуть координаты позиции.
        @return Координаты шашки
        """
        coord = (-1, -1)
        pos = self.pos
        hgt = self.hgt
        if pos in range(6):
            coord = (56 + pos * 41, 548 - hgt * 17)
        elif pos in range(6, 12):
            coord = (116 + pos * 41, 548 - hgt * 17)
        elif pos in range(12, 18):
            coord = (116 + (23 - pos) * 41, 23 + hgt * 17)
        elif pos in range(18, 24):
            coord = (56 + (23 - pos) * 41, 23 + hgt * 17)
        elif pos == 24:
            coord = (4, 4 + hgt * 33)
        elif pos == 25:
            coord = (621, 563 - hgt * 33)
        return coord

    def get_pos(self) -> int:
        """Вернуть позицию по координатам (2 варианта).
        @return Номер позиции
        """
        pos = -1
        x_pos = self.rect.x + self.rect.width // 2
        y_pos = self.rect.y + self.rect.height // 2
        if 56 + 0 * 41 <= x_pos <= 56 + 6 * 41:
            if 548 - 16 * 16 <= y_pos <= 548 + 35:
                pos = (x_pos - 56) // 41
            elif 23 + 16 * 16 >= y_pos >= 23:
                pos = 23 - (x_pos - 56) // 41
        elif 116 + 6 * 41 <= x_pos <= 116 + 12 * 41:
            if 548 - 16 * 16 <= y_pos <= 548 + 35:
                pos = (x_pos - 116) // 41
            elif 23 + 16 * 16 >= y_pos >= 23:
                pos = 23 - (x_pos - 116) // 41
        elif x_pos <= 56 + 0 * 41:
            pos = 24
        elif 116 + 13 * 41 <= x_pos:
            pos = 25
        return pos


class AbstractLayer:
    """Абстрактный класс слоя."""

    def __init__(self, display: Display):
        """Конструктор.
        @param display Экземпляр класса представления
        """
        self.display = display

    def init(self) -> None:
        """Инициализировать.
        @throw NotImplementedError
        """
        raise NotImplementedError()

    def refresh(self) -> None:
        """Обновить слой.
        @throw NotImplementedError
        """
        raise NotImplementedError()

    def click(self, pos: tuple[int, int]) -> None:
        """Обработать нажатие кнопки мыши.
        @throw NotImplementedError
        """
        raise NotImplementedError()

    def draw(self) -> None:
        """Отрисовать слой.
        @throw NotImplementedError
        """
        raise NotImplementedError()


class Menu(AbstractLayer):
    """Класс слоя меню."""

    def __init__(self, display: Display):
        """Конструктор.
        @param display Экземпляр класса представления
        """
        super().__init__(display)
        self.__buttons: list[Button] = []
        self.__group: pygame.sprite.Group[Button] = pygame.sprite.Group()
        self.__surf = pygame.Surface((self.display.width, self.display.height))
        self.init()

    def init(self) -> None:
        """Инициализировать."""
        self.__surf.set_alpha(200)
        self.__group.empty()
        self.__buttons.clear()
        pygame.draw.rect(self.__surf, (0, 0, 0), (self.__surf.get_rect()), 0)
        pygame.draw.rect(self.__surf, (100, 100, 100), (self.__surf.get_rect()), 200)
        self.__buttons.append(Button().init(0, "Меню:", 293, 105))
        self.__buttons.append(Button().init(1, "Игрок 1:", 120, 135))
        self.__buttons.append(Button().init(2, "Игрок 2:", 120, 165))
        self.__buttons.append(Button().init(3, "", 380, 135, ButtonStatus.ENABLED))
        self.__buttons.append(Button().init(4, "", 380, 165, ButtonStatus.ENABLED))
        self.__buttons.append(
            Button().init(5, "Новая партия", 120, 195, ButtonStatus.ENABLED)
        )
        self.__buttons.append(
            Button().init(6, "Продолжить", 380, 195, ButtonStatus.DISABLED)
        )
        self.__buttons.append(Button().init(7, "Таблица рекордов:", 213, 225))
        self.__buttons.append(Button().init(8, "Сыграно партий:", 120, 255))
        self.__buttons.append(Button().init(9, "Не доиграно партий:", 120, 285))
        self.__buttons.append(Button().init(10, "Побед 1 игрока:", 120, 315))
        self.__buttons.append(Button().init(11, "Побед 2 игрока:", 120, 345))
        self.__buttons.append(Button().init(12, "Самая короткая партия:", 120, 375))
        self.__buttons.append(Button().init(13, "Самая длинная партия:", 120, 405))
        self.__buttons.append(Button().init(14, "Среднее время партии:", 120, 435))
        self.__buttons.append(Button().init(15, "", 420, 255))
        self.__buttons.append(Button().init(16, "", 420, 285))
        self.__buttons.append(Button().init(17, "", 420, 315))
        self.__buttons.append(Button().init(18, "", 420, 345))
        self.__buttons.append(Button().init(19, "", 420, 375))
        self.__buttons.append(Button().init(20, "", 420, 405))
        self.__buttons.append(Button().init(21, "", 420, 435))
        self.__buttons.append(
            Button().init(22, "Обнулить", 120, 465, ButtonStatus.ENABLED)
        )
        self.__buttons.append(
            Button().init(23, "Выход", 460, 465, ButtonStatus.ENABLED)
        )
        self.__buttons.append(Button().init(24, "Редактор:", 120, 525))
        self.__buttons.append(Button().init(25, "On", 380, 525, ButtonStatus.ENABLED))
        self.__buttons.append(Button().init(26, "Время партии:", 120, 495))
        self.__buttons.append(Button().init(27, "", 380, 495))
        self.__group.add(self.__buttons)
        self.refresh()
        self.__commands()

    def refresh(self) -> None:
        """Обновить меню."""
        text = (
            "Человек"
            if self.display.control.settings.players[0] == Player.HUMAN
            else "Компьютер"
        )
        self.__buttons[3].change(text=text)
        text = (
            "Человек"
            if self.display.control.settings.players[1] == Player.HUMAN
            else "Компьютер"
        )
        self.__buttons[4].change(text=text)
        text = "On" if self.display.control.editor else "Off"
        self.__buttons[25].change(text=text)

        table = self.display.control.record.get_table()
        for i in range(4):
            self.__buttons[i + 15].change(text=str(table[i]))
        for i in range(3):
            self.__buttons[i + 19].change(text=time_to_text(table[i + 4]))
        self.__buttons[6].pushable(self.display.resume)
        self.__buttons[27].change(text=time_to_text(self.display.control.time))
        self.__group.draw(self.__surf)
        self.display.refresh()

    def __commands(self) -> None:
        """Привязать команды к кнопкам."""
        self.__buttons[3].command = lambda *x: self.display.control.change_settings(0)
        self.__buttons[4].command = lambda *x: self.display.control.change_settings(1)
        self.__buttons[5].command = lambda *x: self.display.control.restart()
        self.__buttons[6].command = lambda *x: self.display.toggle_menu()
        self.__buttons[23].command = lambda *x: self.display.control.exit()
        self.__buttons[22].command = lambda *x: self.display.control.reset_record()
        self.__buttons[25].command = lambda *x: self.display.control.toggle_editor()

    def click(self, pos: tuple[int, int]) -> None:
        """Обработать нажатие кнопки мыши.
        @param pos Координаты нажатия кнопки мыши
        """
        for key in self.__group:
            if key.rect.collidepoint(pos) and key.status == ButtonStatus.ENABLED:
                key.command()

    def draw(self) -> None:
        """Отрисовать меню."""
        pygame.draw.rect(self.__surf, (0, 0, 0), (self.__surf.get_rect()), 0)
        pygame.draw.rect(self.__surf, (100, 100, 100), (self.__surf.get_rect()), 200)
        self.__group.draw(self.__surf)
        self.display.screen.blit(self.__surf, (0, 0))


class Panel(AbstractLayer):
    """Класс слоя панели."""

    def __init__(self, display: Display):
        """Конструктор.
        @param display Экземпляр класса модели
        """
        super().__init__(display)
        self.buttons: list[Button] = []

        self.__group: pygame.sprite.Group[Button] = pygame.sprite.Group()
        self.__surf = pygame.Surface((self.display.width, self.display.height))
        self.init()

    def init(self) -> None:
        """Инициализировать."""
        self.__group.empty()
        self.buttons.clear()
        pygame.draw.rect(self.__surf, (0, 0, 0), (self.__surf.get_rect()))
        self.buttons.append(Button().init(0, "Игрок 1", 5, 5))
        self.buttons.append(Button().init(1, "0:0", 315, 5))
        self.buttons.append(
            Button().init(2, "Бросьте кости", 500, 5, ButtonStatus.ENABLED)
        )
        self.buttons.append(Button().init(3, "Начало игры", 5, 35))
        self.buttons.append(Button().init(4, "Меню", 590, 35, ButtonStatus.ENABLED))
        self.__commands()
        self.__group.add(self.buttons)
        self.__group.draw(self.__surf)

    def toggle_throw(self, push: bool) -> None:
        """Включить/выключить кнопку броска."""
        self.buttons[2].pushable(push)
        self.refresh()

    def refresh(self, view_dice: bool = False) -> None:
        """Обновить панель.
        @param view_dice Флаг отображения состояния кубиков
        """
        dice = self.display.control.dice
        text = f"{dice.first}:{dice.second}"
        self.buttons[1].change(text=text)
        if not view_dice:
            player = self.display.party.state.player
            if self.display.party.stage == Stage.TOSS:
                self.buttons[0].change(text=f"Игрок {player+1}")
                self.buttons[3].change(text="Розыгрыш права первого хода")
            if self.display.party.stage in [Stage.ROLL, Stage.MOVE]:
                color = (
                    "белые"
                    if player ^ self.display.party.state.color == 0
                    else "черные"
                )
                move = self.display.party.state.move
                step = self.display.party.state.step
                left = self.display.party.state.left
                self.buttons[0].change(text=f"Игрок {player+1} ({color})")
                text = (
                    f"Ход {move+1}"
                    if self.display.party.stage == Stage.ROLL
                    else f"Ход {move+1} Шаг {step+1}/{left+step}"
                )
                self.buttons[3].change(text=text)
            if self.display.party.stage == Stage.WIN:
                color = (
                    "Белые"
                    if player ^ self.display.party.state.color == 0
                    else "Черные"
                )
                text = f"{color} выиграли! Игрок {player+1} побеждает"
                self.buttons[3].change(text=text)
        self.__group.draw(self.__surf)
        self.display.refresh()

    def __commands(self) -> None:
        """Привязать команды к кнопкам."""
        self.buttons[2].command = lambda *x: self.display.control.throw_dice()
        self.buttons[4].command = lambda *x: self.display.toggle_menu()

    def click(self, pos: tuple[int, int]) -> None:
        """Обработать нажатие кнопки мыши.
        @param pos Координаты нажатия кнопки мыши
        """
        for key in self.__group:
            if (
                key.rect.collidepoint((pos[0], pos[1] - self.display.height + 60))
                and key.status == ButtonStatus.ENABLED
            ):
                key.command()

    def draw(self) -> None:
        """Отрисовать панель."""
        pygame.draw.rect(self.__surf, (0, 0, 0), (self.__surf.get_rect()))
        self.__group.draw(self.__surf)
        self.display.screen.blit(self.__surf, (0, self.display.height - 60))


class Pieces(AbstractLayer):
    """Класс слоя шашек."""

    def __init__(self, display: Display):
        """Конструктор.
        @param display Экземпляр класса представления
        """
        super().__init__(display)
        self.group: pygame.sprite.OrderedUpdates = pygame.sprite.OrderedUpdates()
        self.stay = False

        # self.__white = pygame.image.load("./resources/white.png").convert_alpha()
        # self.__black = pygame.image.load("./resources/black.png").convert_alpha()
        self.__pieces: list[Piece] = []
        self.__ind = self.display.party.state.ind
        self.init()

    def init(self) -> None:
        """Инициализировать."""
        self.stay = False
        self.group.empty()
        self.__pieces.clear()
        self.__pieces = [Piece() for _ in range(self.display.party.state.amount)]
        for i, _ in enumerate(self.__ind):
            if self.__ind[i][0] != -1:
                for j in range(1, len(self.__ind[i])):
                    player = self.__ind[i][0]
                    tmp = self.__pieces[self.__ind[i][j]]
                    tmp.init(self.__ind[i][j], i, 0, player)
                    self.group.add(tmp)

    def draw(self) -> None:
        """Отрисовать слой шашек."""
        self.group.draw(self.display.screen)

    def click(self, pos: tuple[int, int]) -> None:
        """Обработать нажатие кнопки мыши.
        @param pos Координаты нажатия кнопки мыши
        """
        tops = [self.__pieces[x[-1]] for x in self.__ind if len(x) > 1]
        selected_idx = -1
        for idx, _ in enumerate(tops):
            if tops[idx].rect.collidepoint(pos):
                selected_idx = idx
        if selected_idx != -1:
            selected_key = tops[selected_idx]
            selected_key.old_x = selected_key.rect.x
            selected_key.old_y = selected_key.rect.y
            selected_key.status = PieceStatus.CLICKED
            selected_key.remove(self.group)
            selected_key.add(self.group)

    def release(self) -> None:
        """Обработать отпускание кнопки мыши."""
        for key in self.group:
            if key.status == PieceStatus.CLICKED:
                pos = key.get_pos()
                if (
                    self.display.control.settings.players[
                        self.display.party.state.player
                    ]
                    == Player.COMPUTER
                    or pos == -1
                    or not self.display.control.try_move(key.color, key.pos, pos)
                ):
                    key.status = PieceStatus.TO_HOME
                    self.stay = False

    def refresh(self) -> None:
        """Обновить слой шашек."""
        self.stay = True
        self.group.empty()
        for j in range(1, 17):
            for i in range(26):
                if self.__ind[i][0] != -1:
                    if j < len(self.__ind[i]):
                        piece_id = self.__ind[i][j]
                        piece = self.__pieces[piece_id]
                        self.group.add(piece)
                        if piece.status != PieceStatus.TO_HOME:
                            if piece.pos != i or piece.hgt != j - 1:
                                piece.status = PieceStatus.TO_HOME
                                self.stay = False
                                piece.pos = i
                                piece.hgt = j - 1
                                piece.home_x, piece.home_y = piece.pos_to_coord()
                        else:
                            self.stay = False


class Display:
    """Класс представления."""

    def __init__(self, party: Party, control: Control):
        """Конструктор.
        @param party Экземпляр класса модели
        @param control Экземпляр класса контроллера
        """
        self.party = party
        self.control = control
        self.update = True
        self.resume = False
        self.width = 665
        self.height = 667
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.pieces = Pieces(self)
        self.menu = Menu(self)
        self.panel = Panel(self)

        self.__view_menu = True
        self.__back = pygame.image.load("./resources/board.jpg").convert()

        pygame.display.set_icon(pygame.image.load("./resources/icon.png"))
        pygame.display.set_caption("Длинные нарды")
        self.control.set_display(self)
        self.init()

    def init(self) -> None:
        """Инициализировать."""
        self.menu.init()
        self.panel.init()
        self.pieces.refresh()

    def refresh(self) -> None:
        """Обновить представление."""
        self.update = True

    def toggle_menu(self, view: bool | None = None) -> None:
        """Показать/скрыть меню.
        @param view Флаг включения меню
        """
        if view is None:
            self.__view_menu = not self.__view_menu
        else:
            self.__view_menu = view

    def process(self) -> None:
        """Обновить состояние представления."""
        self.pieces.refresh()
        for key in self.pieces.group:
            if key.status == PieceStatus.CLICKED:
                self.update = True
                pos = pygame.mouse.get_pos()
                key.rect.x = pos[0] - (key.rect.width // 2)
                key.rect.y = pos[1] - (key.rect.height // 2)
            elif key.status == PieceStatus.TO_HOME:
                self.update = True
                dist = math.floor(
                    math.sqrt(
                        (key.home_x - key.rect.x) ** 2 + (key.home_y - key.rect.y) ** 2
                    )
                )
                if dist <= 5:
                    key.status = PieceStatus.STAY
                    next_x = key.home_x
                    next_y = key.home_y
                else:
                    next_x = key.rect.x + (5 * (key.home_x - key.rect.x)) // dist
                    next_y = key.rect.y + (5 * (key.home_y - key.rect.y)) // dist
                key.old_x = key.rect.x
                key.old_y = key.rect.y
                key.rect.x = next_x
                key.rect.y = next_y

    def draw(self) -> None:
        """Отрисовать представление."""
        if self.update:
            self.screen.blit(self.__back, (0, 0))
            self.pieces.draw()
            self.panel.draw()
            if self.__view_menu:
                self.menu.draw()

    def command(self, event: pygame.event.Event) -> None:
        """Обработать события.
        @param event Событие
        """
        self.update = True
        if event.type == pygame.USEREVENT + 1:
            self.control.timer()
        if self.__view_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    self.menu.click(pos)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    self.panel.click(pos)
                    self.pieces.click(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                self.pieces.release()


class Game:
    """Основной класс игры."""

    def __init__(self, record: Record):
        """Конструктор.
        @param record Статистика
        """
        self.record = record

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        self.__clock = pygame.time.Clock()
        self.__settings = Settings([Player.HUMAN, Player.HUMAN])

        self.__party = Party()  # Model
        self.__control = Control(
            self.__party, self.__settings, self.record
        )  # Controller
        self.__display = Display(self.__party, self.__control)  # View
        # self.__party.display = self.display
        self.__upd = False

    def __process_input(self) -> None:
        """Обработать события."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__control.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.__display.command(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.__display.command(event)
            elif event.type == pygame.USEREVENT + 1:
                self.__display.command(event)
                self.__upd = True

    def __update(self) -> None:
        """Обновить состояние игры."""
        self.__display.process()
        self.__control.process()

    def __render(self) -> None:
        """Отрисовать."""
        self.__display.draw()
        self.__display.update = False
        if self.__upd:
            pygame.display.update()
            self.__clock.tick(60)
            self.__upd = False

    def __update_record(self) -> None:
        """Обновить статистику."""
        if self.__control.save:
            self.record.underplayed += 1
        pygame.quit()

    def run(self) -> None:
        """Запустить основной цикл."""
        while self.__control.is_running():
            self.__process_input()
            self.__update()
            self.__render()

        self.__update_record()


def main() -> None:
    """Точка входа."""
    filename = "./resources/record.json"
    record = Record().read(filename)

    game = Game(record)
    game.run()

    record = game.record
    record.write(filename)


if __name__ == "__main__":
    main()
    sys.exit()
