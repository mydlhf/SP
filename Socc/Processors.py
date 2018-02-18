import pandas as pd
import numpy as np
from sklearn.utils import shuffle
def joindata(d1, d2):
    print("combile the data:")
    d1col = d1.columns
    d2col = d2.columns
    # print(type(d1col), len(d1col), d1col)
    # print(type(d2col), len(d2col), d2col)
    dcol = list(set(d1col).intersection(set(d2col)))
    # print(len(dcol), dcol)

    d1fix = d1[dcol]
    d2fix = d2[dcol]
    d = d1fix.append(d2fix)
    return d

def percent2float(data):
    print("percent to float:")
    sd = data.shape
    for i in range(sd[0]):
        for j in range(sd[1]):
            strd = str(data.iloc[i,j])
            if strd.find("%") != -1:
                data.iloc[i,j] = float(strd[:strd.find("%")])/100
    return data

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
    rdata = shuffle(rdata)
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

def gen_result(data):
    print("generate the results:")
    tt = lambda x: 0 if x['host_score']<x['guest_score'] else 2 if x['host_score']>x['guest_score'] else 1
    data.insert(0,'result',data.apply(tt, axis=1))
    return data

def str2int(data, cols=None):
    print("string to ints:")
    if not cols:
        return data
    else:
        for each in cols:
            print("convert the column %s"%each)
            values = data[each]
            distinct_values = set(list(values))
            enum_distinct_values = list(enumerate(distinct_values))
            dict_distinct_values = {x[1]:x[0] for x in enum_distinct_values}
            new_values = [dict_distinct_values[v] for v in values]
            data[each]  = pd.Series(new_values)
    return data


def handle_file(ifname, ofname, *type, C=None):
    d = pd.read_excel(ifname)
    if "p2f" in type:
        d = percent2float(d)
    if "gen" in type:
        d = gen_result(d)
    if "s2i" in type:
        d = str2int(d, cols=C)
    d.to_excel(ofname)


# handle_file('basedata/train1.xls', 'basedata/train2.xls', 's2i', C=['host_name','guest_name','full_host_name', 'full_guest_name'])