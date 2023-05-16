import random

class Graph: 
	# Create a graph with 
	def __init__(self):
		self.nodes = set()
		self.edges = {}

	def add_edge(self, n1, n2, w):
		if not n1 in self.nodes:
			self.nodes.add(n1)
		if not n2 in self.nodes:
			self.nodes.add(n2)
		if n1 in self.edges.keys():
			if n2 in self.edges[n1].keys():
				self.edges[n1][n2] += w
			else:
				self.edges[n1][n2] = w
		else:
			self.edges[n1] = {n2 : w}


	def print_graph(self):
		print(self.edges)

def count_out_edges(graph, node):
	count = 0
	if not node in graph.edges:
		return 0
	for n2 in graph.edges[node].keys():
		count += graph.edges[node][n2]
	return count

def select_random_neighbor(graph, node):
	out_edges = count_out_edges(graph, node)
	if out_edges == 0:
		return None
	else:
		rand = int(random.random()*out_edges)
		for n2 in graph.edges[node].keys():
			rand -= graph.edges[node][n2]
			if rand < 0:
				return n2

def page_rank_random_walk(graph, n = 10000):
	node_count = {}
	for node in graph.nodes:
		node_count[node] = 0

	current_node = random.choice(tuple(graph.nodes))

	i = 0
	while i < n:
		next_node = select_random_neighbor(graph, current_node)
		if next_node == None:
			current_node = random.choice(tuple(graph.nodes))
			continue
		else:
			node_count[next_node] += 1
			current_node = next_node
		i += 1
	return node_count

def normalize_weights_for_pairs(graph, w = 1):
	for n1 in graph.edges.keys():
		for n2 in graph.edges[n1].keys():
			total = graph.edges[n1][n2]
			if n2 in graph.edges.keys():
				if n1 in graph.edges[n2].keys():
					total += graph.edges[n2][n1]
					graph.edges[n2][n1] = graph.edges[n2][n1]*(w/total)
			graph.edges[n1][n2] = graph.edges[n1][n2]*(w/total)

"""
class Edge:

	def __init__(self, n1, n2, w):
		self.start_node = n1
		self.end_node = n2
		self.weight = w

	def add_weight(self, w_change):
		w += w_change
"""