from Offline_Agent_v2.publicFunction import *
# trainPolicy
# 不断读取最新的Qmodel，求解argmax(Qvalue(state,action))，生成PolicyModel建模样本
# 更新PolicyModel并覆盖目录下的PolicyModel.json(权重) 和 QModel.h5(权重)

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

Qmodel=getModelStructureWeight('Q')#获取Qmodel结构与最新权重

PolicyModel=getModelStructureWeight('Policy')#获取PolicyModel结构与最新权重



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


PolicyModel.compile(loss='mean_squared_error', optimizer=adam)



actionMin=getCFG('actionMin')
actionMax=getCFG('actionMax')

QModelStructure=getCFG('QModelStructure')

stateDim=getCFG('stateDim')
actionDim=getCFG('actionDim')

# 水位设定值 水位真实值 入水流量




PolicymodelCFG=getCFG('PolicymodelCFG')

statesSampleNumperDim=PolicymodelCFG['statesSampleNumperDim']
actionSampleNum=PolicymodelCFG['actionSampleNum']

conditionCFG = conditionBaseFilterCFG['conditionCFG']


statesperDim=np.zeros((statesSampleNumperDim,stateDim))



for i in range(stateDim):
    paraname = conditionCFG['paralist'][i]
    parafrom = conditionCFG[paraname + '_From']
    parato = conditionCFG[paraname + '_to']
    statesperDim[:,i]=np.linspace(parafrom, parato, num=statesSampleNumperDim)

statesSampleNum=statesSampleNumperDim**stateDim

states=np.zeros((statesSampleNum,stateDim),dtype=np.float)

for i1 in range(statesSampleNumperDim):
    for i2 in range(statesSampleNumperDim):
        for i3 in range(statesSampleNumperDim):
            stateindex=i1*statesSampleNumperDim**2+i2*statesSampleNumperDim+i3
            states[stateindex, 0] = statesperDim[i1, 0]
            states[stateindex, 1] = statesperDim[i2, 1]
            states[stateindex, 2] = statesperDim[i3, 2]




record=1


def trainPolicyModel(PolicyModel,Qmodel):

    bestAction=[]

    modelweight = Qmodel.get_weights()
    weight = []
    for i in range(len(modelweight)):
        weight.append(modelweight[i].tolist())

    def getMaxQaction(state,Qmodel,weight):

        maxQAction, maxQ = argmax2(state, actionMin, actionMax, Qmodel,weight, QModelStructure)

        return maxQAction

        # actionlist=np.linspace(actionMin, actionMax, num=actionSampleNum).reshape(actionSampleNum,1)
        # statelist=np.tile(state, (actionSampleNum, 1))
        # inputlist=np.hstack((statelist, actionlist))
        #
        # Qvalue=Qmodel.predict(inputlist)
        #
        # Qvalue=Qvalue.tolist()
        #
        # maxIndex=Qvalue.index(max(Qvalue))
        #
        # bestaction=actionlist[maxIndex, 0]
        #
        # return bestaction


    for i in range(statesSampleNum):
        bestAction.append(getMaxQaction(states[i,:], Qmodel,weight))
        if(i%(statesSampleNum/10)==0):
            print('datagenerating: %.0f' % (float(i)/float(statesSampleNum)*100)+' %')

    bestAction=np.array(bestAction).reshape(statesSampleNum,1)

    # toXls(states, 'states')
    # toXls(bestAction, 'bestAction')



    for i in range(states.shape[0]):
        if states[i,1]<=0.2 and states[i,2]<=0.05:
            bestAction[i, 0] = 0.5
        elif states[i,1]>=1.8 and states[i,2]>=0.45:
            bestAction[i, 0] = -0.5

    bestAction = bestAction + 0.5  # policymodel的输出层激活函数为sigmoid 一定要归一化到0~1的区间

    hist=PolicyModel.fit(states, bestAction, batch_size=PolicymodelCFG['batch_size'], epochs=PolicymodelCFG['epochs'])

    # plt.plot(hist.history.get('loss'))
    # plt.show()

    print('----------------------------------------')
    saveWeight(PolicyModel, 'Policy')
    global record
    saveWeight(PolicyModel, 'Records/Policy_' + str(record) + '_')
    record = record + 1
    print('----------------------------------------')

    return PolicyModel


decisionCycle=PolicymodelCFG['DecisionCycle'] #训练周期/秒


while 1:

    starttime = datetime.datetime.now()

    Qmodel = loadModelWeight(Qmodel, 'Q')

    PolicyModel=trainPolicyModel(PolicyModel,Qmodel)

    print('Traing PolicyModel Finished!')

    endtime = datetime.datetime.now()

    TC=(endtime - starttime).seconds + (endtime - starttime).microseconds / 1000000

    print("Time Consuming: %.2f" % (TC)+' s')

    delayTime=decisionCycle-TC

    print('==================' + str(endtime) + '====================')

    if(delayTime>0):
        time.sleep(delayTime)


















