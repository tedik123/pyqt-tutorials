from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor

# packages needed for this specific script
import cv2, os, sys
import pytesseract
from PIL import Image
import glob

# Here we will get the path of the tessdata
# For 64 bit installation of tesseract OCR
language_path = "C:/Program Files/Tesseract-OCR/tessdata/"
language_path_list = glob.glob(language_path + "*.traineddata")

# print('Language Path List:', language_path_list)

language_name_list = []
# not really sure how this works, but it gets the key code name of each language in the data set
for path in language_path_list:
    # basename functions returns the file_name of the path,
    # and then you split the text by the extension by default
    base_name = os.path.basename(path)
    # print(base_name)
    base_name = os.path.splitext(base_name)[0]
    language_name_list.append(base_name)
# then sort it
language_name_list.sort()

# print('Language names list', language_name_list)
font_list = []
font = 2
for font in range(110):
    font += 2
    font_list.append(str(font))


# print("Font list", font_list)


# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # slow way to load UI
        self.ui = loadUi("ocr_gui.ui", self)

        self.image = None
        # you can access things through the load
        self.open_image_button.clicked.connect(self.open)

        # IMPORTANT FOR AREA SELECTION
        self.rubberBand = qtw.QRubberBand(qtw.QRubberBand.Rectangle, self)
        self.photo_label_placeholder.setMouseTracking(True)
        self.photo_label_placeholder.installEventFilter(self)
        self.photo_label_placeholder.setAlignment(qtc.Qt.AlignTop)

        # set default language to english
        self.language = 'eng'
        # set combobox to the list of langauges we have
        self.language_combo_box.addItems(language_name_list)
        self.language_combo_box.currentIndexChanged['QString'].connect(self.update_now)
        # set it at the index of whatever selected language, in this case 'eng'
        self.language_combo_box.setCurrentIndex(language_name_list.index(self.language))

        self.font_size = '20'
        self.text = ''
        self.font_size_combo_box.addItems(font_list)
        self.font_size_combo_box.currentIndexChanged["QString"].connect(self.update_font_size)
        self.font_size_combo_box.setCurrentIndex(font_list.index(self.font_size))

        self.text_edit_area.setFontPointSize(int(self.font_size))
        self.setAcceptDrops(True)

        # End main UI Code
        self.show()

    def open(self):
        filename = qtw.QFileDialog.getOpenFileName(self, "Select File")
        self.image = cv2.imread(str(filename[0]))
        frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # not really sure what this does, but I think it sets by width, height, something idk
        # and image formatting for colors
        image = qtg.QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], qtg.QImage.Format_RGB888)
        # replace the label in the blue with the image
        self.photo_label_placeholder.setPixmap(qtg.QPixmap.fromImage(image))

    def update_now(self, value):
        self.language = value
        print("language selected", self.language)

    def update_font_size(self, value):
        self.font_size = value
        # update the font size
        self.text_edit_area.setFontPointSize(int(self.font_size))
        # and update what's already written if anything to the new font size by copying it and rewriting it
        self.text_edit_area.setText(str(self.text))

    def image_to_text(self, crop_cvimage):
        # get cropped image and convert it to gray scale
        gray = cv2.cvtColor(crop_cvimage, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 1)
        crop = Image.fromarray(gray)
        text = pytesseract.image_to_string(crop, lang=self.language)
        print('image text result', text)
        return text

    def eventFilter(self, source, event):
        width, height = 0, 0
        # when the mouse button is pressed in the image we will get the top left corner of the rectangular region
        if event.type() == qtc.QEvent.MouseButtonPress and source is self.photo_label_placeholder:
            # once the drag is happening within the picture placholder then we show the rectangle
            self.org = self.mapFromGlobal(event.globalPos())
            # get the top left corner?
            self.left_top = event.pos()
            self.rubberBand.setGeometry(qtc.QRect(self.org, qtc.QSize()))
            self.rubberBand.show()

        # here we'll start showing the rectangle while the mosue moves
        elif event.type() == qtc.QEvent.MouseMove and source is self.photo_label_placeholder:
            if self.rubberBand.isVisible():
                self.rubberBand.setGeometry(qtc.QRect(self.org, self.mapFromGlobal(event.globalPos())).normalized())


        # when it's released we'll grab all the data we need from the rectangle and then crop it from the image
        elif event.type() == qtc.QEvent.MouseButtonRelease and source is self.photo_label_placeholder:
            if self.rubberBand.isVisible():
                self.rubberBand.hide()
                rect = self.rubberBand.geometry()
                self.x1 = self.left_top.x()
                self.y1 = self.left_top.y()
                width = rect.width()
                height = rect.height()
                self.x2 = self.x1 + width
                self.y2 = self.y1 + height
            if width >= 10 and height >= 10 and self.image is not None:
                self.crop = self.image[self.y1:self.y2, self.x1:self.x2]
                cv2.imwrite('cropped.png', self.crop)
                self.text = self.image_to_text(self.crop)
                self.text_edit_area.setText(str(self.text))
            else:
                self.rubberBand.hide()
        else:
            return 0
        # i Don't understand why we are returning this
        return qtw.QWidget.eventFilter(self, source, event)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, qtc.Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, qtc.Qt.black)
    palette.setColor(QPalette.ToolTipText, qtc.Qt.white)
    palette.setColor(QPalette.Text, qtc.Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, qtc.Qt.white)
    palette.setColor(QPalette.BrightText, qtc.Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, qtc.Qt.black)
    app.setPalette(palette)

    # execution
    mw = MainWindow()
    sys.exit(app.exec())
