import time
import graph
from collections import defaultdict

###################################################################################################

class ClusterTool(object):
	def __init__(self, seeds = None):
		#seeds should be a set of IPs
		if seeds == None:
			self.seeds = set()
		else:
			self.seeds = seeds
		self.old_seeds = set()
		self.IPlist = defaultdict(set)
		self.conData = defaultdict(list)
		self.g = graph.Graph()
		
	def addAccountList(self, accounts):
		#accounts should be a dict
		#where keys are username
		#and contains a list of (IP, timestamp) tuples
		for name in accounts:
			for tup in accounts[name]:
				IP, timestamp = tup
				self.IPlist[name].add(IP)
				self.conData[name].append(tup)
				
	def buildGraph(self, output = False, nb_iter = 1):
		#This function only loads the graph in memory
		#It is used for test purposes
		self.cluster(output, nb_iter, False)

	def cluster(self, output = False, nb_iter = 1, clustering = True):
		#This is the method that actually clusters the accounts
		#ouput is a boolean that allows the numerous prints
		#nb_iter is the number of "propagations" we want to do
		
		#If this was the last iteration then we actually do the clustering
		if nb_iter < 1:
			if clustering:
				if output:
					print ""
					print "Building the clusters"
				self.g.buildClusters()
			return
		
		if len(self.seeds) <= 0:
			print ""
			if output:
				print "No seeds left, ending the iterations"
			self.cluster(output, -1, clustering)
			return
		
		if output:
			print "Updating the graph : %d new seeds" %len(self.seeds)
		
		start = time.time()
		
		#We start by creating the IPUserDict 
		#which maps accounts to the seeds
		IPUserDict = dict()
		for IP in self.seeds:
			IPUserDict[IP] = list()
		
		self.old_seeds = self.old_seeds.union(self.seeds)
		
		if output:	
			print ""
			print "Creating the association table"
		start1 = time.time()
		i = 0
			
		for name in self.IPlist:
			i += 1
			add_IPs = True
			for IP in self.IPlist[name]:
				try:
					IPUserDict[IP].append(name)
					if add_IPs:
						for IP in self.IPlist[name]:
							self.seeds.add(IP)
						add_IPs = False
				except KeyError:
					pass
			
		if output:
			now = time.time()
			elapsed = now - start1
			print "%d accounts treated in %d seconds" %(i, elapsed)
					
		if output:
			#We calculate the estimate number of edges' creations
			n = 0
			for IP in IPUserDict:
				k = len(IPUserDict[IP])
				n += k*(k-1)
			print ""		
			print "Number of entries in the association table : %d" %len(IPUserDict)
			print "Number of associations : %d" %n
			print ""
		
		#We add edges based on the association table
		start1 = time.time()
		n = 0
		for IP in IPUserDict:
			n += 1
			l = len(IPUserDict[IP])
			for i in range(0, l):
				for j in range(i, l):
					namei = IPUserDict[IP][i]
					namej = IPUserDict[IP][j]
					self.g.add_edge(namei, namej)
					
			if output:
				if n%1000 == 0:
					now = time.time()
					elapsed = now - start1
					nb_nodes = self.g.number_of_nodes()
					nb_edges = self.g.number_of_edges()
					print "%d entries treated in %d seconds : %d nodes and %d edges"\
						%(n, elapsed, nb_nodes, nb_edges)
					

		#We choose the new seeds as follow :
		#We take all the IPs from the accounts in the clusters
		#and we remove the IPs that have already been used as seeds
		self.seeds = self.seeds.difference(self.old_seeds)
		
		now = time.time()
		elapsed = now - start
		print ""
		print "Iteration completed in %d seconds" %(elapsed)
		
		#Finally we call this function to propagate
		#the contamination using the new seeds
		self.cluster(output, nb_iter-1, clustering)
		
	def out(self, details = False):
		clusters = self.g.getClusters()
		
		print "List of clusters :"
		for key in clusters:
			print "Cluster %d contains %d accounts" %(int(key),len(clusters[key])),
			if details:
				print ":"
				for name in clusters[key]:
					print name,
			print ""
		print "%d clusters found" %len(clusters)
		print ""
		
	def outShort(self):
		clusters = self.g.getClusters()
		n = 0
		for key in clusters:
			n += len(clusters[key])
		print "%d accounts clustered in %d clusters" %(n, len(clusters))
		print ""
		
	def getClusters(self):
		return self.g.getClusters()
	
	def saveGraph(self, path):
		self.g.save(path)
		
	def loadGraph(self, path):
		self.g.load(path)
		
	def saveClusters(self, path):
		filename = str(path) + "clusters"
		data = open(filename, 'w')
		
		clusters = self.g.getClusters()
		for key in clusters:
			for name in clusters[key]:
				data.write(str(name) + "\n")
			data.write("end of cluster\n")
		data.close()
	
	def loadClusters(self, path):
		filename = str(path) + "clusters"
		data = open(filename, 'r')
		clusters = defaultdict(list)
		i = 0
		
		for line in data:
			line = line.rstrip("\n")
			if line == "end of cluster":
				i += 1
			else:
				clusters[i].append(line)
				
		self.g.clusters = clusters
		data.close()
			
#save should be rewritten or deleted				
	def save(self, filename):
		#We should store the graph
		#It makes no sense to store the seeds and old seeds without the graph
		data = open(filename, 'w')
		clusters = self.g.getClusters()
		
		data.write("seeds\n")
		for IP in self.seeds:
			data.write(IP)
			data.write("\n")
		data.write("old seeds\n")
		for IP in self.old_seeds:
			data.write(IP)
			data.write("\n")
		data.write("clusters\n")
		for key in clusters:
			for name in clusters[key]:
				data.write(name)
				data.write("\n")
			data.write("end of cluster\n")
				
		data.close()
	
	
#As is the load function has no purpose
#It should be updated
#use rstrip("\n") !!!
	def load(self, filename):
		data = open(filename)
		i = 0
		start = time.time()
		mode = ""
		usernames = list()
		
		for line in data:
			line = line[:len(line)-1]
			i += 1
			
			if line == "clustered_accounts" or line == "seeds" \
					or line == "old_seeds" or line == "clusters":
				mode = line
			elif line == "end of cluster":
				for username in usernames:
					self.makeSet(username)
					self.union(usernames[0], username)
				del usernames[:]
			elif mode == "clustered_accounts":
				self.g.clustered_accounts.add(line)
			elif mode == "seeds":
				self.seeds.add(line)
			elif mode == "old_seeds":
				self.old_seeds.add(line)
			elif mode == "clusters":
				usernames.append(line)
				
		now = time.time()
		elapsed = now - start
		print "%d lines treated in %d seconds" %(i, elapsed)
	
		data.close()
		
###################################################################################################
		
class Account(object):
	def __init__(self, name):
		#The username
		self.name = name
		#The list containing the timestamps of the connexion		
		self.timestamps = list()
		#A set of the different IPs that connected to the account
		self.IPs = set()

	def addIP(self, IP):
		self.IPs.add(IP)
	def addTimestamp(self, timestamp):
		self.timestamps.append(timestamp)
	def getNbIPs(self):
		return len(self.IPs)
				###################################################################################################
