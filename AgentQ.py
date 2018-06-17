from Offline_Agent_v2.publicFunction import *
from multiprocessing import Process, Manager
os.environ["CUDA_VISIBLE_DEVICES"] = "3"

def initialQModel(stateDim, actionDim):
    Qmodel = Sequential()
    Qmodel.add(Dense(QModelStructure['nodes'][0], input_dim=stateDim + actionDim))
    Qmodel.add(Activation(QModelStructure['activation'][0]))

    for i in range(len(QModelStructure['nodes']) - 1):
        Qmodel.add(Dense(QModelStructure['nodes'][i + 1]))
        Qmodel.add(Activation(QModelStructure['activation'][i + 1]))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    Qmodel.compile(loss='binary_crossentropy', optimizer=sgd)
    stateactionInitial = np.random.uniform(-1, 1, (100, stateDim + actionDim))
    valueInitial = np.zeros((100, 1), dtype=float)
    Qmodel.fit(stateactionInitial, valueInitial, batch_size=100, epochs=500, verbose=0,validation_split=0.1)

    saveStructure(Qmodel, 'Q')
    saveWeight(Qmodel, 'Q')

def initialPolicyModel(stateDim, actionDim):
    PolicyModel = Sequential()
    PolicyModel.add(Dense(PolicyModelStructure['nodes'][0], input_dim=stateDim))
    PolicyModel.add(Activation(PolicyModelStructure['activation'][0]))
    for i in range(len(PolicyModelStructure['nodes']) - 1):
        PolicyModel.add(Dense(PolicyModelStructure['nodes'][i + 1]))
        PolicyModel.add(Activation(PolicyModelStructure['activation'][i + 1]))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    PolicyModel.compile(loss='mean_squared_error', optimizer=sgd)
    stateactionInitial = np.random.uniform(-1, 1, (100, stateDim))
    valueInitial = np.zeros((100, actionDim), dtype=float) + 0.5
    # output of PolicyModel is initialized to 0.5
    # so that the Policy is initialized to 0
    PolicyModel.fit(stateactionInitial, valueInitial, batch_size=100, epochs=500, verbose=0,validation_split=0.1)

    saveStructure(PolicyModel, 'Policy')
    saveWeight(PolicyModel, 'Policy')

def initialFullIndex(conditionBaseFilterCFG):

    conditionCFG = conditionBaseFilterCFG['conditionCFG']

    dataExistinOneCell = np.zeros((conditionCFG['s1_cellNum'], conditionCFG['s2_cellNum'],
                                   conditionCFG['s3_cellNum'], conditionCFG['a1_cellNum']), dtype=np.int16)

    fulldict = dict()
    fulldict['dataExistinOneCell'] = dataExistinOneCell.tolist()

    while 1:
        try:
            with open('dataExistinOneCell.json', 'w') as file_object:  # 保存权重的json文件
                json.dump(fulldict, file_object)
            break
        except:
            pass
    print('dataExistinOneCell.json  is updated')

    while 1:
        try:
            with open('conditionCFG.json', 'w') as file_object:  # 保存权重的json文件
                json.dump(conditionCFG, file_object)
            break
        except:
            pass
    print('conditionCFG.json  is updated')

# def initialreadytocollect():
#     readytocollect = dict()
#     readytocollect['readytocollect'] = 1
#     while 1:
#         try:
#             with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
#                 json.dump(readytocollect, file_object)
#             break
#         except:
#             pass
#     print('readytocollect.json  is updated')

def conditionBaseFilter(dt,a):

    config = getCFG('mysqlconfig')

    # 实际的强化学习任务面临着样本不平衡的问题 对Qmodel的估计效果不好

    # 这里的工况边界指的是state和action 不包含nextstate
    # 因为训练Qmodel的目的是获得state,action 到 Qvalue的映射
    # 为了避免训练样本的不平衡分布的问题需要将训练数据中的state,action分布均匀化
    conditionBaseFilterCFG = getCFG('conditionBaseFilterCFG')

    conditionCFG = conditionBaseFilterCFG['conditionCFG']

    BoundryList = []
    for i in range(len(conditionCFG['paralist'])):
        paraname = conditionCFG['paralist'][i]
        parafrom = conditionCFG[paraname + '_From']
        parato = conditionCFG[paraname + '_to']
        cellnum = conditionCFG[paraname + '_cellNum']
        BoundryList.append(np.linspace(parafrom, parato, num=cellnum + 1))

    maxDataNuminOneCell = conditionBaseFilterCFG['maxDataNuminOneCell']

    dataExistinOneCell = loaddataExistinOneCell()

    def conditionBaseFilter(pin, FromTable):

        # 读取新数据
        connection = pymysql.connect(**config)
        try:
            with connection.cursor() as cursor:
                sql = 'select * from ' + FromTable + ' where myindex!=1 and myindex>' + str(
                    pin) + ' order by myindex desc'
                cursor.execute(sql)
                result = cursor.fetchall()
                newcondition = pd.DataFrame(list(result))

        finally:
            connection.close()

        if (not newcondition.empty):

            # readytocollect = dict()
            # readytocollect['readytocollect'] = 0
            # while 1:
            #     try:
            #         with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
            #             json.dump(readytocollect, file_object)
            #         break
            #     except:
            #         pass

            pin = newcondition.max(axis=0)['myindex']  # 更新pin

            dataNuminOneCellperBatch = np.zeros((conditionCFG['s1_cellNum'], conditionCFG['s2_cellNum'],
                                                 conditionCFG['s3_cellNum'], conditionCFG['a1_cellNum']),
                                                dtype=np.int)

            conditionBase = dt['conditionBase']
            for index, row in newcondition.iterrows():

                templist = []
                templist.append(int(row['myindex']))
                templist.append(float(row['s1']))
                templist.append(float(row['s2']))
                templist.append(float(row['s3']))
                templist.append(float(row['a1']))
                templist.append(float(row['ns1']))
                templist.append(float(row['ns2']))
                templist.append(float(row['ns3']))

                # 找到当前数据的工况cell
                indexNow = [-1, -1, -1, -1]
                for i in range(4):
                    # 数据可能落在工况边界之外 如果在外面，则对应维度的index为-1
                    paraname = conditionCFG['paralist'][i]
                    paravalue = row[paraname]
                    parafrom = conditionCFG[paraname + '_From']
                    parato = conditionCFG[paraname + '_to']
                    cellnum = conditionCFG[paraname + '_cellNum']

                    if (paravalue >= parafrom and paravalue <= parato):
                        indexNow[i] = int((paravalue - parafrom) / ((parato - parafrom) / cellnum))
                        if indexNow[i] >= cellnum - 1:
                            indexNow[i] = cellnum - 1

                if min(indexNow) >= 0:  # 如果当前数据属于工况边界内 则累计排序本批次本cell数目 当数量没有超限 则插入数据库
                    dataNuminOneCellperBatch[indexNow[0], indexNow[1], indexNow[2], indexNow[3]] += 1

                    # 这个地方是如果有数据就为1 意思是存在数据
                    dataExistinOneCell[indexNow[0], indexNow[1], indexNow[2], indexNow[3]] = 1
                    # 原始数据是倒序的 所以本轮数据中当前工况cell数量超过maxDataNuminOneCell 后面的就不要往里面插入了 就算插进去 后面也是肯定要被删掉的
                    if dataNuminOneCellperBatch[
                        indexNow[0], indexNow[1], indexNow[2], indexNow[3]] <= maxDataNuminOneCell:

                        conditionBase[indexNow[0]][indexNow[1]][indexNow[2]][indexNow[3]].append(templist)
                        conditionBase[indexNow[0]][indexNow[1]][indexNow[2]][indexNow[3]].pop(0)


            dt['conditionBase']=conditionBase

            fulldict = dict()
            fulldict['dataExistinOneCell'] = dataExistinOneCell.tolist()

            while 1:
                try:
                    with open('dataExistinOneCell.json', 'w') as file_object:  # 保存权重的json文件
                        json.dump(fulldict, file_object)
                    break
                except:
                    pass

            # readytocollect['readytocollect'] = 1
            # while 1:
            #     try:
            #         with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
            #             json.dump(readytocollect, file_object)
            #         break
            #     except:
            #         pass


        return pin

    decisionCycle = conditionBaseFilterCFG['DecisionCycle']

    pin = 0

    while True:

        starttime = datetime.datetime.now()

        pin = conditionBaseFilter(pin, FromTable='history')

        endtime = datetime.datetime.now()

        TC = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1000000

        print(str(endtime) + ' —— ' +'condition Base Filtration Finished!'+' Time Consuming: %.2f' % (TC) + ' s')

        delayTime = decisionCycle - TC

        if (delayTime > 0):
            time.sleep(delayTime)


def trainQ(dt):
    # trainQ
    # 不断读取mysql历史数据，更新Qmodel并覆盖目录下的QWeight.json(权重) 和 QModel.h5(权重)


    QmodelCFG = getCFG('QmodelCFG')

    actionSampleNum = QmodelCFG['actionSampleNum']
    # GAMMA=0.5

    alpha = QmodelCFG['alpha']
    gamma = QmodelCFG['gamma']

    actionMin = getCFG('actionMin')
    actionMax = getCFG('actionMax')

    QModelStructure = getCFG('QModelStructure')

    Qmodel = getModelStructureWeight('Q')  # 读取目录下的QModel

    # coding: utf-8

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    rMSprop = RMSprop(lr=0.001, rho=0.9, epsilon=1e-06)
    adagrad = Adagrad(lr=0.01, epsilon=1e-06)
    adadelta = Adadelta(lr=1.0, rho=0.95, epsilon=1e-06)
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    nadam = Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=0.004)
    adamax = Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08)

    lossF = ['squared_hinge',
             'mean_squared_error',
             'binary_crossentropy'
             ]

    Qmodel.compile(loss=lossF[1], optimizer=adam)

    p1N = 10
    actionN = 10
    p1_fl = np.linspace(0.5, 1.5, num=p1N)
    pa_fl_m = np.linspace(-0.5, -0.1, num=actionN)
    pa_fl_p = np.linspace(0.1, 0.5, num=actionN)

    fzQinput = []
    fzQvalue = []
    for i in range(p1N):
        for j in range(actionN):
            fzQinput.append([p1_fl[i], 0, 0, pa_fl_m[j]])
            fzQvalue.append([0])
            fzQinput.append([p1_fl[i], 2, 0.5, pa_fl_p[j]])
            fzQvalue.append([0])
            fzQinput.append([p1_fl[i], 0, 0, pa_fl_p[j]])
            fzQvalue.append([1])
            fzQinput.append([p1_fl[i], 2, 0.5, pa_fl_m[j]])
            fzQvalue.append([1])

    forbiddenzoneQinput = np.array(fzQinput)
    forbiddenzoneQvalue = np.array(fzQvalue)

    actionlist = np.linspace(actionMin, actionMax, num=actionSampleNum).reshape(actionSampleNum, 1)

    def getR(state, action, Nextstate):
        # 设定值 测量值 流量
        stateErr = state[:, 0] - state[:, 1]  # 设定值减测量值
        stateErrR = 8 ** (-np.abs(8 * stateErr)).reshape(stateErr.shape[0], 1)  # 偏差反馈 0~1
        stateErrR = stateErrR * (1 - gamma)  # 0~(1-gamma) 为了保证Q值0~1 方便神经网络训练
        return stateErrR

        # actionR=4**(-np.abs(4*action[:,0])).reshape(action.shape[0],1)#动作反馈 0~1
        # actionR=actionR*(1-gamma)

        # NextstateErr=Nextstate[:,0]-Nextstate[:,1]#设定值减测量值
        # NextstateErrR = 8**(-np.abs(8*NextstateErr)).reshape(NextstateErr.shape[0],1)#偏差反馈 0~1
        # NextstateErrR = NextstateErrR * (1 - gamma)

        #
        # rateSet=Nextstate[:, 0] - state[:, 0]# 设定值变化率
        # rateReal=Nextstate[:, 1] - state[:, 1]# 实际值变化率
        # rateErr=rateSet-rateReal
        # rateErrR = 8 ** (-np.abs(8 * rateErr)).reshape(rateErr.shape[0], 1)
        # rateErrR = rateErrR * (1 - gamma)

        # rateErrR = 4 ** (-np.abs(4 * rateReal)).reshape(rateReal.shape[0], 1)
        # rateErrR = rateErrR * (1 - gamma)

        # rateErrR=10 ** (-np.abs(4 * rateErr)).reshape(rateErr.shape[0], 1)

        # actionR=np.zeros((err.shape[0],1),dtype=np.float)#动作反馈 -0.5~0.5
        #
        # for i in range(errR.shape[0]):
        #     if err[i]*action[i]>0:
        #         actionR[i]=1
        #     else:
        #         actionR[i]=0

        # return (7*errR+1*actionR)/8
        # (3 * stateErrR + 1 * actionR) / 4

        # return (2 * stateErrR + 1 * NextstateErrR) / 3

    def getMaxQ(state, Qmodel, weight):
        maxQAction, maxQ = argmax2(state, actionMin, actionMax, Qmodel, weight, QModelStructure)
        return maxQ
        # statelist = np.tile(state, (actionSampleNum, 1))
        # inputlist = np.hstack((statelist, actionlist))
        # Qvalue = Qmodel.predict(inputlist).tolist()
        # return max(Qvalue)

    def QLearning(Qstate, Qaction, NextQstate, Qmodel):

        # toXls(Qstate, 'Qstate')
        # toXls(Qaction, 'Qaction')
        # toXls(NextQstate, 'NextQstate')

        R = getR(Qstate, Qaction, NextQstate)

        # toXls(R, 'R')

        modelweight = Qmodel.get_weights()
        weight = []
        for i in range(len(modelweight)):
            weight.append(modelweight[i].tolist())

        nextQ = np.zeros((Qstate.shape[0], 1), dtype=np.float)
        for i in range(Qstate.shape[0]):
            nextQ[i] = getMaxQ(NextQstate[i, :], Qmodel, weight)

        # Q学习迭代公式

        # toXls(nextQ, 'nextQ')

        # 原始的Q值迭代公式
        # Qvalue = (1 - GAMMA) * R + GAMMA * nextQ

        # 新的Q值迭代公式
        currentQ = Qmodel.predict(np.hstack((Qstate, Qaction)))

        Qvalue = currentQ + alpha * (R + gamma * nextQ - currentQ)

        # toXls(Qvalue, 'Qvalue')

        return Qvalue

    def trainQModel(Qmodel,conditionBase):

        conditionNum=conditionCFG['s1_cellNum']*conditionCFG['s2_cellNum']*conditionCFG['s3_cellNum']*conditionCFG['a1_cellNum']

        conditionBase = np.array(conditionBase).reshape(conditionNum*maxDataNuminOneCell, 8)

        conditionBase = np.delete(conditionBase, np.where(conditionBase[:,0] == 0), axis = 0)

        err=-1

        usefuldatanum=conditionBase.shape[0]

        if (usefuldatanum>=int(conditionNum*maxDataNuminOneCell*0.1)):

            Qstate = conditionBase[:, 1:4]
            Qaction = conditionBase[:, 4:5]
            NextQstate = conditionBase[:, 5:8]


            Qinput = np.hstack((Qstate, Qaction))
            Qvalue = QLearning(Qstate, Qaction, NextQstate, Qmodel)

            # # initial forbiddenzone
            # for i in range(Qinput.shape[0]):
            #     if Qinput[i,1]==0 and Qinput[i,2]==0 and Qinput[i,3]<0:
            #         Qvalue[i,0] = 0
            #     elif Qinput[i,1]==2 and Qinput[i,2]==0.5 and Qinput[i,3]>0:
            #         Qvalue[i, 0] = 0
            #     if Qinput[i,1]==0 and Qinput[i,2]==0 and Qinput[i,3]>0:
            #         Qvalue[i,0] = 1
            #     elif Qinput[i,1]==2 and Qinput[i,2]==0.5 and Qinput[i,3]<0:
            #         Qvalue[i, 0] = 1
            #
            #
            # # added forbiddenzone
            # Qinput=np.row_stack((Qinput, forbiddenzoneQinput))
            # Qvalue = np.row_stack((Qvalue, forbiddenzoneQvalue))

            hist = Qmodel.fit(Qinput, Qvalue, batch_size=QmodelCFG['batch_size'], verbose=0,epochs=QmodelCFG['epochs'])

            err=hist.history.get('loss')[-1]

            # plt.plot(hist.history.get('loss'))
            # plt.show()

            saveWeight(Qmodel, 'Q')

        return Qmodel,err,usefuldatanum  # 只负责更新覆盖现有的QModel

    decisionCycle = QmodelCFG['DecisionCycle']  # 训练周期/秒

    while 1:

        starttime = datetime.datetime.now()

        conditionBase=dt['conditionBase']

        Qmodel,err,usefuldatanum = trainQModel(Qmodel,conditionBase)

        endtime = datetime.datetime.now()

        TC = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1000000

        print(str(endtime) + ' —— ' + 'Traing QModel Finished! Err:'+str(err) + ' UDN:'+str(usefuldatanum)+' Time Consuming: %.2f' % (TC) + ' s')

        delayTime = decisionCycle - TC

        if (delayTime > 0):
            time.sleep(delayTime)

def initial(conditionBaseFilterCFG,stateDim,actionDim):

    initialPolicyModel(stateDim, actionDim)

    initialQModel(stateDim, actionDim)

    initialFullIndex(conditionBaseFilterCFG)

    # initialreadytocollect()

    print('----------------------------------------')
    print('QModel is initialized')
    print('PolicyModel  is initialized')
    print('dataExistinOneCell.json  is initialized')
    # print('readytocollect.json  is initialized')
    print('========================================')

if __name__ == "__main__":

    conditionBaseFilterCFG = getCFG('conditionBaseFilterCFG')
    maxDataNuminOneCell = conditionBaseFilterCFG['maxDataNuminOneCell']
    conditionCFG = conditionBaseFilterCFG['conditionCFG']
    stateDim = getCFG('stateDim')
    actionDim = getCFG('actionDim')

    initial(conditionBaseFilterCFG,stateDim,actionDim)

    manager = Manager()
    dt = manager.dict()
    dt['conditionBase'] = np.zeros((conditionCFG['s1_cellNum'],
                   conditionCFG['s2_cellNum'],
                   conditionCFG['s3_cellNum'],
                   conditionCFG['a1_cellNum'], maxDataNuminOneCell, 1+stateDim+actionDim+stateDim), dtype=np.float).tolist()

    p1 = Process(target=conditionBaseFilter, args=(dt,1))
    p1.start()

    trainQ(dt)

    p1.join()
