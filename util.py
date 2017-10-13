import pickle
import os
import random

from adjmat import AdjTypeMat

def get_inputs_data(datatype, shuffle = False, reload = True, listfile_prefix = '', casefile_prefix = ''):
	'''
	input variables
		shuffle = True, do shuffle , shuffle = False, not do shuffle
		reload = True: check pkl file, get from features/labels from pkl file
		       = False: always rebuild from the netlist
		listfile_prefix:
				the prefix of file train_caselist.txt
		casefile_prefix:
				the prefix of case name in file train_caselist.txt
	'''
	assert datatype in ['train', 'test', 'infer'], 'you must specify the data type, train or test'

	if datatype in ['train', 'test'] and reload == True and os.path.isfile(datatype + '_data.pkl'):
		with open(datatype + '_data.pkl', 'rb') as f:
			pickle_data = pickle.load(f)
			features, labels = pickle_data['features'], pickle_data['labels']
			print('get data from previous saved pickle file')
	else:
		adj_obj = AdjTypeMat()
		features = []
		with open(listfile_prefix + datatype + '_caselist.txt', 'r') as f:
			for file in f.readlines():
				file = file.strip()
				file = casefile_prefix + file
				adj_obj.readin(file)
				adj_mat, node_count = adj_obj.buildAdjTypeMat()
				features.append((adj_mat, node_count))

		if datatype in ['train', 'test']:
			labels = []
			with open(listfile_prefix + datatype + '_labellist.txt', 'r') as f:
				for line in f.readlines():
					line = line.strip()
					if line == '1':
						labels.append(1.0)
					else:
						labels.append(0.0)

			with open(datatype + '_data.pkl', 'wb') as f:
				pickle.dump({
					'features': features,
					'labels': labels},
					f, pickle.HIGHEST_PROTOCOL)
		elif datatype == 'infer':
			labels = None

	if shuffle and datatype in ['train', 'test']:
		features, labels = shuffle_data(features, labels)

	return features, labels


def shuffle_data(data1, data2):
	assert len(data1) == len(data2), 'feature/label not match'
	combined = list(zip(data1, data2))
	random.shuffle(combined)
	return zip(*combined)


if __name__ == '__main__':
	# do quick overview of the samples
	print('train dataset')
	features, labels = get_inputs_data('train')
	assert len(features) == len(labels), ' feature/label number not match'
	print('total samples: ', len(features))
	
	sample_count_pos = labels.count(1.0)
	sample_count_neg = labels.count(0.0)
	print('positive samples: ', sample_count_pos, 'negative samples: ', sample_count_neg)
	
	node_counts = [feature[1] for feature in features]
	print('the max node count: ', max(node_counts))
	print('the min node count: ', min(node_counts))


	# do quick overview of the samples
	print('\ntest dataset')
	features, labels = get_inputs_data('test')
	assert len(features) == len(labels), ' feature/label number not match'
	print('total samples: ', len(features))
	
	sample_count_pos = labels.count(1.0)
	sample_count_neg = labels.count(0.0)
	print('positive samples: ', sample_count_pos, 'negative samples: ', sample_count_neg)
	
	node_counts = [feature[1] for feature in features]
	print('the max node count: ', max(node_counts))
	print('the min node count: ', min(node_counts))

