def buildConnectionMapping():
	connection_idx2name = {}
	connection_name2idx = {
	'self': 0,
	'sd_g': 1,
	'g_sd': 2,
	'sd_sd': 3,
	'r_r': 4,
	'c_c': 5,
	'l_l': 6,
	'v_v':7,
	'i_i':8}
	for name, idx in connection_name2idx.items():
		connection_idx2name[idx] = name
	return connection_name2idx, connection_idx2name

connection_name2idx, connection_idx2name = buildConnectionMapping()

class Base(object):
	pass

class TwoNodesElem(Base):
	def updateMat(self, mat, total_nodes, elem_nodes):
		assert len(elem_nodes) == 2, self.elemtype + ' must have 2 nodes!'
		n1, n2 = elem_nodes
		if n1 == n2:
			return
		n1_idx = total_nodes.index(n1)
		n2_idx = total_nodes.index(n2)
		# mat is a 3 dimention matrix
		# [central_node_idx] [connection_type] [adjacent_node_idx] 
		mat[self.connection_idx][n1_idx][n2_idx] = 1
		mat[self.connection_idx][n2_idx][n1_idx] = 1
		

class MosParser(Base):
	def updateMat(self, mat, total_nodes, elem_nodes):
		assert len(elem_nodes) == 4, 'mosfet must have 4 nodes!'
		d, g, s, _ = elem_nodes # nb not cnosidered
		d_idx = total_nodes.index(d)
		g_idx = total_nodes.index(g)
		s_idx = total_nodes.index(s)
		mat[connection_name2idx['sd_g']][d_idx][g_idx] = 1
		mat[connection_name2idx['sd_sd']][d_idx][s_idx] = 1
		mat[connection_name2idx['g_sd']][g_idx][d_idx] = 1
		mat[connection_name2idx['g_sd']][g_idx][s_idx] = 1
		mat[connection_name2idx['sd_sd']][s_idx][d_idx] = 1
		mat[connection_name2idx['sd_g']][s_idx][g_idx] = 1


class ResParser(TwoNodesElem):
	def __init__(self):
		self.elemtype = 'resistor'
		self.connection_idx = connection_name2idx['r_r']


class CapParser(TwoNodesElem):
	def __init__(self):
		self.elemtype = 'capacitor'
		self.connection_idx = connection_name2idx['c_c']


class VsrcParser(TwoNodesElem):
	def __init__(self):
		self.elemtype = 'voltage source '
		self.connection_idx = connection_name2idx['v_v']


class IsrcParser(TwoNodesElem):
	def __init__(self):
		self.elemtype = 'current source '
		self.connection_idx = connection_name2idx['i_i']


def getnodesparser(elemname):
	elemtype = elemname.split('.')[-1][0].lower()
	if elemtype == 'm':
		return MosParser()
	elif elemtype == 'r':
		return ResParser()
	elif elemtype == 'c':
		return CapParser(connection_name2idx)
	elif elemtype == 'v':
		return VsrcParser()
	elif elemtype == 'i':
		return IsrcParser()
	else:
		assert 0, 'element ' + elemname + ' currently not supported!'