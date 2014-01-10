#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright Tamas Marton 2013
#
#
#
# rrdtool needs to be installed on the router
# TODO: check opkg list-installed | grep rrdtool

import os
import time
import threading

class measureLoad(threading.Thread):

	def __init__(self, name):
		super(measureLoad, self).__init__()
		self.loadList = []
		self.SLEEPTIME=2
		self.STOP = False
		self.NAME = name
		self.DBFILE = os.path.join("/tmp",self.NAME+".rrd")
		self.IMGFILE = os.path.join("/tmp",self.NAME+".png")

	def run(self):
		print "Load measurement thread started"
		while not (self.STOP):
			self.loadList.append(open('/proc/loadavg', 'r').read().split()[:3])
			time.sleep(self.SLEEPTIME)

	def getLoadList(self):
		return self.loadList


	def export(self):
		try:
			self.createDB()
			self.populateDB()
			self.makePNG()
			
			if os.path.isfile(self.IMGFILE):
				return self.IMGFILE
			else:
				return None

		except IOError, e:
			print "[Measure Load IOError] "+str(e)
		except Exception, e:
			print "[Measure Load Error] "+str(e)


	def createDB(self):
		if (os.path.isfile(self.DBFILE)):
			print "Old database found, deleting it"
			os.remove(self.DBFILE)

		string = ("rrdtool create "+self.DBFILE+
			" --step "+str(self.SLEEPTIME)+
			" --start now "
			"DS:load:GAUGE:"+str(self.SLEEPTIME*2)+":0:U "
			"RRA:AVERAGE:0.5:1:300")

		os.popen(string)
		if not (os.path.isfile(self.DBFILE)):
			raise IOError("Unable to find rrdtool db file")


	def populateDB(self):
		print "Populate Database"
		self.START = os.popen("date +%s").read().rstrip()
		ltime = 1
		for s in self.loadList:
			string = ("rrdtool update "+self.DBFILE+ ' '+str(int(self.START)+ltime)+':'+s[0])
			os.popen(string)
			ltime+=self.SLEEPTIME
		self.END = str(int(self.START)+ltime-2)


	def makePNG(self):
		if (os.path.isfile(self.IMGFILE)):
			print "Old image found, deleting it"
			os.remove(self.IMGFILE)
		print "Generating Plot"

		string =("rrdtool graph "+self.IMGFILE+
			' --imgformat PNG '
			"--slope-mode "  
			'--start '+str(self.START)+" --end "+str(self.END)+" "
			'--title "CPU load" '
			'--vertical-label "processes in the run queue" '
			'--upper-limit=1 '
			'--height 240 '
			'--width 550 '
			'--x-grid SECOND:2:MINUTE:1:SECOND:10:0:%S '
			'DEF:load='+self.DBFILE+':load:AVERAGE '
			'VDEF:load_avg=load,AVERAGE VDEF:load_max=load,MAXIMUM VDEF:load_min=load,MINIMUM '
			'AREA:load#FF000075:"CPU load" '
			'LINE1:load#FF0000 '
			'GPRINT:load_avg:"Avgerage\: %4.2lf" GPRINT:load_min:"Minimum\: %4.2lf" GPRINT:load_max:"Maximum\: %4.2lf" GPRINT:load:LAST:"Last\: %4.2lf"')

		os.popen(string)

		if not (os.path.isfile(self.IMGFILE)):
			raise IOError("Unable to find the image file")
