import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

#inherit QMainWindow
class MyWindow(QMainWindow):
    def __init__(self):
        # for the actual inheritance
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("TUTORIAL")
        self.initUI()

    # put in all the stuff you want in the window here
    def initUI(self):
        # here it takes in the object it should be placed in!
        self.label = QtWidgets.QLabel(self)
        self.label.setText("My Label")
        # actual location
        self.label.move(50, 50)
        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Click me")
        # connects the button to a function (no parenthesis)
        self.b1.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("You pressed the button")
        self.update()

    def update(self):
        # automatically adjusts the label to fit the text
        self.label.adjustSize()

# for making ui form into real code
# form.ui = ui file name
# test.py = output file name
# pyuic5 -x form.ui -o test.py
# def clicked():
#     print("CLICKED")

def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    # to actually show the window
    win.show()
    # for a proper close
    sys.exit(app.exec())

# withhout class use
# def window():
    # app = QApplication(sys.argv)
    # win = QMainWindow()
    # first 2 values are location on screen width height
    # second 2 values are actual application size
    # win.setGeometry(200, 200, 600, 600)
    # win.setWindowTitle("TUTORIAL")

    # here it takes in the object it should be placed in!
    # label = QtWidgets.QLabel(win)
    # label.setText("My Label")
    # # actual location
    # label.move(50, 50)
    #
    # b1 = QtWidgets.QPushButton(win)
    # b1.setText("Click me")
    # # connects the button to a function (no parenthesis)
    # b1.clicked.connect(clicked)

    # # to actually show the window
    # win.show()
    # # for a proper close
    # sys.exit(app.exec())


window()
