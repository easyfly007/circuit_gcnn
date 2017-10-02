import tensorflow as tf 
import numpy as np 

class GcnNet(object):
	def __init__(self):
		self.layers = []

	def addLayer(self, layer):
		self.layers.append(layer)
		return self.layers[-1]

	def buildNet(self, node_count, adj_mat):
		layer = GcnLayer(
			node_count = node_count, 
			adj_mat = adj_mat,
			input_feature_count = 1,
			output_feature_count = 2,
			input_mat = None,
			is_input = True)


		layer1 = self.addLayer(layer)

		# need to add activation layer here

		layer = GcnLayer(
			node_count = node_count,
			adj_mat = adj_mat,
			input_feature_count = 2,
			output_feature_count = 1,
			input_mat = layer1,
			is_input = False)
		layer2 = self.addLayer(layer)

		self.logits = tf.reduce_mean(layer2)
		return self.logits

'''
graph convolutional operation:
suppose we have:
graph_node_size = 6
input_feature_size = 5
output_feature_size = 3
connection_type_size = 4

the input tensor will be a [6,5] matrix
the output tensor will be a [6, 3] matrix
the weight Variable we need to learn: [4*5, 3]
as for each output ndoe, the value will be each adjacent type node value * weight, and combine all the layer, type together

then how to transfer the input [6,5] matrix to a suitable [6, 20]?
we need the adj matrix by type

as we have 4 types, we will build 4 [6, 6] adj matrix
for each adj matrix [6, 6]
do adj_mat * input_tensor,
[6,6] * [6,5], then we get a [6,5], we have by layer by central node accumulated matrix, for one connection type

we then concatenate these 4 [6, 5] matrix horizontally together,
we have a [6, 5*4] matrix, this is the the input we need for multiply with the weights matrix
using these [6, 20] *[20, 3], we get the output matrix [6, 3] 
'''
class GcnLayer(object):
	def __init__(
		self,
		node_count, 
		adj_mat,
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
		self.adj_mat = tf.reshape(adj_mat, (node_count, node_count,connect_type_count))
		print(adj_mat, self.adj_mat.shape)
		self.connect_type_mat = tf.Variable(
			tf.truncated_normal([connect_type_count, 1]))

		output_by_central = []
		for central_node in range(self.adj_mat.shape[0]):
			output = tf.matmul(self.Weights, self.input_mat)
			output = tf.matmul(output, self.adj_mat[central_node])
			output = tf.matmul(output, self.connect_type_mat)
			output = tf.reshape(output, shape = (-1,))
			output_by_central.append(output)
		self.output_mat = tf.stack(output_by_central, axis = 1)
		# output_mat shape: [output_feature_count, node_count]
		# input_mat shape: [input_feature_count, node_count] 