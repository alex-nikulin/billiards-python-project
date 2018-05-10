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

#прикладные функции
# нахождение минимального расстояния от шара до линий(всех). возвращает массив с высотой и ,если высота не падает на сторону,
#с минимальным расстоянием и с координатой вершины, расстояние до которой минимальное + идентификационный номер линии,
# расстояние до которой минимальное
def find_minimal_distance(mass_line, circle):
    mass_total = []
    for i in range(len(mass_line)):
        mass_temporary = distance_string(circle, mass_line[i])
        if len(mass_temporary) == 1:
            mass_total.append(mass_temporary[0])
        else:
            mass_total.append(mass_temporary[1])
    a = 1000
    b = 0
    for i in range(len(mass_total)):
        if a > mass_total[i]:
            a = mass_total[i]
            b = i
    mass_total = distance_string(circle, mass_line[b])
    mass_total.append(b)
    return mass_total


# раскладывает вектор по базису из двух векторов
def vector_decompos(vec1, vec2, vel):
    g1 = vel.x * vec2.y - vel.y * vec2.x
    g2 = vec1.x * vel.y - vec1.y * vel.x
    g = vec1.x * vec2.y - vec1.y * vec2.x
    return [g1 / g, g2/ g]

# находит расстояние между центром шара и отрезком. возврашает массив с высотой и ,если высота не падает на сторону,
# с минимальным расстоянием и с координатой вершины, расстояние до которой минимальное
def distance_string(circle, line):
    a = Vector(circle.x, circle.y).sub(Vector(line.x1, line.y1))
    b = Vector(circle.x, circle.y).sub(Vector(line.x2, line.y2))
    c = Vector(line.x1, line.y1).sub(Vector(line.x2, line.y2))
    d = Vector(- c.y, c.x)
    s = abs(a.mul_vect(b))
    d = d.mul_num((1 / c.length()) * s / c.length())
    mass = [d.length()]
    if abs(d.mul_vect(a)) + abs(d.mul_vect(b)) > s:
        if a.length() < b.length():
            mass.append(min(a.length(),b.length()))
            mass.append(Vector(line.x1, line.y1))
        else:
            mass.append(min(a.length(),b.length()))
            mass.append(Vector(line.x2, line.y2))
    return mass


# рассматривает сталкивание шара с отрезком
def check_string(circle, mass_line):
    mass = find_minimal_distance(mass_line, circle)
    if circle.check_point_line[mass_line[mass[-1]].individual_number] == 0:
        if len(mass) == 2:
            if mass[0] <= circle.r + mass_line[mass[-1]].width / 2:
                a = Vector(mass_line[mass[-1]].x1 - mass_line[mass[-1]].x2, mass_line[mass[-1]].y1 - mass_line[mass[-1]].y2)
                b = Vector(a.y, -a.x)
                mass_decompos = vector_decompos(a, b, Vector(circle.vel_x, circle.vel_y))
                circle.vel_x = (mass_decompos[0] * a.x - mass_decompos[1] * b.x) * 0.5
                circle.vel_y = (mass_decompos[0] * a.y - mass_decompos[1] * b.y) * 0.5
                circle.check_point_line[mass_line[mass[-1]].individual_number] = 1
        else:
            if mass[1] <= circle.r+ mass_line[mass[-1]].width / 2:
                a = Vector(circle.x, circle.y).sub(mass[2])
                b = Vector(-a.y, a.x)
                mass_decompos = vector_decompos(a, b, Vector(circle.vel_x, circle.vel_y))
                circle.vel_x = (-mass_decompos[0] * a.x + mass_decompos[1] * b.x) * 0.5
                circle.vel_y = (-mass_decompos[0] * a.y + mass_decompos[1] * b.y) * 0.5
                circle.check_point_line[mass_line[mass[-1]].individual_number] = 1
    elif circle.check_point_line[mass_line[mass[-1]].individual_number] == 1:
        if len(mass) == 2:
            if mass[0] > circle.r + mass_line[mass[-1]].width:
                circle.check_point_line[mass_line[mass[-1]].individual_number] = 0
        else:
            if mass[1] > circle.r + mass_line[mass[-1]].width:
                circle.check_point_line[mass_line[mass[-1]].individual_number] = 0


# рассматривает абсолютно упругое столкновение двух шаров
def collisions(circle1, circle2):
#    if (abs(circle1.vel_x) + abs(circle1.vel_y)) + (abs(circle2.vel_y) + abs(circle2.vel_x)) > 0:
        if circle1.check_point_circle[circle2.identical_number] + circle2.check_point_circle[circle1.identical_number] == 0:
            if Vector(circle1.x, circle1.y).distance(Vector(circle2.x, circle2.y)) < circle1.r + circle2.r:
                a = Vector(circle1.x - circle2.x, circle1.y - circle2.y)
                b = Vector(a.y, -a.x)
                mass1 = vector_decompos(a, b, Vector(circle1.vel_x, circle1.vel_y))
                mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
                circle1.vel_x = (b.x * mass1[1] + a.x * mass2[0]) * 0.95
                circle1.vel_y = (b.y * mass1[1] + a.y * mass2[0]) * 0.95
                mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
                circle2.vel_x = (b.x * mass2[1] + a.x * mass1[0]) * 0.95
                circle2.vel_y = (b.y * mass2[1] + a.y * mass1[0]) * 0.95
                circle1.check_point_circle[circle2.identical_number], \
                circle2.check_point_circle[circle1.identical_number] = 1, 1
        elif circle1.check_point_circle[circle2.identical_number] + circle2.check_point_circle[circle1.identical_number] == 2:
            if Vector(circle1.x, circle1.y).distance(Vector(circle2.x, circle2.y)) > circle1.r + circle2.r:
                circle1.check_point_circle[circle2.identical_number], \
                circle2.check_point_circle[circle1.identical_number] = 0, 0
                collisions(circle1, circle2)
        if ((abs(circle1.vel_x) + abs(circle1.vel_y)) + (abs(circle2.vel_y) + abs(circle2.vel_x)) == 0 and
            circle1.check_point_circle[circle2.identical_number] + circle2.check_point_circle[circle1.identical_number] == 2):
            circle1.check_point_circle[circle2.identical_number], \
            circle2.check_point_circle[circle1.identical_number] = 0, 0



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

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def cos(self, other):
        return (self.x * other.x + self.y * other.y) / abs(self) / abs(other)

    def angle(self, other):
        return m.arcos(self.cos(other))

    def devision_num(self, a):
        return Vector(self.x / a, self.y /a)

    def mul_vect(self, vect):
        return self.x * vect.y - self.y * vect.x

    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Line:
    def __init__(self, individual_number, x1, y1, x2, y2, red, green, blue, width=1):
        self.individual_number = individual_number
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.red = red
        self.green = green
        self.blue = blue
        self.width = width


#описание класса шаров
class Circle:
    def __init__(self, id, x, y, r, vel_x, vel_y, mydir,  parent, check_point_line, check_point_circle, friction):
        self.identical_number = id
        self.x = x
        self.y = y
        self.z = 0.82
        self.r = r
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.friction = friction
        self.check_point_line = check_point_line
        self.check_point_circle = check_point_circle
        self.model = loader.loadModel(mydir + "/models/ball.egg")
        self.model.setColorScale(0.9, 0.9, 0.9, 1)
        self.model.setScale(0.1, 0.1, 0.1)
        self.model.reparentTo(parent)
        self.model.setShaderAuto()



    def move(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        if abs(self.vel_x) + abs(self.vel_y) < self.friction:
            self.vel_x = 0
            self.vel_y = 0
        if self.vel_x > 0:
            self.vel_x -= self.friction * abs(self.vel_x) / (abs(self.vel_y) + abs(self.vel_x))
        elif self.vel_x < 0:
            self.vel_x += self.friction * abs(self.vel_x) / (abs(self.vel_y) + abs(self.vel_x))
        if self.vel_y > 0:
            self.vel_y -= self.friction * abs(self.vel_y) / (abs(self.vel_y) + abs(self.vel_x))
        elif self.vel_y < 0:
            self.vel_y += self.friction * abs(self.vel_y) / (abs(self.vel_y) + abs(self.vel_x))

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
        if self.check_point_circle[circle2.identical_number] + circle2.check_point_circle[self.identical_number] == 0:
            if Vector(self.x, self.y).distance(Vector(circle2.x, circle2.y)) < self.r + circle2.r:
                a = Vector(self.x - circle2.x, self.y - circle2.y)
                b = Vector(a.y, -a.x)
                mass1 = vector_decompos(a, b, Vector(self.vel_x, self.vel_y))
                mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
                self.vel_x = (b.x * mass1[1] + a.x * mass2[0]) * 0.95
                self.vel_y = (b.y * mass1[1] + a.y * mass2[0]) * 0.95
                mass2 = vector_decompos(a, b, Vector(circle2.vel_x, circle2.vel_y))
                circle2.vel_x = (b.x * mass2[1] + a.x * mass1[0]) * 0.95
                circle2.vel_y = (b.y * mass2[1] + a.y * mass1[0]) * 0.95
                self.check_point_circle[circle2.identical_number], \
                circle2.check_point_circle[self.identical_number] = 1, 1
        elif self.check_point_circle[circle2.identical_number] + circle2.check_point_circle[self.identical_number] == 2:
            if Vector(self.x, self.y).distance(Vector(circle2.x, circle2.y)) > self.r + circle2.r:
                self.check_point_circle[circle2.identical_number], \
                circle2.check_point_circle[self.identical_number] = 0, 0
                collisions(self, circle2)
        if ((abs(self.vel_x) + abs(self.vel_y)) + (abs(circle2.vel_y) + abs(circle2.vel_x)) == 0 and
                self.check_point_circle[circle2.identical_number] + circle2.check_point_circle[self.identical_number] == 2):
                self.check_point_circle[circle2.identical_number], \
            circle2.check_point_circle[self.identical_number] = 0, 0

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


class Physics:
    def __init__(self, balls, lines, height=1.6, width=3.1):
        self.balls = balls
        self.lines = lines
        self.width = height
        self.height = width

    def collisions_mass(self):
        x = len(self.balls)
        while x > 1:
            for i in range(len(self.balls)):
                if len(self.balls) - x < i:
                    collisions(self.balls[len(self.balls) - x], self.balls[i])
            x -= 1

    def collisions_line(self):
        for i in range(len(self.balls)):
            check_string(self.balls[i], self.lines)

    def drawing_circle(self):
        for i in self.balls:
            i.drawing()

    def checking(self):
        for i in self.balls:
            i.check_circle(self.width, self.height)

    def moving(self, dt=1):
        for i in self.balls:
            i.move(dt)
    """
    def check_boarder(self):
        a = 0
        for i in range(len(self.balls)):
            if self.balls[i - a].x > self.width + self.balls[i - a].r or self.balls[i - a].x < 0 - self.balls[i - a].r:
                self.balls.pop(i - a)
                for j in range(len(self.balls)):
                    self.balls[j].check_point_circle.pop(i - a)
                a += 1
                for t in range(i - a, len(self.balls)):
                    self.balls[t].identical_number -= 1
            if self.balls[i - a].y > self.height + self.balls[i - a].r or self.balls[i - a].y < 0 - self.balls[i - a].r:
                self.balls.pop(i - a)
                for j in range(len(self.balls)):
                    self.balls[j].check_point_circle.pop(i - a)
                a += 1
                for t in range(i - a, len(self.balls)):
                    print(t)
                    self.balls[t].identical_number -= 1
    """
    def check_boarder(self):
        i = 0
        while i < len(self.balls) - 1:
            if (self.balls[i].x > self.height or self.balls[i].x < -self.height or
                self.balls[i].y > self.width  or self.balls[i].y < -self.width):
                self.balls[i].model.hide()
                self.balls.pop(i)
                for j in range(len(self.balls)):
                    self.balls[j].check_point_circle.pop(i)
            i += 1

        for i in range(len(self.balls)):
            self.balls[i].identical_number = i


    def check_velocity(self):
        a = 0
        for i in range(len(self.balls)):
            a += abs(self.balls[i].vel_x) + abs(self.balls[i].vel_y)
        if a == 0:
            return False
        elif a > 0:
            return True



