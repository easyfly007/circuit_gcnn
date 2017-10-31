import tensorflow as tf 
import numpy as np 

TOTAL_CONNECTION_TYPE = 9

class GcnNet(object):
	def __init__(self):
		self.layers = []

	def addLayer(self, layer):
		self.layers.append(layer)
		return self.layers[-1]

	def buildNet(self, node_count, adj_mats, keep_prob):
		input_mat = tf.ones((node_count, 1))

		layer = GcnLayer(
			node_count = node_count, 
			adj_mats = adj_mats,
			input_feature_count = 1,
			output_feature_count = 2,
			input_mat = input_mat,
			is_input = True,
			activation = 'tanh')

		layer1 = self.addLayer(layer)
		dropout1 = tf.nn.dropout(layer1.output, keep_prob)

		layer = GcnLayer(
			node_count = node_count,
			adj_mats = adj_mats,
			input_feature_count = 2,
			output_feature_count = 1,
			input_mat = dropout1,
			is_input = False)
		layer2 = self.addLayer(layer)

		layer = AttenLayer(
			node_count = node_count, 
			adj_mats = adj_mats, 
			input_feature_count = 1,
			input_mat = layer2.output)
		layer3 = self.addLayer(layer)

		layer4 = layer2.output * layer3.output
		
		logits = tf.squeeze(layer4, axis = 1)
		self.logits = tf.reduce_sum(logits)
		return self.logits

'''
graph convolutional operation:
suppose we have:
graph_node_size = 6
input_feature_count = 5
output_feature_count = 3
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
		adj_mats,
		input_feature_count, 
		output_feature_count = 1, 
		input_mat = None,
		connect_type_count = 9,
		is_input = True,
		activation = 'None'):
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
			[input_feature_count *connect_type_count, output_feature_count]))
		self.input_mat = input_mat
		
		self.adj_mats = []
		for i in range(connect_type_count):
			adj_mat = tf.reshape(adj_mats[i], (node_count, node_count))
			a = tf.matmul(adj_mat, self.input_mat)
			self.adj_mats.append(a)
		self.prepare_mat = tf.concat(self.adj_mats, axis = 1)

		self.output = tf.matmul(self.prepare_mat, self.weights)
		if activation.lower() == 'relu':
			self.output = tf.nn.relu(self.output)
		elif activation.lower() == 'tanh':
			self.output = tf.tanh(self.output)
		elif activation.lower() == 'sigmoid':
			self.output = tf.sigmoid(self.output)
		elif activation.lower() == 'softmax':
			self.output = tf.nn.softmax(self.output, dim = 0)
		else:
			pass


# attention layer is the special condition for GcnLayer
# while the output_feature_count must be 1, and activation function should be softmax 
class AttenLayer(GcnLayer):
	def __init__(
		self,
		node_count, 
		adj_mats,
		input_feature_count, 
		input_mat,
		connect_type_count = TOTAL_CONNECTION_TYPE,
		is_input = True,
		):
		super(AttenLayer, self).__init__(
			node_count = node_count,
			adj_mats = adj_mats,
			input_feature_count = input_feature_count,
			output_feature_count = 1,
			input_mat = input_mat,
			connect_type_count = connect_type_count,
			activation = 'softmax')
