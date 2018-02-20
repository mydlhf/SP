import pandas as pd
import numpy as np
import random as rd
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

def gen_result(data, gentype=None):
    print("generate the results:")
    if not gentype:
        tt = lambda x: 0 if x['host_score']<x['guest_score'] else 2 if x['host_score']>x['guest_score'] else 1
    elif gentype == "sheng":
        tt = lambda x: 1 if x['host_score'] > x['guest_score'] else 0
    elif gentype == "ping":
        tt = lambda x: 1 if x['host_score'] == x['guest_score'] else 0
    elif gentype == "fu":
        tt = lambda x: 1 if x['host_score'] < x['guest_score'] else 0

    data.insert(0,'result',data.apply(tt, axis=1))
    return data

def str2int(data, cols=None):  #将字符串转换为数字表示
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

def drop_columns(data, dc=None):
    datacolumns = data.columns
    if dc:    #del not useful columns
        print("dropping the columns:", dc)
        for each in dc:
            if each in datacolumns:
                # print(each)
                data = data.drop(each, axis=1)
    return data

def data_auguments(data, samplerowcount=10, augcount=10000):
    if not augcount:
        augcount = data.shape[0] * 2
    alldata = []
    newdata = pd.DataFrame()
    for i in range(augcount):
        try:
            index = rd.randint(3, samplerowcount)
            temp = data.sample(index)
            newdata = newdata.append(temp.mean(), ignore_index=True)
            if (i+1)%1000 == 0:
                alldata.append(newdata)
                # print([each.shape for each in alldata])
                newdata = pd.DataFrame()
                print("generate %s rows"%i)
        except:
            print("error in %s row"%i)
            continue
    for each in alldata:
        data = data.append(each)

    return data

def handle_file(ifname, ofname, *type, convertcolumns=None, gentype=None, dropcolumns=None):
    d = pd.read_excel(ifname)
    for each in type:
        if "p2f" == each:  #percent to float
            d = percent2float(d)
        if "gen" == each:  #generate the results
            d = gen_result(d, gentype)
        if "s2i" == each:  #string to integer
            d = str2int(d, cols=convertcolumns)
        if "dc" == each:  #drop columns
            d = drop_columns(d, dropcolumns)
        if "da" == each:
            d = data_auguments(d, samplerowcount=8, augcount=1000000)
    d.to_csv(ofname)

def main():
    dc = ["id", "game_name",  'year', 'game_time', 'round', "host_last_rank",
          "guest_last_rank", ]
    #'host_name', 'guest_name', 'full_host_name', 'full_guest_name'
    handle_file('basedata/train2r.xls', 'basedata/train2ra100w.csv', 'da','gen')

if __name__ == "__main__":
    main()