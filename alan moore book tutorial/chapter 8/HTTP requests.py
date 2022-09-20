import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from Poster import Poster


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        widget = qtw.QWidget(minimumWidth= 600)
        self.setCentralWidget(widget)
        widget.setLayout(qtw.QVBoxLayout())
        self.url = qtw.QLineEdit()
        self.table = qtw.QTableWidget(columnCount=2, rowCount=2)
        self.table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['key', 'value'])
        # strange but we store the file name in the button text
        self.fname = qtw.QPushButton('(No file)', clicked=self.on_file_btn)
        submit = qtw.QPushButton('Submit Post', clicked= self.submit)
        self.response = qtw.QTextEdit(readOnly=True)
        for w in (self.url, self.table, self.fname, submit, self.response):
            widget.layout().addWidget(w)

        self.poster = Poster()
        # set the text to the signal that you receive
        self.poster.replyReceived.connect(self.response.setText)


        # End main UI Code
        self.show()

    def on_file_btn(self):
        filename, accepted = qtw.QFileDialog.getOpenFileName()
        if accepted:
            self.fname.setText(filename)

    def submit(self):
        # here we just format everything for our custom make_request method on the poster class
        url = qtc.QUrl(self.url.text())
        filename = self.fname.text()
        if filename == '(No File)':
            filename = None
        data = {}
        for rownum in range(self.table.rowCount()):
            key_item = self.table.item(rownum, 0)
            # only if key exists
            key = key_item.text() if key_item else None
            if key:
                data[key] = self.table.item(rownum, 1).text()
        self.poster.make_request(url, data, filename)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
