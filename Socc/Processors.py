import pandas as pd
import numpy as np
import random as rd
import sklearn as sl
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
import Odatas as od


def process_nan(data, ptype=0):
    if ptype == 0:
        data = data.fillna(data.mean())
    elif ptype == 1:
        data = data.fillna(0)
    else:
        data = data.dropna()
    return data

def joindata(d1, d2):
    print("combine the data:")
    d1col = d1.columns
    d2col = d2.columns
    # print(type(d1col), len(d1col), d1col)
    # print(type(d2col), len(d2col), d2col)
    dcol = [each for each in d1col if each in d2col]
    # print(len(dcol), dcol)

    d1fix = d1[dcol]
    d2fix = d2[dcol]
    d = d1fix.append(d2fix)
    return d

def describeData(data, cols='result'):
    data.describe()
    if cols:
        group = data[cols].groupby(data[cols])
        print(group.count())
        return group
    return None

def percent2float(data):
    sd = data.shape
    for i in range(sd[0]):
        for j in range(sd[1]):
            strd = str(data.iloc[i,j])
            if strd.find("%") != -1:
                data.iloc[i,j] = float(strd[:strd.find("%")])/100
    return data

def standard(data, cols=None):  #not standard the col columns
    data = data.reset_index(drop=True)
    outside = None
    if cols:
        datac = data.columns
        datac = [each for each in datac if each not in cols]
        outside = pd.DataFrame(data[cols])
        data = data[datac]
    ss = StandardScaler()
    scaler = ss.fit(data)
    data = pd.DataFrame(scaler.transform(data), columns=data.columns)
    # print(outside, data)
    # print(outside.shape, data.shape)
    if outside is not None:
        data = pd.concat([outside,data], axis=1)
    return data, scaler  #数据和标准化对象

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

def gen_result(data, gentype=None, err=0.001):  #gentype:None-210 sheng-10 ping-10 fu-10
    data['host_score'] = pd.to_numeric(data['host_score'], errors='raise')
    data['guest_score'] = pd.to_numeric(data['guest_score'], errors='raise')
    if not gentype:
        tt = lambda x: 0 if x['host_score']<x['guest_score']-err else 2 if x['host_score']>x['guest_score']+err else 1
    elif gentype == "sheng":
        tt = lambda x: 1 if x['host_score'] > x['guest_score'] else 0
    elif gentype == "ping":
        tt = lambda x: 1 if x['host_score'] == x['guest_score'] else 0
    elif gentype == "fu":
        tt = lambda x: 1 if x['host_score'] < x['guest_score'] else 0
    if 'result' in data.columns:
        data = data.drop('result',axis=1)
    data.insert(0,'result',data.apply(tt, axis=1))
    return data

def str2int(data, cols=None):  #将字符串转换为数字表示
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

def data_auguments(data, samplerowcount=10, augcount=10000, augtype=["mean", "max", "min"]):
    result = pd.DataFrame()
    if not augcount:
        augcount = data.shape[0] * 2

    alldata = []
    newdata = pd.DataFrame()
    for i in range(augcount):
        try:
            index = rd.randint(3, samplerowcount)
            temp = data.sample(index)
            augid = rd.randint(0,len(augtype)-1)
            newdata = newdata.append(temp.apply(augtype[augid]), ignore_index=True)

            if (i+1)%1000 == 0 or i == augcount-1:
                alldata.append(newdata)
                # print([each.shape for each in alldata])
                newdata = pd.DataFrame()
                print("generate %s rows"%i)

        except Exception as ex:
            print("error in %s row:"%i, ex)
            continue
    for each in alldata:
        result = result.append(each)

    return result


def sep_data_auguments(data, samplerowcount=10, augcount=[10000,10000,10000,10000]):
    result = pd.DataFrame()
    data1 = gen_result(data)
    rcol = data1['result']
    rvalue = sorted(list(set(rcol)))
    if len(rvalue) != len(augcount)-1:
        print(len(rvalue), len(augcount)-1)
        raise("The split data should have the same lengh-1 with the augcount.")

    splitdata = [data1[data1['result'] == each] for each in rvalue]
    # print([each.shape for each in splitdata])
    # augtype = rd.randint(0,4)
    augdata = [data_auguments(splitdata[i], samplerowcount, augcount[i]) for i in range(len(splitdata))]
    augdataall = data_auguments(data, samplerowcount, augcount[-1])
    print(augdataall.shape)
    for each in augdata:
        # print(each.shape)
        result = result.append(each)
    result = result.append(augdataall)
    return result

def drop_error_data(data, cols=None, valueset=None): #删除包含字符串的行
    for each in cols:
        data = data[data[each].astype('str').str.contains(od.NUMBER_RE)]
        data[each] = data[each].astype('float')
    return data


def handle_file(ifname, ofname, *type, withtestdata=14, convertcolumns=None, gentype=None, augc = od.AUGCOUNT[0]):  # preprocess the file
    if "xls" in ifname:
        d = pd.read_excel(ifname)
    else:
        d = pd.read_csv(ifname)
    # print(d.dtypes)
    for each in type:
        if "nan" == each:
            print("Processing the nan value.")
            d = process_nan(d)
        if "std" == each:
            print("Standarding the data.")
            d = standard(d, cols=['result'])[0]
        if "p2f" == each:  #percent to float
            print("Converting the percentage to float value.")
            d = percent2float(d)
        if "gen" == each:  #generate the results
            print("Generating the results.")
            d = gen_result(d, gentype)
        if "s2i" == each:  #gamename to integer
            print("Converting the columns from string to integer.")
            d = str2int(d, cols=convertcolumns)
        if "drop" == each:
            print("Droping the columns not used.")
            d = drop_error_data(d, cols=['host_score','guest_score'])
        if "dc" == each:  #drop columns
            dc = ["id", "game_name", 'year', 'game_time', 'round', "host_last_rank",
                  "guest_last_rank", 'host_name', 'guest_name', 'full_host_name', 'full_guest_name']
            d = drop_columns(d, dc=dc)
        if "da" == each:
            print("Augmenting the data.")
            sc = 8
            augc = 1000000
            if withtestdata:
                x = d.iloc[:-withtestdata,:]
                y = d.iloc[-withtestdata:,:]
                x = data_auguments(x, samplerowcount=sc, augcount=augc)
                d = joindata(d, x)
                d = joindata(d, y)
            else:
                r = data_auguments(d, samplerowcount=sc, augcount=augc)
                d = joindata(d, r)
        if 'sda' == each:
            print("Separately augmenting the data.")
            sc = 100

            if withtestdata:
                x = d.iloc[:-withtestdata, :]
                y = d.iloc[-withtestdata:, :]
                x = sep_data_auguments(x, samplerowcount=sc, augcount=augc)
                d = joindata(d, x)
                d = joindata(d, y)
            else:
                r = sep_data_auguments(d, samplerowcount=sc, augcount=augc)
                d = joindata(d, r)
    print("data has shape with", d.shape)
    # describeData(d, 'result')
    if "xls" in ofname:
        d.to_excel(ofname, index=False)
    else:
        d.to_csv(ofname, index=False)

def main():
    #预处理顺序'p2f', 'dc', 'drop', 'sda','gen', 'nan', 'std'
    #'host_name', 'guest_name', 'full_host_name', 'full_guest_name'
    ModelFILE, TrainFILE, TestFILE, ResultFILE = od.gen_file_name()
    # handle_file('basedata/trainandtest.xls', 'basedata/trainandtest.csv', 'p2f', 'dc','drop')
    handle_file('basedata/trainandtest.csv', TrainFILE, 'sda', 'gen', 'nan', 'std')
    # d = pd.read_excel('basedata/train2r.xls')
    # sep_data_auguments(d)
if __name__ == "__main__":
    main()