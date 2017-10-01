import tensorflow as tf 
import numpy as np 

def GcnNet(object):
	def __init__(self):
		self.layers = []

	def addLayer(layer):
		self.layers.append(layer)

	def buildNet():
		pass


def GcnLayer(object):
	def __init__(
		self,
		node_count, 
		input_feature_count, 
		output_feature_count, 
		input_mat = None,
		connect_type_count = 11,
		is_input = True,):
		''' 
		output = Weights * input_mat * adj_mat * connect_type_mat
		weights:			[output_feature_count, input_feature_count]
		input_mat: 			[input_feature_count, node_count]
		adj_mat: 			node_count *[ node_count, connection_type_count]
		connect_type_mat: 	[connect_type_count, 1]
		output: 			[output_feature_count, 1]

		do a for loop for the node_count in adj_mat, and then output will be
		[output_feature_count, node_count]
		'''
		if is_input:
			self.weights = tf.Variable(tf.truncated_normal([output_feature_count, 1]))
		else:
			self.weights = tf.Variable(tf.truncated_normal(
				[output_feature_count, input_feature_count]))
		self.input_mat = input_mat
		self.adj_mat = adj_mat # no changed for one instance
		self.connect_type_mat = connect_type_count

		output_by_central = []
		for central_node in range(adj_mat.shape[0]):
			output = tf.matmul(self.Weights, self.input_mat)
			output = tf.matmul(output, self.adj_mat[central_node])
			output = tf.matmul(output, self.connect_type_mat)
			output = tf.reshape(output, shape = (-1,))
			output_by_central.append(output)
		self.output_mat = tf.stack(output_by_central, axis = 1)
		# output_mat shape: [output_feature_count, node_count]
		# input_mat shape: [input_feature_count, node_count] 