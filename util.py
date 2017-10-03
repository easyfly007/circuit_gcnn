import pickle
import os
from adjmat import AdjTypeMat

def get_inputs_data(datatype):
	assert datatype in ['train', 'test'], 'you must specify the data type, train or test'

	if os.path.isfile(datatype + '_data.pkl'):
		with open(datatype + '_data.pkl', 'rb') as f:
			pickle_data = pickle.load(f)
			features, labels = pickle_data['features'], pickle_data['labels']
			print('get data from previous saved pickle file')
	else:
		adj_obj = AdjTypeMat()
		features = []
		with open(datatype + '_caselist.txt', 'r') as f:
			for file in f.readlines():
				file = file.strip()
				adj_obj.readin(file)
				adj_mat, node_count = adj_obj.buildAdjTypeMat()
				features.append((adj_mat, node_count))

		labels = []
		with open(datatype + '_labellist.txt', 'r') as f:
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
	return features, labels


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

