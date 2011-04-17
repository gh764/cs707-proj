import datetime, socket, random, array
from database import database
from xmlrpc.server import SimpleXMLRPCServer

class DatabaseHandler:

    def __init__(self, db="./database"):
        self.__database = database(db)
        print('server started...awaiting request')

    def close(self):
        del self.__database

    def register(self, uid, passwd):
        print('%s request::=[type=register;args::=[uid=%d]]' % (datetime.datetime.now() ,uid))
        return self.__database.register(uid, passwd)

    def login(self, uid, passwd):
        print('%s request::=[type=login;args::=[uid=%d]]' % (datetime.datetime.now() ,uid))
        return self.__database.login(uid, passwd)

    def add_location(self, uid, name, longitude, latitude, radius, description=None, altitude=0):
        print('%s request::=[type=add_poi;args::=[uid=%d;name=%s,long=%d,lat=%d,rad=%d,alt=%d]]' %
              (datetime.datetime.now(), uid, name, longitude, latitude, radius, altitude))
        return self.__database.add_location(uid, name, longitude, latitude, radius, altitude)

    def del_location(self, uid, pid):
        return 0

    def get_locations(self, uid):
        print('%s request::=[type=get_poi;args::=[uid=%d]]' % (datetime.datetime.now() ,uid))
        return self.__database.get_locations(uid)

    def get_model(self, uid):
        print('%s request::=[type=get_model;args::=[uid=%d]]' % (datetime.datetime.now() ,uid))
        return self.__database.get_model(uid)

    def snapshot(self, uid, location, start, end):
        print('%s request::=[type=snapshot;args::=[uid=%d,location=%d,s=%s,e=%s]]' %
              (datetime.datetime.now(), uid, location, start, end))
        return self.__database.snapshot(uid, location, start, end)

def main():
    host = "localhost"
    port = 7500

    data_handler = DatabaseHandler()
    
    try:
        server = SimpleXMLRPCServer((host, port))
        server.register_instance(data_handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Caught control-c, closing database connection")
        data_handler.close()

if __name__ == "__main__":
    main()
