from PyQt5 import QtWidgets

# The QApplication class manages the GUI application's control flow and main settings
app = QtWidgets.QApplication([])

window = QtWidgets.QWidget(windowTitle= "Hello Qt")
#optionally just do QWidget.setTitle("Hello QT")

# then actually show
window.show()
# this starts the event loop and keeps track of user interactions with GUI
# the app and widget automatically get connected under the hood
app.exec_()