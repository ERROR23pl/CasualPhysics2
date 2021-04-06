from math import *
import pygame as pg
from copy import copy
import os
from graph import Graph

print("\n---Casual Physics 2.0---\n")

blue = (82, 188, 222)
yellow = (255, 240, 7)
red = (255, 114, 86)
gray = (137, 137, 137)
pink = (222, 91, 194)
lightPink = (243, 152, 171)
green = (127, 182, 98)


def clear():
    os.system('cls')


def splitUp(a, b, step=1):
    result = []
    a = a
    b = b
    while a <= b:
        result.append(a)
        a += step
    return result


def calcGrav(ob1, ob2):
    # the gravitational force object1 exerts ON object2
    try:
        g = 6.7e-11
        value = (g * ob1.mass * ob2.mass) / (distance(ob1, ob2) ** 2)
        alpha = angle(ob2, ob1)
        return Vector.fromTrig(value, alpha)
    except:
        return V(0, 0)


def calcCharge(ob1, ob2):
    # the electromagnetic force object1 exerts ON object2
    try:
        k = 9e9
        value = (k * ob1.charge * ob2.charge) / (distance(ob1, ob2) ** 2)
        alpha = angle(ob2, ob1)
        return Vector.fromTrig(value, alpha).inv()
    except ZeroDivisionError:
        return V(0, 0)


def distance(ob1, ob2):
    if type(ob1) == Vector:
        return (ob1 - ob2).len
    elif type(ob1) == Body:
        return (ob1.coor - ob2.coor).len


def angle(ob1, ob2):
    return atan2(ob2.coor.y - ob1.coor.y, ob2.coor.x - ob1.coor.x)


class Vector:
    def __init__(self, *args, vType=''):
        if type(args[0]) == tuple:
            self.coor = list(args[0])
        elif type(args[0]) == list:
            self.coor = args[0]
        elif (type(args[0]) == float) or (type(args[0]) == int):
            self.coor = list(args)
        self.vType = vType

    @property
    def x(self):
        return self.coor[0]

    @property
    def y(self):
        return self.coor[1]

    @x.setter
    def x(self, v):
        self.coor[0] = v

    @y.setter
    def y(self, v):
        self.coor[1] = v

    def __repr__(self):
        return self.vType + "[" + str(self.x) + ", " + str(self.y) + "]"

    def __add__(self, other):
        tempType = self.vType if self.vType == other.vType else ""
        return Vector(self.x + other.x, self.y + other.y, vType=tempType)

    def __sub__(self, other):
        tempType = self.vType if self.vType == other.vType else ""
        return Vector(self.x - other.x, self.y - other.y, vType=tempType)

    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            return Vector(self.x * other, self.y * other, vType=self.vType)
        elif type(other) == Vector:
            tempType = self.vType if self.vType == other.vType else ""
            return Vector(self.x * other.x, self.y * other.y, vType=tempType)

    def __truediv__(self, other):
        if type(other) == int or type(other) == float:
            return Vector(self.x / other, self.y / other, vType=self.vType)
        elif type(other) == Vector:
            tempType = self.vType if self.vType == other.vType else ""
            return Vector(self.x / other.x, self.y / other.y, vType=tempType)

    def inv(self):
        return Vector([-self.x, -self.y], vType=self.vType)

    @property
    def len(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return atan2(self.y, self.x)

    def draw(self, sim, start, color=blue, width=5, scaling=lambda x: x):
        try:
            end = start + scaling(self)
        except ValueError:
            end = start + self

        sim.drawLine(start, end, color, width)
        sim.drawTriangle(end, self.angle, 2 * width, color)

    @classmethod
    def fromTrig(cls, r, ang):
        return Vector(r * cos(ang), r * sin(ang))


V = Vector


class Velocity(Vector):
    def __init__(self, x, y):
        super().__init__([x, y], vType="v")


class Acceleration(Vector):
    def __init__(self, x, y):
        super().__init__([x, y], vType="a")


class Force(Vector):
    def __init__(self, x, y):
        super().__init__([x, y], vType="f")


class Body:
    count = 0

    def __init__(self, sim, coor=V(0, 0), mass=1, charge=0, width=5, name=None):
        self.sim = sim
        self.sim.bodies.append(self)

        self.coor = coor
        self.mass = mass
        self.charge = charge
        self.width = width
        self.name = name if name is not None else f'Body#{Body.count}'
        Body.count += 1

        self.fList = []
        self.aList = []

        self.force = V(0, 0)
        self.acceleration = V(0, 0)
        self.velocity = V(0, 0)

        self.priority = False

        self.drawProp = {
            "color": (82, 188, 222),  # color of the object
            "showBody": True,  # If False the object will be invisible (But it will still exist!)
            "showVelocity": False,  # If True the Net Velocity vector will be shown
            "showAcceleration": False,  # If True the Net Acceleration vector will be shown
            "showForce": False,  # If True the Net Force vector will be shown
            "showTrail": False  # If True object will draw a trail
        }
        self.trail = [self.coor.coor, self.coor.coor]

        self.moveProp = {
            "doMove": True,
            "generateGravity": False,
            "affectedByGravity": True,
            "generateCharge": True,
            "affectedByCharge": True,
        }

    @property
    def momentum(self):
        return self.velocity * self.mass

    def __repr__(self):
        return f'{self.name} [coor: {self.coor.x}, mass: {self.mass}, charge: {self.charge}]'

    def remove(self):
        del self.sim.bodies[self.sim.bodies.index(self)]
        del self

    def append(self, vec):
        if vec.vType == 'v':
            self.velocity += vec
        elif vec.vType == 'a':
            self.aList.append(vec)
        elif vec.vType == 'f':
            self.fList.append(vec)
        else:
            raise ValueError

    def move(self):
        if self.moveProp['doMove']:
            fNet = V(0, 0)

            if self.moveProp['affectedByGravity']:
                for i in self.sim.bodies:
                    if i.moveProp['generateGravity'] and i is not self:
                        fNet += calcGrav(i, self)

            if self.moveProp['affectedByCharge']:
                for i in self.sim.bodies:
                    if i.moveProp['generateCharge'] and i is not self:
                        fNet += calcCharge(i, self)

            for i in self.fList:
                fNet += i
            self.force = Force(fNet.x, fNet.y)

            aNet = fNet / self.mass
            for i in self.aList:
                aNet += i
            self.acceleration = copy(aNet)

            self.velocity += aNet * self.sim.dt
            self.coor += self.velocity * self.sim.dt


    def draw(self):
        if self.drawProp['showBody']:
            size = self.width * self.sim.cam.scale.x
            size = size if size >= 1 else 1
            # pg.draw.circle(self.sim.dis, (255,255,255), self.sim.cam.trans(self.coor), size+4)
            pg.draw.circle(self.sim.dis, self.drawProp['color'], self.sim.cam.trans(self.coor), size)

            if self.drawProp['showVelocity']:
                self.velocity.draw(self.sim, self.coor, blue, 4)
            if self.drawProp['showAcceleration']:
                self.acceleration.draw(self.sim, self.coor, yellow, 4)
            if self.drawProp['showForce']:
                self.force.draw(self.sim, self.coor, red, 4)

            if self.drawProp['showTrail']:
                temp = []
                for i in self.trail:
                    temp.append(self.sim.cam.trans(V(i)))
                pg.draw.lines(self.sim.dis, self.drawProp['color'], False, temp)

                if not self.sim.pause:
                    if self.sim.operations % 1 == 0:
                        self.trail.append(self.coor.coor)

                    if len(self.trail) > 30:
                        self.trail.pop(0)
        else:
            pass


class Camera:
    def __init__(self, start, resolution=V(1280, 720), display=V(1280, 720)):
        self.pos = start
        self.res = resolution
        self.display = display

    @property
    def scale(self):
        return self.display / self.res

    @property
    def center(self):
        return self.pos + (self.res / 2)

    @property
    def end(self):
        return self.pos + self.res

    def focus(self, point):
        self.pos = point - (self.res / 2)

    def toWidth(self, width):
        k = width / self.res.x
        self.res *= k
        self.focus(V(0, 0))

    def trans(self, point):
        temp = (point - self.pos) * self.scale
        temp.y *= -1
        temp.y += self.display.y
        return temp.coor

    def untrans(self, point):
        temp = V(point)
        temp.y -= self.display.y
        temp.y *= -1
        temp /= self.scale
        temp += self.pos
        return temp

    def inFrame(self, vec):
        return self.pos.x < vec.x <= self.end.x and self.pos.y < vec.y <= self.end.y


class Simulation:
    def __init__(self, width, height):
        pg.init()
        self.res = V(width, height)
        self.cam = Camera(V(0, 0), self.res, self.res)
        self.cam.focus(V(0, 0))
        self.bodies = []

        self.collision = True

        self.t = 0
        self.dt = 0.1
        self.ops = 30
        self.fps = 1
        self.operations = 0

        self.dis = pg.display.set_mode(self.res.coor)
        pg.display.set_caption('Casual Physics 2')
        self.clock = pg.time.Clock()

        logo = pg.image.load('logo.png')
        pg.display.set_icon(logo)

        self.fontStyle = pg.font.SysFont("Times New Roman", 25)

        self.lClickHold = False
        self.lastMousePos = None
        self.lastMouseCoor = None

        self.run = True
        self.pause = True

    def collisions(self):
        result = Graph()
        for i in self.bodies:
            for ii in self.bodies:
                if i is not ii and (ii.coor - i.coor).len < ii.width + i.width and not result.isConnect(i, ii):
                    result.connect(i, ii)

        return result

    def collisionFusion(self):
        all = self.collisions().groups()
        for group in all:
            newBody = Body(self, V(0, 0), 0, 0, 0)
            # newBody.drawProp['color'] = group[0].drawProp['color']
            newBody.drawProp = group[0].drawProp

            priorityFlag = 0
            priorityBody = None
            for i in group:
                # Searching for priority body
                if i.priority:
                    priorityFlag += 1
                    priorityBody = i

                # searching for stationary body
                if not i.moveProp['affectedByGravity']:
                    newBody.moveProp['affectedByGravity'] = False

                # searching for not moving object
                if not i.moveProp['doMove']:
                    newBody.moveProp['doMove'] = False

            priorityFlag = True if priorityFlag == 1 else False

            for body in group:
                newBody.coor += body.coor * body.width
                newBody.moveProp['generateGravity'] += body.moveProp['generateGravity']
                newBody.width += body.width
                newBody.mass += body.mass
                newBody.velocity += body.momentum

            tempColor = [0, 0, 0]
            if priorityFlag:
                tempColor = priorityBody.drawProp['color']
                for body in group:
                    self.bodies.remove(body)
            else:
                for body in group:
                    tempColor[0] += body.drawProp['color'][0] * body.width
                    tempColor[1] += body.drawProp['color'][1] * body.width
                    tempColor[2] += body.drawProp['color'][2] * body.width
                    self.bodies.remove(body)

                tempColor[0] /= sum([temp.width for temp in group])
                tempColor[1] /= sum([temp.width for temp in group])
                tempColor[2] /= sum([temp.width for temp in group])

            newBody.drawProp['color'] = tuple(tempColor)
            newBody.coor /= sum([temp.width for temp in group])
            newBody.velocity /= newBody.mass

    def drawTriangle(self, coor, theta, scale=10, color=blue):

        temp = scale / self.cam.scale.x

        a = V(cos(theta), sin(theta)) * temp + coor
        b = V(cos(2 / 3 * pi + theta), sin(2 / 3 * pi + theta)) * temp + coor
        c = V(cos(4 / 3 * pi + theta), sin(4 / 3 * pi + theta)) * temp + coor

        pg.draw.polygon(self.dis, color, [self.cam.trans(a),
                                          self.cam.trans(b),
                                          self.cam.trans(c)])

    def drawLine(self, start, end, color=blue, width=5):
        pg.draw.lines(self.dis, color, False, [self.cam.trans(start),
                                               self.cam.trans(end)], width)

    def drawPlane(self):
        xgroup = []
        ygroup = []

        xgroup.append(self.cam.pos.x)
        xgroup.append(self.cam.end.x)
        ygroup.append(self.cam.pos.y)
        ygroup.append(self.cam.end.y)

        step = 100
        while True:
            k = len(splitUp(xgroup[0], xgroup[1], step))
            if k > 20:
                step *= 2
            elif k < 6:
                step /= 2
            else:
                break

        for i in splitUp(0, -xgroup[0], step):
            c = self.cam.trans(V(-i, 0))
            pg.draw.lines(self.dis, (64, 64, 64), False, [(c[0], 0), (c[0], self.res.y)], 1)
            pg.draw.circle(self.dis, (128, 128, 128), c, 5)

        for i in splitUp(0, xgroup[1], step):
            c = self.cam.trans(V(i, 0))
            pg.draw.lines(self.dis, (64, 64, 64), False, [(c[0], 0), (c[0], self.res.y)], 1)
            pg.draw.circle(self.dis, (128, 128, 128), c, 5)

        for i in splitUp(0, -ygroup[0], step):
            c = self.cam.trans(V(0, -i))
            pg.draw.lines(self.dis, (64, 64, 64), False, [(0, c[1]), (self.res.x, c[1])], 1)
            pg.draw.circle(self.dis, (128, 128, 128), c, 5)

        for i in splitUp(0, ygroup[1], step):
            c = self.cam.trans(V(0, i))
            pg.draw.lines(self.dis, (64, 64, 64), False, [(0, c[1]), (self.res.x, c[1])], 1)
            pg.draw.circle(self.dis, (128, 128, 128), c, 5)

    def drawAxies(self):
        up = (self.cam.trans(V(0, 0))[0], 0)
        down = (self.cam.trans(V(0, 0))[0], self.res.y)
        left = (0, self.cam.trans(V(0, 0))[1])
        right = (self.res.x, self.cam.trans(V(0, 0))[1])

        pg.draw.lines(self.dis, (128, 128, 128), False, [up, down], 2)
        pg.draw.lines(self.dis, (128, 128, 128), False, [left, right], 2)

    def start(self):
        while self.run:
            self.clock.tick(self.ops)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.cam.res = self.res
                        self.cam.focus(V(0, 0))

                    if event.key == pg.K_SPACE:
                        self.pause = not self.pause

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.lClickHold = True

                    if event.button == 4 or event.button == 5:
                        before = self.lastMouseCoor
                        temp = self.cam.center
                        self.cam.focus(temp)
                        self.cam.res = self.cam.res / 1.1 if event.button == 4 else self.cam.res * 1.1
                        self.cam.focus(temp)
                        self.lastMouseCoor = self.cam.untrans(event.pos)
                        self.cam.pos += before - self.lastMouseCoor

                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.lClickHold = False

                if event.type == pg.MOUSEMOTION:
                    if self.lClickHold:
                        self.cam.pos += (V(event.pos) - V(self.lastMousePos)) / self.cam.scale * V(-1, 1)
                    self.lastMousePos = event.pos
                    self.lastMouseCoor = self.cam.untrans(event.pos)

            if self.operations % self.fps == 0:
                self.drawPlane()
                self.drawAxies()

                for i in self.bodies:
                    i.draw()

                textT = self.fontStyle.render("t = " + str(round(self.t * 10) / 10), True, yellow)
                self.dis.blit(textT, [10, 10])

                if self.pause:
                    textPause = self.fontStyle.render("Pause", True, yellow)
                    self.dis.blit(textPause, [self.res.x - 75, 10])

                try:
                    roundedCoor = [round(self.lastMouseCoor.coor[0] * 10) / 10,
                                   round(self.lastMouseCoor.coor[1] * 10) / 10]
                    textMouseCoor = self.fontStyle.render("pos = " + str(roundedCoor), True, yellow)
                    self.dis.blit(textMouseCoor, [10, 35])
                except AttributeError:
                    pass

                pg.display.update()
                self.dis.fill((0, 0, 0))

            if not self.pause:
                self.t += self.dt
                for i in self.bodies:
                    i.move()

            if self.collision:
                self.collisionFusion()

            self.operations += 1

        pg.quit()


if __name__ == '__main__':
    sim = Simulation(1280, 720)
    sim.start()
