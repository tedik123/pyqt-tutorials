import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
import resources

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here

        # creating the dial pad
        dialpad = qtw.QWidget()
        dialpad.setLayout(qtw.QGridLayout())
        self.setCentralWidget(dialpad)

        # don't get confused i is an index, and the enumerated object is a list of those numbers/symbols
        for i, symbol in enumerate('123456789*0#'):
            button = SoundButton(f':/dtmf/{symbol}.wav', symbol)
            # 3 column calculation for position
            row = i//3
            column = i % 3
            dialpad.layout().addWidget(button, row, column)

        # End main UI Code
        self.show()

class SoundButton(qtw.QPushButton):
    def __init__(self, wav_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wav_file = wav_file
        # create the player and give it the source, assuming a resource file is used
        # QSound effect can only play uncompressed audio!!!
        # so it's good for small soundbites like dialing a number or buttons clicked
        self.player = qtmm.QSoundEffect()
        self.player.setSource(qtc.QUrl.fromLocalFile(wav_file))
        self.clicked.connect(self.player.play)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
