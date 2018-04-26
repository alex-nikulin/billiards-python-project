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
from classes import Balls, Circle
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
        self.add_ball = False
        self.mouse2pressed = False
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
            "target":"zoomed_mode"
        }
        self.currentGameState = "game"
        self.theGameHasChanged = False

    def mouse1down(self):
        if self.currentGameState == "game":
            self.trackMouse = True
            print('down')

    def mouse1up(self):
        if self.currentGameState == "game":
            self.trackMouse = False
            print("up")

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
        self.currentGameState = "zoomed_mode"
        self.gameChanged()
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
        self.setBackgroundColor(0, 0, 0, 1)
        self.scene = self.loader.loadModel("models/environment.egg")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        self.table = self.loader.loadModel(self.mydir + "/models/table.egg")
        self.table.setScale(0.5, 0.5, 0.5)
        self.table.reparentTo(self.render)
        self.table.setPos(0, 0, 3)

        self.velvet = self.loader.loadModel(self.mydir + "/models/velvet.egg")
        self.velvet.reparentTo(self.table)
        self.velvet.setColorScale(0, 0.6, 0, 1)

        self.vborders = self.loader.loadModel(self.mydir + "/models/borders.egg")
        self.vborders.reparentTo(self.table)
        self.vborders.setColorScale(0, 0.6, 0, 1)

        self.loosers = self.loader.loadModel(self.mydir + "/models/loosers.egg")
        self.loosers.reparentTo(self.table)
        self.loosers.setColorScale(0, 0, 0, 1)

        self.loos = self.loader.loadModel(self.mydir + "/models/loos.egg")
        self.loos.reparentTo(self.table)
        self.loos.setColorScale(0, 0, 0, 1)

        self.kiy = self.loader.loadModel(self.mydir + "/models/kiy.egg")

        self.borders = self.loader.loadModel(self.mydir + "/models/woodenborders.egg")
        self.borders.reparentTo(self.table)

        wood = self.loader.loadTexture(self.mydir + '/models/tex/WoodColor.jpg')
        self.table.setTexture(wood)


        velvet = self.loader.loadTexture(self.mydir + '/models/tex/green.jpg')
        self.velvet.setTexture(velvet)

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

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.balls, "balls")
        self.taskMgr.add(self.hitHandler, "tracking")
        #self.taskMgr.add(self.gameStateOvereseer, "overseer")
        #self.taskMgr.add(self.followPointer, "pointer")
        self.disable_mouse()
        self.handler = Handler()
        self.camera.setHpr(0,
                           -20,
                           0)
        self.camera.setPos(self.handler.radius * math.cos(-0.3490658503988659) * math.sin(0),
                           -self.handler.radius * math.cos(-0.3490658503988659) * math.cos(0),
                           -self.handler.radius * math.sin(-0.3490658503988659) + 3.7)

        self.mass = Balls()
        self.current_ball = 0
        self.cameraLookAt = [0, 0, 3.7]


    #camera rotation
    def spinCameraTask(self, Task):
        if ((self.handler.currentGameState == "game" or self.handler.currentGameState == "zoomed_mode")
            and (self.handler.trackMouse or self.handler.currentGameState == "zoomed_mode")
            and (self.newMousePos[2] != "Filled" or self.newMousePos[1] != 0 or self.newMousePos[2] != 0)
            and self.mouseWatcherNode.hasMouse()):

            props = WindowProperties()
            props.setCursorHidden(True)
            self.win.requestProperties(props)

            if (abs(self.mouseWatcherNode.getMouseY()) > 0.01 or abs(self.mouseWatcherNode.getMouseX()) != 0.0
                ):

                if self.newMousePos[2] == "Empty":
                    #self.keepPosition = [0, self.mouseWatcherNode.getMouseX(), self.mouseWatcherNode.getMouseY()]
                    #print(self.keepPosition)
                    self.newMousePos[2] = "Filled"
                    props = self.win.getProperties()
                    self.win.movePointer(0,
                                         int(props.getXSize() / 2),
                                         int(props.getYSize() / 2))


                else:
                    self.newMousePos = [self.mouseWatcherNode.getMouseX(), self.mouseWatcherNode.getMouseY(), "Filled"]
                    changeHor = self.newMousePos[0]
                    changeVer = self.newMousePos[1]
                    if self.handler.slow:
                        times = 2
                    else:
                        times = 20
                    angleHorDegrees = changeHor * times
                    angleVerDegrees = changeVer * times
                    self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                           self.camera.getHpr()[1] + angleVerDegrees,
                                           0)
                    if self.camera.getHpr()[1] < -90:
                        self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                           -90,
                                           0)
                    elif self.camera.getHpr()[1] > 20:
                        self.camera.setHpr(self.camera.getHpr()[0] - angleHorDegrees,
                                           20,
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
            cameraHorHprRadians = self.camera.getHpr()[0] * math.pi / 180.0
            cameraVerHprRadians = self.camera.getHpr()[1] * math.pi / 180.0
            self.camera.setPos(self.handler.radius * math.cos(cameraVerHprRadians) * math.sin(cameraHorHprRadians) + self.cameraLookAt[0],
                               -self.handler.radius * math.cos(cameraVerHprRadians) * math.cos(cameraHorHprRadians) + self.cameraLookAt[1],
                               -self.handler.radius * math.sin(cameraVerHprRadians) + self.cameraLookAt[2])
            self.handler.change_zoom = False

        elif self.newMousePos[2] != "Empty":
            self.newMousePos[2] = "Empty"
            props = WindowProperties()
            props.setCursorHidden(False)
            self.win.requestProperties(props)
        return Task.cont
        # this return means that SpinCameraTask will be called in the next frame

    def balls(self, Task):
        if self.handler.mouse2pressed:

            print("new ball added")
            self.mass.add(Circle(random.uniform(-5.51, 5.51), random.uniform(-2.94, 2.94), 0.82, 0.2, 0.05 * random.random(), 0.05 * random.random(), 255, 0, 0, self.mydir, 0.00008, self.table))
            self.mass.balls[-1].model.setTexture(loader.loadTexture(self.mydir + "/models/tex/white.png"))
            self.mass.balls[-1].model.setShaderAuto()
        self.mass.drawing()
        self.mass.moving()
        self.mass.checking(-5.51, 5.51, -2.94, 2.94)
        self.mass.collisions_mass()
        return Task.cont

    def hitHandler(self, Task):
        if self.handler.theGameHasChanged and self.mass.balls:
            if self.handler.currentGameState == "zoomed_mode":
                self.cameraLookAt = self.mass.balls[self.current_ball].model.getPos(self.render)
                self.handler.theGameHasChanged = False
            elif self.handler.currentGameState == "game":
                self.cameraLookAt = [0, 0, 3.7]
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

app = MyApp()
app.run()
