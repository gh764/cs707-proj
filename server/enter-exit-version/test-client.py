import xmlrpclib
from datetime import datetime

s = xmlrpclib.ServerProxy("http://localhost:7500")

# create some users

if s.register("mnewcomb", "junk")==-1:
    print "user mnewcomb already exists"

if s.register("ghazell", "passwd")==-1:
    print "user ghazell already exists"

if s.register("walker", "sucks")==-1:
    print "user walker already exists"

# login for those users
uid = s.login("ghazell", "passw")
if uid==-1:
    print "wrong username or password for 'ghazell'"
else:
    print "greigs login id=%d" % uid

uid = s.login("walker", "sucks")
if uid is not -1:
    print "walkers login id=%d" % uid
else:
    print "wrong username and/or password for 'walker'"

uid = s.login("mnewcomb", "junk")
if uid is not -1:
    print "mnewcomb login id=%d" % uid
else:
    print "wrong username and/or password for 'mnewcomb'"

start_time = datetime(2011, 4, 18, 8, 0, 0)
end_time = datetime(2011, 4, 18, 22, 0, 0)
model_span_in_weeks = 16
start_state = 'home'
end_state = 'work'
(history_list, prob_vector) = s.eval_model(uid, model_span_in_weeks, 
                                           start_state, end_state,
                                           start_time, end_time)

# history list -> a list of the probability of being in the end_state at 
#                 every step between the start and end
# prob_vector -> the probability in being in any of the known states at
#                the 'end' time

print "history list: ", history_list
print "prob vector: ", prob_vector
