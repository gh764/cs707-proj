from SimpleXMLRPCServer import SimpleXMLRPCServer
import datetime, socket, random, array
from database import database

class DatabaseHandler:

    def __init__(self, db="./database"):
        print("initializing db-handler")
        self.__database = database(db)

    def close(self):
        del self.__database

    def register(self, uname, passwd):
        return self.__database.register(uname, passwd)

    def login(self, uname, passwd):
        print("login:(%s, %s)" % (uname, passwd))
        return self.__database.login(uname, passwd)

    def add_location(self, uid, name, longitude, latitude, radius, altitude=0):
        print("add-location:(%s, %d, %d, %d, %d)" % (name, longitude, latitude, radius, altitude))
        self.__database.add_location(name, longitude, latitude, radius, altitude)
        return 0

    def del_location(self, uid, pid):
        return 0

    def get_locations(self, uid):
        print("get-location:(%d)" % (uid))
        return self.__database.get_locations(uid)

def main():
    host = "localhost"
    port = 7500

    data_handler = DatabaseHandler()
    
    try:
        server = SimpleXMLRPCServer((host, port))
        server.register_instance(data_handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print "Caught control-c, closing database connection"
        data_handler.close()



if __name__ == "__main__":
    main()
