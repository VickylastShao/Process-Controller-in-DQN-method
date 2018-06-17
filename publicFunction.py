
import pymysql.cursors
import numpy as np
from keras.layers.core import Dense
from keras.models import Sequential
from keras.optimizers import SGD,Adam,RMSprop,Adagrad,Adadelta,Nadam,Adamax
from keras.layers import Activation
from keras.models import model_from_json
import os
import pandas as pd
import random
import datetime
import time
import matplotlib.pyplot as plt
import json
from xlwt import Workbook

def saveStructure(model,name):
    model_json = model.to_json()
    while 1:
        try:
            with open(name+'Model.json', "w") as json_file:#保存模型的json文件(结构)
                json_file.write(model_json)
            json_file.close()
            break
        except:
            pass


def saveWeight(model,name):
    modelweight = model.get_weights()
    weight = []
    for i in range(len(modelweight)):
        weight.append(modelweight[i].tolist())
    while 1:
        try:
            # 用于matlab
            with open(name+'Weight.json', 'w') as file_object:#保存权重的json文件
                json.dump(weight, file_object)

            # 用于python
            model.save_weights(name+'Weight.h5')  # 保存模型的h文件(权重)

            break
        except:
            pass


def loadModelWeight(model,name):
    while 1:
        try:
            model.load_weights(name+'Weight.h5')
            break
        except:
            pass
    return model

def getModelStructureWeight(name):
    while 1:
        try:
            json_file = open(name+'Model.json', 'r')#读取结构json文件
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(name+'Weight.h5')#读取结构h文件
            break
        except:
            pass
    return model

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'matlabrealtime',#数据库名称
    'charset': 'gbk',
    'cursorclass': pymysql.cursors.DictCursor,
}


# def getCols(TableName):
#     connection = pymysql.connect(**config)
#     try:
#         with connection.cursor() as cursor:
#             sql = 'SHOW FULL COLUMNS FROM '+TableName
#             cursor.execute(sql)
#             result = cursor.fetchall()
#             colsNumber=len(result)
#     finally:
#         connection.close()
#     return colsNumber

# def getMinIndex(TableName):
#     connection = pymysql.connect(**config)
#     try:
#         with connection.cursor() as cursor:
#             sql = 'select min(myindex) from ' + TableName + ' where myindex!=1 '
#             cursor.execute(sql)
#             result = cursor.fetchall()
#             minIndex=result[0]['min(myindex)']
#             if minIndex==None:
#                 minIndex=0
#     finally:
#         connection.close()
#     return minIndex

# def getMaxIndex(TableName):
#     connection = pymysql.connect(**config)
#     try:
#         with connection.cursor() as cursor:
#             sql = 'select max(myindex) from ' + TableName + ' where myindex!=1 '
#             cursor.execute(sql)
#             result = cursor.fetchall()
#             maxIndex = result[0]['max(myindex)']
#             if maxIndex == None:
#                 maxIndex = 0
#     finally:
#         connection.close()
#     return maxIndex

def getDataSet(TableName):
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * from '+TableName
            cursor.execute(sql)
            result = cursor.fetchall()
            frame = pd.DataFrame(list(result))
    finally:
        connection.close()

    # [Qstate, Qaction, NextQstate]
    Qstate=np.array(frame[['s1','s2','s3']])
    Qaction=np.array(frame[['a1']])
    NextQstate=np.array(frame[['ns1','ns2','ns3']])
    return [Qstate, Qaction, NextQstate]


def getSQL(TableName,colname):
    output = []
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM '+ TableName
            cursor.execute(sql)
            result = cursor.fetchall()
            results=list(result)
            for r in results:
                for col in colname:
                    output.append(r.get(col, 0))
            # sql提交事务,如果没有执行该语句,那上面操作对数据库的修改就是无效的
    finally:
        connection.commit()
        connection.close()
    return np.array(output).reshape(1,len(colname))


def insertSQL(TableName,actions,colname):
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = 'INSERT INTO '\
                  +TableName\
                  +'('+ ','.join(str(col) for col in colname) +')' \
                  +  ' value (' + ','.join(str(action) for action in actions) +')'
            cursor.execute(sql)
            cursor.fetchall()
            # sql提交事务,如果没有执行该语句,那上面操作对数据库的修改就是无效的
    finally:
        connection.commit()
        connection.close()
    return 1


def updateSQL(TableName,actions,colname):
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:

            sql = 'UPDATE '+TableName+' SET '+ ','.join(str(colname[index])+'='+str(actions[index]) for index in range(len(colname)))

            cursor.execute(sql)
            cursor.fetchall()
            # sql提交事务,如果没有执行该语句,那上面操作对数据库的修改就是无效的
    finally:
        connection.commit()
        connection.close()
    return 1




def toXls(Data,Name):
    nrows=Data.shape[0]
    ncols = Data.shape[1]

    book = Workbook()
    sheet1 = book.add_sheet('Sheet 1')
    for i in range(nrows):
        for j in range(ncols):
            sheet1.write(i,j,Data[i,j])
    book.save(Name+'.xls')




def loaddataExistinOneCell():
    while 1:
        try:
            json_file = open('dataExistinOneCell.json', 'r')#读取结构json文件
            jsonstring = json_file.read()
            json_file.close()
            break
        except:
            pass
    dataExistinOneCell = np.array(json.loads(jsonstring)['dataExistinOneCell'])
    return dataExistinOneCell




stateDim=3
actionDim=1



PolicyModelStructure={
    'nodes':[12, 6,3,actionDim],
    'activation':['selu','selu','selu','sigmoid']
}

QModelStructure={
    'nodes':[8,4,1],
    'activation':['selu','selu','sigmoid']
}

conditionBaseFilterCFG={
    'DecisionCycle':10, # 数据处理周期/秒
    'conditionCFG' : {
        'paralist':['s1','s2','s3','a1'],
        's1_From':0.5,
        's1_to':1.5,
        's1_cellNum':10,
        's2_From':0,
        's2_to':2,
        's2_cellNum':10,
        's3_From':0,
        's3_to':0.5,
        's3_cellNum':10,
        'a1_From':-1,
        'a1_to':1,
        'a1_cellNum':10,
    },
    'maxDataNuminOneCell':20
}

QmodelCFG={
    'actionSampleNum':100,
    'alpha':0.8,
    'gamma':0.5,
    'DecisionCycle':10, # 数据处理周期/秒
    'batch_size':500,
    'epochs':1000
}

PolicymodelCFG={
    'statesSampleNumperDim':25,
    'actionSampleNum':500,
    'DecisionCycle':10, # 数据处理周期/秒
    'batch_size':500,
    'epochs':1000
}


actionMin=-0.5
actionMax=0.5



def getCFG(cfgname):
    if cfgname=='mysqlconfig':
        return config
    elif cfgname=='conditionBaseFilterCFG':
        return conditionBaseFilterCFG
    elif cfgname=='QModelStructure':
        return QModelStructure
    elif cfgname=='PolicyModelStructure':
        return PolicyModelStructure
    elif cfgname=='stateDim':
        return stateDim
    elif cfgname=='actionDim':
        return actionDim
    elif cfgname =='QmodelCFG':
        return QmodelCFG
    elif cfgname =='PolicymodelCFG':
        return PolicymodelCFG
    elif cfgname =='actionMin':
        return actionMin
    elif cfgname =='actionMax':
        return actionMax

    else:
        return 'not found cfg'




def selu(x):
    alpha = 1.6732632423543772848170429916717
    scale = 1.0507009873554804934193349852946
    x_p = scale * x * (x>0.0)
    x_m = scale * (alpha * (np.exp(x * (x<=0.0)) - 1))
    return x_p+x_m

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def activity(x,activityname):
    if activityname=='sigmoid':
        return sigmoid(x)
    elif activityname=='selu':
        return selu(x)


def relu_Derivative(z):

    alpha = 1.6732632423543772848170429916717
    scale = 1.0507009873554804934193349852946

    z_p = scale * (z > 0.0)

    z_m = scale * alpha * np.exp(z) * (z <= 0.0)

    return z_p+z_m


def sigmoid_Derivative(z):

    y=1/(1+np.exp(-z))

    return y*(1-y)


def activity_Derivative(z,activityname):
    if activityname=='sigmoid':
        return sigmoid_Derivative(z)
    elif activityname=='selu':
        return relu_Derivative(z)



def argmax(state,actionMin,actionMax,Qmodel,weight,QModelStructure):


    # 基于梯度的方法

    initialactionsamplenum=11
    actionlist = np.linspace(actionMin, actionMax, num=initialactionsamplenum).reshape(initialactionsamplenum, 1)
    statelist = np.tile(state, (initialactionsamplenum, 1))
    inputlist = np.hstack((statelist, actionlist))
    Qvalue = Qmodel.predict(inputlist).tolist()
    maxIndex=Qvalue.index(max(Qvalue))
    bestaction=actionlist[maxIndex, 0]

    QActionIter = bestaction
    maxQAction = bestaction
    alpha=0.5
    dydx_finial=1

    dydxlimit=0.1/alpha

    maxQ=-1

    round=0

    input=np.zeros((1,4),dtype=np.float)
    input[0, 0] = state[0]
    input[0, 1] = state[1]
    input[0, 2] = state[2]

    layerNum=len(QModelStructure['nodes'])

    derinput = np.array([0, 0, 0, 1]).reshape(1, 4)

    while(abs(dydx_finial)>0.0001 and round<1000):

        round+=1

        input[0, 3] = QActionIter

        y = []
        z = []
        y.append(input)

        for i in range(layerNum):

            z.append(np.dot(y[i], weight[2 * i]) + weight[2 * i + 1])

            y.append(activity(z[i], QModelStructure['activation'][i]))


        dydx=[]
        dzdx=[]

        dydx.append(derinput)

        for i in range(layerNum):
            dzdx.append(np.dot(dydx[i], weight[2*i]))
            dydx.append(dzdx[i] * activity_Derivative(z[i],QModelStructure['activation'][i]))

        dydx_finial=dydx[layerNum]


        if dydx_finial>dydxlimit:
            dydx_finial=dydxlimit
        elif dydx_finial<-dydxlimit:
            dydx_finial = -dydxlimit


        maxQAction = QActionIter
        maxQ = y[-1]

        QActionIter = QActionIter+alpha * dydx_finial


        if QActionIter<actionMin:
            break
        if QActionIter>actionMax:
            break

    return maxQAction,maxQ



def objective(Qmodel,state,actions,Npop):
    statelist = np.tile(state, (Npop, 1))
    inputlist = np.hstack((statelist, actions))
    Qvalue = Qmodel.predict(inputlist)
    return Qvalue

def argmax2(state, actionMin, actionMax, Qmodel, weight, QModelStructure):

    Ximin=actionMin
    Ximax=actionMax

    Npop=5
    wmax = 0.9  # inertia    weight
    wmin = 0.1
    c1 = 2 #acceleration
    c2 = 2 #acceleration

    # creating    initial    position and velocity
    x = np.random.rand(Npop).reshape(Npop,1)*(Ximax-Ximin)+Ximin

    delta2 = 0.1

    v = np.random.rand(Npop,1) * ((Ximax + delta2) - (Ximin - delta2)) + (Ximin - delta2 - x)

    # Movement of the Particles

    object = objective(Qmodel,state,x,Npop)
    pbest = np.hstack((x, object))

    maxindex = object.argmax()
    maxvalue = object[maxindex]

    gbest=np.array([x[maxindex],maxvalue])

    ITERA_N = 10
    itera = 0
    r = 0.54

    while(itera <= ITERA_N):

        itera = itera + 1

        h1 = np.random.rand()
        h2 = np.random.rand()

        w = wmax - ((wmax - wmin) / ITERA_N) * itera # 混沌惯性权重
        r = 4.0 * r * (1 - r)
        w = w * r

        for i in range(Npop):
            # Position Modification Considering Constraints
            v[i] = w * v[i] + c1 * h1 * (pbest[i,0] - x[i]) + c2 * h2 * (gbest[0] - x[i])
            x[i] = x[i]+ v[i]

            # Crossover Operation
            if (np.random.rand() > 0.6):
                x[i] = pbest[i,0]

            if (x[i] < Ximin):
                x[i]= Ximin

            if (x[i] > Ximax):
                x[i] = Ximax

        # Update   of  Pbest and Gbest
        object = objective(Qmodel,state,x,Npop)
        maxindex = object.argmax()
        maxvalue = object[maxindex]

        # 更新pbest
        for i in range(Npop):
            if object[i] > pbest[i, 1]:
                pbest[i, 0] = x[i,:]
                pbest[i, 1] = object[i]

        # 更新gbest
        if maxvalue > gbest[1]:
            gbest = np.array([x[maxindex], maxvalue])


    return gbest[0], gbest[1]













