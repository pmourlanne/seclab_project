import time
from timeseries import Timeseries
from collections import defaultdict
from math import sqrt
from math import log
import json

###################################################################################################

def meanstdv(l):
	#Return the mean and the std of a list:
	n, mean, std = len(l), 0., 0.
	for x in l:
		mean += x
	mean /= float(n)

	for x in l:
		std += (x - mean)**2
	std = sqrt(std / float(n-1))
	
	return mean, std

###################################################################################################

class Connexion(object):
	def __init__(self, timestamp, IP, user_agent):
		self.timestamp = timestamp
		self.IP = IP
		self.user_agent = user_agent
		
###################################################################################################
		
class Profile(object):
	def __init__(self):
		self.connexions = list()
		
	def display(self):
		for c in self.connexions:
			print "%s\t%s\t%s" %(c.timestamp, c.IP, c.user_agent),
			
	def addConnexion(self, con):
		self.connexions.append(con)
		
###################################################################################################

class ProfileList(object):
	def __init__(self, directory, client_name):
		self.profiles = defaultdict(Profile)
		self.directory = directory
		self.client_name = client_name #value used to read the output
		self.ratings = dict()
		
	def createFromOutput(self, output, save = False):
		#This function loads the output, creates the profiles and save them in directory
		i = 0
		start = time.time()
	
		with open(output, 'r') as f:
			for line in f:
				l = json.loads(line)
				i += 1
				try:
					IP = l["enduser_ip"]
					timestamp = l["timestamp"].rstrip('Z')
					username = l["user_id"]
					client_id = l["client_name"]
					header = l["http_headers"]
					user_agent = header["HTTP_USER_AGENT"]
				
					if client_id == self.client_name:
						con = Connexion(timestamp, IP, user_agent)
						self.profiles[username].addConnexion(con)
				except:
					pass
				
				if (i%1000000) == 0:
					print "%d lines treated in %d seconds" %(i, time.time() - start)
					
		if save:
			self.save()
			
	def save(self):
		path = str(self.directory) + 'profiles'
		with open(path, 'w') as f:
			for username in self.profiles:
				f.write('new_user ' + str(username) + '\n')
				for con in self.profiles[username]:
					s = str(timestamp) + '\t' + str(IP) + '\t' + str(user_agent)
					f.write(s + '\n')
	
		print "Profiles created and saved in %d seconds" %(time.time() - start)
		
	def load(self):
		#This function loads the profiles saved in directory
		i = 0
		start = time.time()
	
		path = str(self.directory) + 'profiles'
		username = ''
		with open(path, 'r') as f:
			for line in f:
				i += 1
				if 'new_user' in line :
					username = line.split()[1]
				else:
					words = line.split()
					timestamp = words[0].rstrip('Z')
					IP = words[1]
					temp = line.lstrip(words[0]).lstrip() # 2 lstrip to get rid of the space
					user_agent = temp.lstrip(words[1]).lstrip()
					con = Connexion(timestamp, IP, user_agent)
				
					self.profiles[username].addConnexion(con)
		
				if (i%1000000) == 0:
					print "%d lines treated in %d seconds" %(i, time.time() - start)			
	
		print "Profiles loaded in %d seconds" %(time.time() - start)	
		
	def testCorrelation(self):
		#This function computes the correlation for all users appearing at least twice in profiles
		#and then stores it in ratings: ratings[username] = log(c)
	
		mobiles = set(['Mobile', 'Android', 'BlackBerry', 'Fennec', 'GoBrowser', \
						'Minimo', 'NetFront', 'Presto', 'iPad', 'iPhone'])
					
		res = list()
		i = 0
		start = time.time()
	
		for username in self.profiles:
			i += 1
			if len(self.profiles[username].connexions) > 1:
				IPs = set()
				UAs = set()
				k = 0
				for con in self.profiles[username].connexions:
					IP = con.IP
					user_agent = con.user_agent
					mobile = False
					for s in mobiles:
						if s in user_agent:
							mobile = True
							#We discard mobile user agents
							break
				
					if not mobile:
						IPs.add(IP)
						UAs.add(user_agent)
						k += 1
			
				if k > 1:
					j = float(len(UAs))
					n = float(len(IPs))
					res.append(log(j/n))
					self.ratings[username] = log(j/n)
			
			if (i%1000000) == 0:
				print "%d accounts treated in %d seconds" %(i, time.time() - start)			
			
		mean, std = meanstdv(res)
		res.sort()
		median = res[len(res)/2]
	
		return median, mean, std, self.ratings
		
	def saveRatings(self):
		path = self.directory + 'ratings'
		with open(path, 'w') as f:
			for username in self.ratings:
				f.write(username + '\t' + str(self.ratings[username]) + '\n')
				
	def loadRatings(self):
		path = self.directory + 'ratings'
		with open(path, 'r') as f:
			for line in f:
				words = line.split()
				self.ratings[words[0]] = float(words[1])
				
	def createTimeseries(self, usernames, ts_start, ts_end, ts_window):
		#This function goes through the profiles
		#and returns the timeseries of a list of user
		tseries = Timeseries(ts_start, ts_end, ts_window)
		for username in usernames:
			if username in self.profiles:
				for c in self.profiles[username]:
					tseries.addTimestamp(c.timestamp)
		return tseries	
