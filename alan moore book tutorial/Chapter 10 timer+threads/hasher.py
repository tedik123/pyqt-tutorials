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
        form = HashForm()
        self.setCentralWidget(form)

        # let's add our manage
        self.manager = HashManager()
        self.manager_thread = qtc.QThread()
        # we need to move it to a seperate thread because do_hashing will block until all threads are finished otherwise

        self.manager.moveToThread(self.manager_thread)
        self.manager_thread.start()
        # notice we're using signals not a lambda function so it doesn't break the threading!!!
        form.submitted.connect(self.manager.do_hashing)

        # these lambdas don't break threading because they don't manipulate any objects within those seperate threads
        form.submitted.connect(
            lambda x, y, z: self.statusBar().showMessage(
                f'Processing files in {x} into {y} with {z} threads.'))

        self.manager.finished.connect(lambda: self.statusBar().showMessage("Finished"))

        # End main UI Code
        self.show()


class HashForm(qtw.QWidget):
    submitted = qtc.pyqtSignal(str, str, int)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QFormLayout())
        self.source_path = qtw.QPushButton(
            'Click to select...', clicked=self.on_source_click
        )
        self.layout().addRow("Source Path", self.source_path)
        self.destination_file = qtw.QPushButton(
            'Click to select...', clicked=self.on_dest_click
        )
        self.layout().addRow('Destination File', self.destination_file)
        self.threads = qtw.QSpinBox(minimum=1, maximum=7, value=2)
        self.layout().addRow("Threads", self.threads)
        submit = qtw.QPushButton('Go', clicked=self.on_submit)
        self.layout().addRow(submit)

    # we're storing the filename to the buttons text
    def on_source_click(self):
        dirname = qtw.QFileDialog.getExistingDirectory()
        if dirname:
            self.source_path.setText(dirname)

    def on_dest_click(self):
        filename, _ = qtw.QFileDialog.getSaveFileName()
        if filename:
            self.destination_file.setText(filename)

    def on_submit(self):
        self.submitted.emit(self.source_path.text(),
                            self.destination_file.text(),
                            self.threads.value()
                            )

# IMPORTANT
# since our operations are I/O bound and we use C for the hashing we are not blocked by the python GIL!

class HashRunner(qtc.QRunnable):
    file_lock = qtc.QMutex()  # this is shared by all class instances????????????

    def __init__(self, infile, outfile):
        super().__init__()
        self.infile = infile
        self.outfile = outfile
        # takes in a hashing algorithm
        self.hasher = qtc.QCryptographicHash(qtc.QCryptographicHash.Md5)
        # this basically means it will delete after it's done running
        self.setAutoDelete(True)

    def run(self):
        print(f'hashing {self.infile}')
        # this is to clear the hasher so there is no leftover data
        self.hasher.reset()
        with open(self.infile, 'rb') as fh:
            # since the hashign is done by C++ and not python it is not affected by the python GIL
            self.hasher.addData(fh.read())
        # result returns a bytes array
        hash_string = bytes(self.hasher.result().toHex()).decode('UTF-8')

        # traditionally you would use the mutex as such
        # try:
        #     self.file_lock.lock()
        #     with open(self.outfile, 'a', encoding='utf-8') as out:
        #         out.write(f'{self.infile}\t{hash_string}\n')
        # # this is to ensure that if a thread fails it will still unlock the mutex
        # finally:
        #     self.file_lock.unlock()

        # however in python we have a better way
        # it basically waits for us and locks and unlocks for us
        # so only one thread at a time can go
        with qtc.QMutexLocker(self.file_lock):
            with open(self.outfile, 'a', encoding='utf-8') as out:
                out.write(f'{self.infile},{hash_string}\n')


# we need something to manage our threads for us
# we use a qobject so we can have signals
class HashManager(qtc.QObject):
    finished = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        # rather than creating a brand-new thread pool we just grab the one that exists within every QT app
        # you may want to creat your own depending on the circumstances but this is sufficient for most things
        self.pool = qtc.QThreadPool.globalInstance()

    @qtc.pyqtSlot(str, str, int)
    def do_hashing(self, source, destination, threads):
        self.pool.setMaxThreadCount(threads)
        qdir = qtc.QDir(source)
        # we're queuing up N number of threads but only maxThreadCount will be running at any given time
        for filename in qdir.entryList(qtc.QDir.Files):  # this iterates through the files
            filepath = qdir.absoluteFilePath(filename)
            runner = HashRunner(filepath, destination)
            self.pool.start(runner)
        # there is no signal for when its' finished but waitForDone() blocks until all threads finish
        self.pool.waitForDone()
        self.finished.emit()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
