#!/usr/bin/env python2


from PyQt4.QtCore import QObject,pyqtSlot,QUrl,QDir
#from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow,QFileSystemModel,QAbstractItemView
#from PyQt4.QtGui import QSizePolicy, QColor
from fitparse import Activity
from PyQt4 import uic
#from files import getValue, handle_tcxFile, timeFormat

from dbdata import dbHandler




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
        self.dbHandle = dbHandler()
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("main.ui")
        self.ui.webView.load(QUrl("./main.html"))
        self.printer = ConsolePrinter(self)
        self.frame = self.ui.webView.page().mainFrame()
        self.ui.webView.page().settings().setOfflineStoragePath("test.storage")
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

        #FIXME move away
        self.hr = []
        self.ui.show()

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
        fitfiles = (self.fileModel.filePath(x) 
                for x in self.ui.treeView.selectedIndexes() 
                if x.column() == 0)

        if self.fileModel.type(index) == "fit File":
            return
            a = Activity(fitFile)
            a.parse()
            #hrv = filter(lambda x: x.type.num==78, a.records)
            dat = filter(lambda x: x.type.num==20, a.records)
            dlatlo = [[float(u.fields[1].data)/(1<<31)*180,float(u.fields[2].data)/ \
                (1<<31)*180] for u in dat if u.fields[1].data]
            dat = filter(lambda x: x.type.num==20, a.records)
            #timestamp = [u.fields[0].data for u in dat if u.fields[0].data]
            self.hr.append([[i,u.fields[6].data] for i,u in enumerate(dat) if u.fields[6].data])
            dat = filter(lambda x: x.type.num==20, a.records)
            alt = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            hr = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            self.frame.evaluateJavaScript("setLine(%s)"%(dlatlo))
            #self.frame.evaluateJavaScript("showPlot([[[1,2],[2,3],[4,3]]])")
            self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, \
                    label:"altitude", yaxis: 2}]);'%(hr,alt))
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
            if not self.dbHandle.hasFile(fitFile):
                self.dbHandle.newData(fitFile)
            else:
                print('already there')
            self.dFrame = self.dbHandle.getFrame(fitFile)
            #self.mplWidget.plotDataFrame(self.dFrame)
            dlatlo = [[d[0], d[1]] for d in self.dFrame.values if d[0] != 0]
            self.frame.evaluateJavaScript('setLine(%s,"%s");'%(dlatlo,cols.pop()))
            self.dFrame['timeInt'] = self.dFrame.index.astype(int)/1000000 - \
                    self.dFrame.index.astype(int)[0]/1000000
            self.hr.append([[d[-1],d[4]] for d in self.dFrame.values])
            print(self.hr[0][:10])
        strS = ', '.join(['{data: %s, label:"HR%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+1)]) for i,hrI in enumerate(self.hr)])
        ''' { xaxis: { mode: "time", timeformat: "%H:%M:%S" }, grid: { hoverable: true } }
        '''
        self.frame.evaluateJavaScript('showPlot([%s]);'%(strS))
        #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))


