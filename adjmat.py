import numpy as np 
from elemparser import getnodesparser

class AdjTypeMat(object):
	def __init__(self):
		self.connectionTypeCount = 11

	def readin(self, filename):
		''' read in netlist file, with format:
		elem1: n1 n2 n3 n4
		elem2: n1 n5

		'''
		self.elem_nodes = dict()
		nodes_set = set()
		with open(filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				elem, *nodes = line.strip().split()
				self.elem_nodes[elem[:-1]] = nodes # element name end with :
				nodes_set |= set(nodes)
		self.nodes_list = sorted(list(nodes_set)) 
		# make sure the order will not changed run under different python version, as hash map not gaurantee

	def buildAdjTypeMat(self):
		''' 
		suppose we have 
		nodecount: 6, connection type count: 4

		output:matrix with size (6, 4) *6
		[central_node_idx] [connection_type] [adjacent_node_idx] ]
		    ____________    
		   /   /   /   /|     /_/_/_/_/
		  /   /   /   / |    /_/_/_/_/ 6
		 /   /   /   /  |   /_/_/_/_/
		1   0   0   0   |   |_|_|_|_|  
		0   0   1   0   |   |_|_|_|_|
		0   0   0   0  /    |_|_|_|_| 6
		0   0   0   1 /     |_|_|_|_|
		0   1   0   0/      |_|_|_|_|
		0   0   0   0       |_|_|_|_|
		                       4
		'''
		'''
		build adjacent matrix for each connection types
		build 4 adj mat, which are all [6, 6] size
		'''
		# nodes_count = len(self.nodes_list)
		# self.mat = np.zeros((nodes_count, self.connectionTypeCount, nodes_count))
		# for elem, nodes in self.elem_nodes.items():
		# 	elem_node_parser = getnodesparser(elem)
		# 	elem_node_parser.updateMat(self.mat, self.nodes_list, nodes)
		# return self.mat, nodes_count
		nodes_count = len(self.nodes_list)
		self.mat = np.zeros(
			(self.connectionTypeCount, nodes_count, nodes_count), 
			np.float)
		for elem, nodes in self.elem_nodes.items():
			elem_node_parser = getnodesparser(elem)
			elem_node_parser.updateMat(self.mat, self.nodes_list, nodes)
		return self.mat, nodes_count

