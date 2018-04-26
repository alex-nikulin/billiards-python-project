from panda3d.core import Filename
import math as m
import sys, os

mydir = os.path.abspath(sys.path[0])
mydir = Filename.fromOsSpecific(mydir).getFullpath()


def vector_decompos(vec1, vec2, vel):
    g1 = vel.x * vec2.y - vel.y * vec2.x
    g2 = vec1.x * vel.y - vec1.y * vel.x
    g = vec1.x * vec2.y - vec1.y * vec2.x
    return [g1 / g, g2 / g]


# описание класса векторов
class Vector:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def add(self, vect):
        return Vector(self.x + vect.x, self.y + vect.y)

    def sub(self, vect):
        return Vector(self.x - vect.x, self.y - vect.y)

    def mul_num(self, a):
        return Vector(self.x * a, self.y * a)

    def __mul__(self, number):
        return Vector(self.x * number, self.y * number)

    def distance(self, vect):
        return ((self.x - vect.x) ** 2 + (self.y - vect.y) ** 2) ** 0.5

#описание класса шаров
class Circle:
    def __init__(self, x, y, z, r, vel_x, vel_y, red, green, blue, mydir, friction, parent):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.red = red
        self.green = green
        self.blue = blue
        self.friction = friction
        self.model = loader.loadModel(mydir + "/models/ball.egg")
        self.model.setColorScale(0.9, 0.9, 0.9, 1)
        self.model.setScale(0.2, 0.2, 0.2)
        self.model.reparentTo(parent)
        self.model.setShaderAuto()



    def move(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        if abs(self.vel_x) < self.friction:
            self.vel_x = 0
        if abs(self.vel_y) < self.friction:
            self.vel_y = 0

        if self.vel_x > 0:
            self.vel_x -= self.friction
        elif self.vel_x < 0:
            self.vel_x += self.friction
        if self.vel_y > 0:
            self.vel_y -= self.friction
        elif self.vel_y < 0:
            self.vel_y += self.friction

    def change_color(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def drawing(self):
        self.model.setPos(self.x, self.y, self.z)

    def distance(self, circle):
        return ((self.x - circle.x) ** 2 + (self.y - circle.y) ** 2) ** 0.5

    def check(self, low_width, width, low_height, height):
        if self.x > width:
            self.vel_x = - abs(self.vel_x)
        if self.x < low_width + self.r:
            self.vel_x = abs(self.vel_x)
        if self.y > height:
            self.vel_y = - abs(self.vel_y)
        if self.y < low_height:
            self.vel_y = abs(self.vel_y)

    def collisions(self, circle2):
        a = Vector(self.x - circle2.x, self.y - circle2.y)
        b = Vector(a.y, -a.x)
        mass1 = vector_decompos(a, b, Vector(self.vel_x, self.vel_y))
        mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
        self.vel_x = b.x * mass1[1] + a.x * mass2[0]
        self.vel_y = b.y * mass1[1] + a.y * mass2[0]
        mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
        circle2.vel_x = b.x * mass2[1] + a.x * mass1[0]
        circle2.vel_y = b.y * mass2[1] + a.y * mass1[0]

    def getPos(self):
        return [self.x, self.y, self.z]



class Balls:
    def __init__(self, default_list=[]):
        self.balls = default_list

    def add(self, newball):
        self.balls.append(newball)

    def pop(self, number):
        self.balls.pop(number)

    def remove_marked(self):
        for i in range(len(self.balls)):
            if self.balls[i].exist == "false":
                self.balls.pop(i)

    def drawing(self):
        for i in self.balls:
            i.drawing()

    def checking(self, low_width, width, low_height, height):
        for i in self.balls:
            i.check(low_width, width, low_height, height)

    def moving(self, dt=1):
        for i in self.balls:
            i.move(dt)

    def collisions_mass(self):
        x = len(self.balls)
        while x > 1:
            for i in range(len(self.balls)):
                if len(self.balls) - x < i:
                    if self.balls[len(self.balls) - x].distance(self.balls[i]) < self.balls[len(self.balls) - x].r + self.balls[i].r:
                        self.balls[len(self.balls) - x].collisions(self.balls[i])
            x -= 1

