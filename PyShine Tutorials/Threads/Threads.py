import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor

import time


# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # slow way to load UI
        self.ui = loadUi("thread.ui", self)
        self.resize(888, 200)

        self.thread = {}
        self.thread_button_1.clicked.connect(self.start_worker_1)
        self.thread_button_2.clicked.connect(self.start_worker_2)
        self.thread_button_3.clicked.connect(self.start_worker_3)

        self.stop_thread_button_1.clicked.connect(self.stop_worker_1)
        self.stop_thread_button_2.clicked.connect(self.stop_worker_2)
        self.stop_thread_button_3.clicked.connect(self.stop_worker_3)
        # End main UI Code
        self.show()

    def start_worker_1(self):
        self.thread[1] = ThreadClass(parent=None, index=1)
        self.thread[1].start()
        self.thread[1].any_signal.connect(self.my_function)
        self.thread_button_1.setEnabled(False)

    def start_worker_2(self):
        self.thread[2] = ThreadClass(parent=None, index=2)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.my_function)
        self.thread_button_2.setEnabled(False)

    def start_worker_3(self):
        self.thread[3] = ThreadClass(parent=None, index=3)
        self.thread[3].start()
        self.thread[3].any_signal.connect(self.my_function)
        self.thread_button_3.setEnabled(False)

    def stop_worker_1(self):
        self.thread[1].stop()
        self.thread_button_1.setEnabled(True)

    def stop_worker_2(self):
        self.thread[2].stop()
        self.thread_button_2.setEnabled(True)

    def stop_worker_3(self):
        self.thread[3].stop()
        self.thread_button_3.setEnabled(True)

    def my_function(self, counter):
        cnt = counter
        index = self.sender().index
        if index == 1:
            self.thread_bar_1.setValue(cnt)
        if index == 2:
            self.thread_bar_2.setValue(cnt)
        if index == 3:
            self.thread_bar_3.setValue(cnt)


class ThreadClass(qtc.QThread):
    any_signal = qtc.pyqtSignal(int)

    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        print('Starting thread....', self.index)
        cnt = 0
        while True:
            cnt += 1
            if cnt == 99: cnt = 0
            time.sleep(.01)
            self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print("Stopping thread...", self.index)
        self.terminate()


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
