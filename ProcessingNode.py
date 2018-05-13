'''
ProcessingNode
A processing node does some work on a system and returns the result.
If the node has dependencies, it makes sure that the child node has 'processed' the feature first.

Thus, processing node can form a computation graph (which should be acyclic).
'''
class ProcessingNode():
    def __init__(self,settings=None,dependencies=None,dependency_list=None):
        if settings==None:
            settings={}
        if dependencies==None:
            dependencies={}
        if dependency_list==None:
            dependency_list=[]
        self.dependencies = dependencies
        self.dependency_list=dependency_list
        self.settings = {}
        self.settings.update(settings)
        self.do_init()


    def do_init(self):
        raise Exception('Not Implemented')
        pass

    def process(self,feature):
        for k in self.dependencies:
                self.dependencies[k].process(feature)
        return self.do_process(feature)
    
    def do_process(self):
        raise Exception('Not Implemented')
        pass
    
    def setSetting(self,k,val):
        self.settings[k]=val
   
    def getDependencies(self):
        return self.dependencies
    
    def setDependency(self,did,dependency):
        self.dependencies[did] = dependency
 