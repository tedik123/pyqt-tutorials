import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5.uic import loadUi
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi
import seaborn as sns
import pandas as pd
# even tho it says there is an error it works fine
import sip
import platform

# check the platform
op_sys = platform.system()
# we need this for OSx
if op_sys == "Darwin":
    from Foundation import NSURL

# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe
# following this:
# https://www.youtube.com/watch?v=LStHozI2aDo&list=PLjPKPFvkBtZqKg8ugYihcxkWfnIDcwR4K&index=6&ab_channel=PyShine
class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=120):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(fig)
        fig.tight_layout()


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # slow way to load UI
        loadUi("csv_ui.ui", self)
        # combo box settings
        self.themes = ['bmh', 'classic', 'dark_background', 'fast',
                       'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn-bright',
                       'seaborn-colorblind', 'seaborn-dark-palette', 'seaborn-dark',
                       'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 'seaborn-notebook',
                       'seaborn-paper', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk',
                       'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'seaborn',
                       'Solarize_Light2', 'tableau-colorblind10']
        self.theme_selector_box.addItems(self.themes)
        # push button settings
        self.open_button.clicked.connect(self.getFile)
        self.theme_selector_box.currentIndexChanged["QString"].connect(self.update)

        # file import set up stuff
        self.filename = ''
        self.canvas = MatplotlibCanvas(self)
        self.df = []
        self.toolbar = Navi(self.canvas, self.centralwidget)
        self.horizontalLayout.addWidget(self.toolbar)
        self.verticalSpacer_item = self.verticalLayout.itemAt(0)

        # drag and drop functionality
        self.setup_drag_and_drop()

        # End main UI Code
        self.show()


    def setup_drag_and_drop(self):
        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0: qtg.QDragEnterEvent) -> None:
        # this detenctions the drag enter event in the main window I guess
        # mime is a type of Multipurpose Internet Mail Extensions
        # indicates the nature/format of the data type
        if a0.mimeData().hasUrls:
            a0.accept()
        else:
            a0.ignore()

    def dragMoveEvent(self, e: qtg.QDragMoveEvent) -> None:
        # detects the drag move event on the main window
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: qtg.QDropEvent) -> None:
        """Enables the actual drop of the file on the main window"""
        if e.mimeData().hasUrls:
            e.setDropAction(qtc.Qt.CopyAction)
            e.accept()
            for url in e.mimeData().urls():
                if op_sys == "Darwin":
                    fname = str(NSURL.URLWithString_(str(url.toString())).filePathUrl().path())
                else:
                    fname = str(url.toLocalFile())
                self.filename = fname
                print("GOT ADDRESS", self.filename)
                # Then call the read data function we had from earlier
                self.readData()
        else:
            e.ignore()

    # FIXME this kinda works....it doesn't really plot all too well
    # and all the labels are missing or sometimes plain wrong
    # you really need to manipulate the pandas dataframe first to get it to plot correctly
    # but for the basic principle it's pretty cool
    def update(self, selected_theme):
        print(f"Value from Combo box: {selected_theme}")
        plt.clf()
        plt.style.use(selected_theme)
        try:
            self.horizontalLayout.removeWidget(self.toolbar)
            self.verticalLayout.removeWidget(self.canvas)
            sip.delete(self.toolbar)
            sip.delete(self.canvas)
            self.toolbar = None
            self.canvas = None
            self.verticalLayout.removeItem(self.verticalSpacer_item)
        except Exception as e:
            print(e)
            pass
        self.canvas = MatplotlibCanvas(self)
        self.toolbar = Navi(self.canvas, self.centralwidget)
        self.horizontalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canvas)
        self.canvas.axes.cla()
        ax = self.canvas.axes
        # this does the plotting
        self.df.plot(ax=self.canvas.axes)
        legend = ax.legend()
        legend.set_draggable(True)
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.set_title("Title")
        self.canvas.draw()

    def getFile(self):
        # returns a list of file names, but just the first result
        self.filename = qtw.QFileDialog.getOpenFileName(filter="csv (*.csv)")[0]
        print("File selected", self.filename)
        self.readData()

    def readData(self):
        # load in data via pandas and fill nulls with 0's
        self.df = pd.read_csv(self.filename, encoding="utf-8").fillna(0)
        # set default theme
        self.update(self.themes[0])


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
