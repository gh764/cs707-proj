class model:
    def __init__(self, id, version, granularity, agg_fx='a'):
        self.__id = id
        self.__version = version
        self.__granularity = granularity
        self.__agg_fx = agg_fx
        
    def granularity(self):
        return self.__granularity

    def weight(self, w):
        if self.__agg_fx == 'a':
            return 1
        else:
            return 1 

    def id(self):
        return self.__id

    def version(self):
        return self.__version

    def inc_version(self):
        self.__version += 1
