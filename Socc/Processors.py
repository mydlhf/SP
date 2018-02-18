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

import pandas as pd
import numpy as np
import sklearn as sl
from sklearn.preprocessing import StandardScaler

def standard(data):
    ss = StandardScaler()
    scaler = ss.fit(data)
    return scaler.transform(data), scaler

def to_matrix(data):
    return [each.as_matrix() for each in data if type(each) is pd.core.frame.DataFrame or type(each) is pd.core.series.Series]

def sample(data, samplecount=None, rate=None):
    rcol = data['result']
    rvalue = list(set(rcol))
    splitdata = [data[data['result']==each] for each in rvalue]
    if rate:
        sampledata = [each.sample(int(each.shape[0]*rate)) for each in splitdata]
    elif samplecount:
        print("sample count is %s" % samplecount)
        sampledata = [each.sample(samplecount) for each in splitdata]
    else:
        samplecount = min([len(each) for each in splitdata])
        print("sample count is %s" %samplecount)
        sampledata = [each.sample(samplecount) for each in splitdata]
    rdata = pd.concat(sampledata, axis=0)
    print("sample data with shape ", (rdata.shape))
    return rdata


def k_argmax(data, k=2):
    r = []
    for e in data:
        enum = list(enumerate(e))
        denum = [(each[1],each[0]) for each in enum]

        se = sorted(e, reverse=True)
        dindex = []
        for deach in se:
            for each in denum:
                if deach == each[0]:
                    dindex.append(each[1])
                    break
        r.append(dindex[:k])
    # print(r)
    # d = np.array([denum[each] for each in data])
    return np.array(r)

