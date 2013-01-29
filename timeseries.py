import time
from datetime import datetime
from datetime import timedelta
from datetime import date
try:
	from rpy2.robjects import r
except:
	print "Could not find rpy2"

###################################################################################################

#The timeseries class

class Timeseries(object):
	def __init__(self, start, end, window):
		self.start = start
		self.end = end
		self.window = window

		self.ts = list()
		l = timeDiff(start, end) / self.window + 1
		for i in range(l):
			self.ts.append(0)	
			
	def addTimestamp(self, timestamp):
		i = timeDiff(self.start, int(timestamp)) / self.window
		if i>=0 and i<len(self.ts):
			self.ts[i] += 1
	
	def addTimestampList(self, timestamps):
		for timestamp in timestamps:
			self.addTimestamp(timestamp)
	
	def load(self, filename):
		i = 0
		with open(filename) as data:
			for line in data:
				self.ts[i] = int(line)
				i += 1
				if i > len(self.ts):
					break
					print "Too many values in this file"
	
	def write(self, filename, plot = False):
		#This function saves both a data file and a png plot
		data = open(filename, "w")
		for value in self.ts:
			s = str(value)
			data.write(s)
			data.write("\n")
		data.close()
				
		if plot:
			self.plot(filename)
			
	def plot(self, filename):
		l = len(self.ts)
		r.assign('l', l)
		r.assign('rfilename', filename)
		r.assign('img', filename + '.png')
		
		#Label creation
		r('lbl <- rep(NA, l)')
		lastindex = dict()
		
		for key in range(0, l):
			if self.ts[key] > 0:
				value = self.ts[key]
				if not value in lastindex or (key - lastindex[value]) > 8:
					r.assign('stamp', self.getLabel(key))
					r.assign('i', key+1)	#Indexes start at 1 in R
					r('lbl[i] <- stamp')
					lastindex[value] = key
		
		
		r('temp <- scan(rfilename)')
		r('timeseries <- ts(temp)')
		r('png(img, width = 800, height = 800)')
		r('plot.ts(timeseries, type = "p")')
		r('text(timeseries, labels = lbl, pos = 3)')
		r('dev.off()')
										
	def out(self):
		for value in self.ts:
			print str(value) + ' ',
			
	def getLabel(self, index):
		#This function returns the label associated to ts[index]
		#Labels structure: DAY HOUR (TUE_14 for Tuesday 2PM)
		start = makeDatetime(self.start)
		t = start + timedelta(seconds = index * self.window)
		return label(t)	
		
	
###################################################################################################
		
#And some functions regarding the time format
			
def toSeconds(timestamp):
	timestamp = str(timestamp)
	year = timestamp[0:4]
	month = timestamp[4:6]
	day = timestamp[6:8]
	hour = timestamp[8:10]
	minute = timestamp[10:12]
	second = timestamp[12:14]
	temp = year + " " + month + " " + day + " " + hour + " " + minute + " " + second
	temp = time.strptime(temp, "%Y %m %d %H %M %S")
	return int(time.mktime(temp))
	
def getSeconds(timestamp):
	timestamp = str(timestamp)
	second = int(timestamp[12:14])
	return second

def makeDatetime(timestamp):
	timestamp = str(timestamp)
	year = int(timestamp[0:4])
	month = int(timestamp[4:6])
	day = int(timestamp[6:8])
	hour = int(timestamp[8:10])
	minute = int(timestamp[10:12])
	second = int(timestamp[12:14])
	d = datetime(year, month, day, hour, minute, second)
	return d
		
def timeDiff(start, end):
	return toSeconds(end) - toSeconds(start)

weekDays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
		
def label(datetime):
	wd = datetime.weekday()
	h = str(datetime.hour)
	return weekDays[wd] + '_' + h
				
###################################################################################################

#A class allowing to look at the IP usage in a time period

class IPUsageGraph(object):
	def __init__(self, start):
		self.start = start
		#We store the values as tuples (time in hours, IP number)
		self.values = list()
		#We store IPs in a list
		self.IPs = list()
		
	def addValue(self, timestamp, IP):
		x = float(timeDiff(self.start, timestamp))
		x = x/3600.
		
		if not IP in self.IPs:
			self.IPs.append(IP)
		y = self.IPs.index(IP)
		
		value = x,y
		self.values.append(value)
		
	def write(self, filename):
		with open(filename + '_x', 'w') as f:
			for value in self.values:
				x,y = value
				f.write(str(x) + '\n')
		with open(filename + '_y', 'w') as f:
			for value in self.values:
				x,y = value
				f.write(str(y) + '\n')
				
	def load(self, filename):
		self.values[:] = []
		values_x = list()
		values_y = list()
		with open(filename + '_x', 'r') as f:
			for line in f:
				values_x.append(float(line))
		with open(filename + '_y', 'r') as f:
			for line in f:
				values_y.append(int(line))
		for i in range(0, len(values_x)):
			v = values_x[i], values_y[i]
			self.values.append(v)
			
	def plot(self, filename):
		r.assign('file_x', filename + '_x')
		r.assign('file_y', filename + '_y')
		r.assign('img', filename + '.png')
		
		r('x <- scan(file_x)')
		r('y <- scan(file_y)')
		r('png(img, width = 800, height = 800)')
		r('plot(x,y, ann = FALSE, yaxt = "n")')
		r('title(xlab = "Hours")')
		r('title(ylab = "IPs")')
		r('axis(2, at = 0:max(y), labels = 0:max(y))')
		r('dev.off()')
		
###################################################################################################

#A class similar to IPUsageGraph, except it's for accounts

class AccountUsageGraph(IPUsageGraph):
	#We just modify the plot function to change the labels
	def plot(self, filename):	
		r.assign('file_x', filename + '_x')
		r.assign('file_y', filename + '_y')
		r.assign('img', filename + '.png')
		
		r('x <- scan(file_x)')
		r('y <- scan(file_y)')
		r('png(img, width = 800, height = 800)')
		r('plot(x,y, ann = FALSE, yaxt = "n")')
		r('title(xlab = "Hours")')
		r('title(ylab = "Accounts")')
		r('axis(2, at = 0:max(y), labels = 0:max(y))')
		r('dev.off()')		
