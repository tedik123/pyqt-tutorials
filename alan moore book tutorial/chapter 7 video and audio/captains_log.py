import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtMultimediaWidgets as qtmmw

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(qtc.QSize(800, 600))
        # Main UI Code goes here
        base_widget = qtw.QWidget()
        base_widget.setLayout(qtw.QHBoxLayout())
        notebook = qtw.QTabWidget()
        base_widget.layout().addWidget(notebook)
        self.file_list = qtw.QListWidget()
        base_widget.layout().addWidget(self.file_list)
        self.setCentralWidget(base_widget)

        toolbar = self.addToolBar("Transport")
        record_act = toolbar.addAction("Rec")
        stop_act = toolbar.addAction("Stop")
        play_act = toolbar.addAction("Play")
        pause_act = toolbar.addAction("Pause")

        # we want to open/look at a file where we have our captain logs only
        # this is a cross platform way of handling that
        # current is a path object, currentPath is a string!
        self.video_dir = qtc.QDir.current()
        print(self.video_dir)
        if not self.video_dir.cd('captains_log'):
            qtc.QDir.current().mkdir('captains_log')
            self.video_dir.cd('captains_log')
        # self.refresh_video_list()
        #
        #
        # self.player = qtmm.QMediaPlayer()
        # # you need a video widget to be able to play vids
        # self.video_widget = qtmmw.QVideoWidget()
        # # and then attach the player to the widget
        # self.player.setVideoOutput(self.video_widget)
        #
        # notebook.addTab(self.video_widget, "Play")
        # play_act.triggered.connect(self.player.play)
        # pause_act.triggered.connect(self.player.pause)
        # stop_act.triggered.connect(self.player.stop)
        # # this switches to the play tab whenever the play button is clicked
        # play_act.triggered.connect(lambda : notebook.setCurrentWidget(self.video_widget))
        # self.file_list.itemDoubleClicked.connect(self.on_file_selected)
        # self.file_list.itemDoubleClicked.connect(lambda: notebook.setCurrentWidget(self.video_widget))

            # Read the files in the directory
        self.refresh_video_list()
        ############
        # Playback #
        ############
        # setup the player and video widget
        self.player = qtmm.QMediaPlayer()

        self.video_widget = qtmmw.QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        notebook.addTab(self.video_widget, "Play")
        # connect the transport
        play_act.triggered.connect(self.player.play)
        pause_act.triggered.connect(self.player.pause)
        stop_act.triggered.connect(self.player.stop)
        play_act.triggered.connect(
            lambda: notebook.setCurrentWidget(self.video_widget))
        # connect file list
        self.file_list.itemDoubleClicked.connect(
            self.on_file_selected)
        self.file_list.itemDoubleClicked.connect(
            lambda: notebook.setCurrentWidget(self.video_widget))

        self.camera = self.camera_check()
        # block the rest of the code from running if no camera
        if not self.camera:
            self.show()
            return

        # we need to set the capture mode, be it pictures or video
        self.camera.setCaptureMode(qtmm.QCamera.CaptureVideo)
        # that's nice and all but we should be able to see what the camera is recording right?
        # that's where QCameraViewFinder comes in handy
        self.cvf = qtmmw.QCameraViewfinder()
        # attach the camera recording to the Qcameraviewfinder
        self.camera.setViewfinder(self.cvf)
        notebook.addTab(self.cvf, 'Record')
        # then we need to enable the camera
        self.camera.start()

        # first let's create a widget that can record our video input
        # you need to pass in the camera so it knows what to record
        self.recorder = qtmm.QMediaRecorder(self.camera)

        # let's set some settings for the camera recording
        # keep in mind it will throw an error if the settings are not possible
        # IMPORTANT you can query with that video test script to see what formats are available
        # and change the settings from there or just accept the defaults QT gives you
        settings = self.recorder.videoSettings()
        settings.setResolution(1920, 1080)
        settings.setFrameRate(24.0)
        settings.setQuality(qtmm.QMultimedia.VeryHighQuality)
        self.recorder.setVideoSettings(settings)

        record_act.triggered.connect(self.record)
        record_act.triggered.connect(lambda : notebook.setCurrentWidget(self.cvf))
        pause_act.triggered.connect(self.recorder.pause)
        # why not use a lambda to combine them? should you not?
        stop_act.triggered.connect(self.recorder.stop)
        stop_act.triggered.connect(self.refresh_video_list)
        # End main UI Code
        self.show()

    # def refresh_video_list(self):
    #     self.file_list.clear()
    #     video_files = self.video_dir.entryList(
    #         # type of files to read
    #         ["*.ogg", "*.avi", "*.mov", ".mp4", "*.mkv"],
    #         # only show if they're readable
    #         qtc.QDir.Files | qtc.QDir.Readable
    #     )
    #     for fn in sorted(video_files):
    #         self.file_list.addItem(fn)
    # idk why this runs but the above doesn't
    def refresh_video_list(self):
        self.file_list.clear()
        video_files = self.video_dir.entryList(
            ["*.ogg", "*.avi", "*.mov", "*.mp4", "*.mkv"],
            qtc.QDir.Files | qtc.QDir.Readable
        )
        for fn in sorted(video_files):
            self.file_list.addItem(fn)

    # takes in a QListWidgetItem
    def on_file_selected(self, item):
        print("here")
        fn = item.text()
        url = qtc.QUrl.fromLocalFile(self.video_dir.filePath(fn))
        print(url)
        content = qtmm.QMediaContent(url)
        # attach the file to the player and then autoplay
        self.player.setMedia(content)
        self.player.play()

    def camera_check(self):
        # check if there are any cameras
        cameras = qtmm.QCameraInfo.availableCameras()
        if not cameras:
            qtw.QMessageBox.critical(self, "No cameras", "No cameras were found, recording disabled.")
        else:
            # returns a list of avaialble cameras and just pick the first one
            return qtmm.QCamera(cameras[0])


    #IMPORTANT unfortunately video recdording is not supported right now on windows wtf.jpg
    # https://doc.qt.io/qt-5/qtmultimedia-windows.html
    def record(self):
        # create file proces (file extension is not needed it will do this for us)
        datestamp = qtc.QDateTime.currentDateTime().toString()
        print(f'{self.video_dir.filePath("log - " + datestamp)}')
        self.mediafile = qtc.QUrl.fromLocalFile(self.video_dir.filePath('log - ' + datestamp))
        # set where it writes to
        self.recorder.setOutputLocation(self.mediafile)
        #start recording
        self.recorder.record()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
