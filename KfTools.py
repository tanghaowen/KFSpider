from bs4 import BeautifulSoup
import KfThreadInfo
import KfRequest
import re
from bs4 import NavigableString
import KfUserInfo
def getThreadsFromAreaId(areaId,kfrequest):
    threads = []

    unlimareaString = kfrequest.getUrl("http://bbs.2dkf.com/thread.php?fid=%d" % (areaId))
    unlimareaString = unlimareaString.replace("&nbsp;", "")
    unlimareaSoup = BeautifulSoup(unlimareaString)
    threadList = unlimareaSoup.select("table[class='thread1']")[0].select("tr")

    # 移除最上面的页面导航，游戏类cg类和空栏
    # for循环清除置顶帖和之后一个的空栏
    threadList.remove(threadList[0])
    threadList.remove(threadList[0])
    threadList.remove(threadList[0])
    index = 0
    for thread in threadList:
        tds = thread.select("td")
        if len(tds[0].contents) == 0:
            threadList = threadList[index + 1:]
            break
        index += 1

    for thread in threadList:
        threadInfo = KfThreadInfo.KfThreadInfo()
        threads.append(threadInfo)
        tds = thread.select("td")

        threadInfo.url = tds[0].select("a")[0]["href"]
        threadInfo.threadId = filitOutThreadId(threadInfo.url)

        title_as = tds[1].select("div.threadtit1 > a")
        if len(title_as) > 1:
            threadInfo.title = title_as[1].string
        else:
            threadInfo.title = title_as[0].string

        threadInfo.creator = tds[3].select("a")[0].string

        re_res = re.findall("\| *(.*)", tds[3].contents[1])
        if len(re_res) > 0:
            threadInfo.createTime = re_res[0]

    return threads


def getThreadContent(threadPath , kfrequest:KfRequest.KfRequest , kfthreadinfo:KfThreadInfo.KfThreadInfo,domain = "http://bbs.2dkf.com/",ifbuybuybuy = False,page = 1):
    kfthreadinfo.path = threadPath
    kfthreadinfo.threadId = filitOutThreadId( threadPath)
    threadurl = domain+threadPath+"&page=%d" % ( page)
    print("开始获取帖子内容："+kfthreadinfo.title+" - " + threadPath + " - Page: " + str(page))

    response =  kfrequest.getUrl( threadurl)
    if "非缓存页面需登录后访问" in response:
        print("Cookie失效了！！！！！！！！！！！！！！！！！！！！！")
        return "Cookie失效"

    response = response.replace("&nbsp;", "")
    res = re.findall("本帖当前需求\[(.*)\]神秘等级浏览，你的神秘等级为\[(.*)\]" , response)
    if len(res) >0 :
        errorString = "sm等级不够无法浏览此贴：需求 %s 当前sm %s"%( res[0][0] , res[0][1])
        print( errorString )
        kfthreadinfo.setReplyToContents( 0 ,"Unknow" , errorString,"Unknow")
        kfthreadinfo.threadId = filitOutThreadId(threadPath)
        kfthreadinfo.path = threadPath
        kfthreadinfo.title="[[神秘不够]]"
        kfthreadinfo.areaId = -1

        return
    if "帖子ID非法" in response:
        errorString = "帖子ID非法"
        kfthreadinfo.setReplyToContents( 0 ,"Unknow" , errorString,"Unknow")
        kfthreadinfo.threadId = filitOutThreadId(threadPath)
        kfthreadinfo.path = threadPath
        kfthreadinfo.title = "[[帖子ID非法]]"
        kfthreadinfo.areaId = -1
        print(errorString)
        kfthreadinfo.setReplyToContents(0, "Unknow", errorString,"Unknow")
        return
    if "您要访问的链接无效" in response:
        errorString = "读取数据错误,原因：您要访问的链接无效,可能链接不完整,或数据已被删除!"
        kfthreadinfo.setReplyToContents( 0 ,"Unknow" , errorString,"Unknow")
        kfthreadinfo.threadId = filitOutThreadId(threadPath)
        kfthreadinfo.path = threadPath
        kfthreadinfo.title = "[[读取数据错误,原因：您要访问的链接无效,可能链接不完整,或数据已被删除!]]"
        kfthreadinfo.areaId = -1
        print(errorString)
        kfthreadinfo.setReplyToContents(0, "Unknow", errorString,"Unknow")
        return
    if "此帖被管理员关闭" in response:
        errorString = "此帖被管理员关闭"
        kfthreadinfo.setReplyToContents( 0 ,"Unknow" , errorString,"Unknow")
        kfthreadinfo.threadId = filitOutThreadId(threadPath)
        kfthreadinfo.path = threadPath
        kfthreadinfo.title = "[[此帖被管理员关闭]]"
        kfthreadinfo.areaId = -1
        print(errorString)
        kfthreadinfo.setReplyToContents(0, "Unknow", errorString,"Unknow")
        return
    if "本版块为认证版块" in response:
        errorString = "对不起,本版块为认证版块,您没有权限查看此版块的内容"
        kfthreadinfo.setReplyToContents( 0 ,"Unknow" , errorString,"Unknow")
        kfthreadinfo.threadId = filitOutThreadId(threadPath)
        kfthreadinfo.path = threadPath
        kfthreadinfo.title = "[[对不起,本版块为认证版块,您没有权限查看此版块的内容]]"
        kfthreadinfo.areaId = -1
        print(errorString)
        kfthreadinfo.setReplyToContents(0, "Unknow", errorString,"Unknow")
        return

    responseSoup = BeautifulSoup(response,"lxml")

    # 获取标题
    try:
        kfthreadinfo.title = responseSoup.select('form[name="delatc"] > div')[0].select("span")[0].string
    except IndexError as e:
        if "503 Service Temporarily Unavailable" in response:
            print("503 Error!! Service Temporarily Unavailable!!")
            print(threadPath)
        else:
            print(threadPath)
            print(e)
            print(response)
        return "其他错误"

    # 获取所在分区id
    areaPath = responseSoup.select('form[name="delatc"] > div')[0].select("tr")[1].select("a")[0]["href"]
    areaId = int(re.findall("thread.php\?fid=([0-9]+)" , areaPath)[0])
    kfthreadinfo.areaId = areaId



    # div.readlou 为每层回复上部的包含发帖时间的那一部分
    readlous = responseSoup.select("div.readlou")
    for reply_head in readlous:
        for div in reply_head.select("> div"):
            # 这里如果span数量为0的话，代表是右侧的引用等按钮的div，直接跳过
            # 否则获取发表时间 楼层信息等信息
            spans = div.select("span")
            if len(spans) == 0:
                continue

            timeInfoString  = spans[1].string
            res = re.findall("发表于：(.*) .+\r",timeInfoString)
            create_time = res[0]

            floorInfoString = spans[0].string
            floor = -1
            if "楼主" in floorInfoString:
                floor = 0
                kfthreadinfo.creator = ""
                kfthreadinfo.createTime = create_time
            else:
                res = re.findall("([0-9]+)楼" , floorInfoString)
                floor = int(res[0])



            content_div = None
            for next_div in reply_head.next_siblings:
                if isinstance(next_div,NavigableString):continue
                if next_div.has_attr("class") and next_div["class"] == ["readtext"]:
                    content_div = next_div
                    break

            content_elem = content_div.select("table > tr > td")[0]
            # 获取这层楼的发帖者id
            creator_div = content_elem.select("div.readidmsbottom")
            creator = "Unknow"
            if len(creator_div)>0:
                creator = creator_div[0].select("a")[0].string
            else:
                creator_div = content_elem.select("div.readidmleft")[0]
                creator = creator_div.select("a")[0].string
            if "楼主" in floorInfoString:
                kfthreadinfo.creator = creator
            # 如果有购买框，如何处理
            if len(content_elem.select("fieldset")) > 0:
                buyInfo_input = content_elem.select("fieldset")[0].select("input")
                if len(buyInfo_input) > 0 and ifbuybuybuy:
                    buyInfo_input = buyInfo_input[0]["onclick"]
                    res = re.findall('location.href="(.*)"',buyInfo_input)
                    if len(res) > 0:
                        buy_url_path = res[0]
                        buyThread(buy_url_path,kfrequest,kfthreadinfo,domain)

                        response = kfrequest.getUrl(threadurl)
                        responseSoup = BeautifulSoup(response)
                        mainflow = responseSoup.select("div.readtext > table > tr > td")[0]
            content_string = str(content_elem)

            kfthreadinfo.setReplyToContents(floor,create_time,content_string,creator)

    has_next_page = hasNextPage(responseSoup)
    if has_next_page:
        getThreadContent(threadPath,kfrequest,kfthreadinfo,domain,ifbuybuybuy,page+1)


def buyThread( buy_url_path , kfrequest:KfRequest.KfRequest , kfthreadinfo:KfThreadInfo.KfThreadInfo,domain = "http://bbs.2dkf.com/", ):
    buy_full_url = domain + buy_url_path
    response = kfrequest.getUrl(buy_full_url)
    if "操作完成" in response:
        print("购买帖子成功："+buy_url_path)
        print("购买帖子成功：" + kfthreadinfo.title+" - "+kfthreadinfo.creator)
        return True
    elif "您已经购买此帖" in response:
        print("已经购买过此贴："+buy_url_path)
        print("已经购买过此贴：" + kfthreadinfo.title+" - "+kfthreadinfo.creator)
        return True
    else:
        print("购买帖子失败！！："+buy_url_path)
        print("购买帖子失败！！：" + kfthreadinfo.title+" - "+kfthreadinfo.creator)
        return False

def filitOutThreadId( path ):
    return int(re.findall("tid=(.*)", path)[0])

def hasNextPage(responseSoup):
    has_next_page = False
    pages_uls = responseSoup.select("ul.pages")
    for ul in pages_uls:
        if ul.parent.parent.name == "td":
            has_next_page = True
            for li in ul:
                a = li.select("a")[0]
                if "页" in a.string:
                    continue
                if a.has_attr("href") and "javascript" in a["href"]:
                    # now_page = re.findall("([0-9]+)" , a.string)[0]
                    li_next = li.next_sibling
                    if "下一页" in li_next.select("a")[0].string:
                        has_next_page = False
                        break
            break
    return has_next_page


def getUserInfo(uid,kfrequest:KfRequest.KfRequest,kfuserinfo:KfUserInfo.KfUserInfo,domain = "http://bbs.2dkf.com/"):
    userpage_url = domain + "profile.php?action=show&uid=%d"%uid
    user_page_info = kfrequest.getUrl(userpage_url)

    if "不存在" in user_page_info:
        print("用户%d不存在！" % (uid))
        return "用户不存在"


    userpage_bsoup = BeautifulSoup(user_page_info, "lxml")

    try:
        usert_table = userpage_bsoup.select("table.log1 > tr")[1].select("td")
    except IndexError as e:
        print(user_page_info)
        print(uid)
        print(e)
        return "其他错误"
    first_td = usert_table[0]
    second_td = usert_table[1]
    third_td = usert_table[2]


    for ele in second_td.strings:
        if "用户名称" in ele:
            kfuserinfo.username = re.findall("用户名称：(.*) *\(", ele)[0]
        elif "数字序列" in ele:
            kfuserinfo.uid = int(re.findall("数字序列：([0-9].*)", ele)[0])
        elif "系统等级" in ele:
            kfuserinfo.sysclass = re.findall("系统等级：(.*)", ele)[0]
        elif "会员等级" in ele:
            kfuserinfo.member_rank = re.findall("会员等级：(.*)", ele)[0]
        elif "发帖数量" in ele:
            kfuserinfo.replynumber = int(re.findall("发帖数量：([0-9]+)", ele)[0])
        elif "神秘等级" in ele:
            kfuserinfo.sm = int(re.findall("神秘等级：(-*[0-9]+)", ele)[0])
        elif "神秘系数" in ele:
            kfuserinfo.smcoefficent = int(re.findall("神秘系数：([0-9]+)", ele)[0])
        elif "论坛货币" in ele:
            kfuserinfo.kfb = int(re.findall("论坛货币：(-*[0-9]+)", ele)[0])
        elif "贡献数值" in ele:
            kfuserinfo.gongxian = float(re.findall("贡献数值：(.*) *\(", ele)[0])
        elif "注册时间" in ele:
            kfuserinfo.regiest_time = re.findall("注册时间：(.*)", ele)[0]
        elif "在线时间" in ele:
            kfuserinfo.online_time = int(re.findall("在线时间：([0-9]+)", ele)[0])
        elif "日均发帖" in ele:
            kfuserinfo.replyperday = int(re.findall("日均发帖：([0-9]+)", ele)[0])

    for ele in third_td.strings:
        if "个性签名" in ele:
            kfuserinfo.signmessage = re.findall("个性签名：(.*)", ele)[0]
        elif "性别" in ele:

            if "男" in ele:
                kfuserinfo.sex = "Male"
            elif "女" in ele:
                kfuserinfo.sex = "Female"
            elif "保密" in ele:
                kfuserinfo.sex = "Unknow"
