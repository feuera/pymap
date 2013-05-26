#!/usr/bin/env python

import sys,os

from PyQt4.QtCore import QObject,pyqtSlot,QUrl,QDir,pyqtSignal
from PyQt4.QtGui import QMainWindow,QApplication,QFileSystemModel,QAbstractItemView,QSizePolicy,QColor
from PyQt4.QtWebKit import *
from PyQt4 import uic

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import num2date,date2num

import time
from fitparse import Activity
import xml.dom.minidom as xmldom
#from extract import convertName
timeFormat = "%Y-%m-%dT%H:%M:%SZ"
import pandas as pd
from datetime import datetime

def getValue(name, trackPoint):
  try:
    return trackPoint.getElementsByTagName(name)[0].firstChild.nodeValue
  except:
    return 0


def handle_tcxFile(f):
    # returns dictionary of file
    fd = {}
    dom = xmldom.parse(f)
    fd['activity'] = dom.getElementsByTagName('Activity')[0].getAttribute('Sport')
    fd['startDate'] = dom.getElementsByTagName('Lap')[0].getAttribute('StartTime')[:10] 
    fd['allTrackPoints'] = dom.getElementsByTagName('Trackpoint')
    fd['startT'] = time.mktime(time.strptime(getValue('Time',fd['allTrackPoints'][0]),timeFormat))
    fd['distMeter'] = getValue('DistanceMeters',dom)
    fd['maxS'] = getValue('MaximumSpeed',dom)
    'create new training...'
    #t = Training(date=startDate, lat=0, lon=0,distance=distMeter,maxSpeed=maxS)
    #t.save()
    #for i,trackP in enumerate(allTrackPoints):
    #    tim = time.mktime(time.strptime(getValue('Time',trackP),timeFormat)) - startT
    #    hr = getValue('Value',trackP)
    #    alti = getValue('AltitudeMeters',trackP)
    #    posLat = getValue('LatitudeDegrees',trackP)
    #    posLon = getValue('LongitudeDegrees',trackP)
    #    aG = 0
    #    if(posLat > 10 and posLon > 10 and t.lat==0):
    #        t.lat = posLat
    #        t.lon = posLon
    #        t.save()
    #    w = WayPoint(training=t, lat=posLat,lon=posLon,time=tim,heartRate=hr, alt=alti, altGoogle=aG)
    #    w.save()
    return fd


def convertName(x):
    return 'G'+x.split('/')[-1][2:-4].replace('-','_')
    #return 'G'+fname[2:-4].replace('-','_')



class ConsolePrinter(QObject):
    def __init__(self, parent=None):
        super(ConsolePrinter, self).__init__(parent)
        print('init done')

    @pyqtSlot(str)
    def text(self, message):
        #frame.evaluateJavaScript("setLine([[57.3,11.1],[10.3,14.3]]);")
        #frame.evaluateJavaScript("setLine([[47.15, 15.37],[47.26,15.30],[47.16,15.30]]);")
        print(message)

class DataCalc():
    def __init__(self):
        pass

    def calcDa(self):
        frame = store.get('/G13_05_23_14_07_03')
        nF = pd.DataFrame(dict(diffT=dt, diffA=diff(frame.AltitudeMeters.values)), index=range(len(dt)))
        dt = [ a.item() / 1e9 for a in diff(frame.index.values) ]
        frame['Vario'] = pd.Series(diff(frame.AltitudeMeters.values) / dt * 60, index=frame.index[1:])
        frame['Speed'] = pd.Series(diff(frame.DistanceMeters.values) / dt * 3.6, index=frame.index[1:])
        frameD = frame.copy()
        frameD.index = frameD.DistanceMeters
        del frameD['DistanceMeters']
        

class MyMplCanvas(FigureCanvas):
    mouseOver = pyqtSignal(float,float)
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('white')
        self.hrAxes=self.fig.add_subplot(311)
        self.altAxes=self.fig.add_subplot(312)
        self.cadAxes=self.fig.add_subplot(313)
        #self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.hrAxes.hold(False)
        self.altAxes.hold(False)
        self.cadAxes.hold(False)

        #self.hrLinev = self.hrAxes.axvline(self.hrAxes.get_xbound()[0], visible=False)
        #self.hrLineh = self.hrAxes.axhline(self.hrAxes.get_ybound()[0], visible=False)

        self.compute_initial_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.mpl_connect('motion_notify_event', self.onmove)
        self.dFrame = []

    def onmove(self, event):
        if event.inaxes and len(self.dFrame):
            #print('mouse move', event.xdata, event.ydata)
            i=event.xdata
            if i > 70000:
                i = self.dFrame.index.searchsorted(num2date(i))
            (lat,long)=self.dFrame.values[i][:2]
            self.mouseOver.emit(lat,long)
            self.hrLinev.set_xdata(event.xdata)
            self.draw_idle()
            #self.draw()

    def compute_initial_figure(self):
        #self.axes.plot([1,2,3])
        pass

    def plotDataFrame(self,frame):
        labelRot = "vertical"
        frame = frame.resample('20s')
        self.dFrame = frame
        #self.hrAxes.plot(frame.HeartRate,'r',label='HeartRate')
        self.hrAxes.plot(frame.index,frame.HeartRate,'r',label='HeartRate')
        self.altAxes.plot(frame.index,frame.AltitudeMeters,label='Altitude')
        self.cadAxes.plot(frame.index,frame.Cadence,'g',label='Cadence')

        #val = frame.index.values[0]
        #x = date2num((datetime.fromtimestamp(val.astype('O')/1e9)))
        #print x
        self.hrLinev = self.hrAxes.axvline(x=self.hrAxes.get_xbound()[0])#, visible=False)

        #self.hrAxes.set_xticklabels(self.hrAxes.get_xticks(),rotation=labelRot)
        #self.altAxes.set_xticklabels(self.altAxes.get_xticks(),rotation=labelRot)
        #self.cadAxes.set_xticklabels(self.cadAxes.get_xticks(),rotation=labelRot)
        self.draw()

#class MyStaticMplCanvas(MyMplCanvas):
#    """Simple canvas with a sine plot."""
#    def compute_initial_figure(self):
#        t = arange(0.0, 3.0, 0.01)
#        s = sin(2*pi*t)
#        self.axes.plot(t, s)



class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("main.ui")
        self.ui.webView.load(QUrl("./main.html"))
        self.printer = ConsolePrinter(self)
        self.frame = self.ui.webView.page().mainFrame()
        self.ui.webView.loadFinished.connect(self.loadFin)

        #model
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(QDir.currentPath())
        self.fileModel.setNameFilters(['*.py','*.fit','*.tcx'])
        self.ui.treeView.setModel(self.fileModel)
        self.ui.treeView.setAlternatingRowColors(True)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.ui.mdiArea.addSubWindow(self.ui.subwindowMap)
        #self.ui.mdiArea.addSubWindow(self.ui.subwindowGraphs)
        self.ui.mdiArea.tileSubWindows()
        #self.ui.mdiArea.cascadeSubWindows()
        #print self.ui.mdiArea.subWindowList(), self.ui.subwindowMap

        self.ui.treeView.setRootIndex(self.fileModel.index(QDir.currentPath()))
        self.ui.treeView.clicked.connect(self.fileSelected)
        #self.ui.treeView.activated.connect(self.fileSelected)

        #self.mplWidget = MyMplCanvas(self.ui.subwindowGraphs)
        #self.ui.subwindowGraphs.layout().addWidget(self.mplWidget)
        #self.mplWidget.mouseOver.connect(self.onMouseOver)

        self.hr = []
        self.ui.show()
        self.hdStore = pd.HDFStore("/home/andi/workspace/garmin/History/all.h5")
        self.hdKeys = self.hdStore.keys()

        #print (self.hdStore)

    def readFile(self,fname):
        names = ['Time','LatitudeDegrees','LongitudeDegrees','AltitudeMeters','DistanceMeters','Value','Cadence','SensorState']
        cols = ['Time','LatitudeDegrees','LongitudeDegrees','AltitudeMeters','DistanceMeters','HeartRate','Cadence','SensorState']
        convertF = [lambda x: datetime.strptime(x,timeFormat), float, float, float, float, int, int, str]
        d = handle_tcxFile(fname)
        if not d:
            return
        data = [ [convertF[i](getValue(name,p)) for i,name in enumerate(names)] for p in d['allTrackPoints'] ]
        dFrame = pd.DataFrame(data, columns=cols)
        dFrame.index = dFrame.Time
        del dFrame['Time']
        del dFrame['SensorState']
        #print(dFrame.describe())
        #dFrame.to_hdf(h5File,'df')
        #dFrame.to_hdf(h5File,convertName(fname))
        #hrFilt = rolling_median(df.HeartRate, 30)
        print('add new dataset')
        self.hdStore.append('/'+convertName(fname), dFrame)

    def loadFin(self, bTrue):
        #print (self.frame)
        #self.frame.evaluateJavaScript("alert('Hello');")
        self.frame.addToJavaScriptWindowObject('printer', self.printer)
        self.frame.addToJavaScriptWindowObject('gui', self)
        self.printer.text("hi")
        self.frame.evaluateJavaScript("setLine(%s)"%('[[[45.25,15.33],[44.10,14.4]]]'))

    def onMouseOver(self, lat, long):
        #print(lat,long)
        self.frame.evaluateJavaScript('moveMarker([%f,%f]);'%(lat,long))

    @pyqtSlot(str)
    def onGraphHover(self, strTSt):
        timestmp = int(float(str(strTSt)))
        #print('graphHover',timestmp)
        st = self.dFrame.index.astype(int)[0]
        i = self.dFrame.index.astype(int).searchsorted(st + timestmp*1000000)
        (lat,long)=self.dFrame.values[i][:2]
        self.onMouseOver(lat,long)


    def fileSelected(self,index):
        fitFile = self.fileModel.filePath(index)
        #print('click',index.data(),self.fileModel.filePath(index),type(self.fileModel.type(index)))
        fitfiles = (self.fileModel.filePath(x) for x in self.ui.treeView.selectedIndexes() if x.column() == 0)
        #print (fitfiles, [x for x in fitfiles])
        if self.fileModel.type(index) == "fit File":
            return
            a = Activity(fitFile)
            a.parse()
            hrv = filter(lambda x: x.type.num==78, a.records)
            dat = filter(lambda x: x.type.num==20, a.records)
            dlatlo = [[float(u.fields[1].data)/(1<<31)*180,float(u.fields[2].data)/(1<<31)*180] for u in dat if u.fields[1].data]
            dat = filter(lambda x: x.type.num==20, a.records)
            #timestamp = [u.fields[0].data for u in dat if u.fields[0].data]
            self.hr.append([[i,u.fields[6].data] for i,u in enumerate(dat) if u.fields[6].data])
            dat = filter(lambda x: x.type.num==20, a.records)
            alt = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            self.frame.evaluateJavaScript("setLine(%s)"%(dlatlo))
            #self.frame.evaluateJavaScript("showPlot([[[1,2],[2,3],[4,3]]])")
            self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))
            print('finish')
        #if self.fileModel.type(index) == "tcx File":
        self.hr = []
        self.frame.evaluateJavaScript('clearMap();')
        cols = ['darkred','green','red','green','black','yellow','blue','red']
        colsH = ['darkred','green','red','green','black','yellow','blue','red']
        #cols = [str(x) for x in QColor.colorNames()]
        for fitFile in fitfiles:
            fitFile = str(fitFile)
            print(fitFile)
            hdKey = '/'+convertName(fitFile)
            if not hdKey in self.hdKeys:
                self.readFile(fitFile)
                self.hdKeys = self.hdStore.keys()
            else:
                print('already there')
            self.dFrame = self.hdStore.get(hdKey)
            #self.mplWidget.plotDataFrame(self.dFrame)
            dlatlo = [[dat[0], dat[1]] for dat in self.dFrame.values if dat[0] != 0]
            self.frame.evaluateJavaScript('setLine(%s,"%s");'%(dlatlo,cols.pop()))
            self.dFrame['timeInt'] = self.dFrame.index.astype(int)/1000000 - self.dFrame.index.astype(int)[0]/1000000
            self.hr.append([[dat[-1],dat[4]] for dat in self.dFrame.values])
            print(self.hr[0][:10])
        strS = ', '.join(['{data: %s, label:"HR%d", color:"%s"}'%(hrI,i,colsH[-(i+1)]) for i,hrI in enumerate(self.hr)])
        ''' { xaxis: { mode: "time", timeformat: "%H:%M:%S" }, grid: { hoverable: true } }
        '''
        self.frame.evaluateJavaScript('showPlot([%s]);'%(strS))
        #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    #app.exec_()
    sys.exit(app.exec_())

