import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
from PyQt5.QtGui import QPalette, QColor
from os import path

# this is how we would've done it before
# class MainWindow(qtw.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         # Main UI Code goes here
#         form = qtw.QWidget()
#         self.setCentralWidget(form)
#         form.setLayout(qtw.QVBoxLayout())
#         self.filename = qtw.QLineEdit()
#         self.filecontent = qtw.QTextEdit()
#         self.savebutton = qtw.QPushButton('Save', clicked = self.save)
#         form.layout().addWidget(self.filename)
#         form.layout().addWidget(self.filecontent)
#         form.layout().addWidget(self.savebutton)
#
#         # End main UI Code
#         self.show()
#
#     # the way save is now it's doing too much
#     # it not only writes, it outputs errors, and a dialog box
#     def save(self):
#         filename = self.filename.text()
#         error = ''
#         if not filename:
#             error = "Filename empty"
#         # to prevent over writing an existing file even if you want to
#         elif path.exists(filename):
#             error = f'Will not overwrite {filename}'
#         else:
#             try:
#                 with open(filename, 'w') as fh:
#                     fh.write(self.filecontent.toPlainText())
#             except Exception as e:
#                 error = f'Cannot write file: {e}'
#         if error:
#             qtw.QMessageBox.critical(None, 'Error', error)

# model should contain application data and contains logic for retriving storing and manipulating data
# since it requires no GUI stuff we just need to subclass QObject so we get access to pyqt functions
# (such as signals and slots)
class Model(qtc.QObject):
    # this error will be sent back to the view which will create the dialog box for us
    # notice how there's a complete separation of logic vs visualization
    error = qtc.pyqtSignal(str)

    def save(self, filename, content):
        error = ''
        if not filename:
            error = "Filename empty"
        # to prevent over writing an existing file even if you want to
        elif path.exists(filename):
            error = f'Will not overwrite {filename}'
        else:
            try:
                with open(filename, 'w') as fh:
                    fh.write(content)
            except Exception as e:
                error = f'Cannot write file: {e}'
        if error:
            self.error.emit(error)

# this is the view it presents the data and provides an interface for manipulating data
class View(qtw.QWidget):
    # emits a tuple of strings
    # which will be connected to the model save function in the main widget
    submitted = qtc.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.filename = qtw.QLineEdit()
        self.filecontent = qtw.QTextEdit()
        self.savebutton = qtw.QPushButton('Save', clicked = self.submit)
        self.layout().addWidget(self.filename)
        self.layout().addWidget(self.filecontent)
        self.layout().addWidget(self.savebutton)

    def submit(self):
        filename = self.filename.text()
        filecontent = self.filecontent.toPlainText()
        self.submitted.emit(filename, filecontent)

    # it'd be nice if instead of show_error it's more like show_confirmation
    # where it's an either or file saved
    def show_error(self, error):
        qtw.QMessageBox.critical(None, "Error", error)

# it is slightly more lengthy to do it this way and if you know your application will never change then there's no point
# but you almost never know that lol
# so you should do this so it could be more clean and more easily manageable
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.view = View()
        self.setCentralWidget(self.view)
        self.model = Model()
        self.view.submitted.connect(self.model.save)
        self.model.error.connect(self.view.show_error)


        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()

    sys.exit(app.exec())
