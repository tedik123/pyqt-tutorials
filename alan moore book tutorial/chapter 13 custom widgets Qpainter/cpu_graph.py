import sys
from collections import deque

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm

# to get current CPU usage
from psutil import cpu_percent
# import GPUtil
# note: I "stole" GPUtil and modified only part, setting shell = True
# this prevents the pop-up when in exe form
# it also reduces performance significantly from what I understand
# so in the future, if there is a future, i should be weary of that
import stolen_GPUtil


# import nvidia_smi


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    resized = qtc.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # IMPORTANT WOW This is cool
        # it will resize to 70% of the screen available!
        self.resize(qtw.QDesktopWidget().availableGeometry(self).size() * 0.7)
        # self.graph = GraphWidget(scale=self.size().width()/20)
        self.main = qtw.QWidget()
        self.main.setLayout(qtw.QVBoxLayout())
        self.setCentralWidget(self.main)
        self.cpu_graph = GraphWidget(component="CPU")
        self.gpu_graph = GraphWidget(component="GPU")
        self.main.layout().addWidget(self.cpu_graph)
        self.main.layout().addWidget(self.gpu_graph)
        # self.setCentralWidget(self.cpu_graph)
        # we just need to call the cpu usage periodically
        self.timer = qtc.QTimer()
        # 1 second
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start()
        self.cpu_usage = 0
        # print(GPUtil.showUtilization())

        # GPU STUFF
        # nvidia_smi.nvmlInit()
        # self.gpu_handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        # card id 0 hardcoded here, there is also a call to get all available card ids, so we could iterate

        self.gpu = None
        self.gpu_usage = 0
        # End main UI Code
        self.show()

    def update_graph(self):
        # returns 0 to 100 (percent basically)
        self.cpu_usage = cpu_percent()
        self.cpu_graph.add_value(self.cpu_usage)
        # res = nvidia_smi.nvmlDeviceGetUtilizationRates(self.gpu_handle)
        # print(f'gpu: {res.gpu}%, gpu-mem: {res.memory}%')
        gpus = stolen_GPUtil.getGPUs()
        self.gpu = gpus[0]
        self.gpu_usage = self.gpu.load
        self.gpu_graph.add_value(self.gpu_usage * 100)
        # print(self.gpu_usage)

        # for testing
        # import random
        # self.cpu_usage = random.randint(1, 100)
        # self.graph.add_value(self.cpu_usage)


class GraphWidget(qtw.QWidget):
    """A widget to display a running graph of information"""

    crit_color = qtg.QColor(255, 0, 0)
    warn_color = qtg.QColor(255, 255, 0)
    good_color = qtg.QColor(0, 255, 0)

    # takes in a data_width -> how many values to display at a time
    # ranges defined by minimum and maximum
    # critvalue and warn_val are thresholds
    # scale is how many pixels to use for each data point
    def __init__(self, *args, data_width=50, minimum=0, maximum=100, warn_val=60, crit_val=85, scale=10,
                 component="CPU", **kwargs):
        super().__init__(*args, **kwargs)
        self.data_width = data_width
        self.minimum = minimum
        self.maximum = maximum
        self.warn_val = warn_val
        self.crit_val = crit_val
        self.scale = self.width() / data_width
        self.component = component

        # print(self.scale)
        # print(self.width())
        self.component_util = 0
        # this is creating a linked list from an array that is of length of data_width
        self.values = deque([self.minimum] * data_width, maxlen=data_width)
        self.rect = qtc.QRect(int(self.width() * .9), int(self.height() * .0025), 128, 128)
        # this sets the total amount of pixels we want to display
        # self.setFixedWidth(data_width * self.scale)
        self.setBaseSize(self.height(), int(data_width * self.scale))

    # this class will add values to our dequue
    def add_value(self, value):
        # this constrains our value between the min and maximum we have already established
        value = max(value, self.minimum)
        value = min(value, self.maximum)
        self.values.append(value)
        self.component_util = value
        # self.update() tells the widget to redraw itself
        self.update()

    # when update or some other redraw event occurs it calls paintEvent ultimately
    # we can draw our custom widget by overriding the paintEvent
    # IMPORTANT
    # paint event gets called with one argument, the event that requested the repaint
    # it contains the region and rectangle that needs to be redrawn
    # for a complex widget you can only redraw just that one part instead of the whole thing
    # but we're going to ignore it and redraw the whole thing
    def paintEvent(self, a0: qtg.QPaintEvent) -> None:
        painter = qtg.QPainter(self)
        # draw background color
        brush = qtg.QBrush(qtg.QColor(48, 48, 48))
        painter.setBrush(brush)

        # draw a rectangle on the entire screen/region it's given
        # this one takes coordinates instead of a Qrect shape
        painter.drawRect(0, 0, self.width(), self.height())

        # draw the warning threshold
        pen = qtg.QPen()
        # 1 pixel drawn, 1 pixel off, and repeat, you can change this as you please
        # it seems like it has to be 1's and 0's tho?
        pen.setDashPattern([1, 0])
        warn_y = self.val_to_y(self.warn_val)
        pen.setColor(self.warn_color)
        painter.setPen(pen)
        # this draws a horizontal line across our warn threshold value
        painter.drawLine(0, warn_y, self.width(), warn_y)

        # draw the crit threshold
        crit_y = self.val_to_y(self.crit_val)
        # important we can reuse the pen object, but the painter takes in a COPY of the pen
        #   so any changes after it's passed in are not reflected/noticed in the painter
        #   we must pass it back in to update the pen object in the painter!!!!
        pen.setColor(self.crit_color)
        painter.setPen(pen)
        painter.drawLine(0, crit_y, self.width(), crit_y)

        # we'll want to craete a gradient that draw our values at the top as red and medium values as yellow
        # and low values as green
        # the gradient will go from bottom to top
        # NOT top to bottom!
        gradient = qtg.QLinearGradient(qtc.QPointF(0, self.height()), qtc.QPointF(0, 0))
        gradient.setColorAt(0, self.good_color)
        # warn and crit value must be converted to a percentage (decimal) between 0 and 1,
        # so it knows how to draw the gradient
        gradient.setColorAt(self.warn_val / (self.maximum - self.minimum), self.warn_color)
        gradient.setColorAt(self.crit_val / (self.maximum - self.minimum), self.crit_color)

        # now let's set up our painter to draw the data points
        brush = qtg.QBrush(gradient)
        painter.setBrush(brush)
        # this enum prevents the painter from outlining shapes!
        painter.setPen(qtc.Qt.NoPen)

        # we need a previous value to connect the points
        # we want to store the last value/start value
        # if it exists we'll grab it otherwise default to self.minimum
        self.start_value = getattr(self, 'start_value', self.minimum)
        last_value = self.start_value
        # this is updating the start_value for the NEXT call to paint
        self.start_value = self.values[0]

        # we want it connected to the previous point, hence using the old data point
        for idx, value in enumerate(self.values):
            x = (idx + 1) * self.scale
            last_x = idx * self.scale
            y = self.val_to_y(value)
            last_y = self.val_to_y(last_value)

            path = qtg.QPainterPath()
            # this sets a starting point
            path.moveTo(x, self.height())
            # this draws a line from the previous/current point to the next
            # notice the last point to the first point is connected AUTOMATICALLY
            path.lineTo(last_x, self.height())
            path.lineTo(last_x, last_y)
            # path.lineTo(x, y)
            # since we don't want a boring straight line we should use a non-linear drawing method
            c_x = round(self.scale * .5) + last_x
            c1 = (c_x, last_y)
            c2 = (c_x, y)
            # this is a cubic Bezier curve
            # it uses two control points, each control point pulls a segment of the line towards it
            # the first control point pulls the first half,
            # the second control point pulls the second half
            # this gives it an overall S shape
            path.cubicTo(*c1, *c2, x, y)
            # we haven't actually drawn to screen yet just created the path
            # to draw we need the painter
            painter.drawPath(path)
            last_value = value

        # painter.setPen(qtg.QColor(0, 255, 0))
        painter.setPen(self.get_util_color(self.component_util))
        painter.setFont(qtg.QFont("Impact", 16))

        # flags = qtc.Qt.AlignHCenter | qtc.Qt.TextWordWrap
        self.rect = qtc.QRect(int(self.width() - 128), 0, 128, 64)
        # print(self.rect)
        usage_print = " {0:0.2f}".format(self.component_util)
        text = f"{self.component} \t  {usage_print}%"
        painter.drawText(self.rect, qtc.Qt.AlignCenter, text)

    def val_to_y(self, value):
        # first we need to determine what fraction of the data_range the value represents
        data_range = self.maximum - self.minimum
        value_fraction = value / data_range
        # then we need to determine how many pixels from the bottom of the widget it should be
        y_offset = round(value_fraction * self.height())
        # then because pixel coordinates count DOWN from the top we need to subtract it from the height of the widget
        y = self.height() - y_offset
        return y

    def get_util_color(self, value):
        if value < self.warn_val:
            # good
            return self.good_color
        elif value < self.crit_val:
            # warn
            return self.warn_color
        else:
            return self.crit_color

    def resizeEvent(self, a0: qtg.QResizeEvent) -> None:
        super()
        self.scale = self.width() / self.data_width


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
