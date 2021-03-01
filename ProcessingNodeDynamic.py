'''
ProcessingNode
A processing node does some work on a system and returns the result.
If the node has dependencies, it makes sure that the child node has 'processed' the feature first.

Thus, processing node can form a computation graph (which should be directed, acyclic) There ARE mechanisms for feedback (!).
'''

class lazy_function():
    def execute():
        return None
    
    def __repr__(self):
        return str(repr(self.execute()))
    
    def __dict__ (self):
        return dict(eval(repr(self.execute())))
    
    def __str__(self):
        return str(repr(self.execute()))
    
    def __add__(self,ob):
        return ob+self.execute()

def lazy_get(self,key,val):
    if lazy_function == type(val):
        #print("FUNC VAL for key "+str(key))
        retval = val.execute() 
        #print("WITH TYPE  "+str(type(retval)))
        return retval
    else:
        if type(val) == dict:
            return lazy_dict(val)
        elif type(val) == list:
            return lazy_list(val)
        elif type(val) == tuple:
            return lazy_tuple(val)
        else:
            #print("DEFAULT VAL")
            return val

class lazy_dict(dict):
    def __getitem__(self,key):
        #print("__________________________________")
        #print("DICT GET ITEM> " + str(key))
        val = super().__getitem__(key)
        item =lazy_get(self,key,val)
        while type(item) == lazy_function:
                item = item.execute()
        
        #print("GOT ITEM> " + str(item))
        #print("GOT TYPE> " + str(type(item)))
        #print("__________________________________")
        return item
    def copy(self):
        return lazy_dict(super().copy())
        
    '''
    def __repr__(self):
        r_dic = {}
        for k in self.keys():
            r_dic[k] = lazy_get(self,k,self[k])
        import pprint
        print("GENERATING... ")
        print(r_dic.keys())
        pprint.pprint(r_dic)
        print("....FINISHED... ")
        
        return str(r_dic)
    '''
    
    
class lazy_list(list):
    def __getitem__(self,key):
        val = super().__getitem__(key)
        item = lazy_get(self,key,val)  
        while type(item) == lazy_function:
                item = item.execute()
        return item          
    
    def copy(self):
        return lazy_list(super().copy())
    
    '''
    def __repr__(self):
        r_list = [] 
        for i in range(0,len(self)):
            r_list.append(lazy_get(self,i,self[i]))
        return repr(r_list)
    '''
class lazy_tuple(tuple):
    def __getitem__(self,key):
        val = super().__getitem__(key)
        item = lazy_get(self,key,val)
        while type(item) == lazy_function:
                item = item.execute()
        return item
    
    def copy(self):
        return lazy_tuple(super().copy())

    '''
    def __repr__(self):
        r_tuple = tuple()
        for i in range(0,len(self)):
            r_tuple.append(lazy_get(self,i,self[i]))
        return repr(r_tuple)
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


class ProcessingNodeDynamic():
    def __init__(self,settings=None,dependencies=None,dependency_list=None,upstream_dependency_list=None,lazy_load=False):
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
        self.settings = lazy_dict({})
        self.settings.update(settings)
        self.retVal=None
        self.lazy_load = lazy_load
        
        
        self.do_init() 
        #assert 'name' in self.settings

    def do_init(self):
        #raise Exception('Not Implemented')
        pass
    
    def process(self,feature_in,lastFeature={}):
        #print(self.settings['name']+".process()")
        self.lastFeature = lastFeature
        self.feature = feature_in
        #print("ORIG FEATURE")
        #print(self.feature)
        #for k in self.dependencies.keys():
        #    if self.dependencies[k].settings['name'] not in feature_in: 
        #        self.dependencies[k].process(feature_in)
        
        #print("INITALIZING KEYS FOR THIS NODE" + str(list(self.dependencies.keys())))
        
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
            feature_in[self.settings['name']] =  self.do_process(lazy_dict(features),self.settings)
        except Exception as e:
            print(self.settings)
            print(self.settings['name'])
            print(feature_in )
            print(self.settings )
            #print(feature[self.settings['name']])
            raise e

        self.retVal=feature_in
        return self.retVal
    def dynamicProcess(self,classname):
        for str_tuple in self.dependencies.keys():
            tup = eval(str_tuple)
            #print(type(tup))
            #print(tup)
            if tup[0] == classname:
                #print("PROCESSING" + classname)
                #print("PROCESSING FEATURE")
                #print(self.feature)

                obj =  self.dependencies[str_tuple]
                #print('--------------------')
                #print('--------------------')
                #print('--------------------')
                self.dependencies[str_tuple].process(self.feature)

    def getValueForSetting(self,dependency):
            if(isinstance(dependency,list) and  len(dependency) > 0 and dependency[0]=='__ref'):
                dependency = tuple(dependency)
                classname =dependency [1] 
                dependency=dependency[1:]
                #print("LOOKING UP REFRENCE HERE")
                #print(dependency)
                        
                
            if(isinstance(dependency,tuple)):
                breadcrumb = list(dependency)
                className =breadcrumb[0] 
                breadcrumb.pop(0)
                def extract_value_inline():
                    #print("EXTRACTING VALUE FOR "+classname)
                    #print("EXTRACTING VALUE FOR "+className)
                    try:
                        if not classname in self.feature:
                            self.dynamicProcess(classname)
                        valueKey = self.feature[className] #First look for a value from the network
                        #print("EXTRACTING VAL with type "+ str(type(valueKey)))
                    except:
                        return None
                    for k in breadcrumb:
                        try:
                            #print("EXTRACTING V2")
                            valueKey = valueKey[k] # recursively seek the value
                        except:
                            #print("EXTRACTING V3")
                            valueKey = None
                            break
                    #print("RETURNING VAL with type "+ str(type(valueKey)))
                    return valueKey
                lf = lazy_function()
                lf.execute = extract_value_inline 
                
                #if self.lazy_load ==True:
                valueKey = lf
                #else:
                #    valueKey = extract_value_inline()
            else:
                d = {}
                if(isinstance(dependency,dict)):
                    for dkey in dependency.keys():
                        d[dkey] = self.getValueForSetting(dependency[dkey])
                else:
                    d = dependency
                valueKey = d # If the value is not a tuple, it is a hard coded setting
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
            #print(features)
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