'''
ProcessingNode
A processing node does some work on a system and returns the result.
If the node has dependencies, it makes sure that the child node has 'processed' the feature first.

Thus, processing node can form a computation graph (which should be acyclic).
'''
class ProcessingNode():
    def __init__(self,settings = {}):
        self.dependencies = {}
        self.settings = {}
        self.do_init()
        self.settings.update(settings)
    def do_init(self):
        raise Exception('Not Implemented')
        pass

    def process(self,feature):
        if len(self.dependencies) > 0:
            for k in self.dependencies.keys():
                self.dependencies[k].process(feature)
        return self.do_process(feature)
    
    def do_process(self):
        raise Exception('Not Implemented')
        pass
    
    def getDependencies(self):
        return self.dependencies
    
    def setDependency(self,did,dependency):
        self.dependencies[did] = dependency
 