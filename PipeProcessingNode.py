import sys
sys.path.append('../../')
sys.path.append('../')
from processingNetwork import ProcessingNode
from processingNetwork import ProcessingNetwork
import numpy as np



# An output only pipe. This pipe reads some settings, if present, and alters the tensors passed with an operation 
def MultiplyPipe(tensors,context= None):
    
    try:
        multiplier = context['multiplier']
    except:
        multiplier = 10
    
    ## In general Operations should support np.array, or sets {label:np.array}
    
    if isinstance(tensors,dict): # Support  sets {label:np.array}
        output = {}
        for tkey in tensors.keys():
            if type(tensors) is not np.ndarray:
                tensors[tkey] = np.array(tensors[tkey])
                output[tkey] = tensors[tkey]*multiplier
    else: # Support np.array
        if tensors is not None: # Support None
            if type(tensors) is not np.ndarray:
                tensors = np.array(tensors)
            output = tensors*multiplier
        else:
            output = None
    return output

# A configuration only pipe. Alters some settings, if present, and alters the tensors passed with an operation 
def GeneralConfigure(tensors,context= None):
    try:
        context.update(tensors)
    except:
        pass
    return context


# An output pipe that does some processing. In this case we just output data. 
#In general, output can be decorated with logging, saving, gating, signal amplification, and many other tasks
def GeneralOutput(tensors,context= None):
    if 'output_echo' in context and context['output_echo'] == True:
        print(context['name'],tensors)
    return tensors




class PipeProcessingNode(ProcessingNode):
    def addPipe(self,din=None,**kargs):
        # Might be passing a dict
        try:
            self.pipes
        except:
            self.pipes = {}

        if din and isinstance(din,dict):
            kargs =din

        self.pipes[kargs['name']]= {'name':kargs['name'],
                               'type': kargs['type'], 
                               'io':kargs['io'],
                               'examples':kargs['examples'],
                               'dependency':None,
                                }
        if 'dependency' in kargs:
            self.pipes[kargs['name']]['dependency'] = kargs['dependency']

    def pipe_construct(self):
        raise Exception("Not implemented. See PipeProcessingNode pipe_construct for an example. (This file) ")
        self.pipes = {}
        
        self.pipes['parameters']= {'name':'parameters',
                               'type': GeneralConfigure, 
                               'io':'input',
                               'examples':[{'multiply':10},{'multiply':np.array([2,2])}],
                               'dependency':None,
                                }
        
        self.pipes['input']= {'name':'input',
                                 'type': MultiplyPipe, 
                                 'io':'input',
                                 'examples':[{'a':10,'b':np.array([1,2,3])},10,np.array([2,3])],
                                 'dependency':None,
                                }

        self.pipes['output']= {'name':'output',
                               'type': GeneralOutput, 
                               'io':'output',
                                'examples':[{'a':10,'b':np.array([1,2,3])},10,np.array([2,3])],
                               'dependency':'input',
                              }        
        
    def do_init(self):
        # A mini network of functions
        # Pipes progress raw data, or single tier nested data (like dataframes). 
        # Pipes always have a single dependency, but can have multiple destinations
        self.pipe_construct()
        
        self.inputs = {}
        self.outputs = {}
        self.hidden = {}
        
        for key in self.pipes.keys():
            assert self.pipes[key]['examples']
            pipe = self.pipes[key]
            if pipe['io'] == 'input':
                self.inputs[key]= pipe 
            elif pipe['io'] == 'output':
                self.outputs[key] = pipe 
            elif pipe['io'] == 'hidden':
                self.hidden[key] = pipe 
                pass 
            else:
                raise Exception("Unclear input output status for a node")
        
        #print('--------------------------')
        #print('--------------------------')
        #print('--------------------------')
        #for k in self.inputs:
        #    print (self.inputs[k])

    def interface(self):
        return {'inputs':self.inputs.copy(),'outputs':self.outputs.copy()}
    
    def examples(self):
        return {'inputs':self.inputs.copy(),'outputs':self.outputs.copy()}
    
    def do_process(self,feature,context):
        ## Process the inputs, and build up some data
        data = {}
        #if context['name'] == 'PolynomialModel':
        #    print('-------------------------')
        #    print(context)

        for pipe in self.inputs.values():
                key = pipe['name']
                obj = pipe['type']
                try:
                    feature_data = feature[key]
                except Exception as e:
                    print('-Pipe Load FAIL',context['name'],' ',pipe['name'])
                    print('e',e)
                    feature_data = None
                data[key] = obj(feature_data,context)
        
        #if context['name'] == 'PolynomialModel':
        #    print('xxx-------------------------')
        #    print(data)
        #    print(context)

        for pipe in self.hidden.values():
            data[pipe['name']] = pipe['type'](data[pipe['dependency']],context)
        
        
        ## After the store of data, generate some output
        output = {}
        for pipe in self.inputs.values():
            output[pipe['name']] = data[pipe['name']] #Pipe out the inputs, which after extensive use is frequently desiered

        for pipe in self.outputs.values():
            output[pipe['name']] = pipe['type'](data[pipe['dependency']],context)
        
        return output    
    
    def pipe_help(self,i=0):
        import pprint
        print("inputs: ",list(self.interface()['inputs'].keys()))
        print("")
        print("outputs: ", list(self.interface()['outputs'].keys()))
        print("")
        print("Interface: ",list(self.interface()['inputs'].values())[i])
        print("")
        print("Usage Examples: ",list(self.interface()['inputs'].values())[i]['examples'])
        print("")
        print("Usage Full Example: '",list(self.interface()['inputs'].keys())[i],"': ",list(self.interface()['inputs'].values())[i]['examples'][0])


class ExamplePipeNode(PipeProcessingNode):    
    def pipe_construct(self):
        self.pipes = {}
        
        #self.pipes['parameters']= {'name':'parameters',
        #                       'type': GeneralConfigure, 
        #                       'io':'input',
        #                       'examples':[{'multiply':10},{'multiply':np.array([2,2])}],
        #                       'dependency':None,
        #                        }

        #self.pipes['parameters']= {'name':'parameters',
        #                       'type': GeneralConfigure, 
        #                       'io':'input',
        #                       'examples':[{'multiply':10},{'multiply':np.array([2,2])}],
        #                       'dependency':None,
        #                        }
        #self.addPipe({'name':'parameters',
        #                       'type': GeneralConfigure, 
        #                       'io':'input',
        #                       'examples':[{'multiply':10},{'multiply':np.array([2,2])}],
        #                       'dependency':None,
        #                        })
        self.addPipe(name='parameters',
                    type=GeneralConfigure,
                    io='input',
                    examples=[{'multiply':10},{'multiply':np.array([2,2])}])
        self.pipes['input']= {'name':'input',
                                 'type': MultiplyPipe, 
                                 'io':'input',
                                 'examples':[{'a':10,'b':np.array([1,2,3])},10,np.array([2,3])],
                                 'dependency':None,
                                }

        self.pipes['output']= {'name':'output',
                               'type': GeneralOutput, 
                               'io':'output',
                                'examples':[{'a':10,'b':np.array([1,2,3])},10,np.array([2,3])],
                               'dependency':'input',
                              }        
        