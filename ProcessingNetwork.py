'''
A Processing Network is a facade to a collection of processing nodes. 
A Processing Network (PN) is given a json description of a processing network.
The PN constructs this network, and then gives access to the central 'process' method.
'''
class ProcessingNetwork():
    def __init__(self,networkDef,root= ''):
        self.networkDef = networkDef
        self.instanceMap = {}
        self.root = root
        for instanceName in networkDef.keys():
            self.createNodeRecursive(networkDef[instanceName])
            
    def createNodeRecursive(self,instanceDict):
        iName = instanceDict['name']
        
        if(iName in self.instanceMap):
            return self.instanceMap[iName]

        if('settings' in self.networkDef[iName]):
            self.instanceMap[iName] = self.networkDef[iName]['type'](self.networkDef[iName]['settings'],instanceDict['dependencies'])            
        else:
            self.instanceMap[iName] = self.networkDef[iName]['type']()            
        
        instance = self.instanceMap[iName] 
        instanceDict['instance'] = self.instanceMap[iName]        
        
        
        instance.setSetting('name',iName)
        for depName in instanceDict['dependencies']:
            depInstance = self.createNodeRecursive(self.networkDef[depName])
            instance.setDependency(depName,depInstance)

    def process(self,feature={}, rootIn = ''):
        targetNode = rootIn
        if(rootIn == ''):
            targetNode = self.root

        if(targetNode == ''):
            for instanceName in self.networkDef.keys():
                feature = self.instanceMap[instanceName].process(feature)
        else:
            feature = self.instanceMap[targetNode].process(feature)
        return feature
    def __str__(self):
         return self.networkDef