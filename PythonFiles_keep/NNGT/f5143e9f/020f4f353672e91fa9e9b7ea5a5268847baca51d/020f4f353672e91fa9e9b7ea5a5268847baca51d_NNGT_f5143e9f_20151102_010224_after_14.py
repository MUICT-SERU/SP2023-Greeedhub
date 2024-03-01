#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" NeuralNetwork: detailed biological network """

from graph_tool import Graph

from GraphClass import GraphClass
from graph_measure import *



#
#---
# NeuralNetwork
#------------------------

class NeuralNetwork(GraphClass):
    
    """
    .. py:currentmodule:: nngt.core
    
    The detailed class that inherits from :class:`GraphClass` and implements
    additional properties to describe various biological functions
    and interact with the NEST simulator.
	
    :ivar neural_model: :class:`list`
        List of the NEST neural models for each neuron.
    :ivar syn_model: :class:`list`
        List of the NEST synaptic models for each connection.
    :ivar graph: :class:`graph_tool.Graph`
		Main attribute of the class instance
    """

    #------------------#
    # Class attributes #
    #------------------#

    __num_networks = 0
    __max_id = 0
        
    @classmethod
    def num_networks(cls):
        ''' Returns the number of alive instances. '''
        return cls.__num_networks
    
    
    #----------------------------#
    # Instance-related functions #
    #----------------------------#
    
    def __init__ (self, nodes=0, name="Graph",
                  weighted=True, directed=True, graph=None):
        '''
        Initialize GraphClass instance

        Parameters
        ----------
        nodes : int, optional (default: 0)
            Number of nodes in the graph.
        name : string, optional (default: "Graph")
            The name of this :class:`GraphClass` instance.
        weighted : bool, optional (default: True)
            Whether the graph edges have weight properties.
        directed : bool, optional (default: True)
            Whether the graph is directed or undirected.
        graph : :class:`graph_tool.Graph`, optional
            An optional :class:`graph_tool.Graph` to serve as base.
        
        Returns
        -------
        self : :class:`~nggt.core.GraphClass`
        '''
        super(GraphClass, self).__init__()
        self.__id = self.__class__.max_id
        
        self.__class__.__num_networks += 1
        self.__class__.__max_id += 1
        self.__b_valid_properties = True

	@GraphClass.graph.getter
	def graph(self):
		self.__b_valid_properties = False
		warnings.warn("The 'graph' attribute should not be modified!")
		return self._graph

	@GraphClass.graph.setter
	def graph(self, val):
		raise RuntimeError("The 'graph' attribute cannot be substituted after \
                            creation.")
    
    
    #--------#
    # Delete #
    #--------#
    
    def __del__ (self):
        super(GraphClass, self).__del__()
        self.__class__.__num_networks -= 1
