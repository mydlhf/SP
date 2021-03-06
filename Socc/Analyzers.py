import pandas as pd
import numpy as np

from keras import initializers
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import SGD, Adagrad,RMSprop, Adamax, Nadam, Adam, Adadelta
from keras import losses, regularizers
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, LearningRateScheduler
from keras.layers.normalization import BatchNormalization
from keras import backend as K
from sklearn.decomposition import PCA
from sklearn.linear_model import RandomizedLogisticRegression as RLR
from sklearn.linear_model import LinearRegression as LR
from sklearn import svm
from sklearn.model_selection import cross_val_predict as CP
from sklearn.utils import shuffle
import os
import time
import xlwt
import xlrd
import Processors as proc
import Odatas as od
# import tensorflow as tf


FV = 3
EPTIME = 3
BSIZE = 300
DATASPLIT = 0.8
SAMPLECOUNT = 12000
SAMPLERATE = 1
LEARNRATE = 0.01

def to_result(fname, trainfile, testfile, cols=od.RESULTCOLUMN, tt="uni-standard", r=None, aug=od.AUGCOUNT[0]):
    wb = xlwt.Workbook(encoding='utf-8')
    st = wb.add_sheet("result", cell_overwrite_ok=True)
    if not os.path.exists(fname):
        for i in range(0, len(cols)):
            st.write(0, i, cols[i])
        wb.save(fname)

    d = pd.read_excel(fname)
    lend =len(d)
    result = {}
    result['TrainFileName'] = trainfile
    result['TestFileName'] = testfile
    result["FV"] = FV
    result["EpisodeTime"] = EPTIME
    result["BatchSize"] = BSIZE
    result["DataSPlit"] = DATASPLIT
    result["LearningRate"] = LEARNRATE
    result["TestType"] = tt
    result["AugmentFu"] =aug[0]
    result["AugmentPing"] = aug[1]
    result["AugmentSheng"] = aug[2]
    result["AugementCombine"] = aug[3]
    result["TestFirstEqu"], result[ "TestSecEqu"], result["TestTop2Equ"] = np.mean(r['fequ']), np.mean(r['sequ']), np.mean(r['top2equ'])
    result["Time"] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    result = pd.DataFrame([list(result.values())], columns=list(result.keys()))
    d = pd.concat([d,result], axis=0)
    d.to_excel(fname)



def getSparseValue(x, negvalue, posvalue):
    if x>posvalue:
        return 1
    elif x<negvalue:
        return -1
    return 0

#standard 1-整体标准化 2-分开标准化 0-不标准化；issample -1-不采样 1-按数量采样 2-按比率采样 0-按最小类别数量采样
def getTrainData(fname, split=DATASPLIT, issample=-1, isshuffle=True, dropcolumns=None, standard=0, tocategorical=True, filtercolumn=None, withtestdata=14):
    data = pd.read_csv(fname)

    if issample == 1:
        print("sampling with count!")
        data = proc.sample(data, samplecount=SAMPLECOUNT)
    elif issample == 2:
        print("sampling with rate!")
        data = proc.sample(data, rate=SAMPLERATE)
    elif issample == 0:
        print("sampling with minimum count!")
        data = proc.sample(data)

    # data = data.iloc[:3000,:]

    if dropcolumns:    #del not useful columns
        data = proc.drop_columns(data, dropcolumns)
    print("filling nan!")
    data = data.fillna(data.mean())

    # data = data.dropna()


    xcol = list(data.columns)
    xcol.remove("result")
    if filtercolumn:
        print("filtering!")
        xcol = filtercolumn
    ycol = "result"
    # print(xcol, ycol)
    x = data[xcol]
    y = data[ycol]


    if standard == 1:
        x = pd.DataFrame(proc.standard(x)[0])

    if withtestdata:
        xtest = x.iloc[-withtestdata:, :]
        ytest = y.iloc[-withtestdata:]
        x = x.iloc[:-withtestdata, :]
        y = y.iloc[:-withtestdata]

    if isshuffle:
        print("shuffling!")
        x = shuffle(x)
    dlen = len(x)
    trainlen = int(dlen * split)
    xtrain = x.iloc[:trainlen, :]
    ytrain = y.iloc[:trainlen]
    xval = x.iloc[trainlen:, :]
    yval = y.iloc[trainlen:]
    if standard == 2:
        xtrain = pd.DataFrame(proc.standard(xtrain)[0])
        xval = pd.DataFrame(proc.standard(xval)[0])
    if tocategorical:
        ytrain = pd.DataFrame(to_categorical(ytrain, num_classes=FV))
        yval = pd.DataFrame(to_categorical(yval, num_classes=FV))
        ytest = pd.DataFrame(to_categorical(ytest, num_classes=FV))

    # print(xtrain, ytrain, xtest, ytest)

    return xtrain, ytrain, xval, yval, xtest, ytest, data

def getTestData(fname, dropcolumns=None, standard=True, tocategorical=True, filtercolumn=None):
    data = pd.read_csv(fname)
    # data = data.iloc[:3000,:]

    if dropcolumns:    #del not useful columns
        data = proc.drop_columns(data, dropcolumns)
    print("filling nan!")
    data = data.fillna(data.mean())

    xcol = list(data.columns)
    xcol.remove("result")
    if filtercolumn:
        print("filtering!")
        xcol = filtercolumn
    ycol = "result"
    # print(xcol, ycol)
    x = data[xcol]
    y = data[ycol]

    xtest = x
    ytest = y
    if standard:
        xtest = pd.DataFrame(proc.standard(xtest)[0])
    if tocategorical:
        ytest = pd.DataFrame(to_categorical(ytest, num_classes=FV))

    return xtest, ytest

def computePrecision(x, y, negvalue, posvalue, lr):
    lenx = len(x)
    right = []
    for i in range(lenx):
        sparsex = getSparseValue(lr.predict(x[i].reshape(1,-1))[0], negvalue, posvalue)
        sparsey = y[i]
        # print(sparsex, sparsey)
        right.append(sparsex == sparsey)

    lenright = right.count(True)
    # print("lenright=%s, lenx=%s" %(lenright,lenx))
    return lenright/lenx



def trainLR(xtrain, ytrain, xtest, ytest):
    lr = LR()
    lr.fit(xtrain, ytrain)
    print(lr.predict(xtest))
    print(ytest)
    print(lr.score(xtest, ytest))

    results =[]
    for i in range(1,100):
        posvalue = i/100
        for j in range(1,100):
            negvalue = -j/100

            value = (posvalue, negvalue, computePrecision(xtest,ytest, negvalue, posvalue, lr),)
            print(value)
            results.append(value)
    results = sorted(results,key=lambda s:s[2],reverse=True)
    print(results)

def trainSVM(xtrain, ytrain, xtest, ytest):
    clf = svm.SVC()
    clf.fit(xtrain, ytrain)
    print(clf.predict(xtest))
    print(ytest)
    print(clf.score(xtest, ytest))

def lr_scheduler(epoch, lr_base = 0.01, epochs=20000, lr_power = 0.9, mode='power_decay'):

    if mode is 'power_decay':
        # original lr scheduler
        lr = lr_base * ((1 - float(epoch) / epochs) ** lr_power)
    if mode is 'exp_decay':
        # exponential decay
        lr = (float(lr_base) ** float(lr_power)) ** float(epoch + 1)
    # adam default lr
    if mode is 'adam':
        lr = 0.001

    if mode is 'progressive_drops':
        # drops as progression proceeds, good for sgd
        if epoch > 0.9 * epochs:
            lr = 0.0001
        elif epoch > 0.75 * epochs:
            lr = 0.001
        elif epoch > 0.5 * epochs:
            lr = 0.01
        else:
            lr = 0.1

    print('lr: %f' % lr)
    return lr

def predict(model, xtest, ytest):
    print(ytest)
    xtest = xtest.as_matrix()
    ytest = ytest.as_matrix()
    pre = model.predict(xtest)
    # ypre = K.argmax(pre, axis=-1)
    # y = K.argmax(ytest,axis=-1)
    rpre = []
    for eachx in pre:
        rpre.append(np.argmax(eachx))
    toppre = pd.DataFrame(proc.k_argmax(pre, k=2))
    rpre = pd.DataFrame(rpre)
    rpre.columns = ['ypre']
    toppre.columns = ['toppre1','toppre2']
    ry = []
    for eachy in ytest:
        ry.append(np.argmax(eachy))
    ry = pd.DataFrame(ry)
    ry.columns = ['y']
    # print(xtest, ytest)
    # print(pre)
    r = pd.concat([rpre, toppre, ry], axis=1)
    # print(r)
    r['equ'] = r['ypre'] == r['y']
    r['fequ'] = r['y'] == r['toppre1']
    r['sequ'] = r['y'] == r['toppre2']
    r['top2equ']  = r['fequ'] + r['sequ']
    print(pd.concat([pd.DataFrame(pre),r], axis=1))
    print(np.mean(r['equ']), np.mean(r['fequ']), np.mean(r['sequ']), np.mean(r['top2equ']))
    return r

def myloss(y, y_pre, e=0.8):
    l1 = K.categorical_crossentropy(y, y_pre)
    # print(np.mean(np.argmax(y_pre, axis=-1)))
    l2 = K.mean(K.cast(K.argmax(y_pre, axis=-1),'float32'))
    l3 = K.categorical_crossentropy(y_pre, K.ones_like(y_pre)/FV)
    return l1

def mymetrics(y, y_pre):
    a = K.in_top_k(y_pre,K.argmax(y, axis=-1), 2)
    # b = K.top_k_categorical_accuracy(y, y_pre, k=2)
    c = K.cast(K.equal(K.argmax(y, axis=-1), K.argmax(y_pre, axis=-1)), K.floatx())
    return a
    # return

def findSupport(alldata=None, type="pca"): #type="pca"and "rlr"
    if type == "pca":
        pca = PCA()
        pca.fit(alldata)
        print(pca.explained_variance_ratio_)
    elif type == "rlr":
        traindata = proc.to_matrix(alldata)

        rlr = RLR()
        rlr.fit(traindata[0], traindata[1])
        sup = rlr.get_support()
        scores = rlr.scores_
        print(scores)
        print(",".join("'" + alldata[0].columns[sup] + "'"))
        print(list(zip(alldata[0].columns[sup], scores)))


def trainNN(xtrain, ytrain, xval, yval, savemodel):
    print(xtrain.shape, ytrain.shape, xval.shape, yval.shape)
    modelfile = 'modelweight.model'  # 神经网络权重保存
    model = Sequential()  # 层次模型
    #32:85%
    # model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(128,
                    input_dim=xtrain.shape[1],
                    init='uniform',
                    # kernel_initializer='he_normal',#initializers.random_normal(stddev=0.01),
                    # bias_initializer = 'he_normal',
                    activation='relu'))#,kernel_regularizer=regularizers.l1(0.01))) # 输入层，Dense表示BP层
    model.add(BatchNormalization(momentum=0.9))
    # model.add(Dropout(0.6))
    model.add(Dense(64, init='uniform',activation='relu'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(64, init='uniform', activation='relu'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(32, init='uniform', activation='relu'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(16, init='uniform', activation='sigmoid'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(16, init='uniform', activation='tanh'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(8, init='uniform', activation='relu'))  # 输出层
    model.add(BatchNormalization(momentum=0.9))
    model.add(Dense(FV, init='uniform',activation='softmax'))
    # optimizer = (lr=0.000001)
    optimizer = SGD(lr=LEARNRATE)
    model.compile(loss=myloss,#'binary_crossentropy', #'categorical_crossentropy',#
                  optimizer=optimizer,metrics=["acc",mymetrics]) # 编译模型
    early_stopping = EarlyStopping(monitor='val_loss', patience=3)
    scheduler = LearningRateScheduler(lr_scheduler)
    # for i in range(1000):
    model.fit(xtrain, ytrain, epochs=EPTIME, batch_size=BSIZE, verbose=2, validation_data=(xval, yval))#, callbacks=[early_stopping])#early_stopping])  # 训练模型1000次
        # lm = model.evaluate(xtest, ytest)
    # predict(model, xtest, ytest)
        # print(lm)
    model.save(savemodel)
    model.save_weights(modelfile)  # 保存模型权重

def load_and_train(mname, xtrain, ytrain, xtest, ytest):
    model = load_model(mname, {'myloss': myloss, 'mymetrics': mymetrics})
    model.fit(xtrain, ytrain, epochs=EPTIME, batch_size=BSIZE, verbose=2,
              validation_data=(xtest, ytest))  # , callbacks=[early_stopping])#early_stopping])  # 训练模型1000次
    # lm = model.evaluate(xtest, ytest)
    predict(model, xtest, ytest)
    # print(lm)
    # model.save(MODELNAME+"1")


def testNN(mname, xtest, ytest):

    model = load_model(mname, {'myloss':myloss, 'mymetrics':mymetrics})
    r = predict(model, xtest, ytest)
    return r

def single_train():
    dc = ["host_score", "guest_score", ]
    # 'host_name', 'guest_name', 'full_host_name', 'full_guest_name'
    ModelFILE, TrainFILE, TestFILE, ResultFILE = od.gen_file_name()
    traind = getTrainData(TrainFILE, dropcolumns=dc, issample=-1, standard=0,
                          tocategorical=True)  # , filtercolumn=sd.BCNAME)
    proc.describeData(traind[6])
    trainNN(traind[0], traind[1], traind[2], traind[3], ModelFILE)
    print("test with uni-standard:")
    r = testNN(ModelFILE, traind[4], traind[5])
    to_result(ResultFILE, TrainFILE, TestFILE, r=r)
    # load_and_train(MODELNAME, traind[0], traind[1], traind[2], traind[3])
    # findSupport(data, type="rlr")
    print("test with separate standard:")
    testd = getTestData(TestFILE, dropcolumns=dc)
    r = testNN(ModelFILE, testd[0], testd[1])
    to_result(ResultFILE, TrainFILE, TestFILE, tt="sep-standard", r=r)

def main():
    single_train()

if __name__ == "__main__":
    main()
