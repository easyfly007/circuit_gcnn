import tensorflow as tf 
import numpy as np 

class GcnNet(object):
	def __init__(self):
		self.layers = []

	def addLayer(self, layer):
		self.layers.append(layer)
		return self.layers[-1]

	def buildNet(self, node_count):
		layer1 = self.addLayer(
			node_count, 
			input_feature_count = 1,
			output_feature_count = 2,
			input_mat = None,
			is_input = True)

		layer2 = self.addLayer(
			node_count,
			input_feature_count = 2,
			output_feature_count = 1,
			input_mat = layer1,
			is_input = False)
		self.logits = tf.reduce_mean(layer2)
		return self.logits

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
			assert input_feature_count == 1, 'input should have feature count 1'
		self.weights = tf.Variable(tf.truncated_normal(
			[output_feature_count, input_feature_count]))
		self.input_mat = input_mat
		self.adj_mat = adj_mat # no changed for one instance
		self.connect_type_mat = tf.Variable(
			tf.truncated_normal([connect_type_count, 1]))

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