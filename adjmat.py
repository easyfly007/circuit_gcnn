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
		self.elem_node = dict()
		nodes_set = set()
		with open(filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				elem, *nodes = line.strip().split('')
				self.elem_node[elem[:-1]] = nodes # element name end with :
				nodes_set |= set(nodes_set)
		self.nodes_list = sorted(list(nodes_set)) 
		# make sure the order will not changed run under different python version, as hash map not gaurantee



	def buildAdjTypeMat(self, filename):
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


		self.mat = np.zeros((len(self.nodes_list),  len(self.nodes_list)))
		for elem, nodes in self.elem_nodes.items():
			elem_node_parser = getnodesparser(elem)
			elem_node_parser->updateMat(self.mat, self.nodes_list, elem, nodes)

	def buildAdjNodesMat(self):
		# build [node_count, [node_count, nodetype_one_hot]]
		nodesMat = np.zeros((len(self.nodes_list), len(self.nodes_list), self.connectionTypeCount))
		for i in range(self.connectionTypeCount):
			nodesMat[i][:, self.mat[i]] = 1