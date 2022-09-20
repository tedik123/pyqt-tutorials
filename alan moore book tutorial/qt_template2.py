import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe
# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here










        # End main UI Code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
