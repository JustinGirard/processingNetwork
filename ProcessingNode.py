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
            dependency_list=[]
        if upstream_dependency_list==None:
            upstream_dependency_list=[]

        self.dependencies = dependencies
        self.dependency_list=dependency_list
        self.upstream_dependency_list=upstream_dependency_list
        self.settings = {}
        self.settings.update(settings)
        self.retVal=None
        self.processed=False
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
        if not self.processed:
            #print(self.settings['name'] + " executing")
            for k in self.dependencies:
                #print(self.settings['name']+ " calling " + self.dependencies[k].settings['name'])
                self.dependencies[k].process(feature)
            self.retVal=self.do_process(feature)
            self.processed=True
        #else:
            #print(self.settings['name'] + " called but has already executed")
        return self.retVal

    def get_dependency_value(self,keyInt):
        if self.dependency_list:
            valueKey = self.feature[self.dependency_list [keyInt]]
            return valueKey 
        return None

    def get_upstream_dependency_value(self,keyInt):
        if self.upstream_dependency_list:
            valueKey = None
            if self.upstream_dependency_list [keyInt] in self.lastFeature:
                valueKey = self.lastFeature[self.upstream_dependency_list [keyInt]]
            return valueKey 
        return None

    def get_dependency_instance(self,keyInt):
        if self.dependency_list:
            valueKey = self.dependencies[keyInt]
            return valueKey 
        return None


    def do_process(self):
        raise Exception('Not Implemented')
        pass
    
    def setSetting(self,k,val):
        self.settings[k]=val
   
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
   
    def resetProcessed(self):
        self.processed=False
        self.retVal=None
 