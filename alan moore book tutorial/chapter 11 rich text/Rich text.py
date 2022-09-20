import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        main = qtw.QTextBrowser()
        self.setCentralWidget(main)

        # add the styling before the HTML is loaded!
        main.document().setDefaultStyleSheet(
            'body {color: #333; font-size: 14px;} '
            'h2 {background: #CCF; color: #443;} '
            'h1 {background: #001133; color: white;}'
        )
        # important there is a difference between CSS elements you have access to
        #  and widget elements you can style
        # like the background color of the document can't be set
        # it has to be done through the widget as it's a widget property
        # important  keep in mind the document() uses CSS while the widget uses QSS
        main.setStyleSheet('background-color: #EEF')


        with open('fight_fighter2.html', 'r') as fh:
            main.insertHtml(fh.read())
        # this makes it so links are opened up in the browser instead of within the app
        # it uses QDesktopServices.openUrl() to actually do the opening btw
        main.setOpenExternalLinks(True)








        # End main UI Code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
