from Offline_Agent_v2.publicFunction import *
# trainQ
# 不断读取mysql历史数据，更新Qmodel并覆盖目录下的QWeight.json(权重) 和 QModel.h5(权重)

os.environ["CUDA_VISIBLE_DEVICES"] = "3"

QmodelCFG=getCFG('QmodelCFG')

actionSampleNum=QmodelCFG['actionSampleNum']
# GAMMA=0.5

alpha=QmodelCFG['alpha']
gamma=QmodelCFG['gamma']

actionMin=getCFG('actionMin')
actionMax=getCFG('actionMax')

QModelStructure=getCFG('QModelStructure')

Qmodel=getModelStructureWeight('Q') # 读取目录下的QModel


# coding: utf-8

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
rMSprop = RMSprop(lr=0.001, rho=0.9, epsilon=1e-06)
adagrad=Adagrad(lr=0.01, epsilon=1e-06)
adadelta=Adadelta(lr=1.0, rho=0.95, epsilon=1e-06)
adam=Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
nadam=Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=0.004)
adamax=Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08)



lossF=['squared_hinge',
       'mean_squared_error',
       'binary_crossentropy'
       ]


Qmodel.compile(loss=lossF[1], optimizer=adam)



p1N=10
actionN=10
p1_fl = np.linspace(0.5, 1.5, num=p1N)
pa_fl_m = np.linspace(-0.5, -0.1, num=actionN)
pa_fl_p = np.linspace(0.1, 0.5, num=actionN)

fzQinput=[]
fzQvalue=[]
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

forbiddenzoneQinput=np.array(fzQinput)
forbiddenzoneQvalue=np.array(fzQvalue)


actionlist = np.linspace(actionMin, actionMax, num=actionSampleNum).reshape(actionSampleNum, 1)




def getR(state,action,Nextstate):
    #设定值 测量值 流量
    stateErr=state[:,0]-state[:,1]#设定值减测量值
    stateErrR=8**(-np.abs(8*stateErr)).reshape(stateErr.shape[0],1)#偏差反馈 0~1
    stateErrR=stateErrR*(1-gamma)# 0~(1-gamma) 为了保证Q值0~1 方便神经网络训练
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


def getMaxQ(state,Qmodel,weight):
    maxQAction, maxQ = argmax2(state, actionMin, actionMax, Qmodel,weight, QModelStructure)
    return maxQ
    # statelist = np.tile(state, (actionSampleNum, 1))
    # inputlist = np.hstack((statelist, actionlist))
    # Qvalue = Qmodel.predict(inputlist).tolist()
    # return max(Qvalue)


def QLearning(Qstate,Qaction,NextQstate,Qmodel):

    # toXls(Qstate, 'Qstate')
    # toXls(Qaction, 'Qaction')
    # toXls(NextQstate, 'NextQstate')

    R = getR(Qstate, Qaction, NextQstate)

    # toXls(R, 'R')

    modelweight = Qmodel.get_weights()
    weight = []
    for i in range(len(modelweight)):
        weight.append(modelweight[i].tolist())

    nextQ=np.zeros((Qstate.shape[0],1),dtype=np.float)
    for i in range(Qstate.shape[0]):
        nextQ[i] = getMaxQ(NextQstate[i,:], Qmodel,weight)

    # Q学习迭代公式

    # toXls(nextQ, 'nextQ')

    # 原始的Q值迭代公式
    # Qvalue = (1 - GAMMA) * R + GAMMA * nextQ

    # 新的Q值迭代公式
    currentQ = Qmodel.predict(np.hstack((Qstate, Qaction)))

    Qvalue=currentQ+alpha*(R+gamma*nextQ-currentQ)

    # toXls(Qvalue, 'Qvalue')

    return Qvalue

record=1

def trainQModel(Qmodel):

    [Qstate,Qaction,NextQstate] = getDataSet(TableName='conditionbase')

    Qinput = np.hstack((Qstate, Qaction))
    Qvalue = QLearning(Qstate,Qaction,NextQstate,Qmodel)

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


    hist = Qmodel.fit(Qinput, Qvalue, batch_size=QmodelCFG['batch_size'], epochs=QmodelCFG['epochs'])

    # plt.plot(hist.history.get('loss'))
    # plt.show()

    print('----------------------------------------')
    saveWeight(Qmodel, 'Q')
    global record
    saveWeight(Qmodel, 'Records/Q_'+str(record)+'_')
    record=record+1
    print('----------------------------------------')

    return Qmodel # 只负责更新覆盖现有的QModel

decisionCycle=QmodelCFG['DecisionCycle'] #训练周期/秒

while 1:

    starttime = datetime.datetime.now()

    Qmodel=trainQModel(Qmodel)

    print('Traing QModel Finished!')

    endtime = datetime.datetime.now()

    TC = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1000000

    print("Time Consuming: %.2f" % (TC) + ' s')

    delayTime = decisionCycle - TC

    print('====================' + str(endtime) + '===================')

    if(delayTime>0):
        time.sleep(delayTime)



