from direct.showbase.ShowBase import ShowBase
import math
from panda3d.core import Point3, Filename
from direct.showbase import DirectObject
import os, sys
from panda3d.core import *
from pandac.PandaModules import WindowProperties
from classes import Circle, Physics

from direct.gui.DirectGui import *

class Vector3D():
    """
    не нуждается в комментариях
    """
    def __init__(self, x, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __eq__(self, other):
        return True if self.x == other.x and self.y == other.y and self.z == other.z else False

    def __neg__(self):
        return Vector3D(-self.x, -self.y, -self.z)

    def __div__(self, number):
        return Vector3D(self.x / number, self.y / number)

    def __abs__(self):
        return (self.x**2 + self.y**2 + self.z**2)**(1/2)

    def __mul__(self, number):
        return Vector3D(self.x * number, self.y * number, self.z * number)


class Handler(DirectObject.DirectObject):
    """
    Класс - обработчик нажатий клавиатуры и мыши.
    Полностью обеспечивает общение пользователя с основным игровым циклом
    """
    def __init__(self):
        """
        При создании объекта класса каждой кнопке(на нажатие или отжатие или и то и то) назначается функция,
        прописанная в этом же классе.
        Затем создаются всякие флажки, положение которых и сообщает основному циклу всю информацию.
        К сожалению у меня действует правило 'закрывайте за собой двери'. Обратно эти флажки должен опускать
        сам основной цикл. За очень небольшим исключением, когда применение кнопки небольшое.
        Пара слов про gameStateData. Это список смежности для ориентированного графа с двумя компонентами
        связности и с полустепенью исхода для каждой вершины не больше единицы (то есть из данной вершины можно попасть
        только в одну другую вершину или никуда). Вершины графа являются состояниями игры, а по рёбрам можно перемещаться с
        помощью кнопки 'escape'. Переход осуществляется здесь же
        """
        self.accept('mouse1', self.mouse1down)
        self.accept('mouse1-up', self.mouse1up)
        self.accept('shift', self.shift_down)
        self.accept('shift-up', self.shift_up)
        self.accept('wheel_up', self.wheel_up)
        self.accept('wheel_down', self.wheel_down)
        self.accept('mouse2-down', self.mouse3down)
        self.accept('enter', self.enter)
        self.accept('escape', self.escape)
        self.accept('arrow_up', self.arrow_up)
        self.accept('arrow_up-up', self.arrow_up_up)
        self.accept('arrow_down', self.arrow_down)
        self.accept('arrow_down-up', self.arrow_down_up)
        self.accept('arrow_left', self.arrow_left)
        self.accept('arrow_left-up', self.arrow_left_up)
        self.accept('arrow_right', self.arrow_right)
        self.accept('arrow_right-up', self.arrow_right_up)
        #для стрелок
        self.arrow_upv = False
        self.arrow_downv = False
        self.arrow_leftv = False
        self.arrow_rightv = False
        #отслеживай мышку - поднимается при нажатии ЛКМ
        self.trackMouse = False
        #понадобился для отслеживания нажатий в то время как предыдущий флаг может продолжать быть в True
        self.mouseLeftDown = False
        self.slow = False
        self.change_zoom = False
        #дальность камеры от точки cameraLookAt
        self.radius = 20
        #сила удара и расстояние от кия до шара по совместительству
        self.strength = 2
        self.enterPressed = False
        self.remove_ball = False
        self.zoomBall = False
        #это нужно для небольшой особенности правил Московской пирамиды
        self.dontForgetToReplaceBall = False
        self.gameStateData = {
            "menu": "quit",
            "start_game": "menu",
            "load": "menu",
            "about_devs": "menu",
            "game": "pause",
            "pause": "game",
            "zoomed_mode": "game",
            "strength_mode": "zoomed_mode"
        }
        #текущее состояние игры
        self.currentGameState = "menu"
        #отсюда цикл узнаёт, что в предыдущем кадре игра была в другом состоянии и нужно выполнить кое-какие действия
        self.theGameHasChanged = True

    def arrow_up(self):
        self.arrow_upv = True
        print("up")

    def arrow_up_up(self):
        self.arrow_upv = False

    def arrow_down(self):
        self.arrow_downv = True

    def arrow_down_up(self):
        self.arrow_downv = False

    def arrow_left(self):
        self.arrow_leftv = True

    def arrow_left_up(self):
        self.arrow_leftv = False

    def arrow_right(self):
        self.arrow_rightv = True

    def arrow_right_up(self):
        self.arrow_rightv = False


    def mouse1down(self):
        self.trackMouse = True
        self.mouseLeftDown = True

    def mouse1up(self):
        self.trackMouse = False
        self.mouseLeftDown = False

    def shift_down(self):
        self.slow = True

    def shift_up(self):
        self.slow = False

    def wheel_up(self):
        if self.radius > 2 and self.currentGameState != "zoomed_mode":
            self.radius -= 1
            self.change_zoom = True

    def wheel_down(self):
        if self.radius < 40 and self.currentGameState != "zoomed_mode":
            self.radius += 1
            self.change_zoom = True

    def mouse3down(self):
        self.removeBall = True

    def enter(self):
        self.enterPressed = True
        print('lookingAtBall')

    def finishTracking(self):
        self.trackBall = False

    def gameChanged(self):
        self.theGameHasChanged = True
        print("the game has changed")

    def escape(self):
        self.currentGameState = self.gameStateData[self.currentGameState]
        self.gameChanged()
        print(self.currentGameState)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #получаем директорию, в которой лежит игра
        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()

        #загружаем бортики, которые зелёные
        self.vborders = self.loader.loadModel(self.mydir + "/models/borders2.egg")
        self.vborders.reparentTo(self.render)
        self.vborders.setColorScale(0, 0.6, 0, 1)
        self.vborders.setHpr(90, 0, 0)

        #загружаем стол
        self.table = self.loader.loadModel(self.mydir + "/models/table2.egg")
        self.table.reparentTo(self.render)
        self.table.setHpr(90, 0, 0)

        #загружаем зелёное поле, по которому будут кататься шары
        #нужно, чтобы не заморачиваться с текстурированием стола
        self.velvet = self.loader.loadModel(self.mydir + "/models/velvet2.egg")
        self.velvet.reparentTo(self.render)
        self.velvet.setColorScale(0, 0.6, 0, 1)
        self.velvet.setHpr(90, 0, 0)

        #это те металлические дуги, которые держат сетку в лузе
        self.loosers = self.loader.loadModel(self.mydir + "/models/pocket2.egg")
        self.loosers.reparentTo(self.render)
        self.loosers.setColorScale(0, 0, 0, 1)
        self.loosers.setHpr(90, 0, 0)

        #сетка(все шесть штук)
        self.loos = self.loader.loadModel(self.mydir + "/models/pocketnet2.egg")
        self.loos.reparentTo(self.render)
        self.loos.setColorScale(1, 1, 1, 1)
        self.loos.setHpr(90, 0, 0)

        #большие деревянные борты
        self.borders = self.loader.loadModel(self.mydir + "/models/woodenborders2.egg")
        self.borders.reparentTo(self.render)
        self.borders.setHpr(90, 0, 0)

        #загружаем текстуру дерева и устанавоиваем столу и деревянным бортам
        #модели уже развёрнуты
        wood = self.loader.loadTexture(self.mydir + '/models/tex/WoodColor.jpg')
        self.table.setTexture(wood)
        self.borders.setTexture(wood)

        #проблемы с установкой цвета. Да, это просто монотонный зелёный цвет.
        #для этих моделей тоже сделаны развёртки, так что в будущем можно найти качественную текстуру
        #бильярдного сукна (я не нашёл) и просто поменять здесь
        velvet = self.loader.loadTexture(self.mydir + '/models/tex/green.jpg')
        self.velvet.setTexture(velvet)
        self.vborders.setTexture(velvet)

        #освещение
        self.plight = PointLight('plight')
        self.plight.setColor((1, 1, 1, 1))
        plnp = self.render.attachNewNode(self.plight)
        plnp.setPos(0, 0, 10)
        self.render.setLight(plnp)

        #установка шейдеров и теней
        self.plight.setShadowCaster(True, 2048, 2048)
        # Enable the shader generator for the receiving nodes
        self.render.setShaderAuto()

        #просто флажок потом нужен будет
        self.followPointerPos = False

        self.strength = 0
        self.list_of_balls = []

        #это в игру добавляется главная функция, значит что она будет вызвана во время игры
        self.taskMgr.add(self.gameStateOverseer, "overseer")

        #эта функция отключает базовое управление камеры мышкой. Оно крайне неудобно
        self.disable_mouse()
        #создаём обработчика событий, который будет докладывать о всех (всех нужных) действиях пользователя
        self.handler = Handler()

        #стартовое положение камеры
        self.camera.setHpr(0,
                           -90,
                           0)
        self.camera.setPos(self.handler.radius * math.cos(self.camera.getHpr()[1] * 3.1415926 / 180) * math.sin(self.camera.getHpr()[0] * 3.1415926 / 180),
                           -self.handler.radius * math.cos(self.camera.getHpr()[1] * 3.1415926 / 180) * math.cos(self.camera.getHpr()[0] * 3.1415926 / 180),
                           -self.handler.radius * math.sin(self.camera.getHpr()[1] * 3.1415926 / 180) + 0.7)

        #располагаем шары на столе
        r = 0.1
        x = 0
        y = - r * 15
        id = 0
        self.mass_circle = []
        for i in range(1, 6):
            for j in range(i):
                self.mass_circle.append(Circle(id, y, x + j * 2 * (r + 0.0001), r, 0, 0, self.mydir,
                                            self.render, [0 for i in range(18)], [0 for j in range(16)], 0.00005))
                id += 1
            x -= r + 0.0001
            y -= (r + 0.0001) * 3 ** 0.5

        #а это наш биток (красный шар)
        self.mass_circle.append(Circle(id, 15 * r, 0, r, 0, 0, self.mydir,
                                       self.render, [0 for i in range(18)], [0 for j in range(16)], 0.00005))
        self.mass_circle[-1].model.setColorScale(0.54, 0, 0, 1)
        self.mass_circle[-1].model.setTag("unique", "aaa")
        self.mass_circle[-1].model.setShaderAuto()

        #загружаем кий
        """
        Тут стоит сделать лирическое отступление о структуре игровой сцены в panda3d.
        Сцена представляет собой дерево, вершинами которого являются объекты класса NodePath и все наследуемые из него
        модели, источники освещения, и даже 2d объекты.
        Если задать или переназначить объекту родителя (reparentTo()), он возьмёт положение родителя за (0, 0, 0) и 
        изменения положения и поворота родителя сразу же скажутся на нашем объекте.
        К сожалению модель почему-то копирует текстуру родителя и про то, как это отключить в официальном мануале ни 
        слова. Поэтому все модели за ислючением кия назначены корню для 3d объектов - 'render'. Для 2d объектов это 
        'render2d', отображаетя поверх 'render'.
        """
        self.kiy = self.loader.loadModel(self.mydir + "/models/kiy.egg")
        self.kiy.reparentTo(self.mass_circle[-1].model)
        self.kiy.setScale(0.5, 0.5, 0.5)
        self.kiy.hide() #спрятан  и не отрисовыватся


        self.i = 0 #просто счётчик
        self.gameData = Physics(self.mass_circle)
        self.current_ball = -1
        self.cameraLookAt = [0, 0, 0.7]
        self.set_background_color(0.1, 0.1, 0.1)

        self.gameData.balls[-1].model.setPos(0, 0, 0.82)

        #здесь загружаются шрифты
        fontBig = loader.loadFont("century_gothic.ttf")
        fontBig.setPixelsPerUnit(250)
        #менее качественный шрифт для опитимизации, если нужен меньший размер
        font = loader.loadFont("century_gothic.ttf")


        #тут создаются 2д кнопки и тексты для интерфейса
        self.b = OnscreenText(text="Billiards", scale=.5, pos=(self.a2dpLeft * 0.5, self.a2dpBottom * 0.6), font=font,
                              fg=(1, 1, 1, 1))
        self.b.reparentTo(self.a2dTopCenter)
        self.b.setPos(self.a2dpLeft * 0.5, self.a2dpBottom * 0.6)

        self.bNewGame = DirectButton(text="New Game", text_font=fontBig, text_scale=0.8, scale=0.2, command=self.startGame,
                                     text_fg=(1, 1, 1, 1),
                                     frameColor=((0, 0, 0, 0), (0.5, 0.5, 0.5, 0.1)))
        self.bNewGame.reparentTo(self.b)
        self.bNewGame.setPos(self.a2dpLeft * 0.5, 0, self.a2dpBottom)

        self.bquit = DirectButton(text="Quit", text_font=font, text_scale=0.8, command=self.quit,
                                  text_fg=(1, 1, 1, 1), frameColor=((0, 0, 0, 0), (0.5, 0.5, 0.5, 0.1)))
        self.bquit.reparentTo(self.bNewGame)
        self.bquit.setPos(0, 0, self.a2dpBottom * 2)

        #полупрозрачный чёрный прямоугольик, который перекрывает весь экран, чтобы добавить красивого затеменения в меню
        #а на заднем плане был бильярдный стол
        self.back = DirectFrame(frameColor=(0, 0, 0, 0.6),
                                frameSize=(-5, 5, -5, 5),
                                parent=self.a2dBackground)

        self.pauseText = OnscreenText(text="PAUSE", scale=.3, pos=(0, self.a2dpTop * 0.5), font=font,
                              fg=(1, 1, 1, 1))
        self.pauseText.hide()

        self.bResume = DirectButton(text="Resume", text_font=font, text_scale=0.8, command=self.resumeGame, scale=0.2,
                                    text_fg=(1, 1, 1, 1), frameColor=((0, 0, 0, 0), (0.5, 0.5, 0.5, 0.1)))
        self.bResume.hide()

        self.bReturnToMenu = DirectButton(text="Quit to menu", text_font=font, text_scale=0.8, command=self.toMenu,
                           text_fg=(1, 1, 1, 1), frameColor=((0, 0, 0, 0), (0.5, 0.5, 0.5, 0.1)))
        self.bReturnToMenu.reparentTo(self.bResume)
        self.bReturnToMenu.setPos(0, 0, self.a2dpBottom )
        self.bReturnToMenu.hide()

        self.bQuitFromPause = DirectButton(text="Quit to Desktop", text_font=font, text_scale=0.8, command=self.quit,
                                           text_fg=(1, 1, 1, 1), frameColor=((0, 0, 0, 0), (0.5, 0.5, 0.5, 0.1)))
        self.bQuitFromPause.reparentTo(self.bResume)
        self.bQuitFromPause.setPos(0, 0, self.a2dpBottom * 2)
        self.bQuitFromPause.hide()

    def resumeGame(self):
        """
        Вызывается при нажатии кнопки 'Resume' в состоянии игры 'pause'.
        Переводит состояние в 'game', и оповещает о том, что состояние игры изменилось
        """
        self.handler.currentGameState = "game"
        self.handler.theGameHasChanged = True

    def startGame(self):
        """
        Вызывается при начале новой игры (кнопка 'New game') в состоянии игры 'menu'
        Переводит состояние в 'game', и оповещает о том, что состояние игры изменилось
        """
        r = 0.1
        x = 0
        y = - r * 15
        k = 0
        for i in range(1, 6):
            for j in range(i):
                self.mass_circle[k].vel_x = 0.00001
                self.mass_circle[k].vel_y = 0.00001
                self.mass_circle[k].x = y
                self.mass_circle[k].y = x + j * 2 * (r + 0.0001)
                k += 1
            x -= r + 0.0001
            y -= (r + 0.0001) * 3 ** 0.5
        self.camera.setHpr(90, -20, 0)

        self.handler.currentGameState = "game"
        self.handler.theGameHasChanged = True

    def toMenu(self):
        """
        Вызывается при выходе в главное меню. Кнопка 'Quit to menu' в состоянии игры 'pause'
        Переводит состояние в 'game', и оповещает о том, что состояние игры изменилось
        """
        self.handler.currentGameState = "menu"
        self.handler.theGameHasChanged = True

    @staticmethod
    def quit():
        sys.exit()

    #camera rotation
    def spin_camera(self):
        """
        Функция отвечает за поворот камеры. Если это первый кадр после нажатия мышки,
        то она прячет курсор, помещает его в центр, и отмечает тот факт, что с этого момента нужно просто
        поворачивать камеру настолько, насколько сдвинулась мышь. Каждый кадр она будет снова и снова помещаться центр
        так границы экрана не будут мешать крутить сцену. А если не двигать мышкой, то функция не будет лишний раз
        пересчитвать положение камеры. В противном случае неточность вычислений дробных чисел даёт о себе знать
        и камера медленно двигается сама.
        """
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        if abs(self.mouseWatcherNode.getMouseY()) > 0.01 or abs(self.mouseWatcherNode.getMouseX()) != 0.0:
            if not self.followPointerPos:
                self.followPointerPos = True
                props = self.win.getProperties()
                self.win.movePointer(0,
                                     int(props.getXSize() / 2),
                                     int(props.getYSize() / 2))
            else:
                if self.handler.slow:
                    times = 2
                else:
                    times = 20
                angleHorDegrees = self.mouseWatcherNode.getMouseX() * times
                angleVerDegrees = self.mouseWatcherNode.getMouseY() * times
                self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                       self.camera.getHpr()[1] + angleVerDegrees,
                                       0)
                if self.camera.getHpr()[1] < -90:
                    self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                       -90,
                                       0)
                elif self.camera.getHpr()[1] > -10:
                    self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                       -10,
                                       0)

                cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
                cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0

                self.camera.setPos(self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[0],
                                   -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) + self.cameraLookAt[1],
                                   -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

                props = self.win.getProperties()
                self.win.movePointer(0,
                                     int(props.getXSize() / 2),
                                     int(props.getYSize() / 2))
        elif self.handler.change_zoom:
            self.updateCamera()

    def updateCamera(self):
        """
        1. Делает то же самое, что и предыдущая функция, но вызвается из неё же в случае, если мышкой не двигать,
        а колёсиком повернуть.
        2. Вызывается для быстрого обновления положения камеры после изменений переменных,
        связанных с её положеним и поворотом
        (точнее двух - radius и cameraLookAt)

        """
        cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
        cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0
        self.camera.setPos(
            self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[0],
            -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) + self.cameraLookAt[1],
            -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

    def balls(self):
        """
        Вызывается для обновления положения шаров и вычисления соударений, пересчёта скоростей и
        удаления шаров при залёте в лузы.
        dontForgetToReplaceBall - связано с правилами Московской пирамиды. Просто если вдруг
        мы убираем красный шар, то нужно будет после остановки шаров выбрать любой шар на столе и убрать его,
        после этого поставить красный шар в любое место.
        """
        self.gameData.drawing_circle()
        self.gameData.moving()
        if self.gameData.check_boarder():
            self.handler.dontForgetToReplaceBall = True
        self.gameData.collisions_mass()
        self.gameData.correct_collisions(0.1)

    def posKiy(self):
        """
        Располагает кий около шара так, чтобы он смотрел на этот шар, а кончик кия отстоял от него
        на переменную strength (сила удара)
        Там ещё проводится небольшая махинация в прибавлении 90 градусов,
        связанная с поворотом модели.
        """
        self.kiy.setH(self.camera.getH())
        self.kiy.setR(10)
        kiyHorHprRadians = self.kiy.getHpr()[0] * math.pi / 180.0
        kiyVerHprRadians = self.kiy.getHpr()[2] * math.pi / 180.0
        self.kiy.setPos(
            self.handler.strength * math.cos(kiyVerHprRadians) * math.sin(kiyHorHprRadians),
            -self.handler.strength * math.cos(kiyVerHprRadians) * math.cos(kiyHorHprRadians),
            self.handler.strength * math.sin(kiyVerHprRadians))
        self.kiy.setH(self.kiy.getH() + 90)

    def gameStateOverseer(self, Task):
        """
            Функция следит за текущим состоянием игры currentGameState и производит необходимые
            действия по переходу в состояние и поддержание действий, производимых в нём.
            Важное уточнение. Эта функция добвена в менеджер заданий (taskMgr) принимает некую переменную Task,
            эти действия означают, что функция будет вызываться каждый игровой кадр.
            в целях оптимизации я решил огранчиться одной такой функцией и все остальные вызывать в зависимоти от
            состояния игры.
            :return: Task.cont - означает, что будет вызвана в следующий кадр
        """
        if self.handler.currentGameState == "menu":
            #в блоках theGameHasChanged производятся действия по переходу из любого возможного предыдущего
            #состояния игры в текущее, т. е. currentGameState
            if self.handler.theGameHasChanged:
                self.camera.setHpr(112, -20, 0)
                self.cameraLookAt = [0, 0, 0.82]
                self.handler.theGameHasChanged = False
                self.b.show()
                self.bNewGame.show()
                self.bquit.show()
                self.back.show()
                self.pauseText.hide()
                self.bResume.hide()
                self.bQuitFromPause.hide()
                self.bReturnToMenu.hide()
                self.balls()
            if self.mouseWatcherNode.hasMouse():
                cameraHorHprRadians = (100 + self.mouseWatcherNode.getMouseX()) * math.pi / 180.0
                cameraVerHprRadians = (-20 + self.mouseWatcherNode.getMouseY()) * math.pi / 180.0
            else:
                cameraHorHprRadians = 100 * math.pi / 180.0
                cameraVerHprRadians = -20 * math.pi / 180.0

            self.camera.setPos(
                10 * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[
                    0],
                -10 * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) +
                self.cameraLookAt[1],
                -10 * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

        if self.handler.currentGameState == "pause":
            #нажатие на 'esc' в режиме 'game'
            if self.handler.theGameHasChanged:
                self.kiy.hide()
                self.back.show()
                self.bResume.show()
                self.bQuitFromPause.show()
                self.bReturnToMenu.show()
                self.pauseText.show()
                self.handler.theGameHasChanged = False
                print("show")

        if self.handler.currentGameState == "game":
            #режим, в котором можно изменять масштаб, крутить стол, одним словом оценивать сложившееся положение
            #отсюда можно попасть в 'pause' и 'zoomed_mode'
            if self.handler.theGameHasChanged:
                self.cameraLookAt = [0, 0, 0.7]
                self.handler.radius = 10
                self.handler.theGameHasChanged = False
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)
                self.updateCamera()
                self.kiy.hide()
                self.b.hide()
                self.bNewGame.hide()
                self.bquit.hide()
                self.back.hide()
                self.pauseText.hide()
                self.bResume.hide()
                self.bQuitFromPause.hide()
                self.bReturnToMenu.hide()
            print(self.gameData.check_velocity())
            if self.handler.enterPressed and len(self.gameData.balls) > 0 and not self.gameData.check_velocity():
                self.handler.currentGameState = "zoomed_mode"
                self.handler.theGameHasChanged = True
                self.handler.enterPressed = False
            #Поворот камеры
            if self.handler.trackMouse:
                self.spin_camera()
            elif self.handler.change_zoom:
                self.updateCamera()
                self.handler.change_zoom = False
            elif not self.followPointerPos:
                self.followPointerPos = False
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)

            self.balls()
            if self.handler.enterPressed:
                self.handler.enterPressed = False

        elif self.handler.currentGameState == "choose_ball":
            #если в лузу загнан красный шар, то стрелками можно выбрать любой шар
            if self.handler.theGameHasChanged:
                self.i = 0
                self.handler.theGameHasChanged = False
            if self.handler.arrow_leftv:
                self.i -= 1
                if self.i < 0:
                    self.i = 14
                self.gameData.balls[self.i + 1 if self.i != 14 else 0].model.setColorScale(1, 1, 1, 1)
                self.handler.arrow_leftv = False
            if self.handler.arrow_rightv:
                self.i += 1
                if self.i > 14:
                    self.i = 0
                self.gameData.balls[self.i - 1 if self.i else 14].model.setColorScale(1, 1, 1, 1)
                self.handler.arrow_rightv = False
            self.gameData.balls[self.i].model.setColorScale(0.5, 0.5, 0.5, 1)
            if self.handler.trackMouse:
                self.spin_camera()
            elif self.handler.change_zoom:
                self.updateCamera()
                self.handler.change_zoom = False
            elif not self.followPointerPos:
                self.followPointerPos = False
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)
            if self.handler.enterPressed:
                self.gameData.balls[self.i].model.hide()
                self.gameData.balls.pop(self.i)
                for j in range(len(self.gameData.balls)):
                    self.gameData.balls[j].check_point_circle.pop(self.i)
                for i in range(len(self.gameData.balls)):
                    self.gameData.balls[i].identical_number = i
                self.handler.currentGameState = "choose_pos"
                self.handler.theGameHasChanged = True
                self.handler.enterPressed = False



        elif self.handler.currentGameState == "choose_pos":
            #после того, как белый шар убран, в центре появляется красный шар и опять же
            #стрелками можно выбрат его новое положение
            if self.handler.theGameHasChanged:
                self.gameData.balls[-1].x = 0
                self.gameData.balls[-1].y = 0
                self.gameData.balls[-1].vel_x = 0
                self.gameData.balls[-1].vel_y = 0
                self.gameData.balls[-1].model.show()
                self.handler.theGameHasChanged = False

            if self.handler.arrow_upv:
                self.gameData.balls[-1].x += 0.03

            if self.handler.arrow_downv:
                self.gameData.balls[-1].x -= 0.03

            if self.handler.arrow_leftv:
                self.gameData.balls[-1].y += 0.03

            if self.handler.arrow_rightv:
                self.gameData.balls[-1].y -= 0.03

            if self.handler.trackMouse:
                self.spin_camera()
            elif self.handler.change_zoom:
                self.updateCamera()
                self.handler.change_zoom = False
            elif not self.followPointerPos:
                self.followPointerPos = False
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)
            if self.handler.enterPressed:
                self.handler.currentGameState = "game"
                self.handler.theGameHasChanged = True
            self.balls()

        elif self.handler.currentGameState == "zoomed_mode":
            #прицеливание
            #'esc' возвращает в 'game', нажатие ЛКМ переводит в выбор силы
            self.balls()
            if self.handler.theGameHasChanged and self.gameData.balls:
                self.cameraLookAt = self.gameData.balls[self.current_ball].model.getPos(self.render)
                self.handler.radius = 4
                self.handler.theGameHasChanged = False
                self.updateCamera()
                self.posKiy()
                self.kiy.show()
            elif self.handler.mouseLeftDown:
                self.handler.mouseLeftDown = False
                self.handler.currentGameState = "strength_mode"
            elif self.mouseWatcherNode.hasMouse():
                self.spin_camera()
                self.posKiy()
            elif not self.followPointerPos:
                self.followPointerPos = False

        elif self.handler.currentGameState == "strength_mode":
            #после нажатия ЛКМ тянуть мышь на себя - сила увеличивается, обратное также верно.
            #esc вернёт в 'zoomed_mode' с сохранением силы. Для произведения удара отпустить мышь
            self.balls()
            if self.mouseWatcherNode.hasMouse() and self.handler.trackMouse:
                self.handler.strength -= self.mouseWatcherNode.getMouseY()
                if self.handler.strength < 1.46:
                    self.handler.strength = 1.46
                if self.handler.strength > 7:
                    self.handler.strength = 7
                print(self.handler.strength)
                self.posKiy()
                props = self.win.getProperties()
                self.win.movePointer(0,
                                     int(props.getXSize() / 2),
                                     int(props.getYSize() / 2))
            if not self.handler.trackMouse:
                self.handler.currentGameState = "shot"
                self.strength = self.handler.strength

        elif self.handler.currentGameState == "shot":
            #Здесь уже никакой esc не спасёт. Удар почти совершён
            #Небольшая анимация того, как кий стремительно и неумолимо надвигается на шар.
            self.balls()
            if self.handler.strength > 0.5:
                self.handler.strength -= self.strength / 10
                self.posKiy()
            else:
                self.kiy.hide()
                print("кий спрятан")
                self.gameData.balls[-1].vel_x = - 0.01 * self.strength * math.sin(self.camera.getH() * math.pi / 180)
                self.gameData.balls[-1].vel_y = 0.01 * self.strength * math.cos(self.camera.getH() * math.pi / 180)
                self.handler.currentGameState = "game"
                self.handler.theGameHasChanged = True
        return Task.cont


app = MyApp()
app.run()
