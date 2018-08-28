import KfRequest
import KfThreadInfo
from bs4 import BeautifulSoup
import KfTools
import kfSql
import re
import threading
import sys
from queue import Queue
from bs4 import BeautifulSoup
import KfUserInfo
sys.setrecursionlimit(100000000)

def getThreadQueue(que:Queue , kfrequest:KfRequest.KfRequest ):
    while True:
        uid = que.get()
        kfuserinfo = KfUserInfo.KfUserInfo()
        res = KfTools.getUserInfo(uid, kfrequest, kfuserinfo)
        if res == "用户不存在":
            continue

        sqlM = kfSql.sqlDataManager()
        if res == "其他错误":
            sqlM.addUidToErrorTable(uid)
        else:
            sqlM.addUserToDatabase(kfuserinfo)
        sqlM.sqldb.commit()
        sqlM.sqldb.close()

        que.task_done()
cookiestring  = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ol_offset=11446; 2ed4e_ipstate=1509104098; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=AFpTDAUEPlAKU1oEUAFRUlQLUwMEUAYHA1FcBVRUBwVQBwIMAAdTPA%3D%3D; 2ed4e_lastvisit=0%091509104104%09%2Findex.php%3F; PHPSESSID=t129mc4lo3a2er91bj97plt5a1"
cookiestring_yuezhuo = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ol_offset=9312; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=A1BUAQQJPldZBVFVBQIBVVNfBAMEBANSVFVbA1IFBgdRBQsPCVNSPA%3D%3D; 2ed4e_lastvisit=19%091509085581%09%2Findex.php%3F; PHPSESSID=f0um69juiq86bcum2177p6ruo1; 2ed4e_ipstate=1509085562"
cookiestring_3rd_baihe = "2ed4e_skinco=default; 2ed4e_lastpos=index; 2ed4e_ol_offset=9797; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=AldaAgEBPlVbUVNXAVICAwILVVNRAAIBU1IIBlFUBAAHWAZfVwFSPA%3D%3D; 2ed4e_lastvisit=0%091509086179%09%2Findex.php%3F; PHPSESSID=n1m7pt176f0g1pil6v5tcth5i7; 2ed4e_ipstate=1509086179"
kfrequest = KfRequest.KfRequest(cookiestring)
kfrequest_yuezhuo_1080 = KfRequest.KfRequest(cookiestring_yuezhuo,"127.0.0.1:1080")
kfrequest_3rd_baihe = KfRequest.KfRequest(cookiestring_3rd_baihe,"127.0.0.1:1081")

sqlManager = kfSql.sqlDataManager()
start_uid = sqlManager.getLargestUid()
if start_uid == None: start_uid = 0
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


for error_uid in sqlManager.getAllErrorUser():
    que.put(error_uid['uid'])



que.join()







