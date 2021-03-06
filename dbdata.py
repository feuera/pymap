#!/usr/bin/env python2

import pandas as pd
from files import readFile
from datetime import datetime
from fitparse import Activity


def convertName(x):
    return 'G'+x.split('/')[-1][:-4].replace('-', '_')


class dbHandler():
    def __init__(self):
        self.hdStore = pd.HDFStore("./allN.h5")
        self.hdKeys = self.hdStore.keys()
        self.tList = []

    def newFitData(self, fname):
        a = Activity(fname)
        a.parse()
        dat = filter(lambda x: x.type.num == 20, a.records)
        # data = [{f.name: (f.data, f.units) for f in x.fields} for x in dat]
        # fitKeys =['timestamp','position_lat','position_long',
        #           'altitude','distance','altitude','heart_rate',
        #           'cadence','speed','vertical_oscillation',
        #           'stance_time','stance_time_percent']
        funcDict = {}
        funcDict['position_lat'] = lambda x: x/(1 << 31)*180
        funcDict['position_long'] = lambda x: x/(1 << 31)*180

        def calcFun(key, val):
            return funcDict[key](val) if key in funcDict else val
        data = [{f.name: calcFun(f.name, f.data) for f in x.fields}
                for x in dat]
        dFrame = pd.DataFrame(data)
        dFrame.index = dFrame.timestamp
        del dFrame['timestamp']
        # dateF = "%y_%m_%d_%H_%M_%S"
        # dStr = "/G"+datetime.now().strftime(dateF)
        dStr = "/"+convertName(fname)
        self.hdStore.append(dStr, dFrame)
        self.hdKeys.append(dStr)
        # cols = ['Time','LatitudeDegrees','LongitudeDegrees','AltitudeMeters',
        #       'DistanceMeters','HeartRate','Cadence','']

    def newData(self, fname):
        data = readFile(fname)
        cols = ['Time', 'LatitudeDegrees', 'LongitudeDegrees',
                'AltitudeMeters', 'DistanceMeters',
                'HeartRate', 'Cadence', 'SensorState']
        dFrame = pd.DataFrame(data, columns=cols)
        dFrame.index = dFrame.Time
        del dFrame['Time']
        del dFrame['SensorState']
        # hrFilt = rolling_median(df.HeartRate, 30)
        print('add new dataset')
        hdKey = '/'+convertName(fname)
        self.hdStore.append(hdKey, dFrame)
        self.hdKeys.append(hdKey)

    def hasFile(self, fname):
        hdKey = '/'+convertName(fname)
        if len(hdKey) > 10:
            return hdKey in self.hdKeys
        else:
            return fname in self.hdKeys

    def getFrame(self, fname):
        return self.hdStore[fname]

    def getFrameOfFile(self, fname):
        fname = convertName(fname)
        return self.hdStore[fname]

    def getFrameByDate(self, date):
        dateF = "%Y_%m_%d_%H_%M_%S"
        dStr = date.strftime("/G"+dateF)
        return self.hdStore[dStr]

    def getStoreList(self):
        if not self.tList:
            try:
                dateF = "%Y_%m_%d_%H_%M_%S"
                self.tList = [datetime.strptime(key[2:], dateF)
                              for key in self.hdKeys]
                print(self.tList)
                return self.tList
            except:
                return self.hdKeys
        else:
            return self.tList

    def getYearList(self):
        tList = self.getStoreList()
        return list(set(t.year for t in tList if not isinstance(t, str)))

    def getMonths(self, year):
        tList = self.getStoreList()
        return list(set(t.month for t in tList if t.year == year))

    def getTrainings(self, year, month):
        tList = self.getStoreList()
        return (x for x in tList if x.month == month and x.year == year)

    def getKm(self, year, month=0):
        if month:
            return 0
        # int(sum([self.getFrameByDate(x).DistanceMeters.values[-1]
        #  for x in self.getTrainings(year,month)]) / 1000)
        else:
            return sum([self.getKm(year, mon) for mon in self.getMonths(year)])
