'''
A Processing Network is a facade to a collection of processing nodes. 
A Processing Network (PN) is given a json description of a processing network.
The PN constructs this network, and then gives access to the central 'process' method.
'''
class ProcessingNetwork():
    def __init__(self,networkDef,root=''):
        self.networkDef = networkDef
        self.instanceMap = {}
        self.root = root
        for instanceName in networkDef:
            self.createNodeRecursive(networkDef[instanceName])
            
    def createNodeRecursive(self,instanceDict):
        iName = instanceDict['name']
        if not iName in self.instanceMap:
            if 'settings' in self.networkDef[iName]:
                settings=self.networkDef[iName]['settings']
            else:
                settings=None
            if 'dependencies' in self.networkDef[iName]:
                dependency_list=self.networkDef[iName]['dependencies']
            else:
                dependency_list=None
            self.instanceMap[iName] = self.networkDef[iName]['type'](settings=settings,dependency_list=dependency_list)            
            instance = self.instanceMap[iName] 
            instanceDict['instance'] = self.instanceMap[iName]        
        
            instance.setSetting('name',iName)
           
            for depName in instanceDict['dependencies']:
                depInstance = self.createNodeRecursive(self.networkDef[depName])
                instance.setDependency(depName,depInstance) 
        return self.instanceMap[iName]

    def getInstance(self,iName):
        return self.instanceMap[iName]

    def process(self,feature=None, rootIn=''):
        # We have to set every node in the network to it's "unprocessed" state
                 
        for instanceName in self.networkDef.keys():
            self.instanceMap[instanceName].resetProcessed()

        if feature==None:
            feature={}
        targetNode = rootIn
        if rootIn == '':
            targetNode = self.root

        if targetNode == '':
            for instanceName in self.networkDef.keys():
                #print(instanceName + " called by ProcessingNetwork")
                feature = self.instanceMap[instanceName].process(feature)
                #print("back in ProcessingNetwork")
                #print("call from " + instanceName + " has returned with feature=")
                #print(feature)
        else:
            #print(targetNode + " called by ProcessingNetwork")
            feature = self.instanceMap[targetNode].process(feature)
        return feature

    def __str__(self):
         return self.networkDef