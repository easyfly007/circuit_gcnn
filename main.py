import os
import tensorflow as tf 
import random

from gcnn import GcnNet
from util import get_inputs_data
from util import shuffle_data

TOTAL_CONNECTION_TYPE = 9

# 1. prepare the input data,
features_train, labels_train = get_inputs_data('train', 
	shuffle = True, reload = False,
	listfile_prefix = '../circuit_classification_dataset/parsered_cases/', 
	casefile_prefix = '../circuit_classification_dataset/parsered_cases/')

idx = int(len(features_train) *0.8)
features_test, labels_test  = features_train[idx:], labels_train[idx:]
features_train, labels_train  = features_train[:idx], labels_train[:idx]

# features_train, labels_train = features_train[:5], labels_train[:5]


# 2. build the network
# placeholder for one netlist input
placeholder_adj_mats = tf.placeholder(tf.float32, [TOTAL_CONNECTION_TYPE, None], name = 'adj_mat')
placeholder_node_count = tf.placeholder(tf.int32, name = 'node_count')
placeholder_label = tf.placeholder(tf.float32, name = 'label')
placeholder_learning_rate = tf.placeholder(tf.float32, name = 'learning_rate')
placeholder_keep_prob = tf.placeholder(tf.float32, name = 'keep_prob')

network = GcnNet()
logits = network.buildNet(placeholder_node_count, placeholder_adj_mats, placeholder_keep_prob)
prob = tf.sigmoid(logits)

cost = -placeholder_label * tf.log(prob + 1.0e-10) - (1.0- placeholder_label)*tf.log(1.0 - prob + 1.0e-10)
pred = tf.case(
	{tf.greater(prob, 0.5): lambda: tf.constant(1.0)}, 
	default = lambda:tf.constant(0.0))
accu = tf.case(
	{tf.equal(pred, placeholder_label): lambda: tf.constant(1.0)}, 
	default = lambda: tf.constant(0.0))

optimizer = tf.train.AdamOptimizer(learning_rate = placeholder_learning_rate).minimize(cost)


# 3. train
# set super parameters
epoches = 500
learning_rate = 0.001
epoch_print = 20
verbose = False

init = tf.global_variables_initializer()
saver = tf.train.Saver()

print('training begin...')
with tf.Session() as sess:
	sess.run(init)
	for epoch in range(1, epoches+1):
		total_accuracy = 0.0
		features_train, labels_train = shuffle_data(features_train, labels_train)
		for sample_idx, (feature, label) in enumerate(zip(features_train, labels_train)):
			adj_mat, node_count = feature
			feed = {
				placeholder_learning_rate: learning_rate,
				placeholder_adj_mats: adj_mat, 
				placeholder_node_count: node_count,
				placeholder_label: label,
				placeholder_keep_prob: 0.75 }
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
print('testing begin')
# features_test, labels_test = get_inputs_data('test')
with tf.Session() as sess:
	saver.restore(sess, 'saved_models/gcn_model.ckpt')
	print('reload model from \'saved_models/gcn_model.ckpt\'')

	total_accuracy = 0.0
	for sample_idx, (feature, label) in enumerate(zip(features_test, labels_test)):
		adj_mat, node_count = feature

		feed = {
			placeholder_adj_mats: adj_mat, 
			placeholder_node_count: node_count,
			placeholder_label: label,
			placeholder_keep_prob: 1.0}
		probability, accuracy = sess.run((prob, accu), feed_dict = feed)
		total_accuracy += accuracy
		if verbose:
			print('\n\ttest sample:', sample_idx, 'label is:', label)
			print('\tthe predicted probability is:', probability)
			print('\tthe accuracy is:', accuracy)
	total_accuracy /= len(features_test)
	print('total test accuracy is:', total_accuracy)


#5 inference, which means no label provided
print('inference begin...')
label_file = 'infer_labellist.txt'
features_infer, _ = get_inputs_data('infer')

with open(label_file, 'w') as f:
	with tf.Session() as sess:
		saver.restore(sess, 'saved_models/gcn_model.ckpt')
		print('reload model from \'saved_models/gcn_model.ckpt\'')

		total_accuracy = 0.0
		for sample_idx, feature in enumerate(features_infer):
			adj_mat, node_count = feature

			feed = {
				placeholder_adj_mats: adj_mat, 
				placeholder_node_count: node_count}
			predicted = sess.run((pred), feed_dict = feed)
			if verbose:
				print('\n\tinference sample:', sample_idx, 'predicted:', predicted)
			f.write(str(predicted) + '\n')