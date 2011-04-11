import xmlrpclib

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

