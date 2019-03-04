import sys
sys.path.append('../../')
sys.path.append('../')
from processingNetwork import ProcessingNode
from processingNetwork import ProcessingNetwork
from processingNetwork.PipeProcessingNode import ExamplePipeNode
import numpy as np

def large_network_test():
    ndef = {}
    data_id = 'data_in'
    config_id = 'cfg'
    mult = 'multiplier'
    mult2 = 'multiplier2'
    mult3 = 'multiplier3'

    ndef[mult] = {'type': ExamplePipeNode,
                  'dependencies': {'input':(data_id,),
                                   'parameters':{'multiplier':0.1}}
                  }

    ndef[mult2] = {'type': ExamplePipeNode,
                   'dependencies': {'input':(mult,'output'),
                                    'parameters':(config_id ,)}
                  }

    ndef[mult3] = {'type': ExamplePipeNode,
                   'dependencies': {'input':(mult2,'output'),
                                    'parameters':{'multiplier':(mult2,'output')}}
                  }

    pn=ProcessingNetwork(ndef)
    import pprint
    data = {data_id:100,config_id:{}}
    out = pn.process(data)
    pprint.pprint(out)
    
    print("")
    print("")
    print("")
    data = {data_id:100,config_id:{'multiplier':5}}
    out = pn.process(data)
    pprint.pprint(out)

    print("")
    print("")
    print("")
    data = {data_id:100,config_id:{}}
    out = pn.process(data)
    pprint.pprint(out)
    
    print("")
    print("")
    print("")
    data = {data_id:100,config_id:{'multiplier':0.1}}
    out = pn.process(data)
    pprint.pprint(out)
    

def missing_parameter_test1():
    '''
    Testing a missing 'paramaters' input in the source vector.
    '''
    ndef = {}
    hardcoded1 = 'hardcoded'

    ## Tuples, are pointers to data in the datastream. You expect to find tagged data in the data strea,
    ndef = {}
    ndef[hardcoded1] = {'type': ExamplePipeNode,
                  'dependencies': {'input':25}}
    pn=ProcessingNetwork(ndef)
    data = {}
    out = pn.process(data)

def single_node_test2():
    ndef = {}
    hardcoded1 = 'hardcoded'
    
    ndef[hardcoded1] = {'type': ExamplePipeNode,
                  'dependencies': {'input':np.array([0.5,0.5,0.5]),
                                   'parameters':None}}
    pn=ProcessingNetwork(ndef)
    data = {}
    out = pn.process(data)

def single_node_test3():
    ndef = {}
    hardcoded3 = 'hardcoded'

    data_id = "My_Id"
    ndef[hardcoded3] = {'type': ExamplePipeNode,
                  'dependencies': {'input':(data_id,),
                                   'parameters':{'multiplier':np.array([0.2,0.5,0.1])}}}

    pn=ProcessingNetwork(ndef)

    data = {data_id:{'first':1,'second':5,'third':25}}
    out = pn.process(data)

def single_node_help_test():
    pipe = ExamplePipeNode()
    pipe.pipe_help()

def run_tests():
    single_node_test3()
    single_node_test2()
    missing_parameter_test1()
    large_network_test()
    single_node_help_test()

if __name__ == 'main':
    run_tests()
