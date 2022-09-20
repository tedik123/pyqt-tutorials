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
        self.setWindowTitle('Qt Meme Generator')
        self.max_size = qtc.QSize(800, 600)
        # since we don't immediately receive an image we'll use a black fill as our placeholder
        # takes in a size and an image format
        self.image = qtg.QImage(self.max_size, qtg.QImage.Format_ARGB32)
        self.image.fill(qtg.QColor('black'))

        mainwidget = qtw.QWidget()
        self.setCentralWidget(mainwidget)
        mainwidget.setLayout(qtw.QHBoxLayout())
        # we have to convert Qimages to pixmaps before being able to display them
        self.image_display = qtw.QLabel(pixmap=qtg.QPixmap(self.image))
        mainwidget.layout().addWidget(self.image_display)
        # let's add our meme form to input the image and content
        self.form = MemeEditForm()
        mainwidget.layout().addWidget(self.form)
        self.form.changed.connect(self.build_image)

        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction('Save Image', self.save_image)

        # End main UI Code
        self.show()

    def save_image(self):
        save_file, _ = qtw.QFileDialog.getSaveFileName(None, "Save your image", qtc.QDir.currentPath(),
                                                       "PNG Images (*.png)")
        # image takes in a file path and file type
        if save_file:
            self.image.save(save_file, "PNG")

    def build_image(self, data):
        if not data.get('image_source'):
            self.image.fill(qtg.QColor('black'))
        else:
            self.image.load(data.get('image_source'))
            if not (self.max_size - self.image.size()).isValid():
                # isValid returns false if either dimension is negative
                self.image = self.image.scaled(self.max_size, qtc.Qt.KeepAspectRatio)
        # the object to be painted must be a subclass of QPaintDevice
        painter = qtg.QPainter(self.image)
        font_px = qtg.QFontInfo(data['text_font']).pixelSize()
        # the drawn rectangle needs to fit around the font pixel size + the padding provided
        top_px = (data['top_bg_height'] * font_px) + data['bg_padding']
        # coordinates to draw start at upper left corner and to bottom right coordinates
        top_block_rect = qtc.QRect(
            0, 0, self.image.width(), top_px
        )
        # we need to calculate from the bottom of the image so we subtract
        bottom_px = (self.image.height() - data['bg_padding'] - (data['bottom_bg_height'] * font_px))
        bottom_block_rect = qtc.QRect(0, bottom_px, self.image.width(), self.image.height())

        # now the actual drawing part
        painter.setBrush(qtg.QBrush(data['bg_color']))
        # painter of course has plenty of other shapes you can draw
        painter.drawRect(top_block_rect)
        painter.drawRect(bottom_block_rect)

        # to draw text we need this
        # before we draw we need to define a pen color
        painter.setPen(data['text_color'])
        # as well as font object for the pen to use
        painter.setFont(data['text_font'])
        flags = qtc.Qt.AlignHCenter | qtc.Qt.TextWordWrap
        # we could define a bounding box for which to draw in but here we're using alignment and the whole image
        # is our text placeholder
        painter.drawText(self.image.rect(), flags | qtc.Qt.AlignTop, data['top_text'])
        painter.drawText(self.image.rect(), flags | qtc.Qt.AlignBottom, data['bottom_text'])

        self.image_display.setPixmap(qtg.QPixmap(self.image))


class MemeEditForm(qtw.QWidget):
    # instead of submitted we'll use changed
    # this will allow us to update the form in real time
    changed = qtc.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QFormLayout())
        self.image_source = ImageFileButton(changed=self.on_change)
        self.layout().addRow('Image File', self.image_source)

        #       this is our text editing portion for the memes
        self.top_text = qtw.QPlainTextEdit(textChanged=self.on_change)
        self.bottom_text = qtw.QPlainTextEdit(textChanged=self.on_change)
        self.layout().addRow("Top Text", self.top_text)
        self.layout().addRow("Bottom Text", self.bottom_text)
        self.text_color = ColorButton('white', changed=self.on_change)
        self.layout().addRow("Text Color", self.text_color)
        self.text_font = FontButton('Impact', 32, changed=self.on_change)
        self.layout().addRow("Text Font", self.text_font)

        #       this is to draw background boxes for the text
        # you can add how opaque it is to make it easier
        self.text_bg_color = ColorButton('black', changed=self.on_change)
        self.layout().addRow("Text Background", self.text_bg_color)
        self.top_bg_height = qtw.QSpinBox(minimum=0, maximum=32, valueChanged=self.on_change, suffix=' line(s)')
        self.layout().addRow('Top BG height', self.top_bg_height)
        self.bottom_bg_height = qtw.QSpinBox(minimum=0, maximum=32, valueChanged=self.on_change, suffix=' line(s)')
        self.layout().addRow("Bottom BG height", self.bottom_bg_height)
        self.bg_padding = qtw.QSpinBox(
            minimum=0, maximum=10, valueChanged=self.on_change, suffix=' px'
        )
        self.layout().addRow("Padding", self.bg_padding)

    def get_data(self):
        return {
            'image_source': self.image_source._filename,
            'top_text': self.top_text.toPlainText(),
            'bottom_text': self.bottom_text.toPlainText(),
            'text_color': self.text_color._color,
            'text_font': self.text_font._font,
            'bg_color': self.text_bg_color._color,
            'top_bg_height': self.top_bg_height.value(),
            'bottom_bg_height': self.bottom_bg_height.value(),
            'bg_padding': self.bg_padding.value()
        }

    # notice we're returning the execution not the function!
    def on_change(self):
        self.changed.emit(self.get_data())


class ColorButton(qtw.QPushButton):
    changed = qtc.pyqtSignal()

    def __init__(self, default_color, changed=None):
        super().__init__()
        self.set_color(qtg.QColor(default_color))
        self.clicked.connect(self.on_click)
        if changed:
            self.changed.connect(changed)

    # this generates a pixmap of that color you provided
    def set_color(self, color):
        self._color = color
        pixmap = qtg.QPixmap(32, 32)
        pixmap.fill(self._color)
        self.setIcon(qtg.QIcon(pixmap))

    def on_click(self):
        color = qtw.QColorDialog.getColor(self._color)
        if color:
            self.set_color(color)
            self.changed.emit()


class FontButton(qtw.QPushButton):
    changed = qtc.pyqtSignal()

    def __init__(self, default_family, default_size, changed=None):
        super().__init__()
        self.set_font(qtg.QFont(default_family, default_size))
        self.clicked.connect(self.on_click)
        if changed:
            self.changed.connect(changed)

    def set_font(self, font):
        self._font = font
        self.setFont(font)
        self.setText(f'{font.family()} {font.pointSize()}')

    def on_click(self):
        font, accepted = qtw.QFontDialog.getFont(self._font)
        if accepted:
            self.set_font(font)
            self.changed.emit()


class ImageFileButton(qtw.QPushButton):
    changed = qtc.pyqtSignal()

    def __init__(self, changed=None):
        super().__init__("Click to select...")
        self._filename = None
        self.clicked.connect(self.on_click)
        if changed:
            self.changed.connect(changed)

    def on_click(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(
            None, "Select an image to use", qtc.QDir.currentPath(), "Images (*.png *.xpm *.jpg)"
        )
        if filename:
            self._filename = filename
            self.setText(qtc.QFileInfo(filename).fileName())
            self.changed.emit()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
