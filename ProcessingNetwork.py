'''
A Processing Network is a facade to a collection of processing nodes. 
A Processing Network (PN) is given a json description of a processing network.
The PN constructs this network, and then gives access to the central 'process' method.
'''
# TODO: Limit feature access to the subset of keys requested to enforce robust networks
# ----- {k: bigdict.get(k, None) for k in ('l', 'm', 'n')} <--- filters for relevant keys
# TODO: Use Named Dependencies instead of a straight positional list
# TODO: pas feature and last feature in a way better way

class ProcessingNetwork():
    def __init__(self,networkDef,root=''):
        self.networkDef = networkDef
        self.instanceMap = {}
        self.root = root
        for instanceName in networkDef:
            self.createNodeRecursive(networkDef[instanceName])
        self.lastFeature = {}

    def createNodeRecursive(self,instanceDict):
        iName = instanceDict['name']
        if not iName in self.instanceMap:
            if 'settings' in self.networkDef[iName]:
                settings=self.networkDef[iName]['settings']
            else:
                settings=None
            upstream_dependency_list = []
            if 'upstream_dependencies' in self.networkDef[iName]:
                upstream_dependency_list=self.networkDef[iName]['upstream_dependencies']

            if 'dependencies' in self.networkDef[iName]:
                dependency_list=self.networkDef[iName]['dependencies']
            else:
                dependency_list=None
            settings['name'] = iName


            # Assign the type
            typeVar = self.networkDef[iName]['type']
            
            if isinstance(self.networkDef[iName]['type'], str):
                import importlib
                typeVar = getattr(importlib.import_module(self.networkDef[iName]['module']),self.networkDef[iName]['type'])


            self.instanceMap[iName] = typeVar(settings=settings,dependency_list=dependency_list,upstream_dependency_list=upstream_dependency_list)            
            instance = self.instanceMap[iName] 
            instanceDict['instance'] = self.instanceMap[iName]        
        
            instance.setSetting('name',iName)
           
            for depParameter in instanceDict['dependencies'].keys():
                depName = instanceDict['dependencies'][depParameter]
                depInstance = self.createNodeRecursive(self.networkDef[depName])
                instance.setDependency(depParameter,depInstance) 
        return self.instanceMap[iName]

    def getInstance(self,iName):
        return self.instanceMap[iName]

    def process(self,feature=None, rootIn=''):
        # We have to set every node in the network to it's "unprocessed" state

        if feature==None:
            feature={}
        targetNode = rootIn
        if rootIn == '':
            targetNode = self.root

        if targetNode == '':
            for instanceName in self.networkDef.keys():
                #print(instanceName + " called by ProcessingNetwork")
                feature = self.instanceMap[instanceName].process(feature,self.lastFeature)
                #print("back in ProcessingNetwork")
                #print("call from " + instanceName + " has returned with feature=")
                #print(feature)
        else:
            #print(targetNode + " called by ProcessingNetwork")
            feature = self.instanceMap[targetNode].process(feature,self.lastFeature)

        self.lastFeature = feature
        return feature

    def __str__(self):
         return self.networkDef