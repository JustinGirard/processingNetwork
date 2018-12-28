'''
ProcessingNode
A processing node does some work on a system and returns the result.
If the node has dependencies, it makes sure that the child node has 'processed' the feature first.

Thus, processing node can form a computation graph (which should be acyclic).
'''
class ProcessingNode():
    def __init__(self,settings=None,dependencies=None,dependency_list=None,upstream_dependency_list=None):
        if settings==None:
            settings={}
        if dependencies==None:
            dependencies={}
        if dependency_list==None:
            dependency_list={}
        if upstream_dependency_list==None:
            upstream_dependency_list={}

        self.dependencies = dependencies
        self.dependency_list=dependency_list
        self.upstream_dependency_list=upstream_dependency_list
        self.settings = {}
        self.settings.update(settings)
        if not 'name' in self.settings:
            raise Exception("unique name property is required when creating a processing Node")
        self.retVal=None
        self.do_init() 

    def do_init(self):
        raise Exception('Not Implemented')
        pass
    
    def process(self,feature,lastFeature={}):
        #print(self.settings['name']+".process()")
        #print("feature=")
        #print(feature)
        self.lastFeature = lastFeature
        self.feature = feature
        for k in self.dependencies.keys():
            if self.dependencies[k].settings['name'] not in feature: 
                self.dependencies[k].process(feature)
        feature[self.settings['name']] =  self.do_process()
        self.retVal=feature
        return self.retVal



    def get_dependency_value(self,key):
        valueKey = None
        if self.dependency_list:
            try:
                valueKey = self.feature[self.dependency_list [key]] #First look for a value from the network
            except:
                valueKey = self.feature [self.settings['input'][key]] #if that fails, look for a declared input.
            return valueKey 
        return None

    def get_upstream_dependency_value(self,key):
        if self.upstream_dependency_list:
            valueKey = None
            if self.upstream_dependency_list [key] in self.lastFeature:
                valueKey = self.lastFeature[self.upstream_dependency_list [key]]
            return valueKey 
        return None

    def get_dependency_instance(self,key):
        if self.dependency_list:
            valueKey = self.dependencies[key]
            return valueKey 
        return None


    def do_process(self):
        raise Exception('Not Implemented')
        pass
    
    def setSetting(self,k,val):
        self.settings[k]=val
   
    def getSetting(self,k):
        return self.settings[k]

    def setValue(self,dictData={}):
        self.feature[self.settings['name']] = dictData

    def set(self,key='',dictData={}):
        if key == '':
            self.setValue(dictData)
        else:
            self.feature[self.settings['name']][key] = dictData

    def getDependencies(self):
        return self.dependencies
    
    def setDependency(self,did,dependency):
        self.dependencies[did] = dependency 