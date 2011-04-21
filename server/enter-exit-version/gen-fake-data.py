import xmlrpclib
from datetime import timedelta
from datetime import datetime
import random
import itertools

"""
The android phones lent by the professor for CS707 did not have sim cards installed in them.
As a result our code cannot ask the cell network for location information nor transfer it to 
the central server.  So, without significant refactoring our code will not provide useful
location data.  In order to test our markov chain code and central server I wrote a simulator
to generate location information about my day
"""

def pairwise(iterable):
    """take the iterable, make a copy, advance by one in the second 
    and return pairs"""
    iter1, iter2 = itertools.tee(iterable)
    next(iter2, None)
    return itertools.izip(iter1, iter2)



class fake_location_gen:

    def __init__(self, start_dt, end_dt, timestep_min):
        self.timestep_min = timedelta(minutes=timestep_min)
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.known_days_dict = {}
        self.generate()
        

    def day(self, present):
        """
        assume present is the day in question at midnight

        States:
        
        Home
        Other
        Work
        Class
        
        My class schedule:
        M, W ( 2:30 to 3:45 pm)
        T, R ( 1:00 to 2:15 pm)
        F (2:30 to 3:45 pm with a 1/6th chance)
        
        home to other ( earliest 8, latest 10 )
        other to work (8:30 to 10:30)
        1/2 hour to get to class
        work to other (-10 minutes to 5 minutes around 30 minutes before class )
        other to class (-10 minutes to 5 minutes around start of class )
        class to other ( 0 to 10 minutes after end of class )
        other to work ( 30-40 minutes after the end of class )
        saturday or sunday I'll be out for 2 or 3 hours
        """     

        ptuple = present.timetuple()
        index = ptuple.tm_year * 1000 + ptuple.tm_yday
        if index in self.known_days_dict:
            return self.known_days_dict[index]

        # convert present to midnight on the day of present
        present = datetime(ptuple.tm_year, ptuple.tm_mon, ptuple.tm_mday,0,0,0)
        # monday is 0, wednesday is 2, friday is 4
        # sat is 5, sunday is 6
        day_of_week = ptuple.tm_wday
        friday_has_class = random.random()<(1/6.)
        
        if day_of_week==0 or day_of_week==2 or (day_of_week==4 and friday_has_class):
            state_list = []
            # home to other
            early = present+timedelta(hours=8)
            late = present+timedelta(hours=10)
            home_to_other = self.choose_time(early, late)
            state_list.append( ("home", present, home_to_other))
            
            # other to work
            early = home_to_other + timedelta(minutes=30)
            late = home_to_other + timedelta(minutes=40)
            other_to_work = self.choose_time(early, late)
            state_list.append( ("other", home_to_other, other_to_work) )

            # going to class and time at work
            # work to other
            early = present+timedelta(hours=13, minutes=50)
            late = present+timedelta(hours=14, minutes=5)
            work_to_other = self.choose_time(early, late)

            state_list.append( ("work", other_to_work, work_to_other) )

            # other to class
            early = work_to_other + timedelta(minutes=25)
            late = work_to_other + timedelta(minutes=35)
            other_to_class = self.choose_time(early,late)

            state_list.append( ("other", work_to_other, other_to_class))

            # class to other
            early = present + timedelta(hours=15, minutes=45)
            late = present + timedelta(hours=16)
            class_to_other = self.choose_time(early, late)
            
            state_list.append( ("class", other_to_class, class_to_other))

            # other_to_work
            early = class_to_other + timedelta(minutes=30)
            late = class_to_other + timedelta(minutes=45)
            other_to_work_from_class = self.choose_time(early, late)
            
            state_list.append( ("other", class_to_other, other_to_work_from_class))

            # going home for the day

            # work to other
            early = present + timedelta(hours=17,minutes=30)
            late = present + timedelta(hours=19, minutes=30)
            work_to_other_home = self.choose_time(early, late)

            state_list.append( ("work", other_to_work_from_class, work_to_other_home))
            
            # other to home
            early = work_to_other_home + timedelta(minutes=30)
            late = work_to_other_home + timedelta(hours=1)
            other_to_home = self.choose_time(early, late)
            state_list.append( ("other", work_to_other_home, other_to_home))
            
            state_list.append( ("home", other_to_home, present+timedelta(hours=24)))
            
            transition_list = state_list

        elif (day_of_week==4 and not friday_has_class):
            # home to other
            state_list = []

            early = present+timedelta(hours=8)
            late = present+timedelta(hours=10)
            home_to_other = self.choose_time(early, late)

            state_list.append( ("home", present, home_to_other))

            # other to work
            early = home_to_other + timedelta(minutes=30)
            late = home_to_other + timedelta(minutes=40)
            other_to_work = self.choose_time(early, late)
            
            state_list.append( ("other", home_to_other, other_to_work))

            # going home for the day
            # work to other
            early = present + timedelta(hours=17,minutes=30)
            late = present + timedelta(hours=19, minutes=30)
            work_to_other_home = self.choose_time(early, late)
            
            state_list.append( ("work", other_to_work, work_to_other_home))
            
            # other to home
            early = work_to_other_home + timedelta(minutes=30)
            late = work_to_other_home + timedelta(hours=1)
            other_to_home = self.choose_time(early, late)

            state_list.append( ("other", work_to_other_home, other_to_home))

            state_list.append( ("home", other_to_home, present+timedelta(hours=24)))
            
            transition_list = state_list
                               

        elif (day_of_week==1 or day_of_week==3):
            state_list = []
            # home to other
            early = present+timedelta(hours=8)
            late = present+timedelta(hours=10)
            home_to_other = self.choose_time(early, late)

            state_list.append( ("home", present, home_to_other))

            # other to work
            early = home_to_other + timedelta(minutes=30)
            late = home_to_other + timedelta(minutes=40)
            other_to_work = self.choose_time(early, late)
            
            state_list.append( ("other", home_to_other, other_to_work))

            # going to class
            
            # work to other
            early = present+timedelta(hours=12, minutes=20)
            late = present+timedelta(hours=12, minutes=35)
            work_to_other = self.choose_time(early, late)
            
            state_list.append( ("work", other_to_work, work_to_other))

            # other to class
            early = work_to_other + timedelta(minutes=25)
            late = work_to_other + timedelta(minutes=35)
            other_to_class = self.choose_time(early,late)

            state_list.append( ("other", work_to_other, other_to_class))

            # class to other
            early = present + timedelta(hours=13, minutes=15)
            late = present + timedelta(hours=15, minutes=30)
            class_to_other = self.choose_time(early, late)
            
            state_list.append( ("class", other_to_class, class_to_other))

            # other_to_work
            early = class_to_other + timedelta(minutes=30)
            late = class_to_other + timedelta(minutes=45)
            other_to_work_from_class = self.choose_time(early, late)

            state_list.append( ("other", class_to_other, other_to_work_from_class))

            # going home for the day

            # work to other
            early = present + timedelta(hours=17,minutes=30)
            late = present + timedelta(hours=19, minutes=30)
            work_to_other_home = self.choose_time(early, late)
            
            state_list.append( ("work", other_to_work_from_class, work_to_other_home))

            # other to home
            early = work_to_other_home + timedelta(minutes=30)
            late = work_to_other_home + timedelta(hours=1)
            other_to_home = self.choose_time(early, late)

            state_list.append( ("other", work_to_other_home, other_to_home))

            state_list.append( ("home", other_to_home, present+timedelta(hours=24)))

            transition_list = state_list

        else:
            # has to be the weekend

            state_list = []

            # I go out from 1 to 4 hours anywhere from 9 am to 4pm
            # home to other
            early = present + timedelta(hours=9)
            late = present + timedelta(hours=16)
            home_to_other = self.choose_time(early, late)

            state_list.append( ("home", present, home_to_other))

            # other to home
            early = home_to_other + timedelta(hours=1)
            late = home_to_other + timedelta(hours=4)
            other_to_home = self.choose_time(early,late)

            state_list.append( ("other", home_to_other, other_to_home))

            state_list.append( ("home", other_to_home, present+timedelta(hours=24)))
            
            transition_list = state_list
            
        #start_at_home = ( "home", "home", present )
        #transition_list.insert(0, start_at_home)
        self.known_days_dict[index] = transition_list

        return transition_list
            
            

    def choose_time(self, early, late):
        """form a line of 0 % at the early time and 100% at the late
        step from early to late in intervals of 1 second, flipping a coin
        until we find the transition
        """
        done=False
        diff = late-early

        # random() returns between 0 and 1 ( inclusive )
        # so with one random number figure out how many extra seconds to add 
        # to early
        rand_seconds = random.random() * diff.seconds
        choosen_time = early + timedelta(seconds = rand_seconds)

        return choosen_time

    def search(self, current_dt, transition_list):

        p = pairwise(transition_list)
        first = transition_list[0]
        last = transition_list[-1]

        if current_dt < first[2]:
            return first
        elif current_dt >= last[2]:
            return last

        for trans1, trans2 in p:
            if current_dt >= trans1[2] and current_dt < trans2[2]:
                return trans1


    def generate(self):
        s = xmlrpclib.ServerProxy("http://localhost:7500")
        
        if s.register("mnewcomb", "junk")==-1:
            print "user mnewcomb already exists"
        
        uid = s.login("mnewcomb", "junk")
        if uid is -1:
            print "wrong username and/or password for 'mnewcomb'"
            return

        # add work/home/other/class
        s.add_location(uid, "work", "matts work")
        s.add_location(uid, "home", "matts home")
        s.add_location(uid, "other", "other-duh")
        s.add_location(uid, "class", "matts class")
        
        
        current_dt = self.start_dt
        while(current_dt < self.end_dt):
            # do stuff
            transitionList = self.day(current_dt)
            
            for ( name, startTime, endTime ) in transitionList:
                print "%s : ( %s -> %s )" % (name, startTime, endTime)
                s.enter_location(uid, name, startTime)
                s.exit_location(uid, name, endTime)

            current_dt += timedelta(hours=24)


if __name__=="__main__":
    d1 = datetime(2011, 1, 18, 0,0,0)
    d2 = datetime(2011, 5, 13, 0,0,0)
    
    a = fake_location_gen(d1,d2, 15)
