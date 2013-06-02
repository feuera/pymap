#!/usr/bin/env python2

import pandas as pd
from files import readFile
from datetime import datetime

def convertName(x):
    return 'G'+x.split('/')[-1][2:-4].replace('-','_')
    #return 'G'+fname[2:-4].replace('-','_')

class dbHandler():
    def __init__(self):
        self.hdStore = pd.HDFStore("/home/andi/workspace/garmin/History/all.h5")
        self.hdKeys = self.hdStore.keys()

    def newData(self, fname):
        data = readFile(fname)
        cols = ['Time','LatitudeDegrees','LongitudeDegrees','AltitudeMeters',
                'DistanceMeters','HeartRate','Cadence','SensorState']
        dFrame = pd.DataFrame(data, columns=cols)
        dFrame.index = dFrame.Time
        del dFrame['Time']
        del dFrame['SensorState']
        #hrFilt = rolling_median(df.HeartRate, 30)
        print('add new dataset')
        hdKey = '/'+convertName(fname) 
        self.hdStore.append(hdKey,dFrame)
        self.hdKeys.append(hdKey)

    def hasFile(self, fname):
        hdKey = '/'+convertName(fname)
        return hdKey in self.hdKeys

    def getFrame(self, fname):
        return self.hdStore['/'+convertName(fname)]

    def getFrameByDate(self, date):
        dateF = "%y_%m_%d_%H_%M_%S"
        dStr = date.strftime("/G"+dateF)
        return self.hdStore[dStr]

    def getStoreList(self):
        dateF = "%y_%m_%d_%H_%M_%S"
        tList = [datetime.strptime(key[2:], dateF) for key in self.hdKeys]
        return tList

    def getYearList(self):
        tList = self.getStoreList()
        return list(set(t.year for t in tList))

    def getMonths(self, year):
        tList = self.getStoreList()
        return list(set(t.month for t in tList if t.year==year))

    def getTrainings(self, year, month):
        tList = self.getStoreList()
        return (x for x in tList if x.month==month and x.year==year)


