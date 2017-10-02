def buildConnectionMapping():
	connection_idx2name = {}
	connection_name2idx = {
	'self': 0,
	'md_mg': 1,
	'md_ms': 2,
	'mg_md': 3,
	'mg_ms': 4,
	'ms_md': 5,
	'ms_mg': 6,
	'r_r': 7,
	'c_c': 8,
	'l_l': 9,
	'v_v':10,
	'i_i':11}
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
		mat[n1_idx][self.connection_idx][n2_idx] = 1
		mat[n2_idx][self.connection_idx][n1_idx] = 1
		

class MosParser(Base):
	def updateMat(self, mat, total_nodes, elem_nodes):
		assert len(elem_nodes) == 4, 'mosfet must have 4 nodes!'
		d, g, s, _ = elem_nodes # nb not cnosidered
		d_idx = total_nodes.index(d)
		g_idx = total_nodes.index(g)
		s_idx = total_nodes.index(s)
		mat[d_idx][connection_name2idx['md_mg']][g_idx] = 1
		mat[d_idx][connection_name2idx['md_ms']][s_idx] = 1
		mat[g_idx][connection_name2idx['mg_md']][d_idx] = 1
		mat[g_idx][connection_name2idx['mg_ms']][s_idx] = 1
		mat[s_idx][connection_name2idx['ms_md']][d_idx] = 1
		mat[s_idx][connection_name2idx['ms_mg']][g_idx] = 1


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