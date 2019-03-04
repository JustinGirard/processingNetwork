'''
A Processing Network is a facade to a collection of processing nodes. 
A Processing Network (PN) is given a json description of a processing network.
The PN constructs this network, and then gives access to the central 'process' method.
'''
# TODO: Limit feature access to the subset of keys requested to enforce robust networks
# ----- {k: bigdict.get(k, None) for k in ('l', 'm', 'n')} <--- filters for relevant keys
# TODO: Use Named Dependencies instead of a straight positional list
# TODO: pas feature and last feature in a way better way
from findclass.findclass import findclass

class ProcessingNetwork():

    def __init__(self,networkDef,root=''):
        self.networkTemplate = networkDef.copy()
        self.networkDef = networkDef
        self.instanceMap = {}
        self.root = root
        for instanceName in networkDef:
            networkDef[instanceName]['name'] = instanceName
            self.createNodeRecursive(networkDef[instanceName])
        self.lastFeature = {}
    def getNetworkTemplate(self):
        return self.networkTemplate

    def createNodeRecursive(self,instanceDict):
        iName = instanceDict['name']
        if not iName in self.instanceMap:
            #if 'settings' in self.networkDef[iName]:
            #    settings=self.networkDef[iName]['settings']
            #else:
            #    settings=None
            upstream_dependency_list = {}
            dependency_list = {}
            settings = {}
            if 'upstream_dependencies' in self.networkDef[iName]:
                input_list=self.networkDef[iName]['upstream_dependencies']
                for ik in input_list.keys():
                    iItem = input_list[ik]
                    if isinstance(iItem, tuple):
                        upstream_dependency_list[ik]= iItem
                    else:
                        settings[ik] = iItem


            if 'dependencies' in self.networkDef[iName]:
                input_list=self.networkDef[iName]['dependencies']
                for ik in input_list.keys():
                    iItem = input_list[ik]
                    dependency_list[ik]= iItem
                    #if isinstance(iItem, tuple):
                    #    dependency_list[ik]= iItem
                    #else:
                    #    settings[ik] = iItem

            # Assign the type
            if 'module' in self.networkDef[iName]:
                typeVar = findclass(self.networkDef[iName]['type'],self.networkDef[iName]['module'])
            else:
                typeVar = findclass(self.networkDef[iName]['type'])

            try:
                self.instanceMap[iName] = typeVar(settings=settings,dependency_list=dependency_list,upstream_dependency_list=upstream_dependency_list)            
            except Exception as e:
                import traceback
                err_str =  traceback.format_exc(limit=50)
                print(err_str)
                print("Trouble instancing a ProcessingNode, here is some info:")
                print("-----------------------------------")
                print("iName",iName)
                print("settings",settings)
                print("dependency_list",dependency_list)
                print("upstream_dependency_list",upstream_dependency_list)
                print("type",typeVar)
                print("-----------Re-raising error---------")
                raise e
            instance = self.instanceMap[iName] 
            instanceDict['instance'] = self.instanceMap[iName]        
        
            instance.setSetting('name',iName)
           
            for depParameter in instanceDict['dependencies'].keys():
                depName = instanceDict['dependencies'][depParameter]
                if isinstance(depName,tuple):
                    try:
                        depInstance = self.createNodeRecursive(self.networkDef[depName[0]])
                        instance.setDependency(depParameter,depInstance) 
                    except:
                        pass
        return self.instanceMap[iName]

    def getInstance(self,iName):
        return self.instanceMap[iName]

    def do_preprocess(self):
        pass
    def do_postprocess(self):
        pass

    def process(self,feature=None, rootIn=''):
        # We have to set every node in the network to it's "unprocessed" state
        self.do_preprocess()
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
        self.do_postprocess()
        return feature

    def __str__(self):
         return self.networkDef