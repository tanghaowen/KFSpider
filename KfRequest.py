import requests

class KfRequest():
    headers = {"Host":"bbs.2dkf.com",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
             "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
             "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
             "Referer":"http://bbs.2dkf.com/index.php"}

    session = None
    proxies = {}
    def __init__(self , cookie ,proxy = None):
        self.headers["Cookie"] = cookie

        self.session = requests.session()
        self.session.headers.update( self.headers )

        if not proxy == None:

            self.proxies = {
              "http": "http://%s" % proxy,
              "https": "http://%s"% proxy}


    def getUrl(self,url):
        response =  self.session.get(url, proxies=self.proxies)
        return response.text


