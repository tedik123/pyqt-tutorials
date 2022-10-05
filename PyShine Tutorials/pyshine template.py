import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor






# print("Font list", font_list)


# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # slow way to load UI
        self.ui = loadUi("ui.ui", self)



        # End main UI Code
        self.show()




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
