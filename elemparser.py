
connection_idx2name = {}
connection_name2idx = {}

def buildConnectionMapping():
	if len(connection_idx2name) > 0:
		return
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
	for name, idx in connection_name2idx:
		connection_idx2name[idx] = name


class Base(object):
	pass

class TwoNodesElem(Base):
	def updateMat(self, mat, total_nodes, elem_nodes):
		assert len(nodes) == 2, self.elemtype + ' must have 2 nodes!'
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
		assert len(nodes) == 4, 'mosfet must have 4 nodes!'
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
	def __init__(self, connection_type_idx):
		self.elemtype = 'resistor'
		self.connection_idx = connection_type_idx['r_r']


class CapParser(TwoNodesElem):
	def __init__(self, connection_type_idx):
		self.elemtype = 'capacitor'
		self.connection_idx = connection_type_idx['c_c']


class VsrcParser(TwoNodesElem):
	def __init__(self, connection_type_idx):
		self.elemtype = 'voltage source '
		self.connection_idx = connection_type_idx['v_v']


class IsrcParser(TwoNodesElem):
	def __init__(self, connection_type_idx):
		self.elemtype = 'current source '
		self.connection_idx = connection_type_idx['i_i']


def getnodeparser(elemname, connection_type_idx):
	elemtype = elemname.split('.')[-1][0].lower()
	if elemtype == 'm':
		return MosParser(connection_type_idx)
	elif elemtype == 'r':
		return ResParser(connection_type_idx)
	elif elemtype == 'c':
		return CapParser(connection_type_idx)
	elif elemtype == 'v':
		return VsrcParser(connection_type_idx)
	elif elemtype == 'i':
		return IsrcParser(connection_type_idx)
	else:
		assert 0, 'element ' + elemname + ' currently not supported!'