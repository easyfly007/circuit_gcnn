import numpy as np 
from elemparser import getnodesparser

class AdjTypeMat(object):
	def __init__(self):
		self.connectionTypeCount = 12 # including self to self

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
		nodes_count = len(self.nodes_list)
		self.mat = np.zeros(
			(self.connectionTypeCount, nodes_count, nodes_count), np.float)
		
		''' suppose we have 4 different connection types, 6 nodes, 5 different input features, 3 output feature 
		adj mat will be [6, 6*4]

        1. build adjacent matrix[6, 6] for each connection type 4:
		 _ _ _ _ _ _   _ _ _ _ _ _   _ _ _ _ _ _   _ _ _ _ _ _
		|           | |           | |           | |           |
		|  AdjMat 1 | |  AdjMat 2 | |  AdjMat 3 | |  AdjMat 4 |
		|           | |           | |           | |           |
		|           | |           | |           | |           |
		|           | |           | |           | |           |
		|_ _ _ _ _ _| |_ _ _ _ _ _| |_ _ _ _ _ _| |_ _ _ _ _ _| 

		2. multipy each adj matrix ([6, 6]) with input matrix ([6, 5])
		 _ _ _ _ _   _ _ _ _ _   _ _ _ _ _   _ _ _ _ _ 
		|         | |         | |         | |         |
		|         | |         | |         | |         |
		|         | |         | |         | |         |
		|         | |         | |         | |         |
		|         | |         | |         | |         |
		|_ _ _ _ _| |_ _ _ _ _| |_ _ _ _ _| |_ _ _ _ _|
       
		3. concate the result [6,5] matrix, we get [6, 20]
		4. using the [6, 20] to multiply weights matrix [20, 3]
		we got the final output [6, 3]
		 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _       _ _ _     _ _ _ 
		|         |         |         |         |     |     |   |     |
		|         | AdjMat 2| AdjMat 3| AdjMat 4|     |     |   |     |
		|         | type 2  | type 3  | type 4  | *   |     | = |     |
		|         | [6, 6]  | [6, 6]  | [6, 6]  |     |     |   |     |
		|         |         |         |         |     |     |   |     |
		|_ _ _ _ _|_ _ _ _ _|_ _ _ _ _|_ _ _ _ _|     |     |   |_ _ _|
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |     |
                                                      |_ _ _|
		 
		'''
		for elem, nodes in self.elem_nodes.items():
			elem_node_parser = getnodesparser(elem)
			elem_node_parser.updateMat(self.mat, self.nodes_list, nodes)
		
		# return self.mat, nodes_count
		return np.reshape(self.mat, (self.connectionTypeCount, nodes_count * nodes_count)), nodes_count

