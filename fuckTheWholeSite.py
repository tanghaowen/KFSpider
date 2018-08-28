import KfRequest
import KfThreadInfo
from bs4 import BeautifulSoup
import KfTools
import kfSql
import re
import threading
import sys
from queue import Queue

sys.setrecursionlimit(100000000)
def getThreadQueue(que:Queue , kfrequest:KfRequest.KfRequest ):
    while True:
        tid = que.get()

        kfthreadinfo = KfThreadInfo.KfThreadInfo()
        path = "read.php?tid=%d" % (tid)
        res = KfTools.getThreadContent(path, kfrequest, kfthreadinfo)
        if res == "Cookie失效":
            que.put(tid)
            break

        sqlM = kfSql.sqlDataManager()
        if res == "其他错误":
            sqlM.addThreadIdToErrorTable( kfthreadinfo.threadId)
        else:
            sqlM.addNewThreadToDatabase(kfthreadinfo)
        sqlM.sqldb.commit()
        sqlM.sqldb.close()

        que.task_done()

cookiestring  = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=A1pUAAMEPlQLUFQEAwUFVlZdA1tbBgUFBVFcBlMGVAAGVAUMCVJVPA%3D%3D; 2ed4e_ol_offset=30846; 2ed4e_threadlog=%2C106%2C127%2C52%2C9%2C4%2C5%2C56%2C; 2ed4e_ipstate=1509171281; 2ed4e_ipfrom=eadb9f70c8d54d1de25bd27b8bceed44%09%C8%D5%B1%BE%0D; 2ed4e_lastvisit=4714%091509171515%09%2Findex.php%3F; PHPSESSID=evcedi1jk4pckkdbmer3fdmqi7"
cookiestring_yuezhuo = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=A1pUAAMEPlQLUFQEAwUFVlZdA1tbBgUFBVFcBlMGVAAGVAUMCVJVPA%3D%3D; 2ed4e_ol_offset=30846; 2ed4e_threadlog=%2C106%2C127%2C52%2C9%2C4%2C5%2C56%2C; 2ed4e_ipstate=1509171281; 2ed4e_ipfrom=eadb9f70c8d54d1de25bd27b8bceed44%09%C8%D5%B1%BE%0D; 2ed4e_lastvisit=4480%091509171281%09%2Findex.php%3F; PHPSESSID=evcedi1jk4pckkdbmer3fdmqi7"
cookiestring_3rd_baihe = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ol_offset=11058; 2ed4e_ipstate=1509171341; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=AldaAgEBPlVbUVNXAVICAwILVVNRAAIBU1IIBlFUBAAHWAZfVwFSPA%3D%3D; 2ed4e_lastvisit=11%091509171395%09%2Findex.php%3F; PHPSESSID=l7qijuo6690fss53d9gtq84c73"
kfrequest = KfRequest.KfRequest(cookiestring)
kfrequest_yuezhuo_1080 = KfRequest.KfRequest(cookiestring_yuezhuo,"127.0.0.1:1080")
kfrequest_3rd_baihe = KfRequest.KfRequest(cookiestring_3rd_baihe,"127.0.0.1:1081")

sqlManager = kfSql.sqlDataManager()

start_tid = sqlManager.getLargestThreadId()

if start_tid == None: start_tid = 0
que = Queue()
thread_list = []
thread_list_yuezhuo = []
thread_list_baihe = []

for i in range(0, 10):
    thread_list.append(
        threading.Thread(target=getThreadQueue, args=[que, kfrequest]))
    thread_list[i].start()


for i in range(0, 10):
    thread_list_yuezhuo.append(
        threading.Thread(target=getThreadQueue, args=[que, kfrequest_yuezhuo_1080]))
    thread_list_yuezhuo[i].start()


for i in range(0, 10):
    thread_list_baihe.append(
        threading.Thread(target=getThreadQueue, args=[que, kfrequest_3rd_baihe]))
    thread_list_baihe[i].start()


for index in range(start_tid+1,688000):
    que.put(index)

que.join()
