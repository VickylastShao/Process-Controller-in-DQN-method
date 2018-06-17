from Offline_Agent_v2.publicFunction import *

config = getCFG('mysqlconfig')

# 实际的强化学习任务面临着样本不平衡的问题 对Qmodel的估计效果不好

# 这里的工况边界指的是state和action 不包含nextstate
# 因为训练Qmodel的目的是获得state,action 到 Qvalue的映射
# 为了避免训练样本的不平衡分布的问题需要将训练数据中的state,action分布均匀化
conditionBaseFilterCFG=getCFG('conditionBaseFilterCFG')

conditionCFG = conditionBaseFilterCFG['conditionCFG']

BoundryList=[]
for i in range(len(conditionCFG['paralist'])):
    paraname=conditionCFG['paralist'][i]
    parafrom = conditionCFG[paraname + '_From']
    parato = conditionCFG[paraname + '_to']
    cellnum = conditionCFG[paraname + '_cellNum']
    BoundryList.append(np.linspace(parafrom, parato, num=cellnum+1))

maxDataNuminOneCell=conditionBaseFilterCFG['maxDataNuminOneCell']

dataExistinOneCell=loaddataExistinOneCell()


def conditionBaseFilter(pin,FromTable,toTable):

    # 读取新数据
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = 'select * from ' + FromTable + ' where myindex!=1 and myindex>'+str(pin) +' order by myindex desc'
            cursor.execute(sql)
            result = cursor.fetchall()
            newcondition=pd.DataFrame(list(result))

    finally:
        connection.close()

    if(not newcondition.empty):

        readytocollect = dict()
        readytocollect['readytocollect'] = 0
        while 1:
            try:
                with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
                    json.dump(readytocollect, file_object)
                break
            except:
                pass
        print('processing...')


        pin=newcondition.max(axis=0)['myindex']# 更新pin

        #
        # # newcondition里面的数据都是要插入的
        #
        # indextodelete=[] # 要删除的数据 oricondition中的index
        #
        # # 找到newcondition和oricondition中各工况的数据量 计算oricondition需要被删除的数据量
        #
        # newConditionCount = np.array((conditionCFG['s1_cellNum'], conditionCFG['s2_cellNum'], conditionCFG['s3_cellNum'],
        #                               conditionCFG['a1_cellNum']),dtype=np.int)
        # oriConditionCount = np.array((conditionCFG['s1_cellNum'], conditionCFG['s2_cellNum'], conditionCFG['s3_cellNum'],
        #                               conditionCFG['a1_cellNum']), dtype=np.int)
        #
        # for i1 in range(conditionCFG['s1_cellNum']):
        #     for i2 in range(conditionCFG['s2_cellNum']):
        #         for i3 in range(conditionCFG['s3_cellNum']):
        #             for i4 in range(conditionCFG['a1_cellNum']):
        #                 tempDF = newcondition
        #                 tempDF = tempDF[tempDF.s1 > BoundryList[0][i1]]
        #                 tempDF = tempDF[tempDF.s1 < BoundryList[0][i1 + 1]]
        #                 tempDF = tempDF[tempDF.s2 > BoundryList[1][i2]]
        #                 tempDF = tempDF[tempDF.s2 < BoundryList[1][i2 + 1]]
        #                 tempDF = tempDF[tempDF.s3 > BoundryList[2][i3]]
        #                 tempDF = tempDF[tempDF.s3 < BoundryList[2][i3 + 1]]
        #                 tempDF = tempDF[tempDF.a1 > BoundryList[3][i4]]
        #                 tempDF = tempDF[tempDF.a1 < BoundryList[3][i4 + 1]]
        #                 newConditionCount[i1, i2, i3, i4] = tempDF.shape[0]
        #
        #                 tempDF = oricondition
        #                 tempDF = tempDF[tempDF.s1 > BoundryList[0][i1]]
        #                 tempDF = tempDF[tempDF.s1 < BoundryList[0][i1 + 1]]
        #                 tempDF = tempDF[tempDF.s2 > BoundryList[1][i2]]
        #                 tempDF = tempDF[tempDF.s2 < BoundryList[1][i2 + 1]]
        #                 tempDF = tempDF[tempDF.s3 > BoundryList[2][i3]]
        #                 tempDF = tempDF[tempDF.s3 < BoundryList[2][i3 + 1]]
        #                 tempDF = tempDF[tempDF.a1 > BoundryList[3][i4]]
        #                 tempDF = tempDF[tempDF.a1 < BoundryList[3][i4 + 1]]
        #                 oriConditionCount[i1, i2, i3, i4] = tempDF.shape[0]
        #
        #
        # deletedDataNum=newConditionCount+oriConditionCount-maxDataNuminOneCell
        #
        # deletedDataNum[deletedDataNum < 0] = 0 # 如果新数据和原始数据总数少于maxDataNuminOneCell 则不需要删除操作


        #插入所有newcondition

        #将新数据插入工况库

        # 初始化工况计数
        dataNuminOneCellperBatch = np.zeros((conditionCFG['s1_cellNum'], conditionCFG['s2_cellNum'],
                                             conditionCFG['s3_cellNum'], conditionCFG['a1_cellNum']),
                                            dtype=np.int)

        connection = pymysql.connect(**config)
        try:
            with connection.cursor() as cursor:

                # 存储该批数据位于每个cell中的数据数量

                for index, row in newcondition.iterrows():
                    templist = []
                    templist.append(int(row['myindex']))
                    templist.append(row['s1'])
                    templist.append(row['s2'])
                    templist.append(row['s3'])
                    templist.append(row['a1'])
                    templist.append(row['ns1'])
                    templist.append(row['ns2'])
                    templist.append(row['ns3'])

                    # 找到当前数据的工况cell
                    indexNow=[-1,-1,-1,-1]
                    for i in range(4):
                        # 数据可能落在工况边界之外 如果在外面，则对应维度的index为-1
                        paraname=conditionCFG['paralist'][i]
                        paravalue=row[paraname]
                        parafrom=conditionCFG[paraname+'_From']
                        parato=conditionCFG[paraname+'_to']
                        cellnum=conditionCFG[paraname+'_cellNum']

                        if (paravalue >= parafrom and paravalue <= parato):
                            indexNow[i] = int((paravalue - parafrom) / ((parato-parafrom)/cellnum))
                            if indexNow[i]>=cellnum-1:
                                indexNow[i]=cellnum-1

                    if min(indexNow)>=0:# 如果当前数据属于工况边界内 则累计排序本批次本cell数目 当数量没有超限 则插入数据库
                        dataNuminOneCellperBatch[indexNow[0],indexNow[1],indexNow[2],indexNow[3]]+=1

                        # 这个地方是如果有数据就为1 意思是存在数据
                        dataExistinOneCell[indexNow[0], indexNow[1], indexNow[2], indexNow[3]] = 1
                        # 原始数据是倒序的 所以本轮数据中当前工况cell数量超过maxDataNuminOneCell 后面的就不要往里面插入了 就算插进去 后面也是肯定要被删掉的
                        if dataNuminOneCellperBatch[indexNow[0],indexNow[1],indexNow[2],indexNow[3]]<=maxDataNuminOneCell:
                            sql = 'INSERT INTO ' \
                              + toTable \
                              + ' value ('+','.join(str(element) for element in templist)+')'
                            cursor.execute(sql)
                            cursor.fetchall()

                        # else:# 这个地方是如果数据量大于maxDataNuminOneCell就为1 意思是数据满了
                        #     dataExistinOneCell[indexNow[0], indexNow[1], indexNow[2], indexNow[3]] = 1

        finally:
            connection.commit()
            connection.close()

        # 删除多余工况 保留maxDataNuminOneCell个数据
        connection = pymysql.connect(**config)
        try:
            with connection.cursor() as cursor:
                    sql = 'SET SQL_SAFE_UPDATES = 0'#强制关闭安全更新模式
                    cursor.execute(sql)
                    cursor.fetchall()
        finally:
            connection.commit()
            connection.close()

        def less_than(i,n):
            if i==n-1:
                return '<='
            else:
                return '<'

        connection = pymysql.connect(**config)
        try:
            with connection.cursor() as cursor:
                for i1 in range(conditionCFG['s1_cellNum']):
                    for i2 in range(conditionCFG['s2_cellNum']):
                        for i3 in range(conditionCFG['s3_cellNum']):
                            for i4 in range(conditionCFG['a1_cellNum']):

                                # 如果本批次数据中没有工况cell i1,i2,i3,i4 中的数据 则肯定不需要进行删除操作
                                if(dataNuminOneCellperBatch[i1,i2,i3,i4]!=0):

                                    consql='s1 >= ' + str(BoundryList[0][i1]) +'  and s1 '+less_than(i1,conditionCFG['s1_cellNum'])+' ' + str(BoundryList[0][i1 + 1]) + ' and ' \
                                        's2 >= ' + str(BoundryList[1][i2]) + ' and s2 '+less_than(i2,conditionCFG['s2_cellNum'])+' ' + str(BoundryList[1][i2 + 1]) + ' and ' \
                                        's3 >= ' + str(BoundryList[2][i3]) + ' and s3 '+less_than(i3,conditionCFG['s3_cellNum'])+' ' + str(BoundryList[2][i3 + 1]) + ' and ' \
                                        'a1 >= ' + str(BoundryList[3][i4]) + ' and a1 '+less_than(i4,conditionCFG['a1_cellNum'])+' ' + str(BoundryList[3][i4 + 1]) + ' '

                                    sql = 'delete from '+toTable+' where myindex not in (select myindex from (select myindex from '+toTable+' where '+consql+' order by myindex desc limit '+str(int(maxDataNuminOneCell))+') as tempmyindex) and '+consql

                                    cursor.execute(sql)
                                    cursor.fetchall()

        finally:
            connection.commit()
            connection.close()



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



        readytocollect['readytocollect'] = 1
        while 1:
            try:
                with open('readytocollect.json', 'w') as file_object:  # 保存权重的json文件
                    json.dump(readytocollect, file_object)
                break
            except:
                pass
        print('ready to collect data!')


    return pin


decisionCycle=conditionBaseFilterCFG['DecisionCycle']

pin=0

while 1:

    starttime = datetime.datetime.now()

    pin=conditionBaseFilter(pin,FromTable='history',toTable='conditionbase')

    print('condition Base Filtration Finished!')

    endtime = datetime.datetime.now()

    TC = (endtime - starttime).seconds + (endtime - starttime).microseconds / 1000000

    print("Time Consuming: %.2f" % (TC) + ' s')

    delayTime = decisionCycle - TC

    print('====================' + str(endtime) + '===================')

    if(delayTime>0):
        time.sleep(delayTime)

