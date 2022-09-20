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
        rows = 3
        columns = 3
        soundboard = qtw.QWidget()
        soundboard.setLayout(qtw.QGridLayout())
        self.setCentralWidget(soundboard)
        for c in range(columns):
            for r in range(rows):
                sw = SoundWidget()
                soundboard.layout().addWidget(sw, c, r)
        # End main UI Code
        self.show()

class SoundWidget(qtw.QWidget):

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QGridLayout())
        self.label = qtw.QLabel("No file loaded")
        self.layout().addWidget(self.label, 0, 0, 1, 2)
        self.play_button = PlayButton()
        self.layout().addWidget(self.play_button, 3,0, 1, 2)
        self.player = qtmm.QMediaPlayer()
        self.play_button.clicked.connect(self.on_playbutton)
        self.player.stateChanged.connect(self.play_button.on_state_change)
        self.file_button = qtw.QPushButton('Load File', clicked=self.get_file)
        self.layout().addWidget(self.file_button)
        # a slider takes in inputs between a min and max value
        self.position = qtw.QSlider(minimum=0, orientation = qtc.Qt.Horizontal)
        self.layout().addWidget(self.position, 1, 0, 1, 2)
    #   connect the slider and player
    #   as the player plays the slider moves along with the audio length
    #   the qMedia player reports its position in integers representing the number of ms from the start
        self.player.positionChanged.connect(self.position.setSliderPosition)
        # if a new file is selected it changes the maximum of the slider
        # this is only emitted if a file is changed
        self.player.durationChanged.connect(self.position.setMaximum)
        # if you move the slider update the player appropriately
        # important we want to use sliderMoved not valueChanged because valueChanged would send a signal every ms
        # as the video plays and cause a feedback loop and crash
        self.position.sliderMoved.connect(self.player.setPosition)
        self.loop_cb = qtw.QCheckBox('Loop?', stateChanged=self.on_loop_cb)
        self.layout().addWidget(self.loop_cb, 2, 0)
        # for a more traditional volume slider feeling use this
        # https://doc.qt.io/qt-5/qaudio.html#convertVolume
        self.volume = qtw.QSlider(minimum=0, maximum=100, sliderPosition=75,
                                  orientation = qtc.Qt.Horizontal,
                                  sliderMoved = self.player.setVolume)
        self.layout().addWidget(self.volume, 2, 1)

    #   AUDIO RECORDING WIDGET
        self.recorder = qtmm.QAudioRecorder()
        # let's edit the recorder settings a bit
        # keep in mind it will NOT throw an error if you type in the wrong audio input it just won't work
        self.recorder.setAudioInput('default:')
        sample_path = qtc.QDir.home().filePath('sample1')
        # requires a QUrl object not a file string
        # if it can't find it will default to a platform specific location
        self.recorder.setOutputLocation(qtc.QUrl.fromLocalFile(sample_path))
        # used for WAV files, takes in a string, it will error if it's not valid at least
        self.recorder.setContainerFormat('audio/x-wav')
        # to set codec, sample rate, and quality requires a QAudioEncoderSettings Object
        settings = qtmm.QAudioEncoderSettings()
        # not all codecs are compatible with every container type! it may not tell you even when running
        # do your reaseach
        settings.setCodec('audio/pcm')
        settings.setSampleRate(192000)
        settings.setQuality(qtmm.QMultimedia.VeryHighQuality)

        self.record_button = RecordButton()
        self.recorder.stateChanged.connect(self.record_button.on_state_changed)
        self.layout().addWidget(self.record_button, 4, 1)
        self.record_button.clicked.connect(self.on_recordbutton)

    def on_playbutton(self):
        # check the state, if its' playing then stop
        # otherwise it's stopped then play it
        if self.player.state() == qtmm.QMediaPlayer.PlayingState:
            self.player.stop()
        else:
            self.player.play()

    def get_file(self):
        # NOTE: we're getting QUrl object not a file string wtih getOpenFileUrl
        # QT likes QUrl objects a lot more and saves us conversions to do later
        # fn, _ = qtw.QFileDialog.getOpenFileUrl(self,
        #                                        "Select File",
        #                                        qtc.QDir.currentPath(),
        #                                        "Audio Files (*.wav *.flac *.mp3 *.ogg *.aiff);; All Files (*)")
        fn, _ = qtw.QFileDialog.getOpenFileUrl(
            self,
            "Select File",
            # interesting you need to wrap this in a qtc.QUrl function otherwise no likey
            qtc.QUrl(qtc.QDir.currentPath()),
            "Audio files (*.wav *.flac *.mp3 *.ogg *.aiff);; All files (*)"
        )
        # # if the file is found, set it to the button using setFile function
        if fn:
            self.set_file(fn)

    # # original no loop
    # def set_file(self, url):
    #     # unfortunately we need to wrap the url in this QMedia object
    #     # so it can actually be played
    #     content = qtmm.QMediaContent(url)
    #     # then pass the content object to the player and add the name and you're set
    #     self.player.setMedia(content)
    #     self.label.setText(url.fileName())

    def set_file(self, url):
        if url.scheme() == '':
            url.setScheme('file')
        self.label.setText(url.fileName())
        content = qtmm.QMediaContent(url)
        # here we can create a playlist which of course allows us to queue multiple audio samples
        # but also allows to loop over the list infinitely
        self.playlist = qtmm.QMediaPlaylist()
        self.playlist.addMedia(content)
        # you must set the index or it will wait until the index changes
        self.playlist.setCurrentIndex(1)
        self.player.setPlaylist(self.playlist)
        self.loop_cb.setChecked(False)

    def on_loop_cb(self, state):
        # if checked set the playback mode to loop, otherwise just once
        # there's other keys like sequential, loop (repeat the entire playlist), random
        if state == qtc.Qt.Checked:
            self.playlist.setPlaybackMode(qtmm.QMediaPlaylist.CurrentItemInLoop)
        else:
            self.playlist.setPlaybackMode(qtmm.QMediaPlaylist.CurrentItemOnce)


    def on_recordbutton(self):
        # if it's recording stop it
        if self.recorder.state() == qtmm.QMediaRecorder.RecordingState:
            self.recorder.stop()
            # once it stops get the location of where you recorded it
            # which returns a QUrl
            url = self.recorder.actualLocation()
            self.set_file(url)
        else:
            self.recorder.record()





class PlayButton(qtw.QPushButton):
    play_stylesheet = 'background-color: lightgreen; color: black;'
    stop_stylesheet = 'background-color: darkred; color: white;'

    def __init__(self):
        super().__init__('Play')
        self.setFont(qtg.QFont('Sans', 32, qtg.QFont.Bold))
        self.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding )
        self.setStyleSheet(self.play_stylesheet)

    # state change passes in the new state
    def on_state_change(self, state):
        if state == qtmm.QMediaPlayer.PlayingState:
            self.setStyleSheet(self.stop_stylesheet)
            self.setText('Stop')
        else:
            self.setStyleSheet(self.play_stylesheet)
            self.setText('Play')


class RecordButton(qtw.QPushButton):
    record_stylesheet = 'background-color: black; color: white;'
    stop_stylesheet = 'background-color: darkred; color: white;'

    def __init__(self):
        super().__init__('Record')

    def on_state_changed(self, state):
        if state == qtmm.QAudioRecorder.RecordingState:
            self.setStyleSheet(self.stop_stylesheet)
            self.setText('Stop')
        else:
            self.setStyleSheet(self.record_stylesheet)
            self.setText('Record')

# from PyQt5.QtCore import *
# from PyQt5.QtMultimedia import *

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    # app = QCoreApplication([])
    # r = QAudioRecorder()
    # print("Inputs: ", r.audioInputs())
    # print("Codecs: ", r.supportedAudioCodecs())
    # print("Sample rates: ", r.supportedAudioSampleRates())
    # print("Containers: ", r.supportedContainers())

    sys.exit(app.exec())


#Inputs:  ['Wave Link MicrophoneFX (2- Elgato Wave:3)', 'Wave Link Monitor (2- Elgato Wave:3)', 'Microphone (2- High Definition Audio Device)', 'Mic In (2- Elgato Wave:3)', 'Microphone (HD Pro Webcam C920)', 'Microphone (HyperX Cloud Flight S Chat)', 'Microphone (NVIDIA Broadcast)', 'Wave Link Stream (2- Elgato Wave:3)', 'Wave Link MicrophoneFX (2- Elgato Wave:3)', 'Microphone (HyperX Cloud Flight S Chat)', 'Mic In (2- Elgato Wave:3)', 'Wave Link Monitor (2- Elgato Wave:3)', 'Microphone (2- High Definition Audio Device)', 'Microphone (NVIDIA Broadcast)', 'Wave Link Stream (2- Elgato Wave:3)', 'Microphone (HD Pro Webcam C920)']
# Codecs:  ['audio/pcm']
# Sample rates:  ([8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 192000], False)
# Containers:  ['audio/x-wav', 'audio/x-raw']