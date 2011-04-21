import sqlite3, time
from datetime import date, datetime
from model import model

class stats_struct:

    def __init__(self, location):
        self.__location = location
        self.__score = 0
        self.__frequency = 0
        self.__stime = None
        self.__etime = None

    def inc_frequency(self):
        self.__frequency += 1

    def inc_score(self, s):
        self.__score += s

    def period(self, s, start, e, end):
        if (self.__stime is None or self.__stime > start):
            self.__stime = max(s, start)
        if (self.__etime is None or self.__etime < end):
            self.__etime = min(e, end)
            
    def location(self):
        return self.__location

    def frequency(self):
        return self.__frequency

    def score(self):
        return self.__score

    def start(self):
        return self.__stime

    def end(self):
        return self.__etime

class server_task:

    def __get_timeslot(self, weekday, dt, granularity):
        if weekday == dt.date().weekday():
            return (dt.hour * 60 + dt.minute) // granularity
        # determine if previous day
        elif dt.date().weekday() < weekday or \
            weekday == 0 and dt.date().weekday() == 6:
            return 0
        else:
            return((60 * 24) // granularity)

    def __get_timeslot_rng(self, weekday, arrival, departure, granularity):
        start = self.__get_timeslot(weekday, arrival, granularity)
        end = self.__get_timeslot(weekday, departure, granularity) + 1
        
        return range(start, end)

    def __select_loc(self, totals, slot):
        if slot not in totals:
            return None
        else:
            item = None
            max = 0
            for k, v in totals[slot].items():
                if v.score() > max:
                    max = v.score()
                    item = v
            return item
        
    def __find(self, items, i):
        for j in range(i, len(items)):
            if items[j] is not None:
                return j
        return -1

    def __slot2time(self, s, granularity, opt='f'):
        minutes = s * granularity
        if opt == 'f':
            minutes -= granularity
        return minutes // 60 * 100 + minutes % 60

    def __build_agg_snapshot(self, model, c):

        print("build agg-snapshot")
        #select location snapshots for each day of week.
        for weekday in range(7):
            cmd = c.execute('select location, arrival, departure \
                             from location_snapshot \
                             where uid = ? and strftime("%w", arrival) == ? or strftime("%w", departure) == ? \
                             order by arrival asc', (9175021256, str(weekday), str(weekday)))

            totals = {}

            # obtain the result set.
            r = cmd.fetchall()
            # iterate thru each snapshot from result set.
            for s in r:
                # TODO: set w correctly.
                w = 1
                a = time.strptime(s[1], "%Y-%m-%d %H:%M:%S")
                d = time.strptime(s[2], "%Y-%m-%d %H:%M:%S")
                # TODO: verify mapping of sqlite weekday to python weekday value.
                for i in self.__get_timeslot_rng(weekday - 1, datetime(a.tm_year, a.tm_mon, a.tm_mday, a.tm_hour, a.tm_min, a.tm_sec),
                                                 datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour, d.tm_min, d.tm_sec), model.granularity()):
                    if i not in totals:
                        totals[i] = {}
                    if s[0] not in totals[i]:
                        totals[i][s[0]] = stats_struct(s[0])
                        
                    stats = totals[i][s[0]]
                    stats.inc_frequency()
                    stats.inc_score(model.weight(1))
                    start = a.tm_hour * 100 + a.tm_min
                    end = d.tm_hour * 100 + d.tm_min
                    stats.period(self.__slot2time(i, model.granularity(), 'f'), start,
                                 self.__slot2time(i, model.granularity(), 'c'), end)

            agg = []
            # select locations with max value for each time slot.
            today = date.today()
            for slot in self.__get_timeslot_rng(today.weekday(),
                                                datetime(today.year, today.month, today.day, 0, 0),
                                                datetime(today.year, today.month, today.day, 23, 59),
                                                model.granularity()):
                agg.append(self.__select_loc(totals, slot))

            cxl_thrshld = 0
            ext_limit = 0
            # coalesce values
            idx = self.__find(agg, 0)
            if idx != -1:

                record = agg[idx]
                start = record.start()
                end = record.end()
                i = idx
                while record is not None and i < len(agg):
                    
                    if agg[i] is None or agg[i].location() != record.location():
                        
                        # write record to database or cache for bulk write.
                        c.execute('insert into agg_location_snapshot(mid, version, day, location, start, end) \
                                               values(?,?,?,?,?,?)', (model.id(), model.version(), weekday, record.location(),
                                                                      start, end))
                        # continue to next record.
                        idx = self.__find(agg, i+1)
                        if idx != -1:
                            i = idx
                            record = agg[idx]
                            start = record.start()
                            end = record.end()
                        else:
                            i = len(agg)
                            record = None
                    elif agg[i] is not None:
                        end = agg[i].end()
                    i += 1
                        
                # write last record to database.
                if record is not None:
                    c.execute('insert into agg_location_snapshot(mid, version, day, location, start, end) \
                                               values(?,?,?,?,?,?)', (model.id(), model.version(), weekday,
                                                                      record.location(), start, end))

    def build_agg_snapshots(self, db='./database'):
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # force model rebuild if created within last n days.
        created_within = 7
        # select models which require rebuilding.        
        cmd = c.execute('select mid, uid, version, created_on, last_updated_on, agg_fx, granularity \
                         from model \
                         where julianday(current_date) - julianday(last_updated_on) >= expires_in or \
                               rebuild = 1 and julianday(current_date) - julianday(last_updated_on) >= earliest_rebuild or \
                               julianday(current_date) - julianday(created_on) <= ?', (created_within,)) 
        r = cmd.fetchall()
        for m in r:
            mdl = model(m[0], m[2], m[6]) 
            # update model # && force deletion existing aggregrate snapshot.
            c.execute('delete from agg_location_snapshot where mid = ?', (mdl.id(), ))
            mdl.inc_version()
            c.execute('update model \
                       set version = ?, last_updated_on = current_date, \
                       nr_matches = 0, nr_successful = 0, streak = 0, last10 = 0 \
                       where mid = ?', (mdl.version(), mdl.id()))
            # rebuid aggregrate snapshot.
            self.__build_agg_snapshot(mdl, c)

        c.close()
        conn.commit()
        conn.close()

    
    def archive(db='../database'):
        "delete/archive data older than window_size"
        conn = sqlite3.connect(db)
        c = conn.cursor()

        c.close()
        conn.commit()
        conn.close()
