#!/usr/bin/env python2


from PyQt4.QtCore import QObject, pyqtSlot, QUrl, QDir, QDateTime
#from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow, QFileSystemModel, QAbstractItemView, QStandardItemModel, QStandardItem
from PyQt4.QtWebKit import QWebSettings
#from PyQt4.QtGui import QSizePolicy, QColor
from fitparse import Activity
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
        self.ui.subwindowMap.showMaximized()
        #self.ui.mdiArea.addSubWindow(self.ui.subwindowGraphs)
        #self.ui.mdiArea.tileSubWindows()
        #self.ui.mdiArea.cascadeSubWindows()
        #print self.ui.mdiArea.subWindowList(), self.ui.subwindowMap

        self.ui.treeView.setRootIndex(self.fileModel.index(QDir.currentPath()))
        self.ui.treeView.clicked.connect(self.onTreeViewFileSelected)
        self.ui.dbTreeView.clicked.connect(self.onTreeViewDateSelected)

        #FIXME move away
        self.hr = []
        self.ui.show()
        self.initTree()
        #self.monthDict = {v: k for k,v in enumerate(month_abbr)}

    def initTree(self):
        self.itemModel = QStandardItemModel()
        #self.itemModel.
        root = self.itemModel.invisibleRootItem()
        root.setEditable(False)
        for ex in self.dbHandle.getStoreList():
            rItem = QStandardItem("{}".format(ex))
            rItem.setEditable(False)
            root.appendRow(rItem)
        #for year in self.dbHandle.getYearList():
            #rItem = QStandardItem("{} {}km".format(year,0))#self.dbHandle.getKm(year)))
            #rItem.setEditable(False)
            #root.appendRow(rItem)
            #for month in self.dbHandle.getMonths(year):
                #monthEntry = QStandardItem("{} {}km".format(month_abbr[month], \
                        #self.dbHandle.getKm(year,month)))
                #rItem.appendRow(monthEntry)
                #monthEntry.setEditable(False)
                #for ex in self.dbHandle.getTrainings(year,month):
                    #it = QStandardItem("{}".format(ex))
                    #it.setEditable(False)
                    #it.setData(QDateTime(ex))
                    #monthEntry.appendRow(it)

        self.ui.dbTreeView.setModel(self.itemModel)
        self.ui.dbTreeView.setSelectionMode(QAbstractItemView.ExtendedSelection)


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
        timestmp = float(str(strTSt))
        #print('graphHover',timestmp)
        st = self.dFrame.index.astype(int)[0]
        i = self.dFrame.index.astype(int).searchsorted(st + timestmp*1000000.)
        (lat,lng)=(0,0)
        if 'altitude' in self.dFrame:
            (lat,lng) = (self.dFrame['position_lat'][i], self.dFrame['position_long'][i])
        else:
            (lat,lng)=self.dFrame.values[i][:2]
        if lat:
            self.onMouseOver(lat,lng)


    def onTreeViewFileSelected(self,index):
        self.frame.evaluateJavaScript('clearMap();')
        fitFile = self.fileModel.filePath(index)
        #print('click',index.data(),self.fileModel.filePath(index),type(self.fileModel.type(index)))
        fitfiles = (self.fileModel.filePath(x) 
                for x in self.ui.treeView.selectedIndexes() 
                if x.column() == 0)

        frames = []
        if self.fileModel.type(index).lower() == "fit file":
            print('fit file')
            for fitFile in fitfiles:
                fitFile = str(fitFile)
                if not self.dbHandle.hasFile(fitFile):
                    self.dbHandle.newFitData(fitFile)
                print(fitFile)
                frames.append(self.dbHandle.getFrameOfFile(fitFile))
            print('finish')
        elif self.fileModel.type(index) == "tcx File":
            for fitFile in fitfiles:
                fitFile = str(fitFile)
                if not self.dbHandle.hasFile(fitFile):
                    self.dbHandle.newData(fitFile)
                #else:
                    #print('already there')
                frames.append(self.dbHandle.getFrame(fitFile))
            ''' { xaxis: { mode: "time", timeformat: "%H:%M:%S" }, grid: { hoverable: true } }
            '''
            #self.frame.evaluateJavaScript('showPlot([{data: %s,label:"Heartrate"},{data:%s, label:"altitude", yaxis: 2}]);'%(hr,alt))
        else:
            print('found file: ', self.fileModel.type(index))
        if frames:
            self.plotDataFrame(frames)

    def onTreeViewDateSelected(self,index):
        self.frame.evaluateJavaScript('clearMap();')
        #if (len(index.data())==4):
            #print('year')
        #elif (index.data() in month_abbr):
            #print('month')
        #else:
        self.printSelected()

    def printSelected(self):
        frames = []
        for index in self.ui.dbTreeView.selectedIndexes():
            da = self.itemModel.itemFromIndex(index)
            d = da.text()
            print('click:',da.text(), type(da.data()))
            #try:
                #data = d.toDateTime().toPyDateTime()
            #except:
                #data = d.toPyDateTime()
            #dFrame = self.dbHandle.getFrameByDate(data)
            dFrame = self.dbHandle.getFrame(d)
            frames.append(dFrame)
        self.plotDataFrame(frames)

    def getD(self, name, iterObj):
        return [[d[1]['timeInt'], d[1][name]] for d in iterObj if name in d[1] if d[1][name]==d[1][name]] 

    def plotDataFrame(self, dFrames):
        self.hr = []
        self.alt = []
        self.cad = []
        self.stp = []
        self.st = []
        cols = ['darkred','green','red','green','black','yellow','blue','red']
        colsH = ['darkred','green','red','green','black','yellow','blue','red']
        for dframe in dFrames:
            if 'altitude' in dframe.keys():
                dlatlo = [[x[1]['position_lat'],x[1]['position_long']] for x in dframe.iterrows() 
                        if x[1]['position_lat'] == x[1]['position_lat']]
                self.frame.evaluateJavaScript('setLine(%s,"%s");'%(dlatlo,cols.pop()))
                dframe['timeInt'] = dframe.index.astype(int)/1000000 - \
                        dframe.index.astype(int)[0]/1000000
                self.hr.append(self.getD('heart_rate', dframe.iterrows()))
                self.alt.append(self.getD('altitude', dframe.iterrows()))
                self.cad.append(self.getD('cadence', dframe.iterrows()))
                self.st.append(self.getD('stance_time', dframe.iterrows()))
                self.stp.append(self.getD('stance_time_percent', dframe.iterrows()))
                #self.hr.append([[d[1]['timeInt'], d[1]['heart_rate']] for d in dframe.iterrows() if 'heart_rate' in d[1]] )
                #self.alt.append([[d[1]['timeInt'], d[1]['altitude']] for d in dframe.iterrows() if 'altitude' in d[1]] )
                #self.cad.append([[d[1]['timeInt'], d[1]['cadence']] for d in dframe.iterrows() if 'cadence' in d[1]] )
                #self.stp.append([[d[1]['timeInt'], d[1]['stance_time_percent']] for d in dframe.iterrows() if 'stance_time_percent' in d[1]])
                #self.st.append([[d[1]['timeInt'], d[1]['stance_time']] for d in dframe.iterrows() if 'stance_time' in d[1] if d[1]['stance_time']==d[1]['stance_time']])
            else:
                dlatlo = [[d[0], d[1]] for d in dframe.values if d[0] != 0]
                #dlatlo = [x for x in zip(dframe.LatitudeDegrees, dframe.LongitudeDegrees) if x[0]!=0]
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
        print(strS[:100])
        strS = ', '.join(['{data: %s, label:"Cadence%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+3)]) for i,hrI in enumerate(self.cad)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot3");'%(strS))
        strS = ', '.join(['{data: %s, label:"Stance Time%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+4)]) for i,hrI in enumerate(self.st)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot4");'%(strS))
        strS = ', '.join(['{data: %s, label:"Stance Time [percent]%d", color:"%s"}'\
                %(hrI,i,colsH[-(i+4)]) for i,hrI in enumerate(self.stp)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot5");'%(strS))



