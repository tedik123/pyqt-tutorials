import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sounddevice as sd
import queue
import numpy as np

# get a list of audio devices
input_audio_device_infos = qtmm.QAudioDeviceInfo.availableDevices(qtmm.QAudio.AudioInput)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(fig)
        fig.tight_layout()


# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe

class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # slow way to load UI
        self.ui = loadUi("audio_gui.ui", self)
        self.resize(888, 600)
        # icon = qtg.QIcon()
        # icon.addPixmap(qtg.QPixmap("PyShine.png"), qtg.QIcon.Normal, qtg.QIcon.Off)
        # self.setWindowIcon(icon)

        self.threadpool = qtc.QThreadPool()
        self.devices_list = []
        for device in input_audio_device_infos:
            self.devices_list.append(device.deviceName())

        # set devices list combo box
        self.audio_device_box.addItems(self.devices_list)
        self.audio_device_box.currentIndexChanged["QString"].connect(self.update_now)
        self.audio_device_box.setCurrentIndex(0)

        self.canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        # fixme might cause issues
        self.matplot_widget.layout().addWidget(self.canvas)  # ?
        self.reference_plot = None
        self.q = queue.Queue(maxsize=20)

        self.device = 0
        self.window_length = 1000
        self.downsample = 1
        self.channels = [1]
        self.interval = 30

        device_info = sd.query_devices(self.device, 'input')
        self.sample_rate = device_info['default_samplerate']
        length = int(self.window_length * self.sample_rate / (1000 * self.downsample))
        sd.default.samplerate = self.sample_rate

        self.plot_data = np.zeros((length, len(self.channels)))

        self.update_plot()
        self.timer = qtc.QTimer()
        self.timer.setInterval(self.interval)  # in msec
        self.timer.start()

        self.window_length_line_edit.textChanged["QString"].connect(self.update_window_length)
        self.sample_rate_line_edit.textChanged["QString"].connect(self.update_sample_rate)
        self.down_sample_line_edit.textChanged["QString"].connect(self.update_down_sample)
        self.update_interval_line_edit.textChanged["QString"].connect(self.update_interval)

        self.plot_button.clicked.connect(self.start_worker)

        # End main UI Code
        self.show()

    def get_audio(self):
        try:
            def audio_callback(indata, frames, time, status):
                self.q.put(indata[::self.downsample, [0]])

            stream = sd.InputStream(device=self.device, channels=max(self.channels),
                                    samplerate=self.sample_rate, callback=audio_callback)
            with stream:
                input()
        except Exception as e:
            print("ERROR", e)

    def start_worker(self):
        worker = Worker(self.start_stream, )
        self.threadpool.start(worker)

    def start_stream(self):
        self.window_length_line_edit.setEnabled(False)
        self.sample_rate_line_edit.setEnabled(False)
        self.down_sample_line_edit.setEnabled(False)
        self.update_interval_line_edit.setEnabled(False)
        self.audio_device_box.setEnabled(False)
        self.plot_button.setEnabled(False)
        self.get_audio()

    def update_now(self, value):
        self.device = self.devices_list.index(value)
        print("device:", self.device)

    def update_window_length(self, value):
        self.window_length = int(value)
        length = int(self.window_length * self.sample_rate / (1000 * self.downsample))
        self.plot_data = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_sample_rate(self, value):
        self.sample_rate = int(value)
        sd.default.samplerate = self.sample_rate
        length = int(self.window_length * self.sample_rate / (1000 * self.downsample))
        self.plot_data = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_down_sample(self, value):
        self.downsample = int(value)
        length = int(self.window_length * self.sample_rate / (1000 * self.downsample))
        self.plot_data = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_interval(self, value):
        self.interval = int(value)
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        try:
            # placeholder object so we can graph to start
            data = [0]

            while True:
                try:
                    data = self.q.get_nowait()
                except queue.Empty:
                    print("Queue Empty")
                    break
                shift = len(data)
                self.plot_data = np.roll(self.plot_data, -shift, axis=0)
                self.plot_data[-shift:, :] = data
                self.ydata = self.plot_data[:]
                self.canvas.axes.set_facecolor((0, 0, 0))

                if self.reference_plot is None:
                    plot_refs = self.canvas.axes.plot(self.ydata, color=(0, 1, 0.29))
                    self.reference_plot = plot_refs[0]
                else:
                    self.reference_plot.set_ydata(self.ydata)

            self.canvas.axes.yaxis.grid(True, linestyle="--")
            start, end = self.canvas.axes.get_ylim()
            self.canvas.axes.yaxis.set_ticks(np.arange(start, end, .1))
            self.canvas.axes.yaxis.set_major_formatter(ticker.FormatStrFormatter("%0.1f"))
            self.canvas.axes.set_ylim(ymin=-.5, ymax = .5)
            self.canvas.draw()

        except Exception as e:
            print("ERROR IN UPDATE_PLOT", e)


class Worker(qtc.QRunnable):

    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @qtc.pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    # https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, qtc.Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, qtc.Qt.black)
    palette.setColor(QPalette.ToolTipText, qtc.Qt.white)
    palette.setColor(QPalette.Text, qtc.Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, qtc.Qt.white)
    palette.setColor(QPalette.BrightText, qtc.Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, qtc.Qt.black)
    app.setPalette(palette)

    # execution
    mw = MainWindow()
    sys.exit(app.exec())
