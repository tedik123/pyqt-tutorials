import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BORDER_HEIGHT = 100

# TODO this could be fun to create a network game? 1v1
class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.resize(qtc.QSize(SCREEN_WIDTH, SCREEN_HEIGHT))
        # this represents our scene containing all the 2D graphics
        self.scene = Scene()
        # the view object's job is just to render the scene
        view = qtw.QGraphicsView(self.scene)
        self.setCentralWidget(view)

        # End main UI Code
        self.show()


# QGraphics has methods to add ellipses, polygons, text etc etc
# however ti doesn't draw the pixels to screen!
# it creates items of the QGraphicsItem class, which allows you to query/manipulate them
class Scene(qtw.QGraphicsScene):

    def __init__(self):
        super().__init__()
        # start by painting the scene black
        self.setBackgroundBrush(qtg.QBrush(qtg.QColor('black')))
        self.setSceneRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # beginning to place objects
        wall_brush = qtg.QBrush(qtg.QColor('blue'), qtc.Qt.Dense5Pattern)
        # creating a rectangle at the bottom of the screen
        floor = self.addRect(
            qtc.QRectF(0, SCREEN_HEIGHT - BORDER_HEIGHT, SCREEN_WIDTH, BORDER_HEIGHT), brush=wall_brush
        )
        # creating a rectanlge at the top of screen
        ceiling = self.addRect(qtc.QRectF(0, 0, SCREEN_WIDTH, BORDER_HEIGHT), brush=wall_brush)
        self.top_score = 0
        self.bottom_score = 0
        score_font = qtg.QFont('Sans', 32)
        # add text takes in a string + a font object
        self.top_score_display = self.addText(str(self.top_score), score_font)
        self.top_score_display.setPos(10, 10)
        self.bottom_score_display = self.addText(str(self.bottom_score), score_font)
        self.bottom_score_display.setPos(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60)

        # finally let's add our tanks
        self.bottom_tank = Tank('red', floor.rect().top(), Tank.BOTTOM)
        self.addItem(self.bottom_tank)
        self.top_tank = Tank('green', ceiling.rect().bottom(), Tank.TOP)
        self.addItem(self.top_tank)
        # connect the hit signals to proper score
        self.top_tank.bullet.hit.connect(self.top_score_increment)
        self.bottom_tank.bullet.hit.connect(self.bottom_score_increment)


    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        keymap = {
            qtc.Qt.Key_Right: self.bottom_tank.right,
            qtc.Qt.Key_Left: self.bottom_tank.left,
            qtc.Qt.Key_Return: self.bottom_tank.shoot,
            qtc.Qt.Key_A: self.top_tank.left,
            qtc.Qt.Key_D: self.top_tank.right,
            qtc.Qt.Key_Space: self.top_tank.shoot
        }
        # if it exists then execute
        callback = keymap.get(event.key())
        if callback:
            callback()

    def top_score_increment(self):
        self.top_score += 1
        self.top_score_display.setPlainText(str(self.top_score))

    def bottom_score_increment(self):
        self.bottom_score += 1
        self.bottom_score_display.setPlainText(str(self.bottom_score))


class Tank(qtw.QGraphicsObject):
    BOTTOM, TOP = 0, 1
    # this is an 8x8 bytes object of a tank????
    TANK_BM = b'\x18\x18\xFF\xFF\xFF\xFF\xFF\x66'

    def __init__(self, color, y_pos, side=TOP):
        super().__init__()
        self.side = side
        # a Qbitmap is a special type of Qpixmap that is monochromatic
        # by passing the size and a bytes object we can generate a simple bitmap object without
        # the need for an image file
        # pg 568 explains the logic better but tldr; you're literally drawing with the bits outline
        self.bitmap = qtg.QBitmap.fromData(qtc.QSize(8, 8), self.TANK_BM)
        # a QTransform object takes in a series of transformations then a QPixmap or QBitmap, and it will transform
        # and change it according to the parameters passed in
        transform = qtg.QTransform()
        transform.scale(4, 4)  # x4 so scales to 32, 32
        if self.side == self.TOP:  # we need to point down
            transform.rotate(180)
        self.bitmap = self.bitmap.transformed(transform)
        # by default the bitmap is all black to change it we use the PEN NOT the brush
        self.pen = qtg.QPen(qtg.QColor(color))
        if self.side == self.BOTTOM:
            y_pos -= self.bitmap.height()
        # the position of an object always indicates it's upper-left corner!!!
        self.setPos(0, y_pos)

        # using bytes to define the x coordinate values
        self.animation = qtc.QPropertyAnimation(self, b'x')
        self.animation.setStartValue(0)
        # this is so we take into account the width of the tank and so 3/4 of the tank isn't off screen
        self.animation.setEndValue(SCREEN_WIDTH - self.bitmap.width())
        self.animation.setDuration(2000)

    #   this creates a bounce?/boundary limit
        self.animation.finished.connect(self.toggle_direction)
        # start the tanks on oppposite sides of the screen
        if self.side == self.TOP:
            self.toggle_direction()
        self.animation.start()

    #   let's add a bullet
        bullet_y = (
            y_pos - self.bitmap.height()
            if self.side == self.BOTTOM
            else y_pos + self.bitmap.height()
        )
        self.bullet = Bullet(bullet_y, self.side == self.BOTTOM)

    # a property animation can be run forward or backwards
    def toggle_direction(self):
        if self.animation.direction() == qtc.QPropertyAnimation.Forward:
            self.left()
        else:
            self.right()

    # switching directions is just a manner of setting the direction property and calling start()
    def right(self):
        self.animation.setDirection(qtc.QPropertyAnimation.Forward)
        self.animation.start()

    def left(self):
        self.animation.setDirection(qtc.QPropertyAnimation.Backward)
        self.animation.start()

    def shoot(self):
        # first we need to add the bullet to scene if it's not already there
        # this returns none if the bullet is not in the scene
        if not self.bullet.scene():
            self.scene().addItem(self.bullet)
        # pass in the tanks x coordinate (built-in i believe) to the bullet
        self.bullet.shoot(self.x())

    # we need to override the paint method in order to control how the drawing will work
    def paint(self, painter: qtg.QPainter, option: 'QStyleOptionGraphicsItem', widget) -> None:
        painter.setPen(self.pen)
        # the coordinates passed to drawPixmap do not refer to coordinates of the QGraphicsScene class
        # but coordinates within the bounding rectangle of the QGraphicsObject itself
        # so to set the bounding rectangle correctly we make our own in the boundingRect function
        painter.drawPixmap(0, 0, self.bitmap)

    # this returns a bounding rectangle the same size as our pixMap
    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.bitmap.width(), self.bitmap.height())


class Bullet(qtw.QGraphicsObject):
    # this is going to be used to tell us if we hit the enemy tank
    hit = qtc.pyqtSignal()

    def __init__(self, y_pos, up= True):
        super().__init__()
        # whether the bullet is travelling up or down
        self.up = up
        # starting point of bullet
        self.y_pos = y_pos
        # create a bit of a blur to make it look more interesting
        blur = qtw.QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        # this is telling it that it's going to be applied to something with an animation
        # which optimizes for you behind the scenes
        blur.setBlurHints(qtw.QGraphicsBlurEffect.AnimationHint)
        # this sets it for the entire class so everything will be blurred!!!
        self.setGraphicsEffect(blur)

        # animation time
        # this time we're definining behavior of the ycoordinate
        self.animation = qtc.QPropertyAnimation(self, b'y')
        self.animation.setStartValue(y_pos)
        # checking whether shooting down or up
        end = 0 if up else SCREEN_HEIGHT
        self.animation.setEndValue(end)
        # it takes on second for the animation to complete
        # so it will travel from one end of the screen to the other in one second
        self.animation.setDuration(1000)

        # coordinates have signals emitted on every change built-in
        self.yChanged.connect(self.check_collision)

    # this is kinda flawed as it will "delete" the bullet mid air and reset it to shoot again
    def shoot(self, x_pos):
        self.animation.stop()
        self.setPos(x_pos, self.y_pos)
        self.animation.start()

    def check_collision(self):
        # colliding items returns a list of objects whose bounding rectangles overlap with the object calling it
        # including the floor and ceiling objects we have
        colliding_items = self.collidingItems()
        if colliding_items:
            # if it's collided with any of the scene objects such as ceiling or floor we need to remove it?
            self.scene().removeItem(self)
            # otherwise check if any of them are of a tank object
            for item in colliding_items:
                if type(item).__name__ == "Tank":
                    self.hit.emit()


    # Must be defined for collision detection
    def boundingRect(self):
        return qtc.QRectF(0, 0, 10, 10)

    # also must be defined or nothing happens
    def paint(self, painter, options, widget):
        painter.setBrush(qtg.QBrush(qtg.QColor('yellow')))
        painter.drawRect(0, 0, 10, 10)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
