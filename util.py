import pickle
import os
from adjmat import AdjTypeMat

def get_inputs_data():
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as f:
			pickle_data = pickle.load(f)
			features, labels = pickle_data['features'], pickle_data['labels']
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
				if line == '1':
					labels.append(1.0)
				else:
					labels.append(0.0)

		with open('dump.pkl', 'wb') as f:
			pickle.dump({
				'features': features,
				'labels': labels},
				f, pickle.HIGHEST_PROTOCOL)
	print(type(labels[0]))
	return features, labels

if __name__ == '__main__':
	features, labels = get_inputs_data()
