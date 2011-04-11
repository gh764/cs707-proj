import sqlite3
import hashlib

class database:
    
    def __init__(self, database_name = './database'):
        self.__connection = sqlite3.connect(database_name)
        self.__cursor = self.__connection.cursor()

    def __del__(self):
        self.__cursor.close()
        self.__connection.commit()
        self.__connection.close()

    def close(self):
        self.__cursor.close()
        self.__connection.commit()
        self.__connection.close()

    def register(self, uname, passwd):
        
        # don't store the unencrypted password to disk
        # assume this is called via an https connection
        passwdMd5 = hashlib.md5(passwd).hexdigest()

        print("register:(%s, %s)" % (uname, passwd))
        try:
            try:
                self.__cursor.execute('insert into usr(uname, passwd) values(?,?)',
                                      (uname, passwdMd5))
            except sqlite3.OperationalError:
                self.__create_user_table()
                self.__cursor.execute('insert into usr(uname, passwd) values(?,?)',
                                      (uname, passwdMd5))
            print "succesfully registered: %s" % uname
            return 0
        except sqlite3.IntegrityError:
            print "Register for %s failed, user already exists" % uname
            return -1

    def login(self, uname, passwd):
        print("login:(%s, %s)" % (uname, passwd))
        

        passwdMd5 = hashlib.md5(passwd).hexdigest()

        try:
            try:
                r = self.__cursor.execute('select uid from usr where uname=? and passwd=?',
                                          (uname, passwdMd5))
            except sqlite3.OperationalError:
                # usr table does not exist, create it
                self.__create_user_table()
                r = self.__cursor.execute('select uid from usr where uname=? and passwd=?',
                                          (uname, passwdMd5))
        except sqlite3.IntegrityError:
            print "password or username not correct for uname: %s" % uname
            return -1

        r=self.__cursor.fetchone()
        if r == None:
            return -1
        else:
            return r[0]

    def add_location(self, uid, name, longitude, 
                     latitude, radius, altitude=0):
        print("add-location:(%s, %d, %d, %d, %d)" % 
              (name, longitude, latitude, radius, altitude))
        try:
            self.__cursor.execute('insert into pid(uid, name, longitude, latitude, altitude, radius) values(?,?,?,?,?,?)', (name, longitude, latitude, radius, altitude))
        except sqlite3.OperationalError:
            self.__create_poi_table()
            self.__cursor.execute('insert into pid(uid, name, longitude, latitude, altitude, radius) values(?,?,?,?,?,?)', (name, longitude, latitude, radius, altitude))
            

    def get_locations(self, uid):
        print("get-location:(%d)" % (uid))
        try:
            self.__cursor.execute('select * from pid where uid = ?', (uid))
        except sqlite3.OperationalError:
            self.__create_poi_table()
            self.__cursor.execute('select * from pid where uid = ?', (uid))

        return self.__cursor.fetchall()



    # the __ bit means only other methods in this class can execute these 
    # okay, so you can if you are insistent, but you have to take special measures
    def __create_user_table(self):
        # create usr table. 
        self.__cursor.execute("""create table if not exists [usr] (
                  [uid]    [integer]       not null primary key ,
                  [uname]  [varchar](16)   not null unique,
                  [passwd] [varchar](32)   not null )""")
        
    def __create_poi_table(self):
        self.__cursor.execute("""create table if not exists [poi] (
                  [pid]  [int]         not null    primary key,
                  [uid]  [int]         not null    references [usr]([uid]),
                  [name]        [varchar](32) not null,
                  [description] [text],
                  [longitude]   [int]  not null, 
                  [latitude]    [int]  not null,
                  [altitude]    [int],
                  [radius]      [int]  not null    check(radius > 0))""")

    def __create_location_table(self):
        self.__cursor.execute("""create table if not exists [location_snapshot] (
                  [uid]       [int]      not null    references [usr]([uid]),
                  [location]  [int]      not null    references [poi]([pid]),
                  [arrival]   [datetime]  not null,
                  [departure] [datetime]  not null ) """)
        

    def __create_subscription_table(self):
        self.__cursor.execute("""create table if not exists [subscription] (
                  [sid]     [int]   not null primary key,
                  [uid]     [int]   not null references [usr]([uid]),
                  [poi]     [int]   not null references [poi]([pid]),
                  [rule]    [text]  not null,
                  [enabled] [int]   not null default 0)""")


    
