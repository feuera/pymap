#!/usr/bin/env python2

import pandas as pd
from files import readFile

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
        


