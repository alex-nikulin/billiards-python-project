from direct.showbase.ShowBase import ShowBase
import math
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, Filename
from direct.showbase import DirectObject
import os, sys
from panda3d.core import *
from pandac.PandaModules import WindowProperties
from panda3d.core import CollisionTraverser, CollisionHandler, CollisionNode, CollisionRay
from classes import Circle, Physics, Line
import random


from direct.gui.DirectGui import *

class Vector3D():
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

class Ball:
    def __init__(self, model, velocity):
        self.velocity = velocity
        self.model = model

    def update(self):
        self.model.set_pos(self.model.get_pos)



class Handler(DirectObject.DirectObject):
    def __init__(self):
        self.accept('mouse1', self.mouse1down)
        self.accept('mouse1-up', self.mouse1up)
        self.accept('shift', self.shift_down)
        self.accept('shift-up', self.shift_up)
        self.accept('wheel_up', self.wheel_up)
        self.accept('wheel_down', self.wheel_down)
        self.accept('mouse3', self.mouse2)
        self.accept('mouse3-up', self.mouse2up)
        self.accept('mouse2-down', self.mouse3down)
        self.accept('enter', self.enter)
        self.accept('escape', self.escape)
        self.trackMouse = False
        self.slow = False
        self.change_zoom = False
        self.radius = 20
        self.strength = 2
        self.add_ball = False
        self.mouse2pressed = False
        self.enterPressed = False
        self.remove_ball = False
        self.zoomBall = False
        self.gameStateData = {
            "menu":"quit",
            "start_game":"menu",
            "game":"pause",
            "pause":"game",
            "load":"menu",
            "about_devs":"menu",
            "zoomed_mode":"game",
            "strength_mode":"zoomed_mode"
        }
        self.currentGameState = "game"
        self.theGameHasChanged = False

    def mouse1down(self):
        self.trackMouse = True

    def mouse1up(self):
        self.trackMouse = False

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

    def mouse2(self):
        if not self.mouse2pressed:
            self.add_ball = True
            print("new one must be here")
        else:
            self.add_ball = False
        self.mouse2pressed = True

    def mouse2up(self):
        self.mouse2pressed = False

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

        self.mydir = os.path.abspath(sys.path[0])
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()

        #self.myObject = DirectFrame(text="Start", frameColor=(225, 225, 225, 1), frameSize = (1, -1, 1, -1), scale=0.2, pos = (0, 0, 0))
        self.vborders = self.loader.loadModel(self.mydir + "/models/borders2.egg")
        self.vborders.reparentTo(self.render)
        self.vborders.setColorScale(0, 0.6, 0, 1)
        self.vborders.setHpr(90, 0, 0)


        self.table = self.loader.loadModel(self.mydir + "/models/table2.egg")
        self.table.reparentTo(self.render)
        self.table.setHpr(90, 0, 0)


        self.velvet = self.loader.loadModel(self.mydir + "/models/velvet2.egg")
        self.velvet.reparentTo(self.render)
        self.velvet.setColorScale(0, 0.6, 0, 1)
        self.velvet.setHpr(90, 0, 0)


        self.loosers = self.loader.loadModel(self.mydir + "/models/pocket2.egg")
        self.loosers.reparentTo(self.render)
        self.loosers.setColorScale(0, 0, 0, 1)
        self.loosers.setHpr(90, 0, 0)


        self.loos = self.loader.loadModel(self.mydir + "/models/pocketnet2.egg")
        self.loos.reparentTo(self.render)
        self.loos.setColorScale(1, 1, 1, 1)
        self.loos.setHpr(90, 0, 0)

        self.borders = self.loader.loadModel(self.mydir + "/models/woodenborders2.egg")
        self.borders.reparentTo(self.render)
        self.borders.setHpr(90, 0, 0)


        wood = self.loader.loadTexture(self.mydir + '/models/tex/WoodColor.jpg')
        self.table.setTexture(wood)
        self.borders.setTexture(wood)


        velvet = self.loader.loadTexture(self.mydir + '/models/tex/green.jpg')
        self.velvet.setTexture(velvet)
        self.vborders.setTexture(velvet)

        self.plight = PointLight('plight')
        self.plight.setColor((1, 1, 1, 1))
        plnp = self.render.attachNewNode(self.plight)
        plnp.setPos(0, 0, 10)
        self.render.setLight(plnp)

        self.plight.setShadowCaster(True, 2048, 2048)
        # Enable the shader generator for the receiving nodes
        self.render.setShaderAuto()
        self.newMousePos = [0, 0, "Empty"]

        self.strength = 0
        self.list_of_balls = []

        self.taskMgr.add(self.balls, "balls")
        #self.taskMgr.add(self.hitHandler, "tracking")
        self.taskMgr.add(self.gameStateOvereseer, "overseer")
        #self.taskMgr.add(self.followPointer, "pointer")
        self.disable_mouse()
        self.handler = Handler()
        self.camera.setHpr(0,
                           -90,
                           0)
        self.camera.setPos(self.handler.radius * math.cos(self.camera.getHpr()[1] * 3.1415926 / 180) * math.sin(self.camera.getHpr()[0] * 3.1415926 / 180),
                           -self.handler.radius * math.cos(self.camera.getHpr()[1] * 3.1415926 / 180) * math.cos(self.camera.getHpr()[0] * 3.1415926 / 180),
                           -self.handler.radius * math.sin(self.camera.getHpr()[1] * 3.1415926 / 180) + 0.7)
        r = 0.1
        x = 0
        y = - r * 15
        id = 0
        self.mass_circle = []
        for i in range(1, 6):
            for j in range(i):
                self.mass_circle.append(Circle(id, y, x + j * 2 * (r + 0.0001), r, 0, 0, self.mydir,
                                            self.render, [0 for i in range(18)], [0 for j in range(16)], 0.00001))
                id += 1
            x -= r + 0.0001
            y -= (r + 0.0001) * 3 ** 0.5

        self.mass_circle.append(Circle(id, 15 * r, 0, r, 0, 0, self.mydir,
                                       self.render, [0 for i in range(18)], [0 for j in range(16)], 0.00001))
        self.mass_circle[-1].model.setColorScale(0.54, 0, 0, 1)
        self.mass_circle[-1].model.setShaderAuto()
        self.kiy = self.loader.loadModel(self.mydir + "/models/kiy.egg")
        self.kiy.reparentTo(self.mass_circle[-1].model)
        self.kiy.setScale(0.5, 0.5, 0.5)
        self.kiy.hide()

        points1 = [
            (15 * r, 1.5 * r),
            (17 * r, 1.5 * r),
            (15 * r,  30 * r),
            (17 * r, 32  * r),

        ]

        self.mass_string = [Line(0, 2 * r, 0, 4 * r, 2 * r, 255, 255, 0, 6),
                       Line(1, 4 * r, 2 * r, 30.5 * r, 2 * r, 255, 255, 0, 4),
                       Line(2, 30.5 * r, 2 * r, 30.5 * r, 0, 255, 255, 0, 6),
                       Line(3, 33.5 * r, 0, 33.5 * r, 2 * r, 255, 255, 0, 6),
                       Line(4, 33.5 * r, 2 * r, 60 * r, 2 * r, 255, 255, 0, 4),
                       Line(5, 60 * r, 2 * r, 62 * r, 0, 255, 255, 0, 6),
                       Line(6, 2 * r, 34 * r, 4 * r, 32 * r, 255, 255, 0, 6),
                       Line(7, 4 * r, 32 * r, 30.5 * r, 32 * r, 255, 255, 0, 4),
                       Line(8, 30.5 * r, 32 * r, 30.5 * r, 34 * r, 255, 255, 0, 6),
                       Line(9, 33.5 * r, 34 * r, 33.5 * r, 32 * r, 255, 255, 0, 6),
                       Line(10, 33.5 * r, 32 * r, 60 * r, 32 * r, 255, 255, 0, 4),
                       Line(11, 60 * r, 32 * r, 62 * r, 34 * r, 255, 255, 0, 6),
                       Line(12, 0, 2 * r, 2 * r, 4 * r, 255, 255, 0, 6),
                       Line(13, 2 * r, 4 * r, 2 * r, 30 * r, 255, 255, 0, 4),
                       Line(14, 2 * r, 30 * r, 0, 32 * r, 255, 255, 0, 6),
                       Line(15, 64 * r, 2 * r, 62 * r, 4 * r, 255, 255, 0, 6),
                       Line(16, 62 * r, 4 * r, 62 * r, 30 * r, 255, 255, 0, 4),
                       Line(17, 62 * r, 30 * r, 64 * r, 32 * r, 255, 255, 0, 6)]

        for i in range(len(self.mass_string)):
            self.mass_string[i].x1 -= 32 * r
            self.mass_string[i].x2 -= 32 * r
            self.mass_string[i].y1 -= 17 * r
            self.mass_string[i].y2 -= 17 * r

        self.gameData = Physics(self.mass_circle, self.mass_string)
        self.current_ball = -1
        self.cameraLookAt = [0, 0, 0.7]

        """self.tracker = self.loader.loadModel(self.mydir + "/models/circle.egg")
        self.tracker.set_scale(0.015, 0.015, 0.015)
        self.tracker.reparentTo(self.render)
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = self.camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.cTrav.addCollider(self.pickerNP, self.handler)"""

    #camera rotation
    def spin_camera(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        if abs(self.mouseWatcherNode.getMouseY()) > 0.01 or abs(self.mouseWatcherNode.getMouseX()) != 0.0:
            if self.newMousePos[2] == "Empty":
                self.newMousePos[2] = "Filled"
                props = self.win.getProperties()
                self.win.movePointer(0,
                                     int(props.getXSize() / 2),
                                     int(props.getYSize() / 2))
            else:
                self.newMousePos = [self.mouseWatcherNode.getMouseX(), self.mouseWatcherNode.getMouseY(), "Filled"]
                if self.handler.slow:
                    times = 2
                else:
                    times = 20
                angleHorDegrees = self.newMousePos[0] * times
                angleVerDegrees = self.newMousePos[1] * times
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
            self.change_zoom()


    def change_zoom(self):
            cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
            cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0
            self.camera.setPos(self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[0],
                               -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) + self.cameraLookAt[1],
                               -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

    def updateCamera(self):
        cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
        cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0
        self.camera.setPos(
            self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[0],
            -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) + self.cameraLookAt[1],
            -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

    def balls(self, Task):
        self.gameData.drawing_circle()
        self.gameData.moving()
        self.gameData.check_boarder()
        self.gameData.collisions_mass()
        #self.gameData.collisions_line()
        return Task.cont



    def hitHandler(self, Task):
        if self.handler.theGameHasChanged and self.mass_circle:
            if self.handler.currentGameState == "zoomed_mode":
                self.cameraLookAt = self.mass_circle[self.current_ball].model.getPos(self.render)
                self.handler.theGameHasChanged = False
            elif self.handler.currentGameState == "game":
                self.cameraLookAt = [0, 0, 0.7]
                self.handler.theGameHasChanged = False


            cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
            cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0
            self.handler.radius = 3 if self.handler.currentGameState == "zoomed_mode" else 10
            self.camera.setPos(
                self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[
                    0],
                -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) +
                self.cameraLookAt[1],
                -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])

        if self.handler.trackMouse and self.handler.currentGameState == "target":
            self.strength += self.mouseWatcherNode.getMouseY()

        return Task.cont

    def posKiy(self):
        self.kiy.setH(self.camera.getH())
        self.kiy.setR(10)
        kiyHorHprRadians = self.kiy.getHpr()[0] * math.pi / 180.0
        kiyVerHprRadians = self.kiy.getHpr()[2] * math.pi / 180.0
        self.kiy.setPos(
            self.handler.strength * math.cos(kiyVerHprRadians) * math.sin(kiyHorHprRadians),
            -self.handler.strength * math.cos(kiyVerHprRadians) * math.cos(kiyHorHprRadians),
            self.handler.strength * math.sin(kiyVerHprRadians))
        self.kiy.setH(self.kiy.getH() + 90)

    def gameStateOvereseer(self, Task):
        if self.handler.currentGameState == "game":
            if self.handler.theGameHasChanged:
                self.cameraLookAt = [0, 0, 0.7]
                self.handler.radius = 10
                self.handler.theGameHasChanged = False
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)
                self.updateCamera()
                self.kiy.hide()

            if self.handler.enterPressed and len(self.gameData.balls) > 0:
                self.handler.currentGameState = "zoomed_mode"
                self.handler.theGameHasChanged = True
                self.handler.enterPressed = False

            if self.handler.trackMouse:
                self.spin_camera()
            elif self.handler.change_zoom:
                self.change_zoom()
                self.handler.change_zoom = False
            elif self.newMousePos[2] != "Empty":
                self.newMousePos[2] = "Empty"
                props = WindowProperties()
                props.setCursorHidden(False)
                self.win.requestProperties(props)

        elif self.handler.currentGameState == "zoomed_mode":
            if self.handler.theGameHasChanged and self.gameData.balls:
                self.cameraLookAt = self.gameData.balls[self.current_ball].model.getPos(self.render)
                self.handler.radius = 4
                self.handler.theGameHasChanged = False
                self.updateCamera()
                self.posKiy()
                self.kiy.show()
            if self.mouseWatcherNode.hasMouse():
                self.spin_camera()
                self.posKiy()
            elif self.newMousePos[2] != "Empty":
                self.newMousePos[2] = "Empty"
            if self.handler.trackMouse:
                self.handler.currentGameState = "strength_mode"

        elif self.handler.currentGameState == "strength_mode":
            if self.mouseWatcherNode.hasMouse() and self.handler.trackMouse:
                self.handler.strength -= self.mouseWatcherNode.getMouseY()
                if self.handler.strength < 1.46:
                    self.handler.strength = 1.46
                if self.handler.strength > 5:
                    self.handler.strength = 5
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


        elif self.handler.currentGameState == "target":
            self.strength += self.mouseWatcherNode.getMouseY()

        return Task.cont
app = MyApp()
app.run()
