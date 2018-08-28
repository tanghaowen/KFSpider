import MySQLdb
import KfThreadInfo
import base64
import re
import KfUserInfo
import _mysql_exceptions
class sqlDataManager():

    def __init__(self):
        self.sqldb = MySQLdb.connect(host = "133.95.122.92",user="root",passwd = "shinonomehana" ,charset = "UTF8")
        self.cursor = self.sqldb.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor.execute("""
        CREATE DATABASE IF NOT EXISTS kfspider;
        """)
        self.cursor.execute("""
        USE kfspider;
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads(
        a_id INT PRIMARY KEY NOT NULL auto_increment ,
        thread_id INT NOT NULL,
        title VARCHAR(200) NOT NULL ,
        path VARCHAR(200) NOT NULL ,
        create_time VARCHAR(50) ,
        creator VARCHAR(170),
        areaId INT ,


        INDEX(thread_id,title,path)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS contents(
        content_id INT PRIMARY KEY NOT NULL auto_increment ,
        content TEXT NOT NULL ,
        floor INT NOT NULL , 
        creator VARCHAR (40) ,
        create_time VARCHAR(20) NOT NULL,
        parent_thread INT,
        parent_a_id INT
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS threadmap(
        `index` INT PRIMARY KEY NOT NULL auto_increment ,
        a_id INT NOT NULL ,
        content_id INT NOT NULL
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS errortid(
        therad_id int NOT NULL 
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
        uid INT PRIMARY KEY NOT NULL ,
        username VARCHAR(500) NOT NULL ,
        sys_class VARCHAR(500) NOT NULL ,
        member_rank VARCHAR(500) NOT NULL ,
        reply_number INT NOT NULL,
        sm INT NOT NULL,
        sm_coefficent INT NOT NULL,
        kfb INT NOT NULL,
        gongxian FLOAT NOT NULL,
        regiest_time DATE NOT NULL,
        online_time INT NOT NULL,
        reply_perday INT NOT NULL,
        sex VARCHAR(20) NOT NULL,
        sign_message TEXT NOT NULL
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS erroruid(
        uid int NOT NULL 
        );
        """)
        self.sqldb.commit()


    def addNewThreadToDatabase(self,kfthreadinfo:KfThreadInfo.KfThreadInfo):
        try:
            kfthreadinfo.title = kfthreadinfo.title.replace("'","\\'").replace('"','\\"')
        except AttributeError as e :
            print(e)

        kfthreadinfo.creator = kfthreadinfo.creator.replace("'","\\'").replace('"','\\"')

        self.cursor.execute("""
        insert into threads (thread_id , title , path , create_time , creator , areaId) values 
        (%d,TO_BASE64('%s'),'%s','%s' , '%s' , %d);
        """ % ( kfthreadinfo.threadId ,  kfthreadinfo.title , kfthreadinfo.path , kfthreadinfo.createTime,kfthreadinfo.creator,kfthreadinfo.areaId))

        thread_a_id = self.cursor.lastrowid



        for floor,content in kfthreadinfo.threadContents.items():
            create_time = content["createTime"]
            content_string = content["content"].replace("'","\\'").replace('"','\\"')
            creator = content["creator"]
            #content_string_base64 = base64.b64encode(content["content"].encode("utf-8")).decode("utf-8") # type:str
            #print(base64.b64decode( content_string_base64))

            self.cursor.execute("""
            insert into contents (content,floor,creator,create_time,parent_thread,parent_a_id) values ( TO_BASE64('%s'),%d,'%s','%s',%d,%d);"""
                                % (content_string,floor,creator,create_time,kfthreadinfo.threadId,thread_a_id) )
            self.cursor.execute("""
            insert into threadmap ( a_id , content_id ) values ( '%s' , last_insert_id() );
            """ % (thread_a_id) )

        self.sqldb.commit()


    def threadIdInDatabase(self,threadIdOrPath):
        threadId = threadIdOrPath
        if isinstance(  threadIdOrPath , str):
            if "read.php?tid=" in threadIdOrPath:
                threadId = re.findall("([0-9]+)", threadIdOrPath)[0]
                threadId = int(threadId)
            else:
                threadId=int(threadIdOrPath)

        self.cursor.execute("""
        SELECT * FROM threads where thread_id = %d;
        """ % ( threadId ))

        res = self.cursor.fetchall()
        if len(res) > 0:
            return True
        else:
            return False

    def getLargestThreadId(self):
        self.cursor.execute("""
        SELECT MAX( thread_id) AS max_thread_id FROM threads
        """)
        results = self.cursor.fetchall()
        max_thread_id = 0
        for res in results:
            max_thread_id = res["max_thread_id"]
        return max_thread_id
    def getLargestUid(self):
        self.cursor.execute("""
        SELECT MAX( uid ) AS max_uid FROM users
        """)
        results = self.cursor.fetchall()
        max_uid = 0
        for res in results:
            max_uid = res["max_uid"]
        return max_uid
    def addThreadIdToErrorTable(self,tid):
        self.cursor.execute("""
        insert into errortid (therad_id) VALUES (%d)
        """ % (tid))
        self.sqldb.commit()
    def addUidToErrorTable(self,uid):
        self.cursor.execute("""
        insert into erroruid (uid) VALUES (%d)
        """ % (uid))
        self.sqldb.commit()
    def addUserToDatabase(self,userinfo:KfUserInfo.KfUserInfo):
        try:
            userinfo.signmessage = userinfo.signmessage.replace("'","\\'")
            exestring = """
        replace into users ( uid, username , sys_class , member_rank,reply_number,sm,sm_coefficent,kfb,gongxian,regiest_time,online_time,reply_perday,sex,sign_message)
        VALUES 
        (%d , '%s', '%s', '%s', %d, %d , %d , %d ,  %f , '%s' , '%s',%d , '%s', to_base64('%s') );
        """%(userinfo.uid,userinfo.username,userinfo.sysclass,userinfo.member_rank,userinfo.replynumber,userinfo.sm,userinfo.smcoefficent,userinfo.kfb,userinfo.gongxian,userinfo.regiest_time,userinfo.online_time,userinfo.replyperday,userinfo.sex,userinfo.signmessage)
            self.cursor.execute(exestring)
        except TypeError as e:
            print(e)
            print(userinfo.uid)
            self.addUidToErrorTable(userinfo.uid)
        except _mysql_exceptions.ProgrammingError as e:
            print(e)
            print(userinfo.uid)
            self.addUidToErrorTable(userinfo.uid)


        self.sqldb.commit()

    def getAllErrorUser(self):
        self.cursor.execute("""
        SELECT uid FROM erroruid;
        """)
        res = self.cursor.fetchall()

        return res
