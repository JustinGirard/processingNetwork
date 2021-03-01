'''
A Processing Network is a facade to a collection of processing nodes. 
A Processing Network (PN) is given a json description of a processing network.
The PN constructs this network, and then gives access to the central 'process' method.
'''

from conf.conf import objectConf
from .ProcessingNetwork import ProcessingNetwork
class PersistanceNetwork(ProcessingNetwork):

    def __init__(self,networkDef,root='',mongo_connection=None,serverKey = None):
        super().__init__(networkDef,root)
        if not serverKey:
            raise Exception("You need to provide a server key to identify the mongo record we wish to insert") 
        if not mongo_connection:
            raise Exception("To persist this network a mongo dictionary is needed with all details {host, port, username, password, authSource}")
        self.objectConf = objectConf(mongo_connection)
        self.objectConf.setKey(serverKey)
        self.objectConf.load()
        cacheData = self.objectConf.getSetting('cacheData',{})
        for name in cacheData:
            self.instanceMap[name].settings = cacheData[name] 
 

    def do_preprocess(self):
        self.do_postprocess()

    def do_postprocess(self):
        cacheData = {}
        for name in self.instanceMap:
            cacheData[name] = self.instanceMap[name].settings
        self.objectConf.setSetting('cacheData',cacheData)
        self.objectConf.save()
