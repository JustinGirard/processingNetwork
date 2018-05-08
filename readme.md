# ProcessingNetwork

A general graph based processing system. 

## Overview

This is a high level system that can be used to construct graphs that pass data between nodes. Examples:
1. A data processing pipeline with Extract, Transform, and Load nodes.
2. A neural network where each neuron is a node in the network
3. A job or dispatch system that processes jobs in real-time


### Prerequisites

None

### Notebook Examples

```
./roughNotebooks/BasicDataProcessing.ipynb
```

How to process streaming data to apply a moving average filter. How to reconfigure the parameters.

```
./roughNotebooks/NeuralNetwork.ipynb
```
How to create train, and run a basic neural net from scratch. TensorFlow or another platform is better suited in general.


## Instructions to train and predict using codebase
* Import Processing Networks
* Define one more more processing nodes using guidence from ./roughNotebooks/BasicDataProcessing.ipynb
* Create a processing netowork using ./roughNotebooks/BasicDataProcessing.ipynb
* Wrap network as a script
* Run the network as needed


## Known Issues/ Backlog:
* It should be possible to visualize a network
* Fix: Cyclic dependencies will cause a crash



## Authors

* Pax Inc (Justin Girard)

