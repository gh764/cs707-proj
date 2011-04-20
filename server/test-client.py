import xmlrpc.client
from datetime import datetime, timedelta, date
from random_schedule_generator import scheduled_item, daily_schedule, \
     event_generator
from server_task import server_task

s = xmlrpc.client.ServerProxy("http://localhost:7500")

# create new user. uid=last 7 dig of tel#.
uid = 5178293
passwd = 'passwd'
if False and s.register(uid, passwd) != -1: 

    home = s.add_location(uid, "HOME", 170, 180, 50)
    campus = s.add_location(uid, 'CAMPUS', 130, 189, 150)
    work = s.add_location(uid, 'WORK', 120, 179, 75)

    dpt_home = scheduled_item(None, home, 0, 1000, 0, [1, 0, 0], [10, 3, 2], None, [3, 5])
    at_campus = scheduled_item(None, campus, 1030, 1200, 0, [1, 0, 0], [1, 0, 0], [3, 7], [3, 5])
    at_work = scheduled_item(None, work, 1330, 1500, 0.05, [25, 1, 1], [25, 1, 5], [2, 5], [5, 10])
    arv_home = scheduled_item(None, home, 2000, 2359, 0, [1, 0, 0], [1, 0, 0], [3, 5], None)

    monday_schedule = daily_schedule(0)
    monday_schedule.add_scheduled_item(dpt_home)
    monday_schedule.add_scheduled_item(at_campus)
    monday_schedule.add_scheduled_item(at_work)
    monday_schedule.add_scheduled_item(arv_home)

    g = event_generator()
    g.add_daily_schedule(0, monday_schedule)
    today = datetime.today()
    g.generate(s, uid, today + timedelta(days=-90), today)

task = server_task()
task.build_agg_snapshots('./database')
