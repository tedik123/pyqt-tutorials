import sys
# this is for being able to load the UI file as is instead of translating it directly to python
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QSizePolicy
from PyQt5 import QtCore
# load csv module
import csv

user_info = {}


def write_dict(user_dict):
    # open file for writing, "w" is writing
    w = csv.writer(open("user_data.csv", "w"))
    # loop over dictionary keys and values
    for key, val in user_dict.items():
        # write every key and value to file
        w.writerow([key, val])


def read_in_data():
    dict_from_csv = {}
    with open('user_data.csv', mode='r') as inp:
        reader = csv.reader(inp)
        dict_from_csv = {rows[0]: rows[1] for rows in reader}
    return dict_from_csv


# inherits QDialog
class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        # loading the UI file
        loadUi("DesignStuff/FullAppTutorial/welcomescreen.ui", self)
        # bind the button
        self.login.clicked.connect(self.gotologin)
        self.create_account.clicked.connect(self.gotocreate)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #Important this paired with the eventFilter allows for resizing!!!
        self.installEventFilter(self)

    def gotologin(self):
        login = LogInScreen()
        # adding it to the display stack
        widget.addWidget(login)
        # then need to select the added screen
        # since it's the latest go from current_index to the next one up
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        # then need to select the added screen
        # since it's the latest go from current_index to the next one up
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            print( 'Inside event Filter')
        return super().eventFilter(obj, event)

class CreateAccScreen(QDialog):
    global user_info

    def __init__(self):
        super(CreateAccScreen, self).__init__()
        # loading the UI file
        loadUi("DesignStuff/FullAppTutorial/createacc.ui", self)
        # again block the visual of the password field
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_pass_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup_button.clicked.connect(self.signup)

    def signup(self):
        # handle passwords
        user = self.email_field.text()
        password = self.password_field.text()
        confirm_password = self.confirm_pass_field.text()
        if len(user) == 0 or len(password) == 0 or len(confirm_password) == 0:
            self.error_field.setText("Cannot leave any field empty!")
            self.error_field.adjustSize()
        else:
            if password != confirm_password:
                self.error_field.setText("Passwords do not match!")
                self.error_field.adjustSize()
            else:
                # add user data to save
                user_info[user] = password
                write_dict(user_info)
                print(user_info)
                fillprofile = FillProfileScreen()
                widget.addWidget(fillprofile)
                widget.setCurrentIndex(widget.currentIndex() + 1)


class FillProfileScreen(QDialog):
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        # loading the UI file
        loadUi("DesignStuff/FullAppTutorial/profile.ui", self)


class LogInScreen(QDialog):
    global user_info

    def __init__(self):
        super(LogInScreen, self).__init__()
        loadUi("DesignStuff/FullAppTutorial/login.ui", self)
        # to make it so the password field is dots not characters
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button.clicked.connect(self.loginfunction)

    def loginfunction(self):
        global user_info
        # get the text from the text field
        user = self.email_field.text()
        password = self.password_field.text()
        if len(user) == 0 or len(password) == 0:
            self.error_field.setText("Username or password field cannot be empty!")
            self.error_field.adjustSize()
        else:
            saved_password = user_info.get(user, "NaN")
            print('saved_password', saved_password)
            if saved_password != "NaN" and saved_password == password:
                print("Successful login")
                self.error_field.setText("")
            else:
                self.error_field.setText("Username or password is incorrect!")
                self.error_field.adjustSize()
                print("fsdf")


if __name__ == '__main__':
    # for "user data" stuff
    user_info = read_in_data()
    print(user_info)
    # actually run the app
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    # this is for being able to switch between screens IMPORTANT for later!
    widget = QStackedWidget()
    # add welcome widget to stacked widgets
    widget.addWidget(welcome)
    # set the height width to make sure the welcome screen fits
    # widget.setFixedHeight(800)
    # widget.setFixedWidth(1200)

    # to actually show
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
