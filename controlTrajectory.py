import numpy as np
import pymysql.cursors
import pandas as pd
import matplotlib.pyplot as plt


config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'matlab_realtime',#数据库名称
    'charset': 'gbk',
    'cursorclass': pymysql.cursors.DictCursor,
}

TableName='history'

connection = pymysql.connect(**config)
try:
    with connection.cursor() as cursor:
        sql = 'SELECT * from '+TableName+' order by myindex'
        cursor.execute(sql)
        result = cursor.fetchall()
        frame = pd.DataFrame(list(result))
finally:
    connection.close()

# [Qstate, Qaction, NextQstate]
# Qstate=np.array(frame[['s1','s2','s3']])
# Qaction=np.array(frame[['a1']])
# NextQstate=np.array(frame[['ns1','ns2','ns3']])


Trajectory=np.array(frame[['s1','s2']])

plt.plot(Trajectory[257500:262500,:])
plt.show()








