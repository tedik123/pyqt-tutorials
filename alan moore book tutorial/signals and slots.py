import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.setLayout(qtw.QVBoxLayout())
        # self.quitButton = qtw.QPushButton("Quit", self)
        # self.quitButton.clicked.connect(self.close)

        # alternatively you could do
        self.quitButton = qtw.QPushButton("Quit", clicked=self.close)
        self.layout().addWidget(self.quitButton)

        # you can connect a signal to any slot (method)
        self.entry1 = qtw.QLineEdit()
        self.entry2 = qtw.QLineEdit()
        self.layout().addWidget(self.entry1)
        self.layout().addWidget(self.entry2)
        # text changed sends a signal when changed and sends also the text it currently contains
        self.entry1.textChanged.connect(self.entry2.setText)
        # here it just prints the text
        self.entry2.textChanged.connect(print)

        # signals can be connected to other signals!
        # when you connect one signal to another the event and data are passed from one signal to the next
        # it is worth noting that it will crash if the function requires extra arguments, but if
        # the function requires less arguments than the extra arguments will be ignored, and
        # it will continue without crashing
        self.entry1.editingFinished.connect(lambda: print("editing finished"))
        self.entry2.returnPressed.connect(self.entry1.editingFinished)

        # End main UI Code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
