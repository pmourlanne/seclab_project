from timeseries import IPUsageGraph
from timeseries import AccountUsageGraph
from profile import ProfileList

###################################################################################################

client_name = '64d7c69f0679a9ed3df7597352afda1018d63558c87fecc8fcc26e09'
ts_window = 3600
ts_start = 20120501050000
ts_end = 20120508050000
	
###################################################################################################
	
def loadClusters(data):
	clusters = list()
	i = 0
	clusters.append(set())
	with open(data) as f:
		for line in f:
			line = line.rstrip('\n')
			if len(line) == 0:
				clusters.append(set())
				i += 1
			else:
				clusters[i].add(line)	
	
	return clusters
	
def createIPUTable(pl, clusters, directory):
	#This function creates the IPUsage tables for each cluster in clusters
	#and save them in the directory
	#pl is the ProfileList containing the loaded data
	IPU = list()
	for cluster in clusters:
		IPU.append(IPUsageGraph(ts_start))
	
	for username in pl.profiles:
		j = 0
		for cluster in clusters:
			if username in cluster:
				for con in pl.profiles[username].connexions:
					IPU[j].addValue(con.timestamp, con.IP)
				break
			j += 1
			
	j = 0
	for graph in IPU:
		graph.write(directory + str(j))
		j += 1
		
def createACUTable(pl, clusters, directory):
	#Same thing than before, but with Account Usage Table
	ACU = list()
	for cluster in clusters:
		ACU.append(AccountUsageGraph(ts_start))
	
	for username in pl.profiles:
		j = 0
		for cluster in clusters:
			if username in cluster:
				for con in pl.profiles[username].connexions:
					ACU[j].addValue(con.timestamp, username)
				break
			j += 1
			
	j = 0
	for graph in ACU:
		graph.write(directory + str(j))
		j += 1
		
			
###################################################################################################

output = '/home/pmourlanne/graph/to_gianluca.json'
directory = '/home/pmourlanne/graph/save/profiles/'
names = '/home/pmourlanne/graph/save/names'
ts_directory = '/home/pmourlanne/graph/save/profiles/ts/'
IPU_directory = directory + 'IPusage/'
ACU_directory = directory + 'AccountUsage/'
corr_directory = '/home/pmourlanne/graph/save/corr/'

###################################################################################################

clusters = loadClusters(names)
pl = ProfileList(directory, client_name)
pl.load()
median, mean, std, ratings = pl.testCorrelation()

print "Median: %f" %median
print "Mean: %f" %mean
print "Std: %f" %std

print "Script finished"
