import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtChart as qtch
from collections import deque
import psutil


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        tabs = qtw.QTabWidget()
        self.setCentralWidget(tabs)
        disk_usage_view = DiskUsageChartView()
        tabs.addTab(disk_usage_view, 'Disk Usage')
        cpu_usage_view = CPUUsageView()
        tabs.addTab(cpu_usage_view, 'CPU Usage')

        memory_usage = MemoryChartView()
        tabs.addTab(memory_usage, "Memory Usage")
        # End main UI Code
        self.show()


class DiskUsageChartView(qtch.QChartView):
    # chartview is a widget that can display qchart objects!
    chart_title = 'Disk Usage by Partition'

    def __init__(self):
        super().__init__()
        # Qchart is just a cointainer for the data plats it is not the graph itself?
        # series within the chart defines what type of graph it will be
        chart = qtch.QChart(title=self.chart_title)
        # since it's a view you need to attach the chart object
        self.setChart(chart)

        #  creating the series here
        #  the series do not need to be of the same type it could be a line and bar
        series = qtch.QBarSeries()
        series.setLabelsVisible(True)
        chart.addSeries(series)
        # qt bar charts can show data in categories, but also allow for different sets of data to be compared
        # across those categories
        # the argument is just the label of the data set
        bar_set = qtch.QBarSet('Percent Used')
        series.append(bar_set)

        # retrieve the data
        partitions = []
        for part in psutil.disk_partitions():
            # only read write because we don't care about things like DVD readers
            if 'rw' in part.opts.split(','):
                partitions.append(part.device)
                usage = psutil.disk_usage(part.mountpoint)
                bar_set.append(usage.percent)

        # there are different types of axis, but in this case it is categorical
        x_axis = qtch.QBarCategoryAxis()
        x_axis.append(partitions)
        # the axis needs to be attached to the chart and the series
        chart.setAxisX(x_axis)
        series.attachAxis(x_axis)

        y_axis = qtch.QValueAxis()
        y_axis.setRange(0, 100)
        chart.setAxisY(y_axis)
        series.attachAxis(y_axis)


class CPUUsageView(qtch.QChartView):
    num_data_points = 500
    chart_title = "CPU Utilization"

    def __init__(self):
        super().__init__()
        chart = qtch.QChart(title=self.chart_title)
        self.setChart(chart)
        # QSpline will use cubic curves to connect points making it look smoother
        self.series = qtch.QSplineSeries(name="Percentage")
        chart.addSeries(self.series)

        # then we need dummy variables to set the graph
        # there is no need to create a set like before for linegraphs
        self.data = deque(
            [0] * self.num_data_points, maxlen=self.num_data_points
        )
        self.series.append([qtc.QPoint(x, y) for x, y in enumerate(self.data)])

        x_axis = qtch.QValueAxis()
        x_axis.setRange(0, self.num_data_points)
        # x_axis labels are useless since they're just data point labels as in point1 and etc
        x_axis.setLabelsVisible(False)
        y_axis = qtch.QValueAxis()
        y_axis.setRange(0, 100)
        # this automatically attaches are axis for us
        chart.setAxisY(y_axis, self.series)
        chart.setAxisX(x_axis, self.series)
        # visual optimization
        # adds smoothness to the curves, not so necessary for a normal line graph
        self.setRenderHint(qtg.QPainter.Antialiasing)
        # 200 ms timer
        self.timer = qtc.QTimer(interval=200, timeout=self.refresh_stats)
        self.timer.start()

    def refresh_stats(self):
        usage = psutil.cpu_percent()
        self.data.append(usage)
        # this method of creating a copy and replacing all the data points is slightly faster than replacing the series
        # entirely
        new_data = [qtc.QPoint(x, y) for x, y in enumerate(self.data)]
        self.series.replace(new_data)

    def keyPressEvent(self, event: qtg.QKeyEvent) -> None:
        keymap = {
            qtc.Qt.Key_Up: lambda: self.chart().scroll(0, 10),
            qtc.Qt.Key_Down: lambda: self.chart().scroll(0, -10),
            qtc.Qt.Key_Right: lambda: self.chart().scroll(10, 0),
            qtc.Qt.Key_Left: lambda: self.chart().scroll(-10, 0),
            # you could call the method here instead and give a float input
            qtc.Qt.Key_Equal: lambda: self.chart().zoomIn(),
            qtc.Qt.Key_Minus: lambda: self.chart().zoomOut(),
        }
        callback = keymap.get(event.key())
        if callback:
            print("here")
            callback()


class MemoryChartView(qtch.QChartView):
    chart_title = "Memory Usage"
    num_data_points = 50

    def __init__(self):
        super().__init__()
        chart = qtch.QChart(title=self.chart_title)
        self.setChart(chart)
        series = qtch.QStackedBarSeries()
        chart.addSeries(series)
        self.phys_set = qtch.QBarSet("Physical")
        self.swap_set = qtch.QBarSet("Swap")
        series.append(self.phys_set)
        series.append(self.swap_set)

        self.data = deque([(0, 0)] * self.num_data_points, maxlen=self.num_data_points)
        for phys, swap in self.data:
            self.phys_set.append(phys)
            self.swap_set.append(swap)

        x_axis = qtch.QValueAxis()
        x_axis.setRange(0, self.num_data_points)
        x_axis.setLabelsVisible(False)
        y_axis = qtch.QValueAxis()
        y_axis.setRange(0, 100)
        chart.setAxisX(x_axis, series)
        chart.setAxisY(y_axis, series)
        # setting simple animations
        chart.setAnimationOptions(qtch.QChart.AllAnimations)
        chart.setAnimationEasingCurve(qtc.QEasingCurve(qtc.QEasingCurve.OutBounce))
        chart.setAnimationDuration(1000)

        chart.setDropShadowEnabled(True)
        # setting a theme
        chart.setTheme(qtch.QChart.ChartTheme.ChartThemeBrownSand)
        # setting a custom background for the chart using a QBrush
        gradient = qtg.QLinearGradient(
            chart.plotArea().topLeft(), chart.plotArea().bottomRight()
        )
        gradient.setColorAt(0, qtg.QColor('#333'))
        gradient.setColorAt(1, qtg.QColor('#660'))
        chart.setBackgroundBrush(qtg.QBrush(gradient))
        # this drawas the border around the plot area?
        chart.setBackgroundPen(qtg.QPen(qtg.QColor('black'), 5))

        chart.setTitleBrush(qtg.QBrush(qtc.Qt.white))
        chart.setTitleFont(qtg.QFont("Impact", 32, qtg.QFont.Bold))

        # even with those changes not much has changed
        # we need to change certain things individually
        axis_font = qtg.QFont('Mono', 16)
        axis_brush = qtg.QBrush(qtg.QColor('#EEF'))
        y_axis.setLabelsFont(axis_font)
        y_axis.setLabelsBrush(axis_brush)

        # we can change the grid lines as well
        grid_pen = qtg.QPen(qtg.QColor('silver'))
        grid_pen.setDashPattern([1, 1, 1, 0])
        x_axis.setGridLinePen(grid_pen)
        y_axis.setGridLinePen(grid_pen)
        # optional of course
        y_axis.setTickCount(11)

        # for better visibility
        y_axis.setShadesVisible(True)
        y_axis.setShadesColor(qtg.QColor('#884'))

        # now to change the legend
        # grab the current legend
        legend = chart.legend()
        # by default it has no background
        legend.setBackgroundVisible(True)
        legend.setBrush(qtg.QBrush(qtg.QColor('white')))
        legend.setFont(qtg.QFont('Courier', 14))
        # you can also do setLabelBrush
        legend.setLabelColor(qtc.Qt.darkRed)
        legend.setMarkerShape(qtch.QLegend.MarkerShape.MarkerShapeCircle)

        self.timer = qtc.QTimer(interval=1000, timeout = self.refresh_stats)
        self.timer.start()

    def refresh_stats(self):
        phys = psutil.virtual_memory()
        swap = psutil.swap_memory()
        total_mem = phys.total + swap.total
        phys_pct = (phys.used / total_mem) * 100
        swap_pct = (swap.used / total_mem) * 100
        self.data.append((phys_pct, swap_pct))
        for x, (phys, swap) in enumerate(self.data):
            self.phys_set.replace(x, phys)
            self.swap_set.replace(x, swap)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
