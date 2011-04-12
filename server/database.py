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

    def register(self, uid, passwd):
        
        # don't store the unencrypted password to disk
        # assume this is called via an https connection
        passwdMd5 = hashlib.md5(passwd).hexdigest()

        print("register:(%s, %s)" % (uid, passwd))
        try:
            try:
                self.__cursor.execute('insert into usr(uid, passwd) values(?,?)',
                                      (uid, passwdMd5))
            except sqlite3.OperationalError:
                self.__create_user_table()
                self.__cursor.execute('insert into usr(uid, passwd) values(?,?)',
                                      (uid, passwdMd5))
            print("succesfully registered: %s" % uname)
            return 0
        except sqlite3.IntegrityError:
            print("Register for %s failed, user already exists" % uid)
            return -1

    def login(self, uid, passwd):
        print("login:(%s, %s)" % (uid, passwd))
        

        passwdMd5 = hashlib.md5(passwd).hexdigest()

        try:
            try:
                r = self.__cursor.execute('select uid from usr where uid=? and passwd=?',
                                          (uid, passwdMd5))
            except sqlite3.OperationalError:
                # usr table does not exist, create it
                self.__create_user_table()
                r = self.__cursor.execute('select uid from usr where uid=? and passwd=?',
                                          (uid, passwdMd5))
        except sqlite3.IntegrityError:
            print("password or username not correct for uid: %s" % uid)
            return -1

        r=self.__cursor.fetchone()
        if r == None:
            return -1
        else:
            return r[0]

    def add_location(self, uid, name, longitude, latitude, radius, altitude=0):
        print("add-location:(%s, %d, %d, %d, %d)" % 
              (name, longitude, latitude, radius, altitude))
        try:
            self.__cursor.execute('insert into pid(uid, name, longitude, latitude, altitude, radius) values(?,?,?,?,?,?)',
                                  (name, longitude, latitude, radius, altitude))
        except sqlite3.OperationalError:
            self.__create_poi_table()
            self.__cursor.execute('insert into pid(uid, name, longitude, latitude, altitude, radius) values(?,?,?,?,?,?)',
                                  (name, longitude, latitude, radius, altitude))
            

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
        self.__cursor.execute("""
            create table if not exists [usr] (
                  [uid]    [int]    not null primary key ,
                  [passwd] [text]   not null )""")
        
    def __create_poi_table(self):
        self.__cursor.execute("""
            create table if not exists [poi] (
                [pid]			[int]				primary key,
                [uid]			[int]	not null    references [usr]([uid]),
        		[name]			[text]	not null,
                [description]	[text],
        		[longitude]		[int]	not null, 
        		[latitude]		[int]	not null,
                [altitude]		[int],
        		[radius]		[int]	not null    check(radius > 0))""")

    # model table.
    # sections
    # $1: model identifier & owner.
    # $2: version & modification information 
    # $3: data collection and aggregration information.
    # $4: model statistics 
    # $5: triggers which cause the model to be rebuilt at
    #     earliest rebuild date. trigger-value of 0 disables trigger.
    def __create_model_table(self):
        self.__cursor.execute('''
            create table if not exists [model] (
        		[mid]	                [int]   		                primary key,
                [uid]                   [int]   not null                unique references [usr]([uid]),

                [version]               [int]   not null    default 0,
                [created_on]            [text]  not null    default current_date,
                [last_updated_on]       [text]  not null    default current_date,
                [earliest_rebuild]      [int]   not null    default 7,
                [expires_in]            [int]   not null    default 90,

        		[window_size]           [int]   not null    default 2   check([window_size] >= 2 and [window_size] <= 24),
        		[agg_fx]                [char]  not null    default 'a' check([agg_fx] in ('a', 'w')),
        		[granularity]           [int]   not null    default 15  check([granularity] > 0 & [granularity] < 120),

                [nr_matches]            [int]   not null    default 0,
                [nr_successful]         [int]   not null    default 0,
                [streak]                [int]   not null    default 0,
                [last10]                [int]   not null    default 0,

                [rebuild]               [int]   not null    default 0   check([rebuild] = 0 or [rebuild] = 1),
                [total_mismatch_trig]   [real]  not null    default 0.5 check([total_mismatch_trig] >= 0 and [total_mismatch_trig] <= 1),
                [losing_strk_trig]      [int]   not null    default 5   check([losing_strk_trig] >= 0),
                [last10_lsng_strk_trig] [real]  not null    default 0.5 check([last10_lsng_strk_trig] >= 0 and [last10_lsng_strk_trig] <= 1) )
            ''')
            
    # create subscriber table. 
	def __create_location_table(self):
		c.execute('''
    		create table if not exists [subscriber] (
			[sid]	        [int]               primary key,
			[uid]	        [int]   not null    references [usr]([uid]),
        	[name]          [text]  not null,
        	[enbl_alrts]    [int]   not null    default 0)
		''')
            

    # create location_snapshot table. 
    def __create_location_table(self):
        c.execute('''
            create table if not exists [location_snapshot] (
        	[uid]	    [int]	not null    references [usr]([uid]),
        	[location]  [int]	not null    references [poi]([pid]),
        	[arrival]   [datetime]	not null,
        	[departure] [datetime]  not null)
            ''')

    # agg_location_snapshot table.
    def __create_agg_location_table(self):
        c.execute('''
            create table if not exists [agg_location_snapshot] (
                [mid]       [int]   not null,    
                [version]   [int]   not null,

                [day]       [int]   not null    check([day] in (1,2,4,8,16,32,64)),
                [start]     [text]  not null,
                [end]       [text]  not null,
                [location]  [int]               references [poi](pid),
        
                foreign key([mid], [version]) references [model]([mid], [version]))
        ''')

    # alert table.
    def __create_agg_location_table(self):
        c.execute('''
            create table if not exists [alert] (
                [aid]           [int]   		                primary key,
                [sid]           [int]   not null                references [subscriber]([sid]),

                [event]         [char]  not null                check([event] in ('a', 'd')),
                [location]      [int]   not null                references [poi]([pid]),
                [send_within]   [int],

                [is_enabled]    [int]   not null    default 0)
        ''')
