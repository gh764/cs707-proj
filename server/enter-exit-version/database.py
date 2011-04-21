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
                self.__cursor.execute('select uid from usr where uname=? and passwdMd5=?',
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


    def enter_location(self, uid, location_name, timestamp):

        print "enter location"

        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "enter_location called for unknown uid %d" % uid
            return -1
        
        print "uid known"

        # get the location_id for location_name
        location_id = None
        try:
            self.__cursor.execute('select lid from location where name=? and uid=?', (location_name, uid))
            location_id = self.__cursor.fetchone()
            location_id = int(location_id[0])
        except sqlite3.IntegrityError:
            print "exit_location called for unknown place %s with uid: %d" % ( location_name, uid )
            return -1

        
        print "location_id: %d" % location_id
        
        # you cannot enter a location you have already entered
        try:
            self.__cursor.execute('select sum(state_value) from location_state where uid=? and location_id=?', (uid, location_id))
            sumStateVal = self.__cursor.fetchone()[0]
            sumStateVal = int(sumStateVal) if sumStateVal!=None else 0
            if(sumStateVal != 0):
                print "called enter on '%s' when we are already there" % location_name
                return -1
        except sqlite3.OperationalError:
            self.__create_location_state_table()
        except sqlite3.IntegrityError:
            pass
            
        print "no double enter"

        # you can only be in one state at a time
        try:
            self.__cursor.execute('select sum(state_value) from location_state where uid=? and location_id=?', (uid, location_id))
            sumStateVal = self.__cursor.fetchone()[0]
            sumStateVal = int(sumStateVal) if sumStateVal!=None else 0
            if(sumStateVal!=0):
                print "cannot be in more than one state at a time"
                return -1
        except sqlite3.IntegrityError:
            pass
                                  
        print "About to insert the new state"

        # -1 is the state_value for exit
        # 1 is the state_value for enter
        self.__cursor.execute('insert into location_state(uid, location_id, ref_time, state_value) values(?,?,?,?)', (uid, location_id,timestamp, 1))

        print "inserted"

        return 0
        

    def exit_location(self, uid, location_name, timestamp):
        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "exit_location called for unknown uid %d" % uid
            return -1

        # get the location_id for location_name
        location_id = None
        try:
            self.__cursor.execute('select lid from location where name=? and uid=?', (location_name, uid))
            location_id = self.__cursor.fetchone()
            location_id = int(location_id[0])
        except sqlite3.IntegrityError:
            print "exit_location called for unknown place %s with uid: %d" % ( location_name, uid )
            return -1

        # you cannot exit a state you haven't entered.  check this
        try:
            self.__cursor.execute('select sum(state_value) from location_state where uid=? and location_id=?', (uid, location_id))
            sumStateVal = int(self.__cursor.fetchone()[0])
            if(sumStateVal != 1):
                print "called exit on '%s' when it's never been entered" % location_name
                return -1
        except sqlite3.IntegrityError:
            print "called exit on '%s' when it's never been entered" % location_name
            return -1
        except sqlite3.OperationalError:
            self.__create_location_state_table()
            print "called exit on '%s' when it's never been entered" % location_name
            return -1

        # -1 is the state_value for exit
        self.__cursor.execute('insert into location_state(uid, location_id, ref_time, state_value) values(?,?,?,?)', (uid, location_id,timestamp, -1))
        return 0
    
    def __get_location(self, uid, timestamp):
        # assumes uid exists

        self.__cursor.execute('select name, lid from location where uid=?', (uid,))
        lid_list = self.__cursor.fetchall()

        for name, lid in lid_list:
            self.__cursor.execute('select sum(state_value) from location_state where uid=? and location_id=? and ref_time<?', (uid, lid, timestamp))
            sumStateVal = int(self.__cursor.fetchone()[0])

            if sumStateVal>0:
                return (timestamp, name)
            
    def make_model(self, uid, span_in_weeks, bin_size_minutes):

        print "make_model called"

        # check to see if the uid is known
        try:
            self.__cursor.execute('select uid from usr where uid=?', (uid,))
        except sqlite3.IntegrityError:
            print "make_model called for unknown uid %d" % uid
            return None

        print "make_model uid known"
        # what's the latest time in the database for this user
        max_time = None
        try:
            print "before select: ", uid, " ", type(uid)
            self.__cursor.execute('select max(ref_time) from location_state where uid=?', (uid,))
            print "after select"
            mPt = self.__cursor.fetchone()
            print "mPt: ", mPt

            max_time = datetime.strptime(str(mPt[0]), "%Y-%m-%d %H:%M:%S")
        except sqlite3.IntegrityError:
            print "could not get max ref_time from database"
            return None
        except sqlite3.OperationalError:
            print "location state database does not exist"
            self.__create_location_state_table()
            return None

        print "max time: ", max_time

        # count how much data is available for this user in the time range of
        # now to now - span_in_days
        d1 = max_time - timedelta(weeks=span_in_weeks)
        d2 = max_time

        print "D1: ", d1
        print "D2: ", d2

        data = []
        present = d1
        while(present<=d2):
            ts, name = self.__get_location(uid, present)
            data.append( (ts,name) )
            present = present + timedelta(minutes=bin_size_minutes)

        try:
            self.__cursor.execute('select count(*) from location where uid=?', (uid,))
            num_places = int(self.__cursor.fetchone()[0])
        except sqlite3.IntegrityError:
            print "bad count for num_entries and/or num_places %d/%d" % ( num_entries, num_places )
            return None

        print "num_places: %d" % num_places

        steps = int((24.0 * 7. *60.0 ) / bin_size_minutes)
        m = markov.Markov(steps, num_places, bin_size_minutes, data)

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
        

    def __create_location_state_table(self):
        """Note that state_value will be set to 1 for entering a state
        and -1 for exiting.
        """
        self.__cursor.execute("""create table if not exists [location_state] (
                  [uid]         [integer]     not_null     references [usr]([uid]),
                  [location_id] [integer]     not_null     references [location]([lid]),
                  [ref_time]    [timestamp]   not null,
                  [state_value] [integer]     not null)""")


    
