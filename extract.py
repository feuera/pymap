#!/usr/bin/env python

import sys
import glob

from dbdata import dbHandler
from concurrent.futures import ThreadPoolExecutor

def main():
    print(sys.argv[1])
    fnames = glob.glob(sys.argv[1])
    dbH = dbHandler()
    with ThreadPoolExecutor(max_workers=8) as e:
        e.map(dbH.newData, fnames)
        #for fname in fnames:
            #try:
                #e.submit(dbH.newData,fname)
                #print('processed:',fname)
            #except Exception as e:
                #print(e)




if __name__ == '__main__':
    main()
