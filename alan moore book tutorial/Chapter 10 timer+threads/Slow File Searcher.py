import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        form = SearchForm()
        self.setCentralWidget(form)
        self.ss = SlowSearcher()
        # IMPORTANT you need to add the thread before any signals and slots are added
        # by adding it to a thread it won't block our main GUI!
        # to add some threads we can do this
        self.searcher_thread = qtc.QThread()
        # move the object/class to a specific thread
        self.ss.moveToThread(self.searcher_thread)
        # we want the thread to stop itself after it's finished
        self.ss.finished.connect(self.searcher_thread.quit)
        self.searcher_thread.start()

        # remember textChanged emits the string of the QlineEdit
        form.textChanged.connect(self.ss.set_term)
        form.returnPressed.connect(self.ss.do_search)
        # and then we want the thread to restart after a new search is given
        form.returnPressed.connect(self.searcher_thread.start)
        # match found also emits a string and we want to in our results
        self.ss.match_found.connect(form.add_result)

        # let's add the user update information
        self.ss.finished.connect(self.on_finished)
        self.ss.directory_changed.connect(self.on_directory_changed)

        # IMPORTANT THINGS NOT TO DO WITH THREADS
        # this will break the threading because the lambda function is apart of the main thread
        # not the ss_thread, and so search will be executed in the main thread
        # form.returnPressed.connect(lambda: self.ss.do_search() )





        # End main UI Code
        self.show()

    def on_finished(self):
        qtw.QMessageBox.information(self, "Complete", "Search Complete")

    def on_directory_changed(self, path):
        self.statusBar().showMessage(f'Searching in {path}')

    # IMPORTANT THINGS NOT TO DO WITH THREADS
    # this also will live in the main thread and break the threading
    # callbacks can't be used like this
    # you must use signals to connect to the worker thread's methods
    # tldr; use QT methods not python methods to prevent thread breaking
    # def on_return_pressed(self):
    #     self.searcher_thread.start()
    #     self.ss.do_search()

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


class SlowSearcher(qtc.QObject):
    # will output the file name
    match_found = qtc.pyqtSignal(str)
    # will be emitted when we start looking through a new directory
    directory_changed = qtc.pyqtSignal(str)
    # when finished
    finished = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.term = None

    # by adding pyqt signal it makes so it's a pure Qt object/function
    # instead of a python one
    # which will allow you to not have to worry about the order of thread creation and signal connection
    @qtc.pyqtSignal(str)
    def set_term(self, term):
        self.term = term

    @qtc.pyqtSignal()
    # this will be used to start the search
    def do_search(self):
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


    # TODO you should make it so not just contains but is actually a key word
    # or make it an option for contains or keyword
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
