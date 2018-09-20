import sys
sys.path.append('../')

import financialNodes as fn
import nodes as nd
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import numpy as np
import math
import datetime
import random
from pprint import pprint
from datetime import timedelta
from financialNodes import MarketExperiment
from processingNetwork.ProcessingNetwork import ProcessingNetwork
from processingNetwork.ProcessingNode import ProcessingNode


import pprint

def build_toy_dataset(N, w, noise_std=0.1):
    D = len(w)
    x = np.random.randn(N, D)
    
    y = np.dot(x, w) 
    y = y  + np.random.normal(0, noise_std, size=N)
    return x, y


# ---> LoadData ---> PrepareFeature1 ---> 
class LoadData(ProcessingNode):
    def do_init(self):
        pass
    def do_process(self,feature):
        feature_dict=feature[self.settings['input']].copy()
        feature[self.settings['name']]=[{'lat1': 123, 'lon1':200,'lat2': 12, 'lon2':12}]
        return feature

    
class BatchRegressionNode(ProcessingNode):
    '''
    This class trains any model. It buffers runlengths of features and trains a model when it is ready.
    The job of this system is to forcast the relationship between the predictor and amount of profit. 
    In circumstances where the profit looks negative, it actively prevents trading.
    
    '''
    def do_init(self):
        self.regressor = None
        self.trainingFeature = []
        self.testingFeature = []
        self.countTrain = self.settings['trainCount']
        self.countTest = self.settings['testCount']
        self.rawFeatures = []
        self.finishedFeatures = []
        self.modelIndex = 0
        pass
    
    def loadRawFeature(self,feature):
        
        predictionInt = self.get_dependency_value(0)
        symbols =   feature[self.dependency_list[1]+'_securities']
        pastPredictionInt = self.get_upstream_dependency_value(0)
        pastOrders = self.get_upstream_dependency_value(1)
        
        if len(self.lastFeature) > 0:
            pastSymbols =   self.lastFeature[self.upstream_dependency_list[2]+'_securities']
            
            # Create Dictionary of Trades
            pastSymbolTrades = {}
            for i in range(0,len(pastPredictionInt)):
                pastSymbolTrades[pastSymbols[i]]=pastPredictionInt[i]
            
            if pastPredictionInt and pastOrders:
                if len(pastOrders) > 0:
                    for ro in pastOrders['realOrders']:
                        if ro:
                            security = ro[1][0]
                            prediction = pastSymbolTrades[security]
                            rawFeature = {'order':ro, 'prediction':prediction, }
                            self.rawFeatures.append(rawFeature)
                    for ro in pastOrders['paperOrders']:
                        if ro:
                            security = ro[1][0]
                            prediction = pastSymbolTrades[security]
                            rawFeature = {'order':ro, 'prediction':prediction, }
                            self.rawFeatures.append(rawFeature)
    
    def processFeatures(self):
        # 1 Move the finished orders over for processing
        rawf = self.rawFeatures
        for i in range(len( rawf)-1,-1,-1):
            if len(rawf[i]['order'][1]) == 13:
                self.finishedFeatures.append([rawf[i]['order'][1][11]] + [rawf[i]['prediction'] ])
                rawf.pop(i)
                    
    def normalizeArray(self,arr,mean,std):
        df = pd.DataFrame(arr)
        df = df-mean
        df = df/std
        x = np.array(df)
        return x
    
    def unNormalizeArray(self,arr,mean,std):
        df = pd.DataFrame(arr)
        df = df*std
        df = df+mean
        x = np.array(df)
        return x
    
    def doTraining(self):
        print(len(self.finishedFeatures))
        if len(self.finishedFeatures) > self.countTrain:
            #self.finishedFeatures = []
            #if (self.regressor == None):
            df = pd.DataFrame(self.finishedFeatures)
            D = 1 # one dimension
            self.modelIndex = self.modelIndex + 1
            self.regressor = nd.BRNode({'dimensions':(D,1),'name':'thresholdFit' + str(self.modelIndex)})
            self.r_means = df.mean()
            self.r_stds = df.std()

            #df[1] = df[1]-df[1].mean()
            #df[0] = df[0]-df[0].mean()
            #df[1] = df[1]/df[1].std()
            #df[0] = df[0]/df[0].std()
            xt = self.normalizeArray(df[1],self.r_means[1],self.r_stds[1])
            xt = xt.reshape(-1,1)

            yt = self.normalizeArray(df[0],self.r_means[0],self.r_stds[0])
            yt = yt[:,0]
            #xt = np.array(df[1]).reshape(-1,1)
            #yt = np.array(df[0])
            print(np.shape(xt))
            print(np.shape(yt))

            #display(xt)
            #display(yt)
            self.regressor.train(xt,yt)
            self.regressor.criticise(xt,yt)
            #self.finishedFeatures
            print('clearing features')
            self.finishedFeatures = []
            self.rawFeatures = []
    
    def doPredict(self):
            if (self.regressor):
                predictionInt = self.get_dependency_value(0)
                predictionIntNormal = self.normalizeArray(predictionInt,self.r_means[1] ,self.r_stds[1])
                p = self.regressor.predict(predictionIntNormal,11 )
                p = pd.DataFrame(np.array(p)[:,:,0])
                means = p.mean()
                stds = p.std()
                return means
            return []                
                
    def do_process(self,feature):
        self.loadRawFeature(feature)
        self.processFeatures()
        self.doTraining()
        means = self.doPredict()
        
        #Set the mean value
        feature[self.settings['name']] = means
        
        output = False
        if output==True:
            print('-----------------------')
            #print(self.feature)
            print('pastOrders')
            print(pastOrders)
            print('pastPredictionInt')
            print(pastPredictionInt)
            print('predictionInt')
            print(predictionInt)
            print('-----------------------')
        
        return feature




class OrderSubmitterNew(ProcessingNode):    
    def do_init(self):
        self.me = self.settings['market_experiment']
        self.orders = []
        pass
    
    def do_process(self,feature):
        if self.dependency_list:
            valueKey = self.dependency_list[0]
            sec_key = self.dependency_list[1]
        if (valueKey not in feature):
            return feature
        
        #pprint.pprint(feature)
        
        purchase_decision = feature[valueKey]
        securities = feature[sec_key+'_securities']
        realOrders = []
        paperOrders = []
        
        predictionFilter = self.get_dependency_value(2)
        #symbols =   feature[self.dependency_list[1]+'_securities']

        
        for i in range(len(securities)):
            savedOrder = None
            td = timedelta(days=self.settings['dayHold'],minutes=self.settings['minuteHold'])
            
            
            if purchase_decision[i] and len(predictionFilter) > 0 and predictionFilter[i] > 0.008:
                #print ('(purchase decision, prediction filter)')
                #print (purchase_decision[i],predictionFilter[i])
                
                savedOrder = self.me.do_order_bracket(k=securities[i],limit_timedelta=td)
                realOrders.append(savedOrder)
                self.orders.append(savedOrder)
            # Submit some paper orders so that performance can be studied.
            if(savedOrder == None or savedOrder == []):
                savedOrder = self.me.do_order_bracket(k=securities[i],testOrder=True,limit_timedelta=td)
                paperOrders.append(savedOrder)
                self.orders.append(savedOrder)
        orders = {'realOrders':realOrders,'paperOrders':paperOrders}
        feature[self.settings['name']]=orders
        
        return feature
    
    


def init(settings={}):

	
    print ('initing')

def run_step():
    
    

    feature={}
    
 
    import pprint
 
    f = me.context['purchaseDecisionNetwork'].process(feature)
 
        
    print("me.context['value_total']= "+str(me.context['value_total']))  
    return resp

def addLog(label,val):
    global me
    me.addLog(label,val)

def getLog(elems=slice(None,None)):
    global me
    log = me.getLog()
    newlog = []
    for key in list(log.keys()):
        entry=log[key]
        entry['date']=key
        newlog.append(entry)
    return newlog[elems]

def runExperiment():
    init()
    ctx = run_step()
    while ctx != 0:
        ctx =run_step()

def defaultNetwork(me,settings):
    #
    #
    #
    # Train the purchaseDecisionNetwork network
    # This network processes data, and arrives at a prediction
    purchaseDecisionNetwork_def = {}

    purchaseDecisionNetwork_def['loadData'] = {'name': 'loadData',
                          'type': LoadData,
                          'settings': {'input':'predict_features'},
                          'dependencies': []}

    #purchaseDecisionNetwork_def['prepareFeature'] = { 'name': 'prepareFeature',
    #                           'type': PrepareFeature,
    #                           'settings': {},
    #                           'dependencies': ['loadData'] }
    
    #purchaseDecisionNetwork_def['prepareFeature1'] = { 'name': 'prepareFeature1',
    #                           'type': PrepareFeature1,
    #                           'settings': {
    #                                         'begin':0,'end':6,'index':5
    #                                        },
    #                           'dependencies': ['loadData'] }
    
    #purchaseDecisionNetwork_def['fitPolynomial'] = { 'name': 'fitPolynomial',
    #                           'type': FitPolynomial,
    #                           'settings': {'degree':settings['degree'],'n_points':6},
    #                           'dependencies': ['prepareFeature1'] }
    
    
    #purchaseDecisionNetwork_def['PCA'] = {'name': 'PCA',
    #                      'type': PCA,
    #                      'settings': {'dimensions':4},
    #                      'dependencies': ['prepareFeature']} 



    #purchaseDecisionNetwork_def['nearestNeighbor'] = {'name': 'nearestNeighbor',
    #                      'type': NearestNeighbor,
    #                      'settings': {'radius': settings['NN_radius']},
    #                      'dependencies': ['PCA']} 
    
    
    #purchaseDecisionNetwork_def['purchaseDecision'] = {'name': 'purchaseDecision',
    #                      'type': PurchaseDecision,
    #                      'settings': {'min_neighbors': settings['NN_min_neighbors'], 
    #                                   'min_gain': settings['NN_min_gain'],
    #                                   'min_ratio': settings['NN_min_ratio']},
    #                      'dependencies': ['nearestNeighbor']}    
    
    #purchaseDecisionNetwork_def['purchaseDecision1'] = {'name': 'purchaseDecision1',
    #                      'type': PurchaseDecision1,
    #                      'settings': { 'min_gain': settings['min_gain'] },
    #                      'dependencies': ['fitPolynomial']}   
    
    #purchaseDecisionNetwork_def['purchaseDecisionFilter'] = {'name': 'purchaseDecisionFilter',
    #                      'type': BatchRegressionNode,
    #                      'settings': { 'trainCount': 1500,
    #                                   'testCount': 1500},
    #                      'dependencies': ['fitPolynomial','loadData'],
    #                      'upstream_dependencies': ['fitPolynomial','orderSubmitter','loadData']}   
                    

    #purchaseDecisionNetwork_def['tradeEnterAgent'] = {'name': 'tradeEnterAgent',
    #                      'type': TradeEnterAgent,
    #                      'settings': {'nnRadius':settings['NN_radius'], 
    #                                   'nnGainMean':settings['NN_min_gain'],
    #                                   'nnRatio':  settings['NN_min_ratio'],                                 
    #                                   'marketExplorer': me, 
    #                                   'daysInWindow':-10},
    #                      'dependencies': ['purchaseDecision','PCA','nearestNeighbor','loadData']}
    
    
    #purchaseDecisionNetwork_def['orderSubmitter'] = {'name': 'orderSubmitter',
    #                      'type': OrderSubmitterNew,
    #                      'settings': {'market_experiment':me,'dayHold':0,'minuteHold':20},
    #                      'dependencies': ['purchaseDecision1','loadData','purchaseDecisionFilter']}        

    me.context['purchaseDecisionNetwork']=ProcessingNetwork(purchaseDecisionNetwork_def)
    pn = me.context['purchaseDecisionNetwork']
    return  me.context['purchaseDecisionNetwork']
    

def runExperiment():

    import datetime
    block_id = datetime.datetime.now().isoformat(timespec='seconds')

    base_settings = { 'time_res': 'minute'
                    }
     
    settings=base_settings.copy()
    settings['securities']=secs
    settings.update(dateRange)

    print ('Running Test Experiment')

    init(settings)
    i = 0
    while run_step():
        i = i + 1
        print('.')
        #if i > 20:
        #    break
    print('complete')
