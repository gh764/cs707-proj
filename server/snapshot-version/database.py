import sqlite3
import hashlib
from datetime import datetime
from datetime import timedelta
import markov

class database:
    
    def __init__(self, database_name = './database'):
        self.__connection = sqlite3.connect(database_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
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
        """Register:
        uname: <user name>
        passwd: <clear text password>

        Registers the specified user with the database"""

        # don't store the unencrypted password to disk
        # assume this is called via an https connection
        passwdMd5 = hashlib.md5(passwd).hexdigest()

        try:
            try:
                self.__cursor.execute('insert into usr(uname, passwdMD5) values(?,?)',
                                      (uname, passwdMd5))
            except sqlite3.OperationalError:
                self.__create_user_table()
                self.__cursor.execute('insert into usr(uname, passwdMD5) values(?,?)',
                                      (uname, passwdMd5))
            return 0
        except sqlite3.IntegrityError:
            print "Register for %s failed, user already exists" % uname
            return -1

    def login(self, uname, passwd):
        """Login:
        uname: <user name>
        passwd: <clear text password>

        Note that the md5 hash is stored in the database, not the password.  
        """

        passwdMd5 = hashlib.md5(passwd).hexdigest()

        try:
            try:
                r = self.__cursor.execute('select uid from usr where uname=? and passwdMd5=?',
                                          (uname, passwdMd5))
            except sqlite3.OperationalError:
                # usr table does not exist, create it
                # if the table doesn't exist the user isn't going to be there
                self.__create_user_table()
                return -1
        except sqlite3.IntegrityError:
            print "password or username not correct for uname: %s" % uname
            return -1

        r=self.__cursor.fetchone()
        if r == None:
            return -1
        else:
            return r[0]

    def del_location(self, uid, location_name):
        
        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "del_location called for unknown uid %d" % uid
            return -1

        try:
            self.__cursor.execute('delete from location where name=? and uid=?', ( location_name, uid ))
        except sqlite3.OperationalError:
            # location table does not exist
            self.__create_location_table()
            return -1
        except sqlite3.IntegrityError:
            print "unknown location name=%s for uid %d" % ( location_name, uid )
            return -1
                                  
        return 0

    def add_location(self, uid, location_name, location_description):
        """Add a location to the database
        uid -> user id for this location
        location_name -> name of location to add 
        location_description -> description of the location
        """
        
        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "add_location called for unknown uid %d" % uid
            return -1

        # don't let a duplicate place be inserted
        try:
            self.__cursor.execute('select name from location where name=? and uid=?', (location_name, uid))
        except sqlite3.IntegrityError:
            print "add_location called with a duplicate place name: %s for uid %d" % ( location_name, uid)
            return -1
        except sqlite3.OperationalError:
            self.__create_location_table()


        self.__cursor.execute('insert into location(uid, name, description) values(?,?,?)', (uid, location_name, location_description))
                    
        return 0

    def snapshot(self, uid, location_name, timestamp):

        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "snapshot called for unknown uid %d" % uid
            return -1

        # check to see if the location_name is known and get the pid
        location_id = None
        try:
            r = self.__cursor.execute('select lid from location where name=? and uid=?', (location_name, uid))
            location_id = self.__cursor.fetchone()
            location_id = int(location_id[0])
        except sqlite3.IntegrityError:
            print "snapshot alled for unknown place %s with uid: %d" % ( location_name, uid )
            return -1

        print "location id: %d" % location_id

        try:
            self.__cursor.execute('insert into location_snapshot(uid, location_id, ref_time) values(?,?,?)', (uid, location_id, timestamp))
        except sqlite3.OperationalError:
            self.__create_snapshot_table()
            self.__cursor.execute('insert into location_snapshot(uid, location_id, ref_time) values(?,?,?)', (uid, location_id, timestamp))

        return 0

    def make_model(self, uid, span_in_weeks):
        
        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "make_model called for unknown uid %d" % uid
            return None

        # what's the latest time in the database for this user
        max_time = None
        try:
            self.__cursor.execute('select max(ref_time) from location_snapshot where uid=?', (uid,))
            mPt = self.__cursor.fetchone()

            max_time = datetime.strptime(str(mPt[0]), "%Y-%m-%d %H:%M:%S")
        except sqlite3.IntegrityError:
            print "could not get max ref_time from database"
            return None

        # count how much data is available for this user in the time range of
        # now to now - span_in_days
        d1 = max_time - timedelta(weeks=span_in_weeks)
        d2 = max_time

        print "D1: ", d1
        print "D2: ", d2
        
        data = None
        try:
            self.__cursor.execute('select count(*) from location_snapshot where uid=? and ref_time>=? and ref_time<=?', (uid, d1,d2))
            num_entries = int(self.__cursor.fetchone()[0])

            self.__cursor.execute('select count(*) from location where uid=?', (uid,))
            num_places = int(self.__cursor.fetchone()[0])

            # get actual data points
            self.__cursor.execute('select loc.ref_time as "ts [timestamp]", position.name from location_snapshot loc, location position where loc.uid=? and loc.ref_time>? and loc.ref_time<? and loc.uid=position.uid and loc.location_id=position.lid', ( uid, d1, d2))
            
            data = self.__cursor.fetchall()

        except sqlite3.IntegrityError:
            print "bad count for num_entries and/or num_places %d/%d" % ( num_entries, num_places )
            return None

        print "num_places: %d" % num_places
        print "num_entries: %d" % num_entries

        steps = int((24.0 * 7. *60.0 ) / 15.0)
        m = markov.Markov(steps, num_places, 15, data)

        return m



    def get_locations(self, uid):
        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "snapshot called for unknown uid %d" % uid
            return -1

        try:
            self.__cursor.execute('select * from location where uid = ?', (uid))
        except sqlite3.OperationalError:
            self.__create_location_table()
            self.__cursor.execute('select * from location where uid = ?', (uid))

        return self.__cursor.fetchall()



    # the __ bit means only other methods in this class can execute these 
    # okay, so you can if you are insistent, but you have to take special measures
    
    # note that the types declared as 'int' have been switched to 'integer'
    # primary keys do not need a 'not null' specifier.  According to the sqlite 
    # faq an integer type with primary key will do for a table id ( insert a null
    # and it's equivalent to autoincrement in heavier weight databases )
    def __create_user_table(self):
        # create usr table. 
        self.__cursor.execute("""create table if not exists [usr] (
                  [uid]    [integer]       primary key ,
                  [uname]  [varchar](16)   not null unique,
                  [passwdMD5] [varchar](32)   not null )""")
        
    def __create_location_table(self):
        self.__cursor.execute("""create table if not exists [location] (
                  [lid]  [integer]         primary key unique,
                  [uid]  [integer]         not null    references [usr]([uid]),
                  [name]        [varchar](32) not null,
                  [description] [text])""")

    def __create_snapshot_table(self):
        self.__cursor.execute("""create table if not exists [location_snapshot] (
                  [uid]       [integer]      not null    references [usr]([uid]),
                  [location_id]  [integer]      not null    references [location]([lid]),
                  [ref_time]   [timestamp]  not null)""")
        



    
