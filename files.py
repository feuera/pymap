#!/usr/bin/env python2

import time
import xml.dom.minidom as xmldom
#from fitparse import Activity
from datetime import datetime

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
    return fd



def readFile(fname):
    names = ['Time','LatitudeDegrees','LongitudeDegrees','AltitudeMeters',
            'DistanceMeters','Value','Cadence','SensorState']
    convertF = [lambda x: datetime.strptime(x,timeFormat), float, float, float,
            float, int, int, str]
    d = handle_tcxFile(fname)
    if not d:
        return
    data = [ [convertF[i](getValue(name,p)) for i,name in enumerate(names)] 
            for p in d['allTrackPoints'] ]
    return data

