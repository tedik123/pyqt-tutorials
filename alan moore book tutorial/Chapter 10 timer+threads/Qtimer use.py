import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # self.dialog = AutoCloseDialog(self, "Self destructing message",
        #                               "this message will self destruct in 10 seconds",
        #                               10)
        # self.dialog.show()

        interval_seconds = 5
        self.timer = qtc.QTimer()
        self.timer.setInterval(interval_seconds * 1000)
        self.interval_dialog = AutoCloseDialog(self, "It's time again", f"It has been {interval_seconds}"
                                                                        " since this dialog was last shown.", 2000)
        # this will keep emitting at timeout
        # singleshot only does it once but typically you'll want to use this
        self.timer.timeout.connect(self.interval_dialog.show)
        self.timer.start()

        toolbar = self.addToolBar("Tools")
        # timer start and stop removes all progress there is no pause
        toolbar.addAction("Stop Bugging Me", self.timer.stop)
        toolbar.addAction("Start Bugging Me", self.timer.start)

        self.timer2 = qtc.QTimer()
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self.update_status)
        self.timer2.start()


        # this still blocks even though it's passed to the timer
        # qtc.QTimer.singleShot(1, self.long_blocking_function)



        # End main UI Code
        self.show()

    def long_blocking_function(self):
        from time import sleep
        self.statusBar().showMessage("begining long blockingg function")
        sleep(30)
        self.statusBar().showMessage("ending long blocking function")


    def update_status(self):
        if self.timer.isActive():
            time_left = (self.timer.remainingTime()//1000) + 1
            self.statusBar().showMessage(f"Next dialog will be shown in {time_left} seconds.")
        else:
            self.statusBar().showMessage("Dialogs are off.")

class AutoCloseDialog(qtw.QDialog):
    def __init__(self, parent, title, message, timeout):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle(title)
        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(qtw.QLabel(message))
        self.timeout = timeout





    # we want to override the show method so it closes after a bit
    def show(self):
        # super().show()
        # # sleep blocks everything after it
        # # so it will definitely not work the way you want it to
        # from time import  sleep
        # sleep(self.timeout)
        # self.hide()
        super().show()
        # Qtimer adds it to the event loop without blocking like sleep does
        qtc.QTimer.singleShot(self.timeout * 1000, self.hide)




if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
