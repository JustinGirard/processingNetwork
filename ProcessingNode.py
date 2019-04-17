'''
ProcessingNode
A processing node does some work on a system and returns the result.
If the node has dependencies, it makes sure that the child node has 'processed' the feature first.

Thus, processing node can form a computation graph (which should be directed, acyclic) There ARE mechanisms for feedback (!).
'''
import sys
sys.path.append('../')
from  findclass.findclass import findclass
def QuickInputNode(func,input_field):
    def do_input(self,feature,context):
        return func(feature,context)
         
    c = type(func.__name__, (ProcessingNode,), {'do_input':do_input})
    node = {}
    node['type'] = c
    node['dependencies'] = {}
    node['dependencies']['input'] = input_field
    return node

def QuickProcessingNode(func,input_field):
    def do_process(self,feature,context):
        return func(feature,context)
    c = type(func.__name__, (ProcessingNode,), {'do_process':do_process})
    node = {}
    node['type'] = c
    node['dependencies'] = {}
    for k in input_field:
        node['dependencies'][k] = input_field[k]
    return node


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
        self.retVal=None
        self.do_init() 
        #assert 'name' in self.settings

    def do_init(self):
        #raise Exception('Not Implemented')
        pass
    
    def process(self,feature,lastFeature={}):
        #print(self.settings['name']+".process()")
        self.lastFeature = lastFeature
        self.feature = feature
        for k in self.dependencies.keys():
            if self.dependencies[k].settings['name'] not in feature: 
                self.dependencies[k].process(feature)
        
        # Re initalize and locate features
        features = {}
        for key in self.settings:
                features[key] = self.settings[key]
        for key in self.dependency_list:
                features[key] = self.get_dependency_value(key)
        for key in self.upstream_dependency_list:
            features[key] = self.get_upstream_dependency_value(key)
        for key in features:
            self.settings[key] = features[key]

        #print('SETTINGS:')
        #print('features:',features)
        #print('self.settings:',self.settings)
        #print('SETTINGS END:')
        try:
            feature[self.settings['name']] =  self.do_process(features,self.settings)
        except Exception as e:
            print(self.settings)
            print(self.settings['name'])
            print(features )
            print(self.settings )
            #print(feature[self.settings['name']])
            raise e

        self.retVal=feature
        return self.retVal

    def getValueForSetting(self,dependency):
            if(isinstance(dependency,list) and dependency[0]=='__ref'):
                dependency = tuple(dependency)
                dependency=dependency[1:]
            if(isinstance(dependency,tuple)):
                breadcrumb = list(dependency)
                className =breadcrumb[0] 
                breadcrumb.pop(0)
                valueKey = self.feature[className] #First look for a value from the network
                for k in breadcrumb:
                    try:
                        valueKey = valueKey[k] # recursively seek the value
                    except:
                        valueKey = None
                        break
            else:
                valueKey = dependency # If the value is not a tuple, it is a hard coded setting
            return valueKey 

    def get_dependency_value(self,key):
        valueKey = None
        dependency = self.dependency_list [key]
        if(isinstance(dependency,dict)):

            d = {}
            for dkey in dependency.keys():
                d[dkey] = self.getValueForSetting(dependency[dkey])
            
            return d
        else:
            return self.getValueForSetting(dependency)
    def get_upstream_dependency_value(self,key):
        valueKey = None
        try:
            if(isinstance(self.upstream_dependency_list [key],list) and self.upstream_dependency_list [key][0]=='__ref'):
                self.upstream_dependency_list [key] = tuple(self.upstream_dependency_list [key])
                self.upstream_dependency_list [key]= self.upstream_dependency_list [key][1:]
            if(isinstance(self.upstream_dependency_list [key],tuple)):
                breadcrumb = list(self.upstream_dependency_list [key])
                className =breadcrumb[0] 
                breadcrumb.pop(0)
                valueKey = self.lastFeature[className] #First look for a value from the network
                for k in breadcrumb:
                    valueKey = valueKey[k] # recursively seek the value
            else:
                valueKey = self.settings[k] # If the value is not a tuple, it is a hard coded setting
        except:
            pass
        return valueKey 

    #def get_dependency_instance(self,key):
    #    if self.dependency_list:
    #        valueKey = self.dependencies[key]
    #        return valueKey 
    #    return None

    def do_input(self,features,settings):
        raise Exception ("Not implemented")

    def do_process(self,features,settings):
        try:
            return self.do_input(features['input'],settings)
        except Exception as e:
            import traceback
            err_str =  traceback.format_exc(limit=50)
            print(err_str)
            print('missing ["input"]--------------')
            print(features)
            print('--------------')
            raise e
    def setSetting(self,k,val):
        self.settings[k]=val
   
    def getSetting(self,k):
        return self.settings[k]

    def getSettings(self):
        return self.settings

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