from Offline_Agent_v2.publicFunction import *

os.environ["CUDA_VISIBLE_DEVICES"] = "2"


QModelStructure=getCFG('QModelStructure')

def initialQModel(stateDim,actionDim):
    Qmodel = Sequential()
    Qmodel.add(Dense(QModelStructure['nodes'][0], input_dim=stateDim+actionDim))
    Qmodel.add(Activation(QModelStructure['activation'][0]))

    for i in range(len(QModelStructure['nodes'])-1):
        Qmodel.add(Dense(QModelStructure['nodes'][i+1]))
        Qmodel.add(Activation(QModelStructure['activation'][i+1]))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    Qmodel.compile(loss='binary_crossentropy', optimizer=sgd)
    stateactionInitial=np.random.uniform(-1,1,(100,stateDim+actionDim))
    valueInitial=np.zeros((100,1),dtype=float)
    Qmodel.fit(stateactionInitial,valueInitial, batch_size=100, epochs=500, validation_split=0.1)
    print('----------------------------------------')
    saveStructure(Qmodel, 'Q')
    saveWeight(Qmodel, 'Q')
    print('----------------------------------------')


PolicyModelStructure=getCFG('PolicyModelStructure')

def initialPolicyModel(stateDim,actionDim):
    PolicyModel = Sequential()
    PolicyModel.add(Dense(PolicyModelStructure['nodes'][0], input_dim=stateDim))
    PolicyModel.add(Activation(PolicyModelStructure['activation'][0]))
    for i in range(len(PolicyModelStructure['nodes'])-1):
        PolicyModel.add(Dense(PolicyModelStructure['nodes'][i+1]))
        PolicyModel.add(Activation(PolicyModelStructure['activation'][i+1]))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    PolicyModel.compile(loss='mean_squared_error', optimizer=sgd)
    stateactionInitial=np.random.uniform(-1,1,(100,stateDim))
    valueInitial=np.zeros((100,actionDim),dtype=float)+0.5
    # output of PolicyModel is initialized to 0.5
    # so that the Policy is initialized to 0
    PolicyModel.fit(stateactionInitial,valueInitial, batch_size=100, epochs=500, validation_split=0.1)

    print('----------------------------------------')
    saveStructure(PolicyModel, 'Policy')
    saveWeight(PolicyModel, 'Policy')
    print('----------------------------------------')


def initialFullIndex(conditionBaseFilterCFG):

    conditionCFG=conditionBaseFilterCFG['conditionCFG']

    dataExistinOneCell=np.zeros((conditionCFG['s1_cellNum'],conditionCFG['s2_cellNum'],conditionCFG['s3_cellNum'],conditionCFG['a1_cellNum']), dtype=np.int16)

    fulldict = dict()
    fulldict['dataExistinOneCell']=dataExistinOneCell.tolist()

    while 1:
        try:
            with open('dataExistinOneCell.json', 'w') as file_object:#保存权重的json文件
                json.dump(fulldict, file_object)
            break
        except:
            pass
    print('dataExistinOneCell.json  is updated')

    while 1:
        try:
            with open('conditionCFG.json', 'w') as file_object:#保存权重的json文件
                json.dump(conditionCFG, file_object)
            break
        except:
            pass
    print('conditionCFG.json  is updated')

def initialreadytocollect():
    readytocollect = dict()
    readytocollect['readytocollect'] = 1
    while 1:
        try:
            with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
                json.dump(readytocollect, file_object)
            break
        except:
            pass
    print('readytocollect.json  is updated')


stateDim=getCFG('stateDim')
actionDim=getCFG('actionDim')
conditionBaseFilterCFG=getCFG('conditionBaseFilterCFG')


initialPolicyModel(stateDim,actionDim)

# initialQModel(stateDim,actionDim)
#
# initialFullIndex(conditionBaseFilterCFG)
#
# initialreadytocollect()


print('----------------------------------------')
print('QModel is initialized')
print('PolicyModel  is initialized')
print('dataExistinOneCell.json  is initialized')
print('readytocollect.json  is initialized')
print('========================================')















