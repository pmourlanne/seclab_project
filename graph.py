import networkx as nx
import community
import time
from collections import defaultdict

###################################################################################################

#This is an implementation of a weighted graph we use to cluster the accounts			
class Graph(nx.Graph):
	def __init__(self):
		super(Graph, self).__init__()
		#To try to curb the memory usage, we store int in the graph nodes
		self.nameIDDict = dict()
		self.IDNameDict = dict()
		self.id = 0
		self.clusters = defaultdict(list)
		
	def add_edge(self, name1, name2, w = 1):
		if name1 == name2:
			return
		#We first get (or create) the corresponding ids
		if name1 not in self.nameIDDict:
			self.nameIDDict[name1] = self.id
			self.IDNameDict[self.id] = name1
			self.id += 1
		if name2 not in self.nameIDDict:
			self.nameIDDict[name2] = self.id
			self.IDNameDict[self.id] = name2
			self.id += 1
		id1 = self.nameIDDict[name1]
		id2 = self.nameIDDict[name2]
		#We add the edge with weight w
		try:
			self[id1][id2]['w'] += w		
		except KeyError:
			super(Graph, self).add_edge(id1, id2)
			self[id1][id2]['w'] = w
	
	def remove_edge(self, name1, name2):
		id1 = self.nameIDDict[name1]
		id2 = self.nameIDDict[name2]
		super(Graph, self).remove_edge(id1, id2)

	def buildClusters(self):
		#This method builds the clusters using the Louvain method
		#It stores the clustered usernames in a dictionary
		#The keys are int representing the clusters
		#The values are the list of usernames in this cluster
		#IMPORTANT : this method destroys the graph !
		partition = community.best_partition(self)
		for id_name in partition:
			id_cluster = partition[id_name]
			name = self.IDNameDict[id_name]
			self.clusters[id_cluster].append(name)
					
	def getClusters(self):
		#This method returns the clusters
		return self.clusters
		
	def save(self, path = ''):
		print ""
		print "Saving graph"
		#We sotre the IDs and the edgelist in 2 different files
		filename = str(path) + "ids"
		data = open(filename, 'w')
		for name in self.nameIDDict:
			data.write(str(name) + " " + str(self.nameIDDict[name]) + "\n")
		data.close()
		
		filename = str(path) + "edgelist"
		nx.write_edgelist(self, filename, data = 'w')
		
	def load(self, path = ''):
		print ""
		print "Loading graph"
		filename = str(path) + "ids"
		data = open(filename, 'r')
		for line in data:
			line = line.rstrip("\n")
			name, name_id = line.split()
			name_id = int(name_id)
			self.nameIDDict[name] = name_id
			self.IDNameDict[name_id] = name
		data.close()
		
		print "IDs loaded"
		
		start = time.time()
		i = 0
		filename = str(path) + "edgelist"
		data = open(filename, 'r')
		for line in data:
			i += 1
			line = line.rstrip("\n")
			id1, id2, weight = line.split()
			id1 = int(id1)
			id2 = int(id2)
			weight = int(weight)
			name1 = self.IDNameDict[id1]
			name2 = self.IDNameDict[id2]
			self.add_edge(name1, name2, weight)
			
			if i%10000000 == 0:
				elapsed = time.time() - start
				print "%d edges loaded in %d seconds" %(i, elapsed)
		elapsed = time.time() - start
		print "Graph loaded in %d seconds : %d edges" %(elapsed, i)
