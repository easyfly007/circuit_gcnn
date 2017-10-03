import os
import tensorflow as tf 
from gcnn import GcnNet
from util import get_inputs_data


# 1. prepare the input data,
features, labels = get_inputs_data()


# 2. build the network
# placeholder for one netlist input
placeholder_adj_mats = tf.placeholder(tf.float32, [12, None])
placeholder_node_count = tf.placeholder(tf.int32)
placeholder_label = tf.placeholder(tf.float32)
placeholder_learning_rate = tf.placeholder(tf.float32)

network = GcnNet()
logits = network.buildNet(placeholder_node_count, placeholder_adj_mats)
prob = tf.sigmoid(logits)

cost = -placeholder_label * tf.log(prob) - (1.0- placeholder_label)*tf.log(1.0 - prob)
# cost = tf.nn.softmax_cross_entropy_with_logits( logits = logits, labels = placeholder_label)
pred = tf.case(
	{tf.greater(prob, 0.5): lambda: tf.constant(1.0)}, 
	default = lambda:tf.constant(0.0))
accu = tf.case(
	{tf.equal(pred, placeholder_label): lambda: tf.constant(1.0)}, 
	default = lambda: tf.constant(0.0))


optimizer = tf.train.AdamOptimizer(learning_rate = placeholder_learning_rate).minimize(cost)
# optimizer = tf.train.AdamOptimizer().minimize(cost)


# 3. train
# set super parameters
epoches = 20
learning_rate = 0.001
epoch_print = 5
verbose = True

init = tf.global_variables_initializer()
with tf.Session() as sess:
	sess.run(init)
	for epoch in range(epoches):
		total_accuracy = 0.0
		for sample_idx, (feature, label) in enumerate(zip(features, labels)):
			adj_mat, node_count = feature
			feed = {
				placeholder_learning_rate: learning_rate,
				placeholder_adj_mats: adj_mat, 
				placeholder_node_count: node_count,
				placeholder_label: label }
			_, probability, accuracy = sess.run((optimizer, prob, accu), feed_dict = feed)
			total_accuracy += accuracy
			if verbose and epoch % epoch_print == 0:
				print('\n\tsample:', sample_idx, 'label is:', label)
				print('\tthe predicted probability is:', probability)
				print('\tthe accuracy is:', accuracy)
		if epoch % epoch_print == 0:
			total_accuracy /= len(features)
			print('\nEpoch', epoch)
			print('total accuracy is:', total_accuracy)
			print('='*60)


# 4. test