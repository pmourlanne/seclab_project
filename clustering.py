import time
from cluster import ClusterTool
from collections import defaultdict

###################################################################################################

#Test values
#filename = "test.txt"
#out_path = "/home/pmourlanne/stuff/nx_community/test/"
#threshold_IP = 3

#Actual values
filename = "/home/pmourlanne/graph/output_parsed"
out_path = "/home/pmourlanne/graph/save/"
threshold_IP = 50
client_name = '64d7c69f0679a9ed3df7597352afda1018d63558c87fecc8fcc26e09'

###################################################################################################

def loadAccounts(filename):
	accounts = defaultdict(set)
	i = 0
	j = 0
	start = time.time()
	print ""		
	print "Creating the list of accounts"
	
	with open(filename) as data:	
		for line in data:
			words = line.split()
			username = words[-1]
			IP = words[0]
			client = words[2]

			if client == client_name:
				accounts[username].add(IP)
		
			i += 1

	print "List of accounts created in %d seconds" %(time.time() - start)
	print ""
	return accounts

def findSeeds(accounts, threshold):
	seeds = set()

	for username in accounts:
		if len(accounts[username]) >= threshold:
			for IP in accounts[username]:
				seeds.add(IP)
	return seeds

def clusterFromFile(path):
	ct = ClusterTool()
	ct.loadGraph(path)
	ct.g.buildClusters()
	ct.saveClusters(path)

###################################################################################################

start = time.time()

#thresholds = (20, 50, 100, 250)
thresholds = list()
#thresholds.append(100)
for threshold in thresholds:
	accounts = loadAccounts(filename)
	seeds = findSeeds(accounts, threshold)
	ct = ClusterTool(seeds)
	ct.addAccountList(accounts)
	
	ct.buildGraph(False, 20)
	path = out_path + str(threshold) + "IPS/"
	ct.saveGraph(path)
	
	del ct
	print ""
	print "Graph for threshold %d built and saved in %d seconds" %(threshold, time.time() - start)
	print ""
		
path = out_path + "100IPS/"
clusterFromFile(path)	
	
print "Script finished in %d seconds" %(time.time() - start)
