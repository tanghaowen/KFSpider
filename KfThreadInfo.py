class KfThreadInfo():
    def __init__(self):
        self.title = self.creator = self.createTime = self.path = self.threadId = self.areaId=""
        self.threadContents = {}
        """
        threadContents = {
        0:{
            "createTime":"Time",
            "content":"Content",
            "creator":"Jack"
          },
        1:{
        
          }
        
        }
        
        """

    def setReplyToContents(self,floor:int,create_time,content,creator):
        self.threadContents[floor] = {
            "createTime":create_time,
            "content":content,
            "creator":creator
        }
    def setReplyCreateTimeToContents(self,floor:int,create_time):
        self.threadContents[floor] = {
            "createTime":create_time
        }