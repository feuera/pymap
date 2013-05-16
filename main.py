#!/usr/bin/env python

import sys
from PyQt4.QtCore import QObject,pyqtSlot,QUrl,QDir
from PyQt4.QtGui import QMainWindow,QApplication,QFileSystemModel
from PyQt4.QtWebKit import *
from PyQt4 import uic

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
        print('click',index.data(),self.fileModel.fileName(index),self.fileModel.size(index),self.fileModel.type(index))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    #app.exec_()
    sys.exit(app.exec_())

