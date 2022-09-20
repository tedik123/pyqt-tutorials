import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from qt_ui_files.calendar_ui import Ui_MainWindow
from qt_ui_files.category_window_ui import Ui_CategoryWindow


# this is a weird way of importing the files in my opinion i don't like it!
# but it is faster than reading in the UI file yourself tbf
# so once you have a stable build you should probably switch to this method for the increased speed
class MainWindow(qtw.QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.setupUi(self)

        self.event_category.model().item(0).setEnabled(False)
        self.calendar.selectionChanged.connect(self.populate_list)
        # FUNCTIONALITY PARTS
        # if all day is checked then you don't need to set the time ig
        # toggled sends out true false if checked or not,
        # which gets passed into setDisabled which also conveniently takes in a true false value
        self.allday_check.toggled.connect(self.event_time.setDisabled)
        # when you pick a new date it picks new events to display, it does not send any data with selectionChanged() function
        self.calendar.selectionChanged.connect(self.populate_list)  # this activates when you changed dates
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


        # End main UI Code
        self.show()

    def clear_form(self):
        self.event_title.clear()
        self.event_category.setCurrentIndex(0)
        self.event_time.setTime(qtc.QTime(8, 0))
        self.allday_check.setChecked(False)
        self.event_detail.setPlainText("")

        # this will be called every time you pick a calander date to show you all the events happening that day

    def populate_list(self):
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
        self.clear_form()  # delete old content
        date = self.calendar.selectedDate()
        event_number = self.event_list.currentRow()
        if event_number == -1:  # -1 is no selection!
            return
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
            'time': None if self.allday_check.isChecked() else self.event_time.time(),  # if it's all day set it as none
            'detail': self.event_detail.toPlainText()
        }
        # date is our key for our dictionary
        date = self.calendar.selectedDate()
        event_list = self.events.get(date, [])
        event_number = self.event_list.currentRow()  # I think it's how many itmes are already in the list
        if event_number == -1:  # -1 is no selection!
            event_list.append(event)
        else:
            event_list[event_number] = event
        event_list.sort(key=lambda x: x['time'] or qtc.Qtime(0, 0))  # then do a custom sort by earliest time
        self.events[date] = event_list  # u pdate the dictionary
        self.populate_list()  # display it

    def delete_event(self):
        date = self.calendar.selectedDate()
        row = self.event_list.currentRow()
        del (self.events[date][row])
        self.event_list.setCurrentRow(-1)  # -1 is no selection!
        self.clear_form()
        self.populate_list()

    def check_delete_btn(self):
        self.del_button.setDisabled(self.event_list.currentRow() == -1)  # disable it if there is nothing selected

        # simply just adds it to the list and selects it as the current event

    def add_category(self, category):
        self.event_category.addItem(category)
        self.event_category.setCurrentText(category)

    def on_category_change(self, text):
        if text == 'New':
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
        self.ui = Ui_CategoryWindow()
        self.ui.setupUi(self)
        # IMPORTANT notice we never connected the submit button to on submit take a look at the on submit method
        self.show()

    # @qtc.pyqtSlot()
    # def onSubmit(self):
    #     # if string/input exists send it
    #     if self.category_entry.text():
    #         self.submitted.emit(self.category_entry.text())
    #     self.close()

    # IMPORTANT since we used a pyqtslot and named on_submit_btn where submit_btn is our object name (NOT variable name)
    # it automatically knows to connect the two and does so at run time!
    # honestly a bit confusing and hard to follow so i don't know if it's actually worth doing
    @qtc.pyqtSlot()
    def on_submit_btn_clicked(self):
        # if string/input exists send it
        if self.ui.category_entry.text():
            self.submitted.emit(self.ui.category_entry.text())
        self.close()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
