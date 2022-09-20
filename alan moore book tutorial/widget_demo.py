import sys
import typing

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


# the validator class must return a tuple that contains state, the string, and the position
# this is not documented!!!!

class IPv4Validator(qtg.QValidator):
    #    the states of the input are qtg.QtValidator.Acceptable, Intermediate or Invalid

    # def __init__(self):
    #     pass

    def validate(self, a0: str, a1: int) -> typing.Tuple['QValidator.State', str, int]:
        octets = a0.split('.')
        #       if there's more than 4 segments can't be ipv4
        if len(octets) > 4:
            state = qtg.QValidator.Invalid
        elif not all([x.isdigit() for x in octets if x != '']):
            state = qtg.QValidator.Invalid
        # all values between dots must be in the range of 0 - 255
        elif not all([0 <= int(x) <= 255 for x in octets if x != '']):
            state = qtg.QValidator.Invalid
        # if it hasn't failed checks yet then it's still in progress
        elif len(octets) < 4:
            state = qtg.QValidator.Intermediate
        elif any([x == '' for x in octets]):
            state = qtg.QValidator.Intermediate
        # if it hasn't failed yet then it has passed all the tests
        else:
            state = qtg.QValidator.Acceptable
        return state, a0, a1


class ChoiceSpinBox(qtw.QSpinBox):
    """A spin box for selecting choices"""

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super().__init__(
            *args,
            maximum=len(self.choices) - 1,
            minimum=0,
            **kwargs
        )

    # converts string to index
    def valueFromText(self, text: str) -> int:
        return self.choices.index(text)

    # converts in index to string
    def textFromValue(self, v: int) -> str:
        try:
            return self.choices[v]
        except IndexError:
            return '!Error!'

    # check if it's a valid choice
    def validate(self, string: str, pos: int):
        if string in self.choices:
            state = qtg.QValidator.Acceptable
        elif any([v.startswith(string) for v in self.choices]):
            state = qtg.QValidator.Intermediate
        else:
            state = qtg.QValidator.Invalid
        return state, string, pos


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        # here you pass in the parent, it's good to do so beacuse then when parent gets destroyed so will the child
        # important most objects that get passed in to Qt objects are turned in QT objects
        # so here the string is transformed into a QString under the hood
        # not all conversions happen in the background!!!
        subwidget = qtw.QWidget(self, toolTip="This is a tooltip")
        # here the parent is passed as a second argument
        label = qtw.QLabel("Hello Widget!", self)
        label.setFixedSize(150, 40)  # literally just sets it fixed
        layout.addWidget(label)

        # line_edit = qtw.QLineEdit("SOMETHING", self)
        line_edit = qtw.QLineEdit('default value', placeholderText='0.0.0.0', clearButtonEnabled=True, maxLength=20)
        line_edit.setMinimumSize(100, 15)
        line_edit.setMaximumSize(500, 20)
        # passing in our custom validator
        line_edit.setText('0.0.0.0')
        line_edit.setValidator(IPv4Validator())
        # layout.addWidget(line_edit)

        # button = qtw.QPushButton("Push me", self).move(50, 50)
        # you could also write the sequence as qtg.QKeySequence(qtc.Qt.CTRL + qtc.Qt.Key_P)
        button = qtw.QPushButton("Push me", self, checkable=True, checked=True, shortcut=qtg.QKeySequence('Ctrl+p'))
        layout.addWidget(button)
        # combo box is a drop down list
        combobox = qtw.QComboBox(self)
        combobox.move(50, 100)
        # to add items you can use addItem() or insertItem()
        # the first value is the displayed value, the second value is what's passed back to whatever is watching it
        # so if you chose lemon it'll return 1
        # if you don't need a second property you can just pass in a list of values with addItems() (with an S)
        combobox.addItem("lemon", 1)
        combobox.addItem("Peach", "Oh I like peaches!")
        combobox.addItem("Strawberry", qtw.QWidget)
        # insert puts it in the specific position provided by argument 1
        combobox.insertItem(1, "Radish", 2)
        comboboxList = qtw.QComboBox(self)
        comboboxList.move(50, 150)
        comboboxList.addItems(["poop", "soup", "tears", "fears"])
        # this allows you to add things to a list from the GUI
        comboboxEditable = qtw.QComboBox(self, editable=True, insertPolicy=qtw.QComboBox.InsertAtTop)
        comboboxEditable.move(50, 200)

        spinBox = qtw.QSpinBox(self, value=12, maximum=100, minimum=10, prefix='$', suffix=' + Tax', singleStep=5)
        # spinBox.move(120, 200)
        spinBox.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Preferred)
        # for floats/doubles
        doublespinBox = qtw.QDoubleSpinBox(self, value=12, maximum=100, minimum=10, prefix='$', suffix=' + Tax',
                                           singleStep=.25)
        doublespinBox.move(120, 250)

        # kind of like a spin box but for calander/dates
        # you could also pass in a python date time object qt can use that
        # and if you're gonna be passing around the time you should use python's datetime
        datetimebox = qtw.QDateTimeEdit(self, date=qtc.QDate.currentDate(),
                                        time=qtc.QTime(12, 30), calendarPopup=True,
                                        maximumDate=qtc.QDate(2030, 1, 1),
                                        maximumTime=qtc.QTime(17, 0),
                                        displayFormat="yyyy-MM-dd HH:mm A")
        datetimebox.move(100, 300)
        datetimebox.sizePolicy()
        # line wrap mode is whether to use columns or pixels
        # the linewrapcolumnorwidth is at what column or pixel it will begin to wrap
        textedit = qtw.QTextEdit(self, acceptRichText=True, lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                                 lineWrapColumnOrWidth=25, placeholderText="Enter your text here")
        textedit.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)
        # alternatively you can override the size hint and size it with a lambda function
        textedit.sizeHint = lambda: qtc.QSize(500, 500)
        sublayout = qtw.QHBoxLayout()
        layout.addLayout(sublayout)
        sublayout.addWidget(combobox)
        sublayout.addWidget(comboboxList)
        sublayout.addWidget(comboboxEditable)
        # layout.addWidget(textedit)
        # qstacked widget is similar but it has no built in way of switching between widgets
        # useful for building your own custom tab widget/page switching mechanism
        tab_widget = qtw.QTabWidget(movable=True, tabPosition=qtw.QTabWidget.West, tabShape=qtw.QTabWidget.Triangular)
        layout.addWidget(tab_widget)
        container = qtw.QWidget(self)
        grid_layout = qtw.QGridLayout()
        # layout.addLayout(grid_layout)
        container.setLayout(grid_layout)
        grid_layout.addWidget(spinBox, 0, 0)
        grid_layout.addWidget(datetimebox, 0, 1)
        grid_layout.addWidget(doublespinBox)
        # argument order: widget, row number (vertical coordinate), column number(horizontal coordinatee), row span (optional), column span (optional)
        # important if you want each widget to stretch independently, in a column or row,use nested box layouts!
        grid_layout.addWidget(textedit, 1, 0, 2, 2)
        # with this you can type in the value as well
        ratingbox = ChoiceSpinBox(['bad', 'average', 'good', 'awesome'], self)
        grid_layout.addWidget(ratingbox)

        # then add the container to the tab widget
        tab_widget.addTab(container, 'Tab the first')
        tab_widget.addTab(subwidget, 'Tab the second')
        # can also use insert tab

        form_layout = qtw.QFormLayout()
        layout.addLayout(form_layout)
        form_layout.addRow("Item 1", qtw.QLineEdit(self))
        form_layout.addRow("Item 2", qtw.QLineEdit(self))
        form_layout.addRow(qtw.QLabel('<b>This is a label</b>'), self)
        form_layout.addRow("IP", line_edit)
        stretch_layout = qtw.QHBoxLayout()
        layout.addLayout(stretch_layout)
        # the second parameter allows to set the stretching
        # strech only works within layout classes
        # FYI stretch doesn't override the size hint or size policies, so the long widget might not necessarily be twice as long as the short widget
        stretch_layout.addWidget(qtw.QLineEdit("Short"), 1)
        stretch_layout.addWidget(qtw.QLineEdit("Long"), 2)

        # groupboxes are used for grouping things with similar content
        # flat removes the frame, checkable is whether to "show" (disabled) or not
        groupbox = qtw.QGroupBox('Buttons', checkable=True, checked=True, alignment=qtc.Qt.AlignHCenter, flat=True)
        groupbox.setLayout(qtw.QHBoxLayout())
        groupbox.layout().addWidget(qtw.QPushButton("OK"))
        groupbox.layout().addWidget(qtw.QPushButton("Cancel"))
        layout.addWidget(groupbox)

        # if there is no parent show() makes it a top-level window.
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setMinimumSize(500, 500)
    sys.exit(app.exec())
