import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtNetwork as qtn

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.cw = ChatWindow()
        self.setCentralWidget(self.cw)

        # End main UI Code
        self.show()


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class ChatWindow(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.setLayout(qtw.QGridLayout())
        self.message_view = qtw.QTextEdit(readOnly=True)
        self.layout().addWidget(self.message_view, 1, 1, 1, 2)
        self.message_entry = qtw.QLineEdit()
        self.layout().addWidget(self.message_entry, 2, 1)
        self.send_btn = qtw.QPushButton("Send", clicked = self.send)
        self.layout().addWidget(self.send_btn, 2, 2)

        # End main UI Code
        # self.show()


    def write_message(self, username, message):
        self.message_view.append(f'<b>{username}: </b> {message} <br>')

    def send(self):
        message = self.message_entry.text().strip()
        if message:
            self.submitted.emit(message)
            self.message_entry.clear()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
