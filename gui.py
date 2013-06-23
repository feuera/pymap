#!/usr/bin/env python2


from PyQt4.QtCore import QObject, pyqtSlot, QUrl, QDir, QDateTime
#from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow, QFileSystemModel, QAbstractItemView, QStandardItemModel, QStandardItem
from PyQt4.QtWebKit import QWebSettings
#from PyQt4.QtGui import QSizePolicy, QColor
#from fitparse import Activity
from PyQt4 import uic
#from files import getValue, handle_tcxFile, timeFormat

from dbdata import dbHandler
from calendar import month_abbr




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
        self.ui.webView.page().settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
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
        self.ui.treeView.clicked.connect(self.onTreeViewFileSelected)
        self.ui.dbTreeView.clicked.connect(self.onTreeViewDateSelected)

        self.initTree()

    def initTree(self):
        self.itemModel = QStandardItemModel()
        #self.itemModel.
        root = self.itemModel.invisibleRootItem()
        root.setEditable(False)
        for year in self.dbHandle.getYearList():
            rItem = QStandardItem("{}".format(year))
            rItem.setEditable(False)
            root.appendRow(rItem)
            for month in self.dbHandle.getMonths(year):
                monthEntry = QStandardItem("{}".format(month_abbr[month]))
                rItem.appendRow(monthEntry)
                monthEntry.setEditable(False)
                for ex in self.dbHandle.getTrainings(year,month):
                    it = QStandardItem("{}".format(ex))
                    it.setEditable(False)
                    it.setData(QDateTime(ex))
                    monthEntry.appendRow(it)

        self.ui.dbTreeView.setModel(self.itemModel)
        self.ui.dbTreeView.setSelectionMode(QAbstractItemView.ExtendedSelection)

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


    def onTreeViewFileSelected(self,index):
        fitFile = self.fileModel.filePath(index)
        #print('click',index.data(),self.fileModel.filePath(index),type(self.fileModel.type(index)))
        fitfiles = (self.fileModel.filePath(x) 
                for x in self.ui.treeView.selectedIndexes() 
                if x.column() == 0)

        #if self.fileModel.type(index) == "fit File":
            #return
            #a = Activity(fitFile)
            #a.parse()
            ##hrv = filter(lambda x: x.type.num==78, a.records)
            #dat = filter(lambda x: x.type.num==20, a.records)
            #dlatlo = [[float(u.fields[1].data)/(1<<31)*180,float(u.fields[2].data)/ \
                #(1<<31)*180] for u in dat if u.fields[1].data]
            #dat = filter(lambda x: x.type.num==20, a.records)
            ##timestamp = [u.fields[0].data for u in dat if u.fields[0].data]
            #self.hr.append([[i,u.fields[6].data] for i,u in enumerate(dat) if u.fields[6].data])
            #dat = filter(lambda x: x.type.num==20, a.records)
            #alt = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            #hr = [[i,u.fields[4].data] for i,u in enumerate(dat) if u.fields[4].data]
            #self.frame.evaluateJavaScript("setLine(%s)"%(dlatlo))
            ##self.frame.evaluateJavaScript("showPlot([[[1,2],[2,3],[4,3]]])")
            #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, \
                    #label:"altitude", yaxis: 2}]);'%(hr,alt))
            #print('finish')
        ##if self.fileModel.type(index) == "tcx File":

        frames = []
        for fitFile in fitfiles:
            fitFile = str(fitFile)
            if not self.dbHandle.hasFile(fitFile):
                self.dbHandle.newData(fitFile)
            #else:
                #print('already there')
            frames.append(self.dbHandle.getFrame(fitFile))
        ''' { xaxis: { mode: "time", timeformat: "%H:%M:%S" }, grid: { hoverable: true } }
        '''
        self.plotDataFrame(frames)
        #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))

    def onTreeViewDateSelected(self,index):
        self.frame.evaluateJavaScript('clearMap();')
        frames = []
        for index in self.ui.dbTreeView.selectedIndexes():
            d = self.itemModel.itemFromIndex(index).data()
            try:
                data = d.toDateTime().toPyDateTime()
            except:
                data = d.toPyDateTime()
            print(data)
            dFrame = self.dbHandle.getFrameByDate(data)
            frames.append(dFrame)
        self.plotDataFrame(frames)


    def plotDataFrame(self, dFrames):
        self.hr = []
        self.alt = []
        self.cad = []
        cols = ['darkred','green','red','green','black','yellow','blue','red']
        colsH = ['darkred','green','red','green','black','yellow','blue','red']
        for dframe in dFrames:
            dlatlo = [[d[0], d[1]] for d in dframe.values if d[0] != 0]
            self.frame.evaluateJavaScript('setLine(%s,"%s");'%(dlatlo,cols.pop()))
            dframe['timeInt'] = dframe.index.astype(int)/1000000 - \
                    dframe.index.astype(int)[0]/1000000
            self.hr.append([[d[-1],d[4]] for d in dframe.values])
            self.alt.append([[d[-1],d[2]] for d in dframe.values])
            self.cad.append([[d[-1],d[5]] for d in dframe.values])
            #print(self.hr[0][:10])
        self.dFrame = dframe
        strS = ', '.join(['{data: %s, label:"HR%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+1)]) for i,hrI in enumerate(self.hr)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot1");'%(strS))
        strS = ', '.join(['{data: %s, label:"Altitude%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+2)]) for i,hrI in enumerate(self.alt)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot2");'%(strS))
        strS = ', '.join(['{data: %s, label:"Cadence%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+3)]) for i,hrI in enumerate(self.cad)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot3");'%(strS))


