import pprint
import numpy as np
import pandas as pd
import nodes as nd
import time

from .ProcessingNode import ProcessingNode 
from .ProcessingNetwork import ProcessingNetwork 

# ---> LoadData ---> 
class LoadData(ProcessingNode):
    def do_init(self):
        pass
    def do_process(self,feature):
        feature_dict=feature[self.settings['input']].copy()
        
        # These two lines accomplish the identical task. The second variable is not reccomended.
        self.setValue(feature_dict)
        self.set(key='',dictData=feature_dict)
        self.set(key='test',dictData="test_value")
        #print(feature)
        #['latln', 'elevation'])
        return feature


    
class BatchRegressionNode(ProcessingNode):
    '''
    This class trains a BR model. It buffers runlengths of features and trains a model when it is ready.
    '''
    def do_init(self):
        self.regressor = None
        self.trainingFeature = []
        self.testingFeature = []
        self.pastFeatures = []
        try:
            self.countTrain = self.settings['trainCount']
            self.countTest = self.settings['testCount']
            self.xKey = self.settings['xKey']
            self.yKey = self.settings['yKey']
            self.predictionLength = self.settings['predictionLength']
            # TODO: generalize so the model can be configured from outside of the class.
        except:
            raise Exception("Could not access settings 'trainCount' and/or 'testCount' in BatchRegressionNode")
            
        self.rawFeatures = []
        self.modelIndex = 0
        pass
    
    def loadRawFeature(self,feature):
        dataIn = self.get_dependency_value(0)
        trainingData = dataIn[self.xKey]
        targetValues = dataIn[self.yKey]
        #TODO - Generalize so this supports all shapes of array.
        newFeature = np.append(trainingData,targetValues)
        self.rawFeatures.append(newFeature)
        #print ('adding features')
        #print(newFeature)
                    
    def normalizeArray(self,arr,mean,std):
        #print(arr)
        # This is very sketchy. Replace with a method to test for lists vs single elements
        try:
            l = len(arr)
            df = pd.DataFrame(arr)
            df = df-mean
            df = df/std
            x = np.array(df)
        except:
            x = arr-mean
            x = arr/std
        return x
    
    def unNormalizeArray(self,arr,mean,std):
        df = pd.DataFrame(arr)
        df = df*std
        df = df+mean
        x = np.array(df)
        return x
    
    def doTraining(self):
        #print(len(self.rawFeatures))
        if len(self.rawFeatures) > self.countTrain:
            self.pastFeatures = self.pastFeatures  + self.rawFeatures 
            self.rawFeatures = []
            #print(self.pastFeatures)
            dataSet = np.array(self.pastFeatures)
            #self.finishedFeatures = []
            #if (self.regressor == None):
            #print (dataSet[0])
            D = len(dataSet[0])-1 # tie the dimension to the length of the feature minus the predictor
            df = pd.DataFrame(dataSet )
            self.modelIndex = self.modelIndex + 1
            dt = time.time()
            dt = str(dt)
            self.regressor = nd.BRNode({'dimensions':(D,1),'name':'thresholdFit' + str(self.modelIndex) + str(dt)})
            self.r_means = df.mean()
            self.r_stds = df.std()
            xt = []

            for i in range(0,D):
                arr = self.normalizeArray(df[i],self.r_means[i],self.r_stds[i])
                xt.append(arr)
                xt[i] = xt[i]
            
            xt = np.array(xt )
            xt = xt[:,:,0]
            xt = xt.transpose()
            #display(df)
            yt = self.normalizeArray(df[D],self.r_means[D],self.r_stds[D])
            yt = yt[:,0]
            yt = np.array(yt )

            print ('shape of training set:')
            print(np.shape(xt))
            print(np.shape(yt))
            

            self.regressor.train(xt,yt)
            #self.regressor.criticise(xt,yt)
            #print('clearing features')
    

    def doPredict(self):
            if (self.regressor):
                dataIn = self.get_dependency_value(0)
                trainingData = dataIn[self.xKey]
                #targetValues = dataIn[self.yKey]
                xt = []

                #print ('shape of training set:')
                for i in range(0,len(trainingData)):
                    arr = self.normalizeArray(trainingData[i],self.r_means[i],self.r_stds[i])
                    xt.append(arr)
                    xt[i] = xt[i]
                xt = np.array(xt)
                
                
                
                p = self.regressor.predict(xt,self.predictionLength )
                #display(p)
                p = np.array(p)
                #print(p)
                if len(np.shape(p)) ==3:
                    p = pd.DataFrame(np.array(p)[:,:,0])
                else:
                    p = pd.DataFrame(np.array(p))
                    
                means = p.mean()
                stds = p.std()
                
                return [means,stds]
            return [0,0]                
                
    def do_process(self,feature):
        self.loadRawFeature(feature)
        self.doTraining()
        [means,stds] = self.doPredict()
        ym = 0
        ys = 0
        if len(self.pastFeatures) > 0:

            dataSet = np.array(self.pastFeatures)
            D = len(dataSet[0])-1 # tie the dimension to the length of the feature minus the predictor

            ym = self.unNormalizeArray(means,self.r_means[D],self.r_stds[D])
            ys = self.unNormalizeArray(stds,self.r_means[D],self.r_stds[D])

        #Set the mean value
        self.setValue({'means':ym,'stds':ys})
        return feature
    
def defaultNetwork(settings):
    purchaseDecisionNetwork_def = {}

    purchaseDecisionNetwork_def['loadData'] = {'name': 'loadData',
                          'type': LoadData,
                          'settings': {'input':'predict_features'},
                          'dependencies': []}
    
    purchaseDecisionNetwork_def['BatchRegressionNode'] = {'name': 'BatchRegressionNode',
                          'type': BatchRegressionNode,
                          'settings': {'trainCount':50,
                                       'testCount':100,
                                       'xKey':'latln',
                                       'yKey':'elevation',
                                       'predictionLength':5},
                          'dependencies': ['loadData']
                            }

    pn=ProcessingNetwork(purchaseDecisionNetwork_def)
    return  pn

# This builds a random dataset with a linear relationship underneath, governed by y= w*x + b
def build_toy_dataset(N, w, noise_std=0.01):
    D = len(w)
    x = np.random.randn(N, D)*5
    
    y = np.dot(x, w) 
    y = y  + np.random.normal(0, noise_std, size=N)
    return x, y

