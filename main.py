import os
import tensorflow as tf 
from gcnn import GcnNet
from util import get_inputs_data

# 1. prepare the input data,
features, labels = get_inputs_data()

# 2. build the network
# placeholder for one netlist input
placeholder_adj_map = tf.placeholder(tf.float32, [None, ])
placeholder_node_count = tf.placeholder(tf.int32)
placeholder_label = tf.placeholder(tf.int32)
placeholder_learning_rate = tf.placeholder(tf.float32)

network = GcnNet()
logits = network.buildNet(placeholder_node_count, placeholder_adj_map)
cost = tf.reduce_mean(
	tf.nn.softmax_cross_entropy_with_logits(
		logits = logits, labels = placeholder_label))
optimizer = tf.train.AdamOptimizer(learning_rate = placeholder_learning_rate).minimize(cost)


# 3. train
# set super parameters
epoches = 20
learning_rate = 0.001

init = tf.global_variables_initializer()
with tf.Session() as sess:
	tf.run(init)
	for epoch in range(epoches):
		for feature, label in zip(features, labels):
			feed = {placeholder_learning_rate: learning_rate, placeholder_adj_map: feature}
			sess.run(optimizer, feed_dict = feed)


# 4. test