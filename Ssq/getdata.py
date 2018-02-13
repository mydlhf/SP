import pandas as pd
import numpy as np
#import tensorflow as tf
import matplotlib.pyplot as plt
LINESIZE = 33
JOINNUM = 30
RATE = 0.9
def getlabels(matrix, inputrowcount, rowsize):
    msize = np.size(matrix)
    result = []
    inputdata = np.reshape(matrix, (1,msize))
    print (len(inputdata[0]))
    for i in range(0,int(msize/rowsize-inputrowcount*rowsize)):
        begin = rowsize*(i+inputrowcount)
        end = rowsize*(i+inputrowcount+1)
        temp = inputdata[0][begin:end]
        #print temp
        #result.append(temp) #以整行作为预测结果
        result.append(sum(temp)) #以整行的和作为预测结果
    #print result
    #print len(result)
    return result
         
def getimages(matrix,inputrowcount, rowsize):
    msize = np.size(matrix)
    #print msize
    result = []
    inputdata = np.reshape(matrix, (1,msize))
    print (len(inputdata[0]))
    for i in range(0,int(msize/rowsize-inputrowcount*rowsize)):
        begin = rowsize*i
        end = rowsize*(i+inputrowcount)
        #print begin, end
        temp = inputdata[0][begin:end]
        #print temp
        result.append(temp)
    #print inputdata.reshape()
    return result


def write32(bytestream, data, datatype=np.uint32):
    dt = np.dtype(datatype).newbyteorder('>')
    #np.getbuffer(bytestream.write(4), dtype=dt)
    ndata = np.array(data, dtype=dt)
    ndata.tofile(bytestream)

def array2idx(array, magicnum, filename, isimage=True, rowsize=6, columnsize=6):
    lenarray = len(array)
    print (lenarray)
    #print lenarray, len(array[0])
    f = open(filename, 'wb')
    write32(f,[magicnum])
    write32(f,[lenarray])
    if(isimage):
        write32(f,[rowsize])  #size of lines, original is rowsize*2
        write32(f,[columnsize])  #the size of columns, original is columnsize*2
        write32(f,array)
    #print array
    else:
        write32(f,array,np.uint8)
    f.close()

def array2vec(alist, vsize=33): #[1,3,5,7,9,11]-->[10101010100000000...] count: vsize
    result = np.zeros((vsize,))
    result[alist-1] = 1
    result.astype(np.uint8)
    return result

def arrays2vecs(data):    #all arrays to vectors
    results = []
    for each in data:
        results.append(array2vec(each))
    return np.concatenate(results)

#vectors split into lines with each line size 33, and join every 10 lines to 1 line
def getimageandlabel(vecs, linesize=33, joinnum=10):  
    allsize = len(vecs)
    linecount = int(allsize/linesize)
    splitvecs = vecs.reshape(linecount,linesize)
    imagevecs = splitvecs[:linecount-joinnum+1]
    labelvecs = splitvecs[joinnum:] #shape:[linecount-joinnum,linesize]

    for i in range(joinnum-1):
        imagevecs = np.concatenate((imagevecs,splitvecs[i+1:linecount-joinnum+1+i+1]), axis=1)
    imagevecs = imagevecs[:-1]
    return imagevecs, labelvecs
#    print(imagevecs) #shape[linecount-joinnum+1, linesize*joinnum]
#    print(labelvecs)
#    print(imagevecs.shape)
#    print(labelvecs.shape)
#    plt.imshow(imagevecs)

def plotimage(bindata, count, columnsize): # all data with 1D, convert to image with RGB value
    transdata = bindata^1
    temp = ((transdata)*255).reshape(count*columnsize, 1)
    image = np.concatenate((temp,temp,temp),axis=1).reshape(count,columnsize,3)
    print(image)
    plt.imshow(image)
    plt.show()
        

def getData(fname="redandblue.xlsx", linesize=LINESIZE, joinnum=JOINNUM):
    data = pd.read_excel(fname)
    red = data.iloc[:,:6].as_matrix().astype(np.uint32)
    blue = data.iloc[:,6].as_matrix().astype(np.uint32)
    redvector = np.array(arrays2vecs(red)).astype(np.uint8)
    image, label = getimageandlabel(redvector, linesize, joinnum)
    return getTrainandTestData(image, label, RATE)

def getTrainandTestData(image, label, rate):
    size = len(image)
    tsize = int(size*rate)
    trainimage = image[:tsize]
    trainlabel = label[:tsize]
    testimage = image[tsize:]
    testlabel = label[tsize:]
    return trainimage, trainlabel, testimage, testlabel
#lenred = len(redvector)
#leninput = int(lenred * 8/9)
#inputred = redvector[:leninput]
#testred = redvector[leninput:]
#redimage = plotimage(redvector,int(lenred/33),33)
#redvector.reshape(33, lenred/33)
#array2idx(redimage, 2051, "allimages.bin", True, lenred/33, 33)
#with tf.Session() as sess:
#    image = tf.image.decode_jpeg(redimage)
##print(red[0], red[0][0])
##lenred = len(red)
#inputlenred = int(lenred * 0.8)
#inputred = red[:inputlenred]
#testred = red[inputlenred:]
#inputimage = getimages(inputred, 10, 6)
#inputlabel = getlabels(inputred, 10, 6)
#testimage = getimages(testred, 10, 6)
#testlabel = getlabels(testred, 10, 6)
##print inputdata,outputdata
#array2idx(inputimage,2051,"inputimages.bin", True,10,6)
#array2idx(inputlabel,2049,"inputlabels.bin", False,10,1)
#array2idx(testimage,2051,"testimages.bin", True,10,6)
#array2idx(testlabel,2049,"testlabels.bin", False,10,1)
#print ("done!")


    