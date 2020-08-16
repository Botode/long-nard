"""Длинные нарды"""
import os
import sys
import random
import math
import pygame


def emptyfunc():
    """empty"""


class Dice:
    """Класс зар"""

    def __init__(self, dice: 'Dice' = None):
        if dice:
            self.numbers = dice.numbers[:]
        else:
            self.numbers = [0, 0]

    def rolldice(self, value: int = 2) -> None:
        """Бросить зары"""
        if value in range(0, 2):
            self.numbers[value] = random.randint(1, 6)
        elif value == 2:
            self.numbers = [random.randint(1, 6), random.randint(1, 6)]
        else:
            self.numbers = [0, 0]

    def isdoubling(self) -> bool:
        """Выпал ли дубль"""
        return self.numbers[0] == self.numbers[1]


class State:
    """Класс состояния игровой доски"""

    def __init__(self, state: 'State' = None):
        self.checkers = [0]*26
        self.owner = [-1]*26
        self.ind = [[-1] for i in range(26)]
        self.player = 0
        self.dice: Dice = Dice()
        self.step = 0
        self.move = 0
        self.remained_die = []
        self.played_head = False
        self.color = 0
        self.amount = 0
        self.left = 0
        if state is not None:
            self.copy(state)
        else:
            self.init()

    def init(self):
        """fsdfsd"""
        for i in range(26):
            self.checkers[i] = 0
            self.owner[i] = -1
        self.checkers[24] = self.checkers[25] = 15
        self.owner[24] = 0
        self.owner[25] = 1
        self.initind()
        self.dice.rolldice(-1)
        self.player = 0
        self.step = 0
        self.move = 0
        self.remained_die = []
        self.played_head = False
        self.color = 0
        self.amount = 30
        self.left = 0

    def copy(self, state: 'State'):
        """dfsdf"""
        self.checkers = state.checkers[:]
        self.owner = state.owner[:]
        for i in range(26):
            self.ind[i].clear()
            for j in range(len(state.ind[i])):
                self.ind[i].append(state.ind[i][j])
        self.player = state.player
        self.dice.numbers = state.dice.numbers[:]
        self.remained_die = state.remained_die[:]
        self.step = state.step
        self.move = state.move
        self.color = state.color
        self.played_head = state.played_head
        self.amount = state.amount
        self.left = state.left

    def initind(self) -> None:
        """gdfgdfg"""
        cntw = 0
        cntb = 15
        for i in range(26):
            self.ind[i].clear()
            self.ind[i].append(self.owner[i])
            for _ in range(self.checkers[i]):
                if self.owner[i] == 0:
                    self.ind[i].append(cntw)
                    cntw += 1
                if self.owner[i] == 1:
                    self.ind[i].append(cntb)
                    cntb += 1

    def relativepos(self, pos: int) -> int:
        """Возвращает позицию относительно головы"""
        return (pos+12*(self.player)) % 24

    def opponentpos(self, pos: int) -> int:
        """Возвращает позицию относительно головы оппонента"""
        return (pos+12*(1-self.player)) % 24

    def isplayerpos(self, pos: int):
        """Есть ли шашки игрока в лунке"""
        return self.owner[pos] == self.player ^ self.color

    def isemptypos(self, pos: int) -> bool:
        """Свободна ли лунка"""
        return self.owner[pos] == -1

    def isopponentpos(self, pos: int) -> bool:
        """Занята ли лунка оппонентом"""
        return not self.isemptypos(pos) and not self.isplayerpos(pos)

    def ishome(self) -> bool:
        """Все ли шашки в доме"""
        for i in range(18):
            if self.isplayerpos(self.relativepos(i)):
                return False
        return True

    def isremovecheckers(self, pos: int, number: int) -> bool:
        """Снятие ли шашки с доски"""
        return self.relativepos(pos) + number >= 24

    def ishighorder(self, pos: int, number: int) -> bool:
        """Снимается ли с доски шашка старшего разряда"""
        diff = self.relativepos(pos) + number-24
        for i in range(pos-diff, pos):
            if self.isplayerpos(i):
                return False
        return True

    def isoneline(self) -> bool:
        """Проверяет законность шешара"""
        maxcount = 0
        count = 0
        for i in range(23, -1, -1):
            if self.isplayerpos(self.opponentpos(i)):
                count += 1
                maxcount = max(maxcount, count)
            if self.isemptypos(self.opponentpos(i)):
                count = 0
            if self.isopponentpos(self.opponentpos(i)):
                break
        if maxcount > 5:
            return True
        return False

    def getcheckerspos(self) -> list:
        """Возвращает номера полей игрока"""
        res = []
        for i in range(24):
            if self.isplayerpos(i):
                res.append(i)
        return res

    def filldice(self) -> None:
        """Заполняет очки на ход"""
        if len(self.remained_die) == 0 and self.step == 0:
            self.remained_die = self.dice.numbers[:]
            if self.dice.isdoubling():
                self.remained_die += self.dice.numbers[:]

    def playdie(self, number: int) -> None:
        """Убирает зар"""
        self.filldice()
        del self.remained_die[self.remained_die.index(number)]

    def rightmove(self, start: int, number: int) -> bool:
        """Проверка и ход"""
        if not self.isplayerpos(start):
            return False
        if (self.step > 0 and len(self.remained_die) == 0):
            return False
        if number not in self.remained_die:
            return False
        # Ход шашек
        if not self.isremovecheckers(start, number):
            if not self.isopponentpos((start+number) % 24):
                if self.relativepos(start) == 0:
                    if self.played_head:
                        if self.move == 0:
                            if self.dice.isdoubling():
                                if not ((self.dice.numbers[0] == 3 and self.step == 3)
                                        or (self.dice.numbers[0] == 4 and self.step == 2)
                                        or (self.dice.numbers[0] == 6 and self.step == 1)):
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        self.played_head = True
                self.ind[(start+number) % 24].append(self.ind[start].pop())
                if len(self.ind[start]) == 1:
                    self.ind[start][0] = -1
                if self.ind[(start+number) % 24][0] == -1:
                    self.ind[(start+number) % 24][0] = self.owner[start]
                self.checkers[(start+number) % 24] += 1
                self.owner[(start+number) % 24] = self.owner[start]
                self.checkers[start] -= 1
                if self.checkers[start] == 0:
                    self.owner[start] = -1
                self.playdie(number)

                self.step += 1
                return True
            return False
        # Вывод шашек
        if not self.ishome():
            return False
        # Вывод шашек низшего разряда
        if self.ishighorder(start, number):
            self.ind[24+self.player].append(self.ind[start].pop())
            if len(self.ind[start]) == 1:
                self.ind[start][0] = -1
            self.checkers[24+self.player] += 1
            self.checkers[start] -= 1
            if self.checkers[start] == 0:
                self.owner[start] = -1
            self.playdie(number)
            self.step += 1
            return True
        return False


class TreeMove:
    """Класс дерева возможных ходов"""

    def __init__(self, state: 'State', start: int, die: int):
        self.state: 'State' = state
        self.state.left = 0
        self.start = start
        self.die = die
        self.end = (start+die) % 24
        if self.state.isremovecheckers(start, die):
            self.end = 24+self.state.player
        self.checkers = self.state.getcheckerspos()
        self.childs = [[], []]
        self.value = [0, 0]
        if start == -1 or die == -1:
            self.state.remained_die = []
            self.state.filldice()

    def possiblemove(self, start, end) -> 'TreeMove':
        """fdfdf"""
        for item1 in self.childs:
            for item2 in item1:
                if start == item2.start:
                    if end == item2.end:
                        return item2
                    else:
                        res = item2.possiblemove(item2.end, end)
                        if res is not None:
                            return res
        return None

    def next(self):
        """Просчитывает следующие ходы"""
        self.checkers = self.state.getcheckerspos()
        self.childs = [[], []]
        self.value = [0, 0]
        self.state.left = 0
        if len(self.state.remained_die) == 0:
            return
        last = 1
        if self.state.step == 0:
            if not self.state.dice.isdoubling():
                last = 2
        for i in range(0, last):
            if i == 0:
                current_die = max(self.state.remained_die)
            else:
                current_die = min(self.state.remained_die)
            for current_start in self.checkers:
                vstate = State(self.state)
                flag = vstate.rightmove(current_start, current_die)
                if flag:
                    current_tree = TreeMove(vstate, current_start, current_die)
                    current_tree.next()
                    if vstate.left != 0 or not vstate.isoneline():
                        self.childs[i].append(current_tree)
                        self.value[i] = max(vstate.left+1, self.value[i])
            if len(self.childs[i]) > 1:
                self.childs[i].sort(key=lambda x: x.start)
        if last == 2:
            if self.value[0] == 1 and self.value[1] > 1:
                self.childs[0] = []
                self.value[0] = 0
            if self.value[1] == 1 and self.value[0] > 1:
                self.childs[1] = []
                self.value[1] = 0
            if self.value[0] == 1 and self.value[1] == 1:
                self.childs[1] = []
                self.value[1] = 0
            if len(self.childs[0]) == 0 and len(self.childs[1]) > 0:
                self.childs[0] = self.childs[1][:]
                self.value[0] = self.value[1]
                self.childs[1] = []
                self.value[1] = 0
        self.state.left = max(self.value[0], self.value[1])


class Party:
    """Класс игровой доски"""

    def __init__(self):
        self.stage = ""
        self.tree: TreeMove = None
        self.state: State = State()
        self.newparty()

    def newparty(self):
        """Инициализация новой партии"""
        self.stage = "begin"
        self.state.init()
        self.tree: TreeMove = None
        self.phase = ""
        self.count = 0
        self.color = None

    def initplayers(self, dice: 'Dice'):
        """Расстановка шашек"""
        diff = dice.numbers[0]-dice.numbers[1]
        self.state.player = 0
        if diff > 0:
            self.state.color = 0
        else:
            self.state.color = 1
        for i in range(26):
            self.state.checkers[i] = 0
            self.state.owner[i] = -1
        self.state.owner[24] = self.state.color
        self.state.owner[25] = 1-self.state.color
        self.state.checkers[0] = 15
        self.state.checkers[12] = 15
        self.state.owner[0] = self.state.color
        self.state.owner[12] = 1-self.state.color
        self.state.initind()
        self.state.player = self.state.color
        self.state.move = 0

    def getstage(self) -> str:
        """fsdfsdf"""
        return self.stage

    def setdice(self, dice: 'Dice'):
        """fsdfsd"""
        if self.stage == "toss":
            if self.state.player == 0:
                self.state.player = 1
            elif self.state.player == 1:
                if dice.isdoubling():
                    self.state.player = 0
                else:
                    self.initplayers(dice)
                    self.stage = "roll"
        elif self.stage == "roll":
            self.state.dice.numbers[:] = dice.numbers[:]
#            self.state.dice.numbers = [4, 3]
            self.initmove()

    def startparty(self) -> None:
        """fsdfsdf"""
        if self.stage == "begin":
            self.state.player = 0
            self.stage = "toss"

    def nextplayer(self):
        """gsdgdsg"""
        self.stage = "roll"
        if (self.state.player ==
                1-self.state.color):
            self.state.move += 1
        self.state.player = 1-self.state.player
        self.state.step = 0
        self.state.played_head = False

    def initmove(self):
        """fdfd"""
        self.stage = "move"
        self.tree = TreeMove(self.state, -1, -1)
        self.tree.next()
        if self.state.left == 0:
            self.stage = "next"


class Button(pygame.sprite.Sprite):
    """Класс кнопок"""

    def __init__(self, idd, text, xpos, ypos, status="text"):
        super().__init__()
        self.status = status
        if self.status == "enable":
            self.color = (255, 255, 0)
        elif self.status == "unable":
            self.color = (100, 100, 100)
        else:
            self.color = (255, 255, 255)
        self.text = text
        self.font = pygame.font.Font('freesansbold.ttf', 22)
        self.image = self.font.render(self.text, True, (self.color))
        self.rect = self.image.get_rect()
        self.idd = idd
        self.xpos = xpos
        self.ypos = ypos
        self.rect.x = self.xpos
        self.rect.y = self.ypos
        self.command = emptyfunc

    def change(self, xpos=None, ypos=None, text=None, status=None):
        """fdfdf"""
        if text is not None:
            self.text = text
        if status is not None:
            self.status = status
        if xpos is not None:
            self.xpos = xpos
        if ypos is not None:
            self.ypos = ypos
        if self.status == "enable":
            self.color = (255, 255, 0)
        elif self.status == "unable":
            self.color = (100, 100, 100)
        else:
            self.color = (255, 255, 255)
        self.image = self.font.render(self.text, True, (self.color))
        self.rect = self.image.get_rect()
        self.rect.x = self.xpos
        self.rect.y = self.ypos

    def pushable(self, yes: bool) -> None:
        """fsdfsdf"""
        if self.status != "text":
            if yes:
                self.change(status="enable")
            else:
                self.change(status="unable")


class Control:
    """gregerg"""

    def __init__(self, party: 'Party', settings: list, record: dict):
        self.clock = pygame.time.Clock()
        self.party = party
        self.settings = settings
        self.record = record
        self.display: 'Display' = None
        self.dice: 'Dice' = Dice()
        self.count = 0
        self.editor = False
        self.save = False
        self.time = 0

    def timer(self) -> None:
        """fdfdf"""
        if self.party.stage not in ["begin", "win"]:
            self.time += 1
            self.display.menu.refresh()

    def resetrecord(self) -> None:
        """fsdfsdf"""
        self.record['1'] = 0
        self.record['2'] = 0
        self.record['3'] = 0
        self.record['4'] = 0
        self.record['5'] = 0
        self.record['6'] = 0
        self.record['7'] = 0
        self.display.refresh()
        self.display.menu.refresh()

    def setdisplay(self, display: 'Display'):
        """gergerg"""
        self.display = display

    def onoffeditor(self) -> None:
        """fdfd"""
        if self.party.stage == "roll" and self.count == 0:
            self.editor = not self.editor
            self.display.panel.onoffthrow(not self.editor)
            self.display.refresh()
            self.display.menu.refresh()

    def restart(self, change: bool = True):
        """"gergerg"""
        self.editor = False
        self.party.newparty()
        self.party.startparty()
        self.display.resume = True
        self.display.init()
        if change:
            self.display.onoffmenu(False)
        self.dice.rolldice(-1)
        self.display.refresh()
        self.display.menu.refresh()
        self.display.panel.refresh()
        self.time = 0

    def throwdice(self):
        """gergerg"""
        if self.party.stage == "toss":
            if self.count == 0:
                self.display.panel.onoffthrow(False)
                if self.party.state.player == 0:
                    self.dice.rolldice(-1)
            self.dice.rolldice(self.party.state.player)
        if self.party.stage == "roll":
            self.display.panel.onoffthrow(False)
            self.dice.rolldice(2)
        self.count += 1
        if self.count >= 1:
            self.count = -1

    def process(self):
        """gergerg"""
        if self.party.stage in ["toss", "roll"]:
            if self.count > 0:
                self.throwdice()
                self.display.panel.refresh()
                self.display.refresh()
            if self.count == -1 and self.display.pieces.stay != "":
                self.count = 0
                self.party.setdice(self.dice)
                if self.party.stage in ["toss", "roll", "next"]:
                    self.display.panel.onoffthrow(True)
        if self.party.stage == "next" and self.display.pieces.stay != "":
            self.display.panel.onoffthrow(True)
            self.party.nextplayer()
        if self.party.stage == "roll":
            self.display.panel.refresh()
        if self.party.stage == "move" and self.display.pieces.stay != "":
            self.save = True
            self.display.panel.refresh()
        if self.party.stage == "win":
            if self.display.resume:
                self.save = False
                if self.record['5'] == 0:
                    self.record['5'] = self.time
                else:
                    self.record['5'] = min(self.record['5'], self.time)
                self.record['6'] = max(self.record['6'], self.time)
                self.record['7'] = (
                    self.record['7']*self.record['1']+self.time)//(self.record['1']+1)
                self.record['1'] += 1
                if self.party.state.player == 0:
                    self.record['3'] += 1
                else:
                    self.record['4'] += 1
                self.display.resume = False
                self.display.panel.refresh()
                self.display.menu.refresh()
            self.display.resume = False
        if self.settings[self.party.state.player] == "computer" and not self.editor:
            if self.display.pieces.stay:
                if (self.party.stage in ["toss", "roll"] and
                        self.display.panel.buttons[2].status == "enable"):
                    self.throwdice()
                if self.party.stage == "move":
                    if self.party.state.player == 0:
                        item1 = random.choice(self.party.tree.childs)
                    else:
                        item1 = self.party.tree.childs[0]
                    if len(item1) != 0:
                        if self.party.state.player == 0:
                            item2 = random.choice(item1)
                        else:
                            if self.party.state.step == 0:
                                item2 = item1[0]
                            else:
                                item2 = item1[-1]
                        flag = self.trymove(self.party.state.player ^
                                            self.party.state.color, item2.start, item2.end)
                        if flag:
                            self.display.pieces.refresh()
                if self.party.stage == "win" and not self.display.resume:
                    self.restart(False)

    def changesettings(self, player):
        """htrhrth"""
        if self.settings[player] == "human":
            self.settings[player] = "computer"
        else:
            self.settings[player] = "human"
        self.display.menu.refresh()

    def trymove(self, color, start, end) -> bool:
        """fsdfsdf"""

        if self.party.state.ind[end][0] == 1 - color:
            return False
        if len(self.party.state.ind[end]) > 15:
            return False
        if not self.editor:
            if self.party.stage != "move":
                return False
            if color != self.party.state.player ^ self.party.state.color:
                return False
            tree = self.party.tree.possiblemove(start, end)
            if tree is not None:
                self.party.state.copy(tree.state)
                self.party.tree = tree
                self.party.tree.state = self.party.state
                if max(tree.value) == 0:
                    if len(self.party.state.ind[24]) == 16 or len(self.party.state.ind[25]) == 16:
                        self.party.stage = "win"
                    else:
                        self.party.stage = "next"
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


class Piece(pygame.sprite.Sprite):
    """wewewee"""

    def __init__(self, idd, pos, hgt, color, clickable):
        super().__init__()
        self.idd = idd
        self.color = color
        if color == 0:
            self.image = pygame.image.load("white1.png").convert_alpha()
        else:
            self.image = pygame.image.load("black1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = pos
        self.hgt = hgt
        coord = self.postocoord()
        self.rect.x = coord[0]
        self.rect.y = coord[1]
        self.oldx = self.rect.x
        self.oldy = self.rect.y
        self.homex = self.rect.x
        self.homey = self.rect.y
        self.status = "stay"
        self.clickable = clickable

    def postocoord(self) -> list:
        """Возвращает координаты позиции"""
        coord = [-1, -1]
        pos = self.pos
        hgt = self.hgt
        if pos in range(6):
            coord[0] = 56+pos*41
            coord[1] = 548-hgt*17
        if pos in range(6, 12):
            coord[0] = 116+pos*41
            coord[1] = 548-hgt*17
        if pos in range(12, 18):
            coord[0] = 116+(23-pos)*41
            coord[1] = 23+hgt*17
        if pos in range(18, 24):
            coord[0] = 56+(23-pos)*41
            coord[1] = 23+hgt*17
        if pos == 24:
            coord[0] = 4
            coord[1] = 4+hgt*33
        if pos == 25:
            coord[0] = 621
            coord[1] = 563-hgt*33
        return coord

    def getpos(self) -> list:
        """Возвращает позицию по координатам (2 варианта)"""
        pos = -1
        xpos = self.rect.x+self.rect.width//2
        ypos = self.rect.y+self.rect.height//2
        if 56 + 0*41 <= xpos <= 56 + 6*41:
            if 548 - 16*16 <= ypos <= 548 + 35:
                pos = (xpos-56)//41
            if 23 + 16*16 >= ypos >= 23:
                pos = 23-(xpos-56)//41
        if 116 + 6*41 <= xpos <= 116 + 12*41:
            if 548 - 16*16 <= ypos <= 548 + 35:
                pos = (xpos-116)//41
            if 23 + 16*16 >= ypos >= 23:
                pos = 23-(xpos-116)//41
        if xpos <= 56 + 0*41:
            pos = 24
        if 116 + 13*41 <= xpos:
            pos = 25
        return pos


class Menu:
    """Класс Меню"""

    def __init__(self, display: 'Display'):
        self.display = display
        self.buttons = []
        self.group = pygame.sprite.Group()
        self.surf = pygame.Surface((self.display.width, self.display.height))
        self.init()

    def init(self) -> None:
        """sdfsegf"""
        self.surf.set_alpha(200)
        self.group.empty()
        self.buttons.clear()
        pygame.draw.rect(self.surf, (0, 0, 0),
                         (self.surf.get_rect()), 0)
        pygame.draw.rect(self.surf, (100, 100, 100),
                         (self.surf.get_rect()), 200)
        self.buttons.append(Button(0, "Меню:", 293, 105))
        self.buttons.append(Button(1, "Игрок 1:", 120, 135))
        self.buttons.append(Button(2, "Игрок 2:", 120, 165))
        self.buttons.append(Button(3, "", 380, 135, "enable"))
        self.buttons.append(Button(4, "", 380, 165, "enable"))
        self.buttons.append(Button(5, "Новая партия", 120, 195, "enable"))
        self.buttons.append(Button(6, "Продолжить", 380, 195, "unable"))
        self.buttons.append(Button(7, "Таблица рекордов:", 213, 225))
        self.buttons.append(Button(8, "Сыграно партий:", 120, 255))
        self.buttons.append(Button(9, "Недоиграно партий:", 120, 285))
        self.buttons.append(Button(10, "Побед 1 игрока:", 120, 315))
        self.buttons.append(Button(11, "Побед 2 игрока:", 120, 345))
        self.buttons.append(Button(12, "Самая короткая партия:", 120, 375))
        self.buttons.append(Button(13, "Самая длинная партия:", 120, 405))
        self.buttons.append(Button(14, "Среднее время партии:", 120, 435))
        self.buttons.append(Button(15, "", 420, 255))
        self.buttons.append(Button(16, "", 420, 285))
        self.buttons.append(Button(17, "", 420, 315))
        self.buttons.append(Button(18, "", 420, 345))
        self.buttons.append(Button(19, "", 420, 375))
        self.buttons.append(Button(20, "", 420, 405))
        self.buttons.append(Button(21, "", 420, 435))
        self.buttons.append(Button(22, "Обнулить", 120, 465, "enable"))
        self.buttons.append(Button(23, "Выход", 460, 465, "enable"))
        self.buttons.append(Button(24, "Редактор:", 120, 525))
        self.buttons.append(Button(25, "On", 380, 525, "enable"))
        self.buttons.append(Button(26, "Время партии:", 120, 495))
        self.buttons.append(Button(27, "", 380, 495))
        self.group.add(self.buttons)
        self.refresh()
        self.commands()

    def timetotext(self, time) -> str:
        """fdfdf"""
        tsec = time % 60
        tmin = (time//60) % 60
        thour = time//3600
        return "{:d}:{:02d}:{:02d}".format(thour, tmin, tsec)

    def refresh(self) -> None:
        """Обновляет меню"""
        if self.display.control.settings[0] == "human":
            text = "Человек"
        else:
            text = "Компьютер"
        self.buttons[3].change(text=text)
        if self.display.control.settings[1] == "human":
            text = "Человек"
        else:
            text = "Компьютер"
        self.buttons[4].change(text=text)
        if self.display.control.editor:
            text = "On"
        else:
            text = "Off"
        self.buttons[25].change(text=text)
        table = list(self.display.control.record.values())
        for i in range(4):
            self.buttons[i+15].change(text=str(table[i]))
        for i in range(3):
            self.buttons[i+19].change(text=self.timetotext(table[i+4]))
        self.buttons[6].pushable(self.display.resume)
        self.buttons[27].change(
            text=self.timetotext(self.display.control.time))
        self.group.draw(self.surf)
        self.display.refresh()

    def commands(self):
        """fsdfsdf"""
        self.buttons[3].command = (
            lambda *x: self.display.control.changesettings(0))
        self.buttons[4].command = (
            lambda *x: self.display.control.changesettings(1))
        self.buttons[5].command = self.display.control.restart
        self.buttons[6].command = self.display.onoffmenu
        self.buttons[23].command = self.display.exit
        self.buttons[22].command = self.display.control.resetrecord
        self.buttons[25].command = self.display.control.onoffeditor

    def click(self, pos) -> None:
        """gdfgdfg"""
        for key in self.group:
            if key.rect.collidepoint(pos) and key.status == "enable":
                key.command()

    def draw(self) -> None:
        """Отрисовка меню"""
        pygame.draw.rect(self.surf, (0, 0, 0),
                         (self.surf.get_rect()), 0)
        pygame.draw.rect(self.surf, (100, 100, 100),
                         (self.surf.get_rect()), 200)
        self.group.draw(self.surf)
        self.display.screen.blit(self.surf, (0, 0))


class Panel:
    """gdfgdfgdf"""

    def __init__(self, display: 'Display'):
        self.display = display
        self.buttons = []
        self.group = pygame.sprite.Group()
        self.surf = pygame.Surface((self.display.width, 60))
        self.init()

    def init(self) -> None:
        """fsdfsdfsd"""
        self.group.empty()
        self.buttons.clear()
        pygame.draw.rect(self.surf, (0, 0, 0), (self.surf.get_rect()))
        self.buttons.append(Button(0, "Игрок 1", 5, 5))
        self.buttons.append(Button(1, "0:0", 315, 5))
        self.buttons.append(Button(2, "Бросьте кости", 500, 5, "enable"))
        self.buttons.append(Button(3, "Начало игры", 5, 35))
        self.buttons.append(Button(4, "Меню", 590, 35, "enable"))
        self.commands()
        self.group.add(self.buttons)
        self.group.draw(self.surf)

    def onoffthrow(self, push: bool):
        """fsdfsdf"""
        self.buttons[2].pushable(push)
        self.refresh()

    def refresh(self, dice: bool = False):
        """fsdfsdf"""
        self.buttons[1].change(
            text=f"{self.display.control.dice.numbers[0]}:{self.display.control.dice.numbers[1]}")
        if not dice:
            player = self.display.party.state.player
            if self.display.party.stage == "toss":
                self.buttons[0].change(
                    text=f"Игрок {player+1}")
                self.buttons[3].change(text="Розыгрыш права первого хода")
            if self.display.party.stage in ["roll", "move"]:
                color = "белые" if player ^ self.display.party.state.color == 0 else "черные"
                move = self.display.party.state.move
                step = self.display.party.state.step
                left = self.display.party.state.left
                self.buttons[0].change(
                    text=f"Игрок {player+1} ({color})")
                if self.display.party.stage == "roll":
                    text = (f"Ход {move+1}")
                else:
                    text = (f"Ход {move+1} Шаг {step+1}/{left+step}")
                self.buttons[3].change(text=text)
            if self.display.party.stage == "win":
                color = "Белые" if player ^ self.display.party.state.color == 0 else "Черные"
                self.buttons[3].change(
                    text=f"{color} выиграли! Игрок {player+1} побеждает")
        self.group.draw(self.surf)
        self.display.refresh()

    def commands(self):
        """fdsfsdf"""
        self.buttons[2].command = (
            lambda *x: self.display.control.throwdice())
        self.buttons[4].command = (lambda *x: self.display.onoffmenu())

    def click(self, pos):
        """gdfgdfgdf"""
        for key in self.group:
            if (key.rect.collidepoint((pos[0], pos[1]-self.display.height+60))
                    and key.status == "enable"):
                key.command()

    def draw(self) -> None:
        """fsdfsdf"""
        pygame.draw.rect(self.surf, (0, 0, 0), (self.surf.get_rect()))
        self.group.draw(self.surf)
        self.display.screen.blit(self.surf, (0, self.display.height - 60))


class Pieces:
    """fsdfsdfsdf"""

    def __init__(self, display: 'Display'):
        self.display = display
        self.white = pygame.image.load('white1.png').convert_alpha()
        self.black = pygame.image.load('black1.png').convert_alpha()
        self.pieces = []
        self.group = pygame.sprite.OrderedUpdates()
        self.ind = self.display.party.state.ind
        self.init()
        self.stay = False

    def init(self) -> None:
        """rerer"""
        self.stay = False
        self.group.empty()
        self.pieces.clear()
        self.pieces = [None]*self.display.party.state.amount
        for i in range(len(self.ind)):
            if self.ind[i][0] != -1:
                for j in range(1, len(self.ind[i])):
                    clickable = j == len(self.ind[i])-1
                    player = self.ind[i][0]
                    tmp = Piece(self.ind[i][j], i, 0, player, clickable)
                    self.pieces[self.ind[i][j]] = tmp
                    self.group.add(tmp)

    def draw(self) -> None:
        """fdfdf"""
        self.group.draw(self.display.screen)

    def click(self, pos) -> None:
        """dsfsdfsd"""
        tops = [self.pieces[x[-1]] for x in self.ind if len(x) > 1]
        selectedkey = None
        for key in tops:
            if key.rect.collidepoint(pos):
                selectedkey = key
        if selectedkey:
            selectedkey.oldx = selectedkey.rect.x
            selectedkey.oldy = selectedkey.rect.y
            selectedkey.status = "clicked"
            selectedkey.remove(self.group)
            selectedkey.add(self.group)

    def release(self) -> None:
        """fdfdf"""
        for key in self.group:
            if key.status == "clicked":
                pos = key.getpos()
                if (self.display.control.settings[self.display.party.state.player] == "computer"
                        or pos == -1 or not self.display.control.trymove(key.color, key.pos, pos)):
                    key.status = "tohome"
                    self.stay = False

    def refresh(self):
        """fsdfsdf"""
        self.stay = True
        self.group.empty()
        for j in range(1, 17):
            for i in range(26):
                if self.ind[i][0] != -1:
                    if j < len(self.ind[i]):
                        val = self.ind[i][j]
                        self.group.add(self.pieces[val])
                        if self.pieces[val].status != "tohome":
                            if self.pieces[val].pos != i or self.pieces[val].hgt != j-1:
                                self.pieces[val].status = "tohome"
                                self.stay = False
                                self.pieces[val].pos = i
                                self.pieces[val].hgt = j-1
                                coord = self.pieces[val].postocoord()
                                self.pieces[val].homex = coord[0]
                                self.pieces[val].homey = coord[1]
                        else:
                            self.stay = False
                        clickable = j == len(self.ind[i])-1
                        if self.pieces[val].clickable == clickable:
                            self.pieces[val].clickable = clickable


class Display:
    """Класс Экран"""

    def __init__(self, party: 'Party', control: 'Control'):
        self.party = party
        self.control = control
        self.run = True
        self.update = True
        self.viewmenu = True
        self.resume = False
        self.width = 665
        self.height = 667
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_icon(pygame.image.load('nard_icon_3.png'))
        pygame.display.set_caption('Длинные нарды')
        self.back = pygame.image.load('board_game.jpg').convert()
        self.pieces = Pieces(self)
        self.menu = Menu(self)
        self.panel = Panel(self)
        self.control.setdisplay(self)
        self.init()

    def refresh(self) -> None:
        """fdsfsd"""
        self.update = True

    def exit(self) -> None:
        """fsdfsdfsd"""
        self.run = False

    def init(self) -> None:
        """tertert"""
        self.menu.init()
        self.panel.init()
        self.pieces.refresh()

    def onoffmenu(self, view: bool = None):
        """fsdfsdf"""
        if view is None:
            self.viewmenu = not self.viewmenu
        else:
            self.viewmenu = view

    def process(self) -> None:
        """2323"""
        self.pieces.refresh()
        for key in self.pieces.group:
            if key.status == "clicked":
                self.update = True
                pos = pygame.mouse.get_pos()
                key.rect.x = pos[0]-(key.rect.width//2)
                key.rect.y = pos[1]-(key.rect.height//2)
            if key.status == "tohome":
                self.update = True
                dist = math.floor(math.sqrt((key.homex-key.rect.x) **
                                            2 + (key.homey-key.rect.y)**2))
                if dist <= 5:
                    key.status = "stay"
                    nextx = key.homex
                    nexty = key.homey
                else:
                    nextx = key.rect.x + (5*(key.homex-key.rect.x))//dist
                    nexty = key.rect.y + (5*(key.homey-key.rect.y))//dist
                key.oldx = key.rect.x
                key.oldy = key.rect.y
                key.rect.x = nextx
                key.rect.y = nexty

    def draw(self):
        """@#@#@"""
        if self.update:
            self.screen.blit(self.back, (0, 0))
            self.pieces.draw()
            self.panel.draw()
            if self.viewmenu:
                self.menu.draw()

    def command(self, event) -> None:
        """fdfdfdf"""
        self.update = True
        if event.type == pygame.USEREVENT+1:
            self.control.timer()
        if self.viewmenu:
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
    """Основной класс игры"""

    def __init__(self, record):
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT+1, 1000)
        self.settings = ["human", "human"]
        self.record = record
        self.events = []
        self.party = Party()
        self.control = Control(self.party, self.settings, self.record)
        self.display = Display(self.party, self.control)
        self.party.display = self.display

    def loop(self) -> None:
        """Основной цикл"""
        while self.display.run:
#            upd = False
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.display.command(event)
                if event.type == pygame.MOUSEBUTTONUP:
                    self.display.command(event)
                if event.type == pygame.QUIT:
                    self.display.run = False
                if event.type == pygame.USEREVENT+1:
                    self.display.command(event)
#                    upd = True
            self.display.process()
            self.control.process()
            self.display.draw()
            self.display.update = False
#            if upd:
            pygame.display.update()
            self.control.clock.tick(60)
        self.exit()
        pygame.quit()

    def exit(self) -> None:
        """Режим выхода"""
        if self.control.save:
            self.record['2'] += 1


def readrecord(filename) -> dict:
    """Считывает статистику из файла"""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            table = [word for line in file for word in line.split()]
    try:
        record = {
            '1': int(table[0]), '2': int(table[1]),
            '3': int(table[2]), '4': int(table[3]),
            '5': int(table[4]), '6': int(table[5]),
            '7': int(table[6])
        }
    except ValueError:
        record = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0}
    return record


def main() -> None:
    """Main"""
    filename = "record.dat"
    record = readrecord(filename)
    game = Game(record)
    game.loop()
    record = game.record
    with open(filename, "w") as file:
        file.write(" ".join(str(x) for x in record.values()))


if __name__ == "__main__":
    main()
    sys.exit()
