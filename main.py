#!/usr/bin/env python2

import sys
from PyQt4.QtGui import QApplication

#from .gui import MainWindow
from gui import MainWindow


class DataCalc():
    def __init__(self):
        pass

    def calcDa(self):
        #frame = store.get('/G13_05_23_14_07_03')
        ##nF = pd.DataFrame(dict(diffT=dt, diffA=diff(frame.AltitudeMeters.values)), index=range(len(dt)))
        #dt = [ a.item() / 1e9 for a in diff(frame.index.values) ]
        #frame['Vario'] = pd.Series(diff(frame.AltitudeMeters.values) / dt * 60, index=frame.index[1:])
        #frame['Speed'] = pd.Series(diff(frame.DistanceMeters.values) / dt * 3.6, index=frame.index[1:])
        #frameD = frame.copy()
        #frameD.index = frameD.DistanceMeters
        #del frameD['DistanceMeters']
        pass
        
#class MyStaticMplCanvas(MyMplCanvas):
#    """Simple canvas with a sine plot."""
#    def compute_initial_figure(self):
#        t = arange(0.0, 3.0, 0.01)
#        s = sin(2*pi*t)
#        self.axes.plot(t, s)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    #app.exec_()
    sys.exit(app.exec_())

