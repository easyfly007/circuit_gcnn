import pickle
import os
from adjmat import AdjTypeMat

def get_inputs_data():
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as f:
			pickle_data = pickle.load(f)
			features, labels = pickle_data['features'], pickle_data['labels']
			print('get input data from previous saved pickle file')
	else:
		adj_obj = AdjTypeMat()
		features = []
		with open('caselist.txt', 'r') as f:
			for file in f.readlines():
				file = file.strip()
				adj_obj.readin(file)
				adj_mat, node_count = adj_obj.buildAdjTypeMat()
				features.append((adj_mat, node_count))

		labels = []
		with open('labellist.txt', 'r') as f:
			for line in f.readlines():
				line = line.strip()
				if line == '1':
					labels.append(1.0)
				else:
					labels.append(0.0)

		with open('dump.pkl', 'wb') as f:
			pickle.dump({
				'features': features,
				'labels': labels},
				f, pickle.HIGHEST_PROTOCOL)
	return features, labels


if __name__ == '__main__':
	# do quick overview of the samples
	features, labels = get_inputs_data()
	assert len(features) == len(labels), ' feature/label number not match'
	print('total samples: ', len(features))
	
	sample_count_pos = labels.count(1.0)
	sample_count_neg = labels.count(0.0)
	print('positive samples: ', sample_count_pos, 'negative samples: ', sample_count_neg)
	
	node_counts = [feature[1] for feature in features]
	print('the max node count: ', max(node_counts))
	print('the min node count: ', min(node_counts))
