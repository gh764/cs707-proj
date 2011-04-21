from SimpleXMLRPCServer import SimpleXMLRPCServer
import datetime, socket, random, array
from database import database
import datetime

class DatabaseHandler:

    def __init__(self, db="./database"):
        print("initializing db-handler")
        self.__database = database(db)

    def close(self):
        del self.__database

    def register(self, uname, passwd):
        return self.__database.register(uname, passwd)

    def login(self, uname, passwd):
        return self.__database.login(uname, passwd)

    def add_location(self, uid, name, description):
        return self.__database.add_location(uid, name, description)

    def snapshot(self, uid, location_name, timestamp):
        converted = datetime.datetime.strptime(str(timestamp), "%Y%m%dT%H:%M:%S")
        return self.__database.snapshot(uid, location_name, converted)

    def del_location(self, uid, location_name):
        return self.__database.del_location(uid, location_name)

    def get_locations(self, uid):
        return self.__database.get_locations(uid)

    def eval_model(self, uid, span_in_weeks, 
                   start_state, end_state, start_time_str, end_time_str):
        
        start_time = datetime.datetime.strptime(str(start_time_str), "%Y%m%dT%H:%M:%S")
        end_time = datetime.datetime.strptime(str(end_time_str), "%Y%m%dT%H:%M:%S")

        print "start_time: ", start_time
        print "end_time: ", end_time

        model = self.__database.make_model(uid, span_in_weeks)

        # okay, this is annoying but xmlrpc doesn't understand
        # scipy's float64 type so we can convert to a python float
        (history_list_scipy, prob_vector_scipy) = model.get_prob_vector(start_state, start_time, end_time, end_state)

        history_list = [ float(a) for a in history_list_scipy ]
        prob_vector = [ float(a) for a in prob_vector_scipy ]

        return (history_list, prob_vector)
        
        
        

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
