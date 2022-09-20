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

        self.label = qtw.QLabel("Click to change this text")
        self.change = qtw.QPushButton("Change", clicked=self.onChange)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.change)

        # End main UI Code
        self.show()

    # when the button is clicked open a formwindow
    # then when you submit the submit singal will be emitted (implemented in the form window class)
    # you pass in the setText function which accepts the string emitted and updates the label
    @qtc.pyqtSlot(bool)  # completely optional type decorater where can you also pass in an object type to enforce type safety
    # improves performance marginally with type decorators, useful if a method would only be used as a slot and nothign else
    def onChange(self):
        self.formwindow = FormWindow()
        # original connection
        # self.formwindow.submitted.connect(self.label.setText)
        # new connection
        self.formwindow.submitted[str].connect(self.onSubmittedStr)
        self.formwindow.submitted[int, str].connect(self.onSubmittedIntStr)
        self.formwindow.show()

    # as the name implies these are the slots that activate on the signal change
    @qtc.pyqtSlot(str)
    def onSubmittedStr(self, string):
        self.label.setText(string)

    @qtc.pyqtSlot(int, str)
    def onSubmittedIntStr(self, integer, string):
        text = f'The string {string} becomes the number {integer}'
        self.label.setText(text)

class FormWindow(qtw.QWidget):
    # IMPORTANT custom signals
    # you make it by calling qtc.pyqtSignal and passing in the data type it will emit
    # originally we made it like this
    # submitted = qtc.pyqtSignal(str)

    #  two lists are passed in and each is a list of potential arguments it could emit
    # so one sends out only a string, another sends out an int and a string
    submitted = qtc.pyqtSignal([str], [int, str])

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.edit = qtw.QLineEdit()
        self.submit = qtw.QPushButton("Submit", clicked=self.onSubmit)

        self.layout().addWidget(self.edit)
        self.layout().addWidget(self.submit)

    # original with just a str
    # def onSubmit(self):
    #     # we created the base signal
    #     # now here we emit it with the text (string object) taken from the .text() function
    #     self.submitted.emit(self.edit.text())
    #     # after emitting the signal close the application
    #     self.close()


    # this is the function that actually emits the signal
    def onSubmit(self):
        # first check if it can be translated into a number
        # if it is then emit a number version and a string versio
        if self.edit.text().isdigit():
            text = self.edit.text()
            # you select with which signature to emit with the [] syntax
            self.submitted[int, str].emit(int(text), text)
        # otherwise it just emits the string version
        else:
            self.submitted[str].emit(self.edit.text())
        # after emitting the signal close the application
        self.close()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
