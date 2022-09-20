import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.resize(800, 600)
        main = qtw.QWidget()
        self.setCentralWidget(main)
        main.setLayout(qtw.QVBoxLayout())
        oglw = GlWidget()
        main.layout().addWidget(oglw)

        # Animation controls
        btn_layout = qtw.QHBoxLayout()
        main.layout().addLayout(btn_layout)
        for direction in ('none', 'left', 'right', 'up', 'down'):
            button = qtw.QPushButton(
                direction,
                autoExclusive=True,
                checkable=True,
                # this is a clever way of getting the function without staticly stating the name
                clicked=getattr(oglw, f'spin_{direction}')
            )
            btn_layout.addWidget(button)
        zoom_layout = qtw.QHBoxLayout()
        main.layout().addLayout(zoom_layout)
        zoom_in = qtw.QPushButton('zoom in', clicked=oglw.zoom_in)
        zoom_layout.addWidget(zoom_in)
        zoom_out = qtw.QPushButton('zoom out', clicked=oglw.zoom_out)
        zoom_layout.addWidget(zoom_out)

        # End main UI Code
        self.show()


# you could subclass QOpenGLWindow which offers better performance
# but only if you're not gonna be using any other widgets and teh whole window is OpenGl based
class GlWidget(qtw.QOpenGLWidget):
    """A widget to display our OpenGl drawing"""

    def initializeGL(self) -> None:
        super().initializeGL()
        # this represents our context from the QOpenGlWidget which is basically our interface
        gl_context = self.context()
        # we need to get the specific version interace
        version = qtg.QOpenGLVersionProfile()
        # 2.1 version
        version.setVersion(2, 1)
        # now the API  is stored in here
        self.gl = gl_context.versionFunctions(version)

        # now let's configure open GL
        # depth testing will allow OPENGL to figure out which of the points is in the background
        # and which are in the foreground
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        # this is the function that determines whether or not a depth tested pixel will be drawn
        # the one with the lowest depth (i.e. the closest one to us) will be drawn
        self.gl.glDepthFunc(self.gl.GL_LESS)
        # this makes it so it doesn't draw the side(s) the viewer cannot see
        # which saves resources and improves performance
        self.gl.glEnable(self.gl.GL_CULL_FACE)
        # there's a lot of options you can configure look them up!

        self.program = qtg.QOpenGLShaderProgram()
        # you could do strings instead of files with addShaderFromSourceCode
        # best use is to use resource files for better error checking(?)
        # first argument is what type of shader you're adding, very important!
        self.program.addShaderFromSourceFile(qtg.QOpenGLShader.Vertex, 'vertex_shader.glsl')
        self.program.addShaderFromSourceFile(qtg.QOpenGLShader.Fragment, 'fragment_shader.glsl')
        self.program.link()
        # make sure to retrieve by the appropriate type
        # internally these just return integers which represent the object location but it doesn't matter for us
        self.vertex_location = self.program.attributeLocation("vertex")
        self.matrix_location = self.program.uniformLocation("matrix")
        self.color_location = self.program.attributeLocation('color_attr')
        # this basically represents our FoV in 2D
        self.view_matrix = qtg.QMatrix4x4()
        # we want to create a frustum which is a shape between two parallel planes?
        self.view_matrix.perspective(45,  # angle
                                     self.width() / self.height(),  # aspect ratio
                                     .1,  # near clipping plane
                                     100.0  # far clipping plane
                                     )
        # this moves it back a  via translation
        # x, y, z
        self.view_matrix.translate(0, 0, -5)

        # this is for establishing rotation
        self.rotation = [0, 0, 0, 0]  # starts at 0 for all

    def paintGL(self) -> None:
        # clears/changes the background color specified by our arguments'
        # also instead of 0 - 255, it's 0 to 1
        self.gl.glClearColor(.1, 0, .2, 1)
        # this clears out the buffers we've specified from the GPU which leads to better performance
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        # bind basically tells OpenGl that it's this program that is calling the shape draw or something?
        self.program.bind()
        # shapes are drawn via vertices
        # 0, 0, 0 is the center
        front_vertices = [
            qtg.QVector3D(0.0, 1.0, 0.0),  # Peak
            qtg.QVector3D(-1.0, 0.0, 0.0),  # Bottom left
            qtg.QVector3D(1.0, 0.0, 0.0)  # Bottom right
        ]
        # by default openGl draws in black so let's add some colors
        # remember openGl only takes 0 to 1 so we need to conver it
        face_colors = [
            qtg.QColor('red'),
            qtg.QColor('orange'),
            qtg.QColor('yellow')
        ]
        gl_colors = [self.qcolor_to_glvec(color) for color in face_colors]

        self.program.setUniformValue(self.matrix_location, self.view_matrix)
        # enable i guess just unlocks it or something
        # while set actually updates/changes things
        self.program.enableAttributeArray(self.vertex_location)
        self.program.setAttributeArray(self.vertex_location, front_vertices)
        self.program.enableAttributeArray(self.color_location)
        # every time it runs it grabs the next value in the list of colors? make sure your list is long enough!
        self.program.setAttributeArray(self.color_location, gl_colors)

        # this will send all arrays we've definied into OpenGl to draw
        # this tells it will be drawing triangle primitives?
        # also tells it to start at array item 0 and then draw 3
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, 3)
        # basically just copying the front-vertices but moving them back a little
        back_vertices = [qtg.QVector3D(x.toVector2D(), -.5) for x in front_vertices]
        # by default the closest points are drawn first?
        self.program.setAttributeArray(self.vertex_location, reversed(back_vertices))
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, 3)

        # to draw the sides of the triangle we need 4  points
        sides = [(0, 1), (1, 2), (2, 0)]
        side_vertices = list()
        for index1, index2 in sides:
            side_vertices += [
                front_vertices[index1],
                back_vertices[index1],
                back_vertices[index2],
                front_vertices[index2]
            ]

        side_colors = [qtg.QColor('blue'), qtg.QColor('purple'), qtg.QColor("cyan"), qtg.QColor("magenta")]
        # we need 12 colors sicne we have 12 vertices
        gl_colors = [self.qcolor_to_glvec(color) for color in side_colors] * 3
        # the first argument is what attribute the 2nd argumetn is being applied to
        self.program.setAttributeArray(self.color_location, gl_colors)
        self.program.setAttributeArray(self.vertex_location, side_vertices)
        # instead of drawing triangles we're doing quadrilaterals
        # but usually you should use triangles cause they're the fastest to draw
        self.gl.glDrawArrays(self.gl.GL_QUADS, 0, len(side_vertices))

        # some clean up
        self.program.disableAttributeArray(self.vertex_location)
        self.program.disableAttributeArray(self.color_location)
        # like unlock with multithreading
        self.program.release()
        # need to pass in so it knows which direction
        self.view_matrix.rotate(*self.rotation)
        # update puts in the paintGL in a loop
        self.update()

    # normalizes from 0 to 1
    def qcolor_to_glvec(self, qcolor):
        return qtg.QVector3D(qcolor.red() / 255,
                             qcolor.green() / 255,
                             qcolor.blue() / 255)


    def spin_none(self):
        self.rotation = [0, 0, 0, 0]

    def spin_left(self):
        self.rotation = [-1, 0, 1, 0]

    def spin_right(self):
        self.rotation = [1, 0, 1, 0]

    def spin_up(self):
        self.rotation = [1, 1, 0, 0]

    def spin_down(self):
        self.rotation = [-1, 1, 0, 0]

    # you could use translate but it'll be difficult with rotation
    def zoom_in(self):
        self.view_matrix.scale(1.1, 1.1, 1.1)

    def zoom_out(self):
        self.view_matrix.scale(.9, .9, .9)



if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
