import pandas as pd
import numpy as np

def joindata(ifname1='all1.xls', ifname2='all2.xlsx', ofname="all.xls"):
    d1 = pd.read_excel(ifname1)
    d2 = pd.read_excel(ifname2)
    d1col = d1.columns
    d2col = d2.columns
    # print(type(d1col), len(d1col), d1col)
    # print(type(d2col), len(d2col), d2col)
    dcol = list(set(d1col).intersection(set(d2col)))
    # print(len(dcol), dcol)

    d1fix = d1[dcol]
    d2fix = d2[dcol]

    d = d1fix.append(d2fix)
    print("write the data:")
    d.to_excel(ofname)

def percent2float(ifname='all.xls',ofname="allfix.xls"):
    d = pd.read_excel(ifname)
    sd = d.shape
    for i in range(sd[0]):
        for j in range(sd[1]):
            strd = str(d.iloc[i,j])
            if strd.find("%") != -1:
                d.iloc[i,j] = float(strd[:strd.find("%")])/100
    d.to_excel(ofname)

def getresult(ifname='all.xls',ofname="allfix.xls"):
    d = pd.read_excel(ifname)

    tt = lambda a: 0 if a['host_score']<a['guest_score'] else 2 if a['host_score']>a['guest_score'] else 1
    d.insert(0,'result',d.apply(tt,axis=1))
    d.to_excel(ofname)
#
# def getresult1(ifname='all.xls',ofname="allfix.xls"):
#     d = pd.read_excel(ifname)
#     tt = lambda a: 1 if a['host_score']>a['guest_score'] else 0
#     d = d.drop('result', axis=1)
#     d.insert(0,'result',d.apply(tt,axis=1))
#     d.to_excel(ofname)
# getresult(ifname='all1.xls',ofname="all1fix.xls")
# getresult('test1.xls','test1fix.xls')
percent2float('test1fix.xls','test1.xls')