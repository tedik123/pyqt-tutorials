import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QWidget):

    def __init__(self):
        """MainWindow constructor.
        This widget will be our main window.
        We'll define all the UI components in here.
        """
        super().__init__()
        # Main UI code goes here
        self.setLayout(qtw.QVBoxLayout())
        data = [
            'Hamburger', 'Cheeseburger',
            'Chicken Nuggets', 'Hot Dog', 'Fish Sandwich'
        ]

        listwidget = qtw.QListWidget()
        listwidget.addItems(data)
        combobox = qtw.QComboBox()
        combobox.addItems(data)
        self.layout().addWidget(listwidget)
        self.layout().addWidget(combobox)


        # notice that even tho you're changing listwidget content the combobox does not change
        # that's cause each object stores their own copy
        for i in range(listwidget.count()):
            item = listwidget.item(i)
            item.setFlags(item.flags() | qtc.Qt.ItemIsEditable)

        self.layout().addWidget(qtw.QLabel("Below it's editable properly."))
        # what are we doing here?
        # Qlist is a combination of a model and a view
        # the QstringListMOdel is the model
        # the QlistView is the view
        # remember model handles the logic
        model_list = qtc.QStringListModel(data)
        listview = qtw.QListView()
        listview.setModel(model_list)
        # we then pass the model that the combobox should use
        # and now they have a shared object (with the same exact data)
        # so if it changes for one it changes for both
        model_combobox = qtw.QComboBox()
        model_combobox.setModel(model_list)
        self.layout().addWidget(listview)
        self.layout().addWidget(model_combobox)

        # End main UI code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    sys.exit(app.exec())
