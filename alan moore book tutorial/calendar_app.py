import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
from PyQt5.QtGui import QPalette, QColor


class MainWindow(qtw.QWidget):
    events = {}
    # where each key is QDate object and the value is another dict that looks like this:
    # {
    # 'title': "Some title",
    # 'category': "String of category event"
    # 'time': QTime object or NOne if all day
    # 'detail': "String of details"
    #}
    def __init__(self):
        super().__init__()
        # Main UI Code goes here

        self.setWindowTitle("My Calendar App")
        self.resize(800, 600)

        # creating all the widgets
        self.calendar = qtw.QCalendarWidget()
        self.event_list = qtw.QListWidget()
        self.event_title = qtw.QLineEdit()
        self.event_category = qtw.QComboBox()
        self.event_time = qtw.QTimeEdit(qtc.QTime(8, 0))
        self.allday_check = qtw.QCheckBox("All Day")
        self.event_detail = qtw.QTextEdit()
        self.add_button = qtw.QPushButton("Add/Update")
        self.del_button = qtw.QPushButton("Delete")

        # adding event categories
        self.event_category.addItems(['Select Category...', 'New...', "Work", "Meeting", 'Doctor', "Family"])
        # then disable the first item, that acts as our placeholder text since there is no placeholder text option
        self.event_category.model().item(0).setEnabled(False)

        # now begin the layouts
        main_layout = qtw.QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.calendar)
        # give the calendar all the space
        self.calendar.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        # now create the right side layout which is a vertical layout
        right_layout = qtw.QVBoxLayout()
        main_layout.addLayout(right_layout)
        right_layout.addWidget(qtw.QLabel('Events on Date'))
        right_layout.addWidget(self.event_list)
        # set it so the event_list takes up as much space as possible
        self.event_list.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)

        # next is the event form which should be grouped by the group box since it's similar content
        event_form = qtw.QGroupBox("Event")
        right_layout.addWidget(event_form)
        event_form_layout = qtw.QGridLayout()
        event_form.setLayout(event_form_layout)

        # now add all the widgets to the right_layout
        # last 2 arguments are row span and column span respectively
        event_form_layout.addWidget(self.event_title, 1, 1, 1, 3)
        event_form_layout.addWidget(self.event_category, 2, 1)
        event_form_layout.addWidget(self.event_time, 2, 2)
        event_form_layout.addWidget(self.allday_check, 2, 3)
        event_form_layout.addWidget(self.event_detail, 3, 1, 1, 3)
        event_form_layout.addWidget(self.add_button, 4, 2)
        event_form_layout.addWidget(self.del_button, 4, 3)

        # FUNCTIONALITY PARTS
        # if all day is checked then you don't need to set the time ig
        # toggled sends out true false if checked or not,
        # which gets passed into setDisabled which also conveniently takes in a true false value
        self.allday_check.toggled.connect(self.event_time.setDisabled)
        # when you pick a new date it picks new events to display, it does not send any data with selectionChanged() function
        self.calendar.selectionChanged.connect(self.populate_list) # this activates when you changed dates
        # again no data is sent with this signal and activates when you pick a list item
        self.event_list.itemSelectionChanged.connect(self.populate_form)

        self.add_button.clicked.connect(self.save_event)

        self.del_button.clicked.connect(self.delete_event)

        # notice we're adding another slot to the same signal this is not a problem!
        self.event_list.itemSelectionChanged.connect(self.check_delete_btn)
        # and also to start disable the button
        self.check_delete_btn()

        self.event_category.currentTextChanged.connect(self.on_category_change)
        # End main UI Code
        self.show()

    def clear_form(self):
        self.event_title.clear()
        self.event_category.setCurrentIndex(0)
        self.event_time.setTime(qtc.QTime(8,0))
        self.allday_check.setChecked(False)
        self.event_detail.setPlainText("")


    # this will be called every time you pick a calander date to show you all the events happening that day
    def populate_list(self):
        # to unselect list items since the selected index may not exist
        # in the new list.  This line is not in the book code.
        self.event_list.setCurrentRow(-1)
        self.event_list.clear()
        self.clear_form()
        date = self.calendar.selectedDate()
        # the empty array is the default value returned if an object doesn't exist with that key
        for event in self.events.get(date, []):
            # formatting time is provided in this documentation
            # https://doc.qt.io/qt-5/qtime.html
            time = (
                # this is some interesting syntax, if event time does exist do the to string otherwise make it 'all day'
                # I don't know why you would do this it makes it hard to read and no way it's faster right?
                event['time'].toString('hh:mm A')
                if event['time']
                else 'All Day'
            )
            self.event_list.addItem(f"{time}: {event['title']}")


    # this gives you the details of an event that is selected from the events_list
    def populate_form(self):
        self.clear_form() # delete old content
        date = self.calendar.selectedDate()
        event_number = self.event_list.currentRow()
        if event_number == -1: # -1 is no selection!
            return
        print(date)
        print(event_number)
        event_data = self.events.get(date)[event_number]
        # change the category label
        self.event_category.setCurrentText(event_data['category'])
        if event_data['time'] is None:
            self.allday_check.setChecked(True)
        else:
            self.event_time.setTime(event_data['time'])
        self.event_title.setText(event_data['title'])
        self.event_detail.setPlainText(event_data['detail'])


    def save_event(self):
        # grab the respective info from each input area
        event = {
            'title': self.event_title.text(),
            'category': self.event_category.currentText(),
            'time': None if self.allday_check.isChecked() else self.event_time.time(), #if it's all day set it as none
            'detail': self.event_detail.toPlainText()
        }
        # date is our key for our dictionary
        date = self.calendar.selectedDate()
        event_list = self.events.get(date, [])
        event_number = self.event_list.currentRow() #I think it's how many itmes are already in the list
        if event_number == -1: # -1 is no selection!
            event_list.append(event)
        else:
            event_list[event_number] = event
        event_list.sort(key = lambda x: x['time'] or qtc.Qtime(0,0)) # then do a custom sort by earliest time
        self.events[date] = event_list #u pdate the dictionary
        self.populate_list() #display it

    def delete_event(self):
        date = self.calendar.selectedDate()
        row = self.event_list.currentRow()
        del(self.events[date][row])
        self.event_list.setCurrentRow(-1) # -1 is no selection!
        self.clear_form()
        self.populate_list()

    def check_delete_btn(self):
        self.del_button.setDisabled(self.event_list.currentRow() == -1) # disable it if there is nothing selected

    # simply just adds it to the list and selects it as the current event
    def add_category(self, category):
        self.event_category.addItem(category)
        self.event_category.setCurrentText(category)

    def on_category_change(self, text):
        if text == 'New...':
            # YOU NEED SELF HERE, otherwise it gets immediately deleted! I assume by some GC
            # I guess here there's an actual pointer within the main class so it can't get deleted until we kill it
            self.dialog = CategoryWindow()
            self.dialog.submitted.connect(self.add_category)
            self.event_category.setCurrentIndex(0)



class CategoryWindow(qtw.QWidget):
    # creating a new signal that will emit a string
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__(None, modal = True)
        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(qtw.QLabel("Please enter a new category name:"))
        self.category_entry = qtw.QLineEdit()
        self.layout().addWidget(self.category_entry)
        self.submit_btn = qtw.QPushButton("Submit", clicked = self.onSubmit)
        self.layout().addWidget(self.submit_btn)
        self.cancel_btn = qtw.QPushButton("Cancel", clicked = self.close)
        self.layout().addWidget(self.cancel_btn)
        self.show()

    @qtc.pyqtSlot()
    def onSubmit(self):
        # if string/input exists send it
        if self.category_entry.text():
            self.submitted.emit(self.category_entry.text())
        self.close()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, qtc.Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ToolTipText, qtc.Qt.white)
    dark_palette.setColor(QPalette.Text, qtc.Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, qtc.Qt.white)
    dark_palette.setColor(QPalette.BrightText, qtc.Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, qtc.Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, qtc.Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, qtc.Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
    app.setPalette(dark_palette)
    sys.exit(app.exec())
