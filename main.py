#!/usr/bin/env python2

import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow


class DataCalc():
    def __init__(self):
        pass

    def calcDa(self):
        pass

# class MyStaticMplCanvas(MyMplCanvas):
#    """Simple canvas with a sine plot."""
#    def compute_initial_figure(self):
#        t = arange(0.0, 3.0, 0.01)
#        s = sin(2*pi*t)
#        self.axes.plot(t, s)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
