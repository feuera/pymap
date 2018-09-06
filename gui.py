#!/usr/bin/env python2

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QDir, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWidgets import QMainWindow, QFileSystemModel, QAbstractItemView
# from fitparse import Activity
from PyQt5 import uic
# from files import getValue, handle_tcxFile, timeFormat

from dbdata import dbHandler
from calendar import month_abbr


class ConsolePrinter(QObject):
    def __init__(self, parent=None):
        super(ConsolePrinter, self).__init__(parent)
        print('init done')

    @pyqtSlot(str)
    def text(self, message):
        # frame.evaluateJavaScript("setLine([[57.3,11.1],[10.3,14.3]]);")
        # frame.evaluateJavaScript(
        #  "setLine([[47.15, 15.37],[47.26,15.30],[47.16,15.30]]);")
        print(message)

class MainWindow(QMainWindow):
    def __init__(self):
        self.dbHandle = dbHandler()
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("main.ui")
        # self.ui.webView.load(QUrl("./main.html"))
        self.printer = ConsolePrinter(self)
        self.frame = self.ui.webView.page().mainFrame()
        pSettings = self.ui.webView.page().settings()
        pSettings.setOfflineStoragePath("test.storage")
        pSettings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.ui.webView.show()
        self.ui.webView.loadFinished.connect(self.loadFin)

        # model
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(QDir.currentPath())
        self.fileModel.setNameFilters(['*.py', '*.fit', '*.tcx'])
        self.ui.treeView.setModel(self.fileModel)
        self.ui.treeView.setAlternatingRowColors(True)
        self.ui.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.ui.mdiArea.addSubWindow(self.ui.subwindowMap)
        self.ui.subwindowMap.showMaximized()
        # self.ui.mdiArea.addSubWindow(self.ui.subwindowGraphs)
        # self.ui.mdiArea.tileSubWindows()
        # self.ui.mdiArea.cascadeSubWindows()
        # print self.ui.mdiArea.subWindowList(), self.ui.subwindowMap

        self.ui.treeView.setRootIndex(self.fileModel.index(QDir.currentPath()))
        self.ui.treeView.clicked.connect(self.onTreeViewFileSelected)
        self.ui.dbTreeView.clicked.connect(self.onTreeViewDateSelected)

        # FIXME move away
        self.hr = []
        self.ui.show()
        self.initTree()
        # self.monthDict = {v: k for k,v in enumerate(month_abbr)}

    def initTree(self):
        self.itemModel = QStandardItemModel()
        root = self.itemModel.invisibleRootItem()
        root.setEditable(False)
        for year in self.dbHandle.getYearList():
            print("year", year)
            rItem = QStandardItem("{} {}km".format(year, 0))
            # self.dbHandle.getKm(year)))
            rItem.setEditable(False)
            root.appendRow(rItem)
            for month in self.dbHandle.getMonths(year):
                s = "{} {}km".format(month_abbr[month],
                                     self.dbHandle.getKm(year, month))
                monthEntry = QStandardItem(s)
                rItem.appendRow(monthEntry)
                monthEntry.setEditable(False)
                for ex in self.dbHandle.getTrainings(year, month):
                    it = QStandardItem("{}".format(ex))
                    it.setEditable(False)
                    it.setData(QDateTime(ex))
                    monthEntry.appendRow(it)

        self.ui.dbTreeView.setModel(self.itemModel)
        self.ui.dbTreeView.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def loadFin(self, bTrue):
        self.frame.addToJavaScriptWindowObject('printer', self.printer)
        self.frame.addToJavaScriptWindowObject('gui', self)
        self.printer.text("hi")
        self.frame.evaluateJavaScript("setLine(%s)"
                                      % ('[[[45.25,15.33],[44.10,14.4]]]'))

    def onMouseOver(self, lat, long):
        self.frame.evaluateJavaScript('moveMarker([%f,%f]);' % (lat, long))

    @pyqtSlot(str)
    def onGraphHover(self, strTSt):
        try:
            timestmp = float(str(strTSt))
            st = self.dFrame.index.astype(int)[0]
            i = self.dFrame.index.astype(int).searchsorted(st + timestmp*1000000.)
            (lat, lng) = (0, 0)
            if 'altitude' in self.dFrame:
                (lat, lng) = (self.dFrame['position_lat'][i],
                              self.dFrame['position_long'][i])
            else:
                # if i < len(self.dFrame):
                (lat, lng) = self.dFrame.values[i][:2]
            if lat:
                self.onMouseOver(lat, lng)
        except:
            pass

    def onTreeViewFileSelected(self, index):
        self.frame.evaluateJavaScript('clearMap();')
        fitFile = self.fileModel.filePath(index)
        fitfiles = (self.fileModel.filePath(x)
                    for x in self.ui.treeView.selectedIndexes()
                    if x.column() == 0)

        frames = []
        print(self.fileModel.type(index))
        if self.fileModel.type(index) == "FIT File":
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
                frames.append(self.dbHandle.getFrameOfFile(fitFile))
            ''' { xaxis: { mode: "time", timeformat: "%H:%M:%S" },
                  grid: { hoverable: true } }
            '''
        else:
            print('found file: ', self.fileModel.type(index))
        if frames:
            self.plotDataFrame(frames)

    def onTreeViewDateSelected(self, index):
        self.frame.evaluateJavaScript('clearMap();')
        self.printSelected()

    def printSelected(self):
        frames = []
        for index in self.ui.dbTreeView.selectedIndexes():
            da = self.itemModel.itemFromIndex(index)
            d = da.text()
            print('click:', da.text(), type(da.data()))
            try:
                dFrame = self.dbHandle.getFrameByDate(da.data().toPyDateTime())
                ds = int(len(dFrame)/300)
                dfS = dFrame[::ds]
                frames.append(dfS)
            except:
                pass
        if len(frames):
            self.plotDataFrame(frames)

    def getD(self, name, iterObj):
        return [[d[1]['timeInt'], d[1][name]] for d in iterObj
                if name in d[1]
                if d[1][name] == d[1][name]]

    def plotDataFrame(self, dFrames):
        self.hr = []
        self.alt = []
        self.cad = []
        self.stp = []
        self.st = []
        cols = ['darkred', 'green', 'red', 'green',
                'black', 'yellow', 'blue', 'red']
        colsH = ['darkred', 'green', 'red', 'green',
                 'black', 'yellow', 'blue', 'red']
        for dframe in dFrames:
            if 'altitude' in dframe.keys():
                dlatlo = [[x[1]['position_lat'], x[1]['position_long']]
                          for x in dframe.iterrows()
                          if x[1]['position_lat'] == x[1]['position_lat']]
                evStr = 'setLine(%s,"%s");' % (dlatlo, cols.pop())
                self.frame.evaluateJavaScript(evStr)
                dframe['timeInt'] = dframe.index.astype(int)/1000000 - \
                    dframe.index.astype(int)[0] / 1000000
                self.hr.append(self.getD('heart_rate', dframe.iterrows()))
                self.alt.append(self.getD('altitude', dframe.iterrows()))
                self.cad.append(self.getD('cadence', dframe.iterrows()))
                self.st.append(self.getD('stance_time', dframe.iterrows()))
                self.stp.append(self.getD('stance_time_percent',
                                          dframe.iterrows()))
            else:
                dlatlo = [[d[0], d[1]] for d in dframe.values if d[0] != 0]
                evStr = 'setLine(%s,"%s");' % (dlatlo, cols.pop())
                self.frame.evaluateJavaScript(evStr)
                dframe['timeInt'] = dframe.index.astype(int)/1000000 - \
                    dframe.index.astype(int)[0]/1000000
                self.hr.append([[d[-1], d[4]] for d in dframe.values])
                self.alt.append([[d[-1], d[2]] for d in dframe.values])
                self.cad.append([[d[-1], d[5]] for d in dframe.values])
        self.dFrame = dframe
        strS = ', '.join(['{data: %s, label:"HR%d", color:"%s"}'
                          % (hrI, i, colsH[-(i+1)])
                          for i, hrI in enumerate(self.hr)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot1");' % (strS))
        strS = ', '.join(['{data: %s, label:"Altitude%d", color:"%s"}'
                          % (hrI, i, colsH[-(i+2)])
                          for i, hrI in enumerate(self.alt)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot2");' % (strS))
        print(strS[:100])
        strS = ', '.join(['{data: %s, label:"Cadence%d", color:"%s"}'
                          % (hrI, i, colsH[-(i+3)])
                          for i, hrI in enumerate(self.cad)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot3");' % (strS))
        strS = ', '.join(['{data: %s, label:"Stance Time%d", color:"%s"}'
                          % (hrI, i, colsH[-(i+4)])
                          for i, hrI in enumerate(self.st)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot4");' % (strS))
        strS = ', '.join(['{data: %s, \
                          label: "Stance Time [percent]%d", color:"%s"}'
                          % (hrI, i, colsH[-(i+4)])
                          for i, hrI in enumerate(self.stp)])
        self.frame.evaluateJavaScript('showPlot([%s],"plot5");' % (strS))
