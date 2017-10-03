import os
import tensorflow as tf 
from gcnn import GcnNet
from util import get_inputs_data


# 1. prepare the input data,
features_train, labels_train = get_inputs_data('train')


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
pred = tf.case(
	{tf.greater(prob, 0.5): lambda: tf.constant(1.0)}, 
	default = lambda:tf.constant(0.0))
accu = tf.case(
	{tf.equal(pred, placeholder_label): lambda: tf.constant(1.0)}, 
	default = lambda: tf.constant(0.0))

optimizer = tf.train.AdamOptimizer(learning_rate = placeholder_learning_rate).minimize(cost)


# 3. train
# set super parameters
epoches = 100
learning_rate = 0.001
epoch_print = 10
verbose = True

init = tf.global_variables_initializer()
saver = tf.train.Saver()

with tf.Session() as sess:
	sess.run(init)
	for epoch in range(epoches):
		total_accuracy = 0.0
		for sample_idx, (feature, label) in enumerate(zip(features_train, labels_train)):
			adj_mat, node_count = feature
			feed = {
				placeholder_learning_rate: learning_rate,
				placeholder_adj_mats: adj_mat, 
				placeholder_node_count: node_count,
				placeholder_label: label }
			_, probability, accuracy = sess.run((optimizer, prob, accu), feed_dict = feed)
			total_accuracy += accuracy
			if verbose and epoch % epoch_print == 0:
				print('\n\ttrain sample:', sample_idx, 'label is:', label)
				print('\tthe predicted probability is:', probability)
				print('\tthe accuracy is:', accuracy)
		if epoch % epoch_print == 0:
			total_accuracy /= len(features_train)
			print('\nEpoch', epoch)
			print('total accuracy is:', total_accuracy)
			print('='*60)
	saver.save(sess, 'saved_models/gcn_model.ckpt')
	print('trained model saved at \'saved_models/gcn_model.ckpt\'')


# 4. test
features_test, labels_test = get_inputs_data('test')
with tf.Session() as sess:
	saver.restore(sess, 'saved_models/gcn_model.ckpt')
	print('reload model from \'saved_models/gcn_model.ckpt\'')

	total_accuracy = 0.0
	for sample_idx, (feature, label) in enumerate(zip(features_test, labels_test)):
		adj_mat, node_count = feature

		feed = {
			placeholder_adj_mats: adj_mat, 
			placeholder_node_count: node_count,
			placeholder_label: label }
		probability, accuracy = sess.run((prob, accu), feed_dict = feed)
		total_accuracy += accuracy
		if verbose:
			print('\n\ttest sample:', sample_idx, 'label is:', label)
			print('\tthe predicted probability is:', probability)
			print('\tthe accuracy is:', accuracy)
	total_accuracy /= len(features_test)
	print('total test accuracy is:', total_accuracy)