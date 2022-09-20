import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python


# IMPORTANT
# EVEN though subclassing Qthread is convenient
# it creates a few problems, the thread is still attached to the main thread
# and the object itself lives in the main thread
# if we use moveToThread we can be guaranteed a seperate object and seperate thread
# tldr; it's better to use the moveToThread function then subclass Qthread
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        form = SearchForm()
        self.setCentralWidget(form)
        self.ss = SlowSearcher()
        #
        #  NOTICE
        # we have a much cleaner implementation by inheriting QThread, compared to the origina slow file seacher
        #

        # remember textChanged emits the string of the QlineEdit
        form.textChanged.connect(self.ss.set_term)
        # we want the thread to restart after a new search is given
        # start automatically runs the run method
        # DO NOT CALL RUN yourself!
        form.returnPressed.connect(self.ss.start)
        # match found also emits a string and we want to in our results
        self.ss.match_found.connect(form.add_result)
        # let's add the user update information
        self.ss.finished.connect(self.on_finished)
        self.ss.directory_changed.connect(self.on_directory_changed)

        # End main UI Code
        self.show()

    def on_finished(self):
        qtw.QMessageBox.information(self, "Complete", "Search Complete")

    def on_directory_changed(self, path):
        self.statusBar().showMessage(f'Searching in {path}')


class SearchForm(qtw.QWidget):
    textChanged = qtc.pyqtSignal(str)
    returnPressed = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        # we're basically pairing the default signals to our "custom" signals for easier manipulation
        self.search_term_inp = qtw.QLineEdit(placeholderText="Search term",
                                             textChanged=self.textChanged,
                                             returnPressed=self.returnPressed)
        self.layout().addWidget(self.search_term_inp)
        self.results = qtw.QListWidget()
        self.layout().addWidget(self.results)
        self.returnPressed.connect(self.results.clear)

    def add_result(self, result):
        self.results.addItem(result)


# all we've done here is change from a Qobject to Qthread
# and changed the do_search to run
class SlowSearcher(qtc.QThread):
    # will output the file name
    match_found = qtc.pyqtSignal(str)
    # will be emitted when we start looking through a new directory
    directory_changed = qtc.pyqtSignal(str)
    # when finished
    finished = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.term = None

    def set_term(self, term):
        self.term = term

    # this will be used to start the search
    # instead of search we rename it to run
    def run(self):
        root = qtc.QDir.rootPath()
        print(qtc.QDir.homePath())
        print(qtc.QDir("This PC"))
        print(root)
        # root = qtc.QDir("This PC").path()
        # print(root)
        # I added this extra bit but I wanted it to go through all hard drives on the computer
        storage = qtc.QStorageInfo.mountedVolumes()
        hard_drives = [drive.rootPath() for drive in storage]
        print("Hard drives available", hard_drives)
        for hard_drive in hard_drives:
            print(hard_drive)
            self._search(self.term, hard_drive)
        self.finished.emit()

    # this is a recursive method that will do the actual searching
    def _search(self, term, path):
        self.directory_changed.emit(path)
        directory = qtc.QDir(path)
        print(directory.path())
        # dot is like cd . and cd .. so it avoids an infinite loop
        directory.setFilter(directory.filter() | qtc.QDir.NoDotAndDotDot | qtc.QDir.NoSymLinks)
        for entry in directory.entryInfoList():
            if term in entry.filePath().split("/")[-1]:
                print(entry.filePath())
                self.match_found.emit(entry.filePath())
            if entry.isDir():
                self._search(term, entry.filePath())


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
