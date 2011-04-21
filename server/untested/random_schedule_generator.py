import datetime
import random
import time

from datetime import timedelta

class activity:
    def __init__(self, description, location, start, finish):
        self.__location = location
        self.__start = start
        self.__finish = finish

    def location(self):
        return self.__location

    def start(self):
        return self.__start

    def finish(self):
        return self.__finish

    def __str__(self):
        return str(self.__location) + ' ' + str(self.__start) + ' - ' + str(self.__finish)
        
class scheduled_item:
    
    def __init__(self, description, location, start, finish,
                 prob_cxl, start_dist=[1, 0, 0], finish_dist=[1,0,0],
                 erly_thrshlds=None, delay_thrshlds=None, sdate=None, edate=None):

        self.__description = description
        self.__location = location
        self.__stime = self.__strptime(start)
        self.__ftime = self.__strptime(finish)
        self.__prob_cxl = prob_cxl
        self.__stime_dist = start_dist
        self.__ftime_dist = finish_dist

        self.__sdate = sdate;
        self.__edate = edate

        self.__thrshlds = (erly_thrshlds, delay_thrshlds)

    def __strptime(self, value):
        if value > 60:
            t = time.strptime(str(value), "%H%M")
        else:
            t = time.strptime(str(value), "%M")
        return datetime.datetime(*t[:6])

    def __rdelta(self, t):
        if t is None or any(t) == False:
            return timedelta(minutes=0)
        elif all(t) == True:
            return timedelta(minutes=random.randint(t[0], t[1]))
        elif t[0] is not None:
            return timedelta(minutes=t[0])
        else:
            return timedelta(minutes=t[1])

    def __date_is_out_of_rng(self, dt):
        
        if (self.__sdate is  None and self.__edate is  None):
            return False
        elif self.__sdate is not None and dt < self.__sdate:
            return True
        elif self.__edate is not None and dt > self.__edate:
            return True
        else:
            return False

    def generate(self, dt, start=None, finish=None):
        # determine if activity is cancelled.
        if random.random() < self.__prob_cxl or \
            self.__date_is_out_of_rng(dt):
            return None

        if start is None:
            start = self.__stime
        if finish is None:
            finish = self.__ftime

        # determine start-time for activity [on_time|early|delayed]
        flg = random.randint(0, sum(self.__stime_dist))
        if flg <= self.__stime_dist[0] and self.__stime_dist[0] != 0:
            s = start
        elif flg <= sum(self.__stime_dist[:2]) and self.__stime_dist[1] != 0:
            s = start - self.__rdelta(self.__thrshlds[0])
        else:
            s = start + self.__rdelta(self.__thrshlds[0])

        # determine stop-time for activity [on_time|early|delayed]
        flg = random.randint(0, sum(self.__ftime_dist))
        if flg <= self.__ftime_dist[0] and self.__ftime_dist[0] != 0:
            e = finish
        elif flg <= sum(self.__ftime_dist[:2]) and self.__ftime_dist[1] != 0:
            e = finish - self.__rdelta(self.__thrshlds[1])
        else:
            e = finish + self.__rdelta(self.__thrshlds[1])
            
        return activity(self.__description, self.__location, datetime.datetime(dt.year, dt.month, dt.day, *s.timetuple()[3:6]),
                        datetime.datetime(dt.year, dt.month, dt.day, *e.timetuple()[3:6]))

class tentative_item:
    def __init__(self, start, finish):
        self.__stime = start
        self.__ftime = finish

class daily_schedule:
    def __init__(self, weekday):
        self.__weekday = weekday
        self.__scheduled_items = []
        self.__tentative_items = []

    def add_scheduled_item(self, i):
        self.__scheduled_items.append(i)

    def add_tentative_item(self, i):
        self.__tentative_items.append(i)

    def generate(self, dt, stime=0, etime=0):
        activities = []
        for s in self.__scheduled_items:
            activity = s.generate(dt)
            activities.append(activity)

        return activities

class event_generator:
    def __init__(self):
        self.__schedule = {}
        
    def add_daily_schedule(self, weekday, s):
        self.__schedule[weekday] = s

    def generate(self, server, uid, start, end):

        u_location = 0 
        u_start = None
        u_finish = None
        
        previous = None
        d = start
        day = timedelta(hours=24)
        while d < end:
            if d.weekday() in self.__schedule:
                ds = self.__schedule[d.weekday()]
                activites = ds.generate(d)
                for a in activites:
                    if a is not None:
                        # snapshot unspecified activity. 
                        if u_start is not None:
                            u_finish = a.start()
                            print("%d  %s - %s" % (u_location, u_start, u_finish))
                            server.snapshot(uid, u_location, str(u_start), str(u_finish))

                        print(a)
                        server.snapshot(uid, a.location(), str(a.start()), str(a.finish()))
                        u_start = None
                        previous = a
                    else:
                        if previous is not None:
                            u_start = previous.finish()
                        elif u_start is not None:
                            u_start = d
                            
            d = d + day
