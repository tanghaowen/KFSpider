import KfRequest
import KfThreadInfo
from bs4 import BeautifulSoup
import KfTools
import kfSql
import re
cookiestring  = "2ed4e_skinco=default; 2ed4e_lastpos=F9; 2ed4e_ck_info=%2F%09; 2ed4e_winduser=A1pUAAMEPlQLUFQEAwUFVlZdA1tbBgUFBVFcBlMGVAAGVAUMCVJVPA%3D%3D; 2ed4e_ol_offset=8148; 2ed4e_threadlog=%2C56%2C106%2C52%2C5%2C127%2C9%2C; 2ed4e_ipstate=1508901710; 2ed4e_ipfrom=7ae251b7b2f8ac6405504b8a71cf6fe2%09%C5%B7%D6%DE%0D; 2ed4e_lastvisit=16%091508901731%09%2Fthread.php%3Ffid%3D9; PHPSESSID=evcedi1jk4pckkdbmer3fdmqi7"
kfrequest = KfRequest.KfRequest(cookiestring)
sqlManager = kfSql.sqlDataManager()
threadsList = None # type: List[KfThreadInfo.KfThreadInfo]

threadsList = KfTools.getThreadsFromAreaId(9,kfrequest)

for thread in threadsList:
    content = KfTools.getThreadContent(thread.url, kfrequest, thread)
    if content == None:
        continue
    thread.threadMainContents.append( content )


for thread in threadsList:
    sqlManager.addNewThreadToDatabase(
        thread.threadId,
        thread.title,
        thread.url,
        thread.creator,
        thread.createTime,
        thread.threadMainContents[0]
    )
print()


