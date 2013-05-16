#!/usr/bin/env python

import sys,os
from PyQt4.QtCore import QObject,pyqtSlot,QUrl,QDir
from PyQt4.QtGui import QMainWindow,QApplication,QFileSystemModel
from PyQt4.QtWebKit import *
from PyQt4 import uic

import time
from fitparse import Activity
import xml.dom.minidom as xmldom
timeFormat = "%Y-%m-%dT%H:%M:%SZ"

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




class ConsolePrinter(QObject):
    def __init__(self, parent=None):
        super(ConsolePrinter, self).__init__(parent)
        print('init done')

    @pyqtSlot(str)
    def text(self, message):
        #frame.evaluateJavaScript("setLine([[57.3,11.1],[10.3,14.3]]);")
        #frame.evaluateJavaScript("setLine([[47.15, 15.37],[47.26,15.30],[47.16,15.30]]);")
        print(message)


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

        self.ui.treeView.setRootIndex(self.fileModel.index(QDir.currentPath()))
        self.ui.treeView.clicked.connect(self.fileSelected)
        #self.ui.treeView.activated.connect(self.fileSelected)
        self.ui.show()

    def loadFin(self, bTrue):
        #print (self.frame)
        #self.frame.evaluateJavaScript("alert('Hello');")
        self.frame.addToJavaScriptWindowObject('printer', self.printer)
        #self.printer.text("hi")

    def fileSelected(self,index):
        fitFile = self.fileModel.filePath(index)
        print('click',index.data(),self.fileModel.filePath(index),type(self.fileModel.type(index)))
        if self.fileModel.type(index) == "fit File":
            a = Activity(fitFile)
            a.parse()
            hrv = filter(lambda x: x.type.num==78, a.records)
            dat = filter(lambda x: x.type.num==20, a.records)
            dlatlo = [[float(u.fields[1].data)/(1<<31)*180,float(u.fields[2].data)/(1<<31)*180] for u in dat if u.fields[1].data]
            dat = filter(lambda x: x.type.num==20, a.records)
            #timestamp = [u.fields[0].data for u in dat if u.fields[0].data]
            hr = [[i,u.fields[6].data] for i,u in enumerate(dat) if u.fields[6].data]
            dat = filter(lambda x: x.type.num==20, a.records)
            alt = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            self.frame.evaluateJavaScript("setLine(%s)"%(dlatlo))
            #self.frame.evaluateJavaScript("showPlot([[[1,2],[2,3],[4,3]]])")
            self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))
            print('finish')
        if self.fileModel.type(index) == "tcx File":
            tr = handle_tcxFile(fitFile)
            dlatlo = [[float(getValue('LatitudeDegrees',trackP)), float(getValue('LongitudeDegrees',trackP))] for trackP in tr['allTrackPoints'] if int(float(getValue('LongitudeDegrees',trackP)))]
            self.frame.evaluateJavaScript("setLine(%s)"%(dlatlo))
            hr = [[i,getValue('Value',trackP)] for i,trackP in enumerate(tr['allTrackPoints'])]
            self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"}]);'%(hr))
            #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    #app.exec_()
    sys.exit(app.exec_())

