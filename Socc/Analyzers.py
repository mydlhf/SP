import pandas as pd
from sklearn.linear_model import LinearRegression as LR
from sklearn.model_selection import cross_val_predict as CP
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import SGD, Adagrad
from keras.utils import to_categorical
from keras import losses

def getSparseValue(x, negvalue, posvalue):
    if x>posvalue:
        return 1
    elif x<negvalue:
        return -1
    return 0


def getData(fname):
    data = pd.read_excel(fname)
    data = data.drop(["host_score", "guest_score","round",'game_time','year','guest_last_rank','host_last_rank'], axis=1)
    data = data.fillna(data.mean())
    datalen = len(data)
    trainlen = int(datalen * 0.9)
    xcol = list(data.columns)
    xcol.remove("result")
    ycol = "result"
    print(xcol, ycol)
    x = data[xcol]
    y = data[ycol].astype("int32")
    # y = to_categorical(y)
    # for each in x:
    #     # print(each, y[each].dtype)
    #     if x[each].dtype == 'object':
    #         # y[each] = y[each].str.strip("%").astype("float64")/100
    #         x = x.drop(each, axis=1)

    xtrain = x.iloc[:trainlen, :].as_matrix()
    ytrain = y.iloc[:trainlen].as_matrix()
    xtest = x.iloc[trainlen:, :].as_matrix()
    ytest = y.iloc[trainlen:].as_matrix()
    print(xtrain, ytrain)
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

def trainNN(xtrain, ytrain, xtest, ytest):
    print(xtrain.shape, ytrain.shape, xtest.shape, ytest.shape)
    modelfile = 'modelweight.model'  # 神经网络权重保存
    model = Sequential()  # 层次模型
    model.add(Dense(800, input_dim=xtrain.shape[1], init='uniform'))  # 输入层，Dense表示BP层
    model.add(Activation('relu'))  # 添加激活函数
    model.add(Dense(600, init='uniform',activation='relu'))  # 输出层
    model.add(Dropout(0.2))
    model.add(Dense(200, init='uniform', activation='relu'))  # 输出层
    model.add(Dropout(0.2))
    model.add(Dense(40, init='uniform', activation='relu'))  # 输出层
    model.add(Dropout(0.2))
    # model.add(Dense(100, init='uniform', activation='relu'))  # 输出层
    #
    # model.add(Dense(100, init='uniform', activation='relu'))  # 输出层
    #
    # model.add(Dense(200, init='uniform',activation='relu'))
    # model.add(Dense(100, init='uniform',activation='relu'))
    #
    # model.add(Dense(100, init='uniform', activation='relu'))  # 输出层
    #
    # model.add(Dense(100, init='uniform', activation='relu'))  # 输出层
    #
    # model.add(Dense(50, init='uniform',activation='relu'))
    model.add(Dense(1, init='uniform',activation='relu'))
    optimizer = Adagrad(lr=0.1)
    model.compile(loss=losses.mae,
                  optimizer=optimizer,metrics=['accuracy']) # 编译模型
    model.fit(xtrain, ytrain, nb_epoch=30000, batch_size=10)  # 训练模型1000次
    model.save('my_model.h5')
    model.save_weights(modelfile)  # 保存模型权重

def main():
    xtrain, ytrain, xtest, ytest = getData("data/all.xls")
    trainNN(xtrain, ytrain, xtest, ytest)

main()