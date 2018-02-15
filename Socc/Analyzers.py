import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression as LR
from sklearn import svm
from sklearn.model_selection import cross_val_predict as CP
from sklearn.utils import shuffle
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import SGD, Adagrad,RMSprop, Adamax, Nadam, Adam, Adadelta
from keras.utils import to_categorical
from keras import losses, regularizers
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, LearningRateScheduler
from keras import backend as K
from sklearn.decomposition import PCA
from sklearn.linear_model import RandomizedLogisticRegression as RLR
import Processors as proc
import Odatas as sd
# import tensorflow as tf
DFILE = "basedata/train1sample.xls"
FV = 3
EPTIME = 1000
BSIZE = 600
DATASPLIT = 0.9
SCOUNT = 10000
SRATE = 0.1
def getSparseValue(x, negvalue, posvalue):
    if x>posvalue:
        return 1
    elif x<negvalue:
        return -1
    return 0

def getData(fname, split=DATASPLIT, issample=1, isshuffle=True, dropcolumns=None, standard=True, tocategorical=True, filtercolumn=None):
    data = pd.read_excel(fname)
    if issample == 1:
        print("sampling with count!")
        data = proc.sample(data, samplecount=SCOUNT)
    elif issample == 2:
        print("sampling with rate!")
        data = proc.sample(data, rate=SRATE)
    if isshuffle:
        print("shuffling!")
        data = shuffle(data)
    # data = data.iloc[:3000,:]
    datacolumns = data.columns
    if dropcolumns:    #del not useful columns
        print("dropping the columns:", dropcolumns)
        for each in dropcolumns:
            if each in datacolumns:
                # print(each)
                data = data.drop(each, axis=1)
    print("filling nan!")
    data = data.fillna(data.mean())

    datalen = len(data)
    trainlen = int(datalen * split)

    xcol = list(data.columns)
    xcol.remove("result")
    if filtercolumn:
        print("filtering!")
        xcol = filtercolumn
    ycol = "result"
    # print(xcol, ycol)
    x = data[xcol]
    y = data[ycol]

    xtrain = x.iloc[:trainlen, :]
    ytrain = y.iloc[:trainlen]
    xtest = x.iloc[trainlen:, :]
    ytest = y.iloc[trainlen:]
    if standard:
        xtrain = pd.DataFrame(proc.standard(xtrain)[0])
        xtest = pd.DataFrame(proc.standard(xtest)[0])
    if tocategorical:
        ytrain = pd.DataFrame(to_categorical(ytrain, num_classes=FV))
        ytest = pd.DataFrame(to_categorical(ytest, num_classes=FV))

    # print(xtrain, ytrain, xtest, ytest)

    return xtrain, ytrain, xtest, ytest


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
    xtest = xtest.as_matrix()
    ytest = ytest.as_matrix()
    pre = model.predict(xtest)
    # ypre = K.argmax(pre, axis=-1)
    # y = K.argmax(ytest,axis=-1)
    rpre = []
    toppre = []
    for eachx in pre:
        rpre.append(np.argmax(eachx))
    toppre = pd.DataFrame(proc.k_argmax(pre))
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


def trainNN(xtrain, ytrain, xtest, ytest):
    print(xtrain.shape, ytrain.shape, xtest.shape, ytest.shape)
    modelfile = 'modelweight.model'  # 神经网络权重保存
    model = Sequential()  # 层次模型
    #32:85%
    model.add(Dense(60, input_dim=xtrain.shape[1], init='uniform',activation='relu'))#,kernel_regularizer=regularizers.l1(0.01))) # 输入层，Dense表示BP层
    # model.add(Dropout(0.6))
    # model.add(Dense(30, init='uniform',activation='relu'))  # 输出层

    model.add(Dense(FV, init='uniform',activation='softmax'))
    # optimizer = RMSprop(lr=0.000001)
    optimizer = SGD()
    model.compile(loss=myloss,#'binary_crossentropy', #'categorical_crossentropy',#
                  optimizer=optimizer,metrics=["acc",mymetrics]) # 编译模型
    early_stopping = EarlyStopping(monitor='val_loss', patience=6)
    scheduler = LearningRateScheduler(lr_scheduler)
    # for i in range(1000):
    model.fit(xtrain, ytrain, epochs=EPTIME, batch_size=BSIZE, verbose=2, validation_data=(xtest, ytest))#, callbacks=[early_stopping])#early_stopping])  # 训练模型1000次
        # lm = model.evaluate(xtest, ytest)
    predict(model, xtest, ytest)
        # print(lm)
    model.save('my_model_or1.h5')
    model.save_weights(modelfile)  # 保存模型权重





def testNN(xtest, ytest):
    model = load_model("my_model_or1_0.54.h5")
    lm = model.evaluate(xtest, ytest)
    # print(model.predict(xtest))

def main():
    dc = ["game_name", "host_score", "guest_score", 'year', 'game_time', 'round', "host_last_rank",
                   "guest_last_rank", 'host_name', 'guest_name', 'full_host_name', 'full_guest_name']

    d = getData(DFILE, dropcolumns=dc, standard=True, tocategorical=True)#, filtercolumn=sd.BCNAME)

    # findSupport(data, type="rlr")
    trainNN(d[0], d[1], d[2], d[3])
    # testNN(xtest, ytest)
main()
