import os
import tensorflow as tf 
from gcnn import GcnNet
from util import get_inputs_data

# 1. prepare the input data,
features, labels = get_inputs_data()

# 2. build the network
net = GcnNet()
logit = net.logits


# 3. train
epoches = 20
init = tf.global_variables_initializer()
with tf.Session() as sess:
	tf.run(init)
	for epoch in range(epoches):
		for feature, label in zip(features, labels):
			pass

# 4. test