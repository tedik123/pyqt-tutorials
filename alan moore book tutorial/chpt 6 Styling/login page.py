import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
from PyQt5.QtGui import QPalette, QColor
from os import path

# this is our custom XML resource file we created, well the python script version at least
import resources


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fight Fighter Game Lobby")
        cx_form = qtw.QWidget()
        self.setCentralWidget(cx_form)
        cx_form.setLayout(qtw.QFormLayout())
        heading = qtw.QLabel("Fight Fighter!")
        cx_form.layout().addRow(heading)

        inputs = {
            'Server': qtw.QLineEdit(),
            'Name': qtw.QLineEdit(),
            'Password': qtw.QLineEdit(echoMode=qtw.QLineEdit.Password),
            'Team': qtw.QComboBox(),
            'Ready': qtw.QCheckBox("Check when ready")
        }
        teams = ("Crimson Sharks", "Shadow Hawks", "Night Terrors", "Blue Crew")
        inputs['Team'].addItems(teams)
        for label, widget in inputs.items():
            cx_form.layout().addRow(label, widget)

        # self.submit = qtw.QPushButton("Connect", clicked=lambda: qtw.QMessageBox.information(None, 'Connecting...',
        #                                                                                      "Prepare for battle!"))
        # using our fancy color button class
        self.submit =ColorButton("Connect", clicked=lambda: qtw.QMessageBox.information(None, 'Connecting...',
                                                                                             "Prepare for battle!"))
        # self.cancel = qtw.QPushButton('Cancel', clicked=self.close)
        self.cancel = ColorButton('Cancel', clicked=self.close)

        cx_form.layout().addRow(self.submit, self.cancel)

        # STYLING
        #                       a string indicating font family, point size, and a qtg.QFont Enum for weight
        #                                                                   in this case bold
        heading_font = qtg.QFont("Impact", 32,
                                 qtg.QFont.Bold)  # the final optional argument is whether it's italicized or not
        # stretch property is also set with an enum (look them up for extra options)
        heading_font.setStretch(qtg.QFont.ExtraExpanded)
        # set the font to the widget
        heading.setFont(heading_font)

        # you can also creat a custom font object
        label_font = qtg.QFont()
        label_font.setFamily('Impact')
        label_font.setPointSize(14)
        label_font.setWeight(qtg.QFont.DemiBold)
        label_font.setStyle(qtg.QFont.StyleItalic)

        # fonts trickle down from parent widget to children
        # so you could just set it to the cx_form
        for inp in inputs.values():
            cx_form.layout().labelForField(inp).setFont(label_font)


        # not all fonts are in all OS's so QFont objects ignore it if they can't find it and use the system default
        # it produces a soft error (doesn't crash)
        # button_font = qtg.QFont("Totally NonExistant Font Family XYZ", 15.2233)
        button_font = qtg.QFont("Totally NonExistant Font Family XYZ", 15)
        print(f'Font is {button_font.family()}')  # will actually print out that's using the fake font, but it's NOT!
        # to figure out if it's using the font
        actual_font = qtg.QFontInfo(button_font).family()
        print(f'Actual font is {actual_font}')

        # you could give QT a font hint so it can guess what type of font it should use if it can't find anything
        # style hint suggests the general quality to fall back to which is the fantasy font category
        button_font.setStyleHint(qtg.QFont.Fantasy)
        # strategy is technical preferences such as antialias, OpenGl compatitbility, and whether the
        # size will be matched exactly or rounded to the nearest non-scaled size
        # more can be found online
        button_font.setStyleStrategy(qtg.QFont.PreferAntialias | qtg.QFont.PreferQuality)

        actual_font = qtg.QFontInfo(button_font)
        print(f'Actual font is {actual_font.family()}')
        print(f'Actual font size is {actual_font.pointSize()}')

        self.submit.setFont(button_font)
        self.cancel.setFont(button_font)

        # IMAGES
        logo = qtg.QPixmap('logo.png')
        # you could set it to a QLabel or QButton like this
        # FYI labels can either display a pixmap or a string NOT both
        heading.setPixmap(logo)
        # pixmap is optimized for display so you can't really edit much besides transformations
        # Qimages you can play with more
        # we restrict the size to about 400
        if logo.width() > 400:
            logo = logo.scaledToWidth(400, qtc.Qt.SmoothTransformation)

        # here we create a simple color mesh stand in
        go_pixmap = qtg.QPixmap(qtc.QSize(32, 32))
        stop_pixmap = qtg.QPixmap(qtc.QSize(32, 32))
        go_pixmap.fill(qtg.QColor('green'))
        stop_pixmap.fill(qtg.QColor('red'))
        # icons can be used for basically any Qt.object by the way!
        connect_icon = qtg.QIcon()
        # when it's active it'll be the green icon
        connect_icon.addPixmap(go_pixmap, qtg.QIcon.Active)
        # when it's disabled it will be the red icon
        connect_icon.addPixmap(stop_pixmap, qtg.QIcon.Disabled)
        # now for the basic logic of setting the icon to change with the state
        self.submit.setIcon(connect_icon)
        self.submit.setDisabled(True)
        # once the text changes and the text is not empty then we changed the icon
        # notice it automatically knows to switch states based on the lambda function (or any function provided)
        inputs['Server'].textChanged.connect(lambda x: self.submit.setDisabled(x == ''))

        # IMPORTANT we have a problem, images passed into these constructors are thought to be absolute
        # so if you run the file from somewhere else thennnnnnn you're fucked it won't be able to find it
        # fortunately Qt resource files handle that type of logic for you
        # the syntax is ":/prefix/file_name_or_alias.extension"
        inputs['Team'].setItemIcon(
            0, qtg.QIcon(':/teams/crimson_sharks.png')
        )
        inputs['Team'].setItemIcon(
            1, qtg.QIcon(':/teams/shadow_hawks.png')
        )
        inputs['Team'].setItemIcon(
            2, qtg.QIcon(':/teams/night_terrors.png')
        )
        inputs['Team'].setItemIcon(
            3, qtg.QIcon(':/teams/blue_crew.png')
        )

        # AS FOR FONTS
        # first we must add it to the database, after an insertion it returns a unique id (key)
        libsans_id = qtg.QFontDatabase.addApplicationFont(':/fonts/LiberationSans-Regular.ttf')
        print(libsans_id)
        # we can then use the ID number to find the font's family string
        family = qtg.QFontDatabase.applicationFontFamilies(libsans_id)[0]
        print(family)
        libsans = qtg.QFont(family, 10)
        inputs['Team'].setFont(libsans)

        # COLORS
        # color is a literal color value
        # brush combines color with a style, such as pattern, gradient, or texture
        # color role represents the way the widget uses the color such as in the foreground, background, or for borders
        # color group refers to the the interaction state of the widget; it can be:
        # normal, active, disabled, or inactive

        # this as the name implies grabs the instance of the global app
        app = qtw.QApplication.instance()
        # it is best practice to grab the pallete directly from the app
        # instead of making your own
        palette = app.palette()
        # again we use Enums to identify what object/part to color
        palette.setColor(qtg.QPalette.Button,
                         qtg.QColor('#333'))
        palette.setColor(qtg.QPalette.ButtonText,
                         qtg.QColor('#3F3'))
        # to override the color of a particular button state we need to pass the state
        palette.setColor(qtg.QPalette.Disabled,
                         qtg.QPalette.ButtonText,
                         qtg.QColor('#3F3'))
        palette.setColor(qtg.QPalette.Disabled,
                         qtg.QPalette.Button,
                         qtg.QColor('#888'))
        # to apply the pallete we must assign it to the widget
        self.submit.setPalette(palette)
        self.cancel.setPalette(palette)

        # for fancier stuff that isn't fill or solid colors
        # we can use brushes
        # which let us fill colors based on patterns, textures (image-based), gradients
        # dense2pattern is one of 15 patterns available
        dotted_brush = qtg.QBrush(qtg.QColor('white'), qtc.Qt.Dense2Pattern)

        # brushes are cool and all but most modern styles use gradients
        # so let's make one
        # first for it to be used for a brush we must create a gradient object
        # it takes in starting coordinates which in this case is top-left (0, 0)
        # and end coordinates which is the bottom-right (width, height)
        gradient = qtg.QLinearGradient(0, 0, self.width(), self.height())
        # the number is the % to start at and it steps at th next call
        # so the first one is from 0 - 50%
        gradient.setColorAt(0, qtg.QColor('navy'))
        gradient.setColorAt(.5, qtg.QColor('darkred'))
        gradient.setColorAt(1, qtg.QColor('orange'))
        # then we pass the gradient to the brush
        gradient_brush = qtg.QBrush(gradient)
        window_palette = app.palette()
        window_palette.setBrush(qtg.QPalette.Window, gradient_brush)
        window_palette.setBrush(qtg.QPalette.Active, qtg.QPalette.WindowText, dotted_brush)
        self.setPalette(window_palette)

        # ALTERNATIVELY
        # Color object manipulation and styling can be difficult
        # QT also provides a CSS duplicate -> QSS
        stylesheet = """
            QMainWindow {
                background-color: black;
            }
            QWidget {
                background-color: transparent;
                color: #3F3;
            }
            QLineEdit, QComboBox, QCheckBox {
                font-size: 16pt;
            }
        """
        # self.setStyleSheet(stylesheet)
        # what you might notice is that the stylesheet trickles down from parent to children
        # and everything is difficult to distinguish from each other due to the merged colors/properties
        # so let's override some of the forgotten properties
        # specific styles override generic inherited styles
        # double colons let you specify a subelement of a widget
        # in this case we do that to check indicator and change it's color from red to green
        stylesheet+= """
            QPushButton {
                background-color: #333;
            }
            
            QCheckBox::indicator:unchecked {
                border: 1px solid silver;
                background-color: darkred;    
            }
            QCheckBox::indicator:checked {
                border: 1px solid silver;
                background-color: #3F3;   
            }
        """
        # self.setStyleSheet(stylesheet)

        # if you want to restrict change to a particular class only and not any subclasses you can simply add .
        stylesheet += """
            .QWidget {
                background:url(tile.png);
            }
            .QLabel {
                color: orange;
            }
            
        """
        # self.setStyleSheet(stylesheet)

        # if you want to specify a specific object you must first set the object name and then call it in the stylesheet
        self.submit.setObjectName('SubmitButton')
        # then you reference the specific object name with #
        # also it's very peculiar about semicolons!
        stylesheet += """
            #SubmitButton:disabled {
                background-color: #888;
                color: darkred;
            }
        """
        # self.setStyleSheet(stylesheet)

        # you can also set the style sheet of specific widgets
        for inp in ("Server", 'Name', 'Password'):
            inp_widget = inputs[inp]
            inp_widget.setStyleSheet('background-color: black')

        # although stylesheets are very familiar they're a basic version of CSS
        # they are also slower than the other ways and have unpredictable and different behavior compared to CSS

        #############
        # Animation #
        #############
        # QPropertyAnimation takes in a widget to be animated, and a BYTES object NOT a string indicating what property
        # to animate
        self.heading_animation = qtc.QPropertyAnimation(heading, b'maximumSize')
        self.heading_animation.setStartValue(qtc.QSize(10, logo.height()))
        self.heading_animation.setEndValue(qtc.QSize(485, logo.height()))
        self.heading_animation.setDuration(2000) # default is 250 ms
        # then we need to tell the animation to start
        # self.heading_animation.start()
        # for animations to work thety must be Qobject subclass
        # this includes all widgets but not all QTClasses like QPalette
        # the property to be animated must be a Qt property, it can't be a python property
        # the property must have a read-and-write accessor (getters and settors)
        # the property must be one of the following types
        # int, float, QLine, QLineF, QPoint, QPointF, QSizeF, QSize, QRect, QRectF or QColor
        # unfortunately we can't animate things like a color property of a widget
        # because colors are a property of the palette
        # we can hack it by creating a class for it

        # now that we changed our buttons to a ColorButton class we can manipulate the animations
        # changing the color property
        self.text_color_animation = qtc.QPropertyAnimation(self.submit, b'color')
        self.text_color_animation.setStartValue(qtg.QColor("#FFF"))
        self.text_color_animation.setEndValue(qtg.QColor('#888'))
        self.text_color_animation.setLoopCount(-1) # repeat forever
        # this particular curve slows the rate of change at the beginning and end
        self.text_color_animation.setEasingCurve(qtc.QEasingCurve.InOutQuad)
        self.text_color_animation.setDuration(2000)
        # self.text_color_animation.start()


        # self.bg_color_animation = qtc.QPropertyAnimation(self.submit, b'backgroundColor')
        # self.bg_color_animation.setStartValue(qtg.QColor('#000'))
        # # key value sets a color in the middle of the animation
        # # so it goes from black to red to black again
        # self.bg_color_animation.setKeyValueAt(.5, qtg.QColor('darkred'))
        # self.bg_color_animation.setEndValue(qtg.QColor('#000'))
        # self.bg_color_animation.setLoopCount(-1)
        # self.bg_color_animation.setDuration(1500)
        # self.bg_color_animation.start()
        # this just doesn't work for some reason
        self.bg_color_animation = qtc.QPropertyAnimation(
            self.submit, b'backgroundColor')
        self.bg_color_animation.setStartValue(qtg.QColor('#000'))
        self.bg_color_animation.setKeyValueAt(0.5, qtg.QColor('darkred'))
        self.bg_color_animation.setEndValue(qtg.QColor('#000'))
        self.bg_color_animation.setLoopCount(-1)
        self.bg_color_animation.setDuration(1500)
        # self.bg_color_animation.start()
        # this plays all animations in the list at the same time
        self.button_animations = qtc.QParallelAnimationGroup()
        self.button_animations.addAnimation(self.text_color_animation)
        self.button_animations.addAnimation(self.bg_color_animation)
        # self.button_animations.start()

        # if you want to start sequentially you can do this
        self.all_animations = qtc.QSequentialAnimationGroup()
        self.all_animations.addAnimation(self.heading_animation)
        self.all_animations.addAnimation(self.button_animations)
        self.all_animations.start()

        # by grouping animations you can create a more complex series of animations
        # and you have more control/easier control
        # End code here
        self.show()


class ColorButton(qtw.QPushButton):
    def _color(self):
        return self.palette().color(qtg.QPalette.ButtonText)

    def _setColor(self, qcolor):
        palette = self.palette()
        palette.setColor(qtg.QPalette.ButtonText, qcolor)
        self.setPalette(palette)

    # the first is the data type required by the property, and the next two arguments are the getter/setter methods
    color = qtc.pyqtProperty(qtg.QColor, _color, _setColor)

    # alternative to the above you can use this decorator
    @qtc.pyqtProperty(qtg.QColor)
    def backgroundColor(self):
        return self.palette().color(qtg.QPalette.Button)

    @backgroundColor.setter
    def backgroundColor(self, qcolor):
        palette = self.palette()
        palette.setColor(qtg.QPalette.Button, qcolor)
        self.setPalette(palette)

# we can do some style overrides to get certain features we want without having to create a brand new style
class StyleOverrides(qtw.QProxyStyle):

    def drawItemText(self, painter, rect, flags, pal, enabled, text, textRole):
        """Force uppercase in all text"""
        text = text.upper()
        super().drawItemText(painter, rect, flags, pal, enabled, text, textRole)

#    if we want to modify specific elements of a widget we need to find the enum constant that it belongs to
# primitiveElement: includes fundamental, non-interactive GUI elements such as frames or backgruonds
# controlElement: includes interactive elements such as buttons or tabs
# ComplexControl: which includes complex interactive elements such as combo boxes and sliders
# each of these is draw by a different QStyle method

# so if we want to edit the border of our qline edits it would be in PE_FrameLineEdit
    def drawPrimitive(self, element, option: 'QStyleOption', painter, widget):
        """Outline QLineEdits in Green"""
        self.green_pen = qtg.QPen(qtg.QColor('green'))
        self.green_pen.setWidth(4)
        if element == qtw.QStyle.PE_FrameLineEdit:
            painter.setPen(self.green_pen)
            painter.drawRoundedRect(widget.rect(), 10, 10)
        else:
            super().drawPrimitive(element, option, painter, widget)


# the takeway is that you should use either QSS or styles and palettes but not both
# overriding styles gives you basically infinite control but it is much more difficult/time consuming
# mixing them can cause unpredictable behavior
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    proxy_style = StyleOverrides()
    app.setStyle(proxy_style)
    mw = MainWindow()

    mw.resize(510, 200)
    sys.exit(app.exec())
