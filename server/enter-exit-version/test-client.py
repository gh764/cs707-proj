import xmlrpclib
from datetime import datetime
import sys

if len(sys.argv)!=2:
    print "Usage problem: expected <%s> uid" % (sys.argv[0])
    exit()

uid = int(sys.argv[1])

s = xmlrpclib.ServerProxy("http://localhost:7500")

# get some uid's

print "getting some random uids"
for _ in range(64):
    print "uid: ", s.request_uid()
print "done getting some random uids"

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
