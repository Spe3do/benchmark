# -*- coding: utf-8 -*-
# Author: Tamas Marton

import os
import time
import measureLoad

DEBUG = 1

class taskUsb:

	def __init__(self):
		self.ID = 5
		self.NAME='USB Speed Test'
		self.DESCRIPTION='Testing the reading and writing speed of the connected USB device'
		self.MOUNTFOLDER=None
		self.DEFAULT_TIMER=time.time
		self.TESTFILE='usb_testfile_10M'
		self.WRITESPEED = None
		self.READSPEED = None
		self.ENABLED = True

		self.checkRequirements()


	def checkRequirements(self):
		if os.popen("opkg list-installed | grep rrdtool") == '':
			self.ENABLED = False


	def executeTask(self, controller):
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")
		try:
			controller.sendToClient(str(self.ID))

			self.MOUNTFOLDER = controller.WORKFOLDER
			if self.MOUNTFOLDER == None:
				raise Exception("No folder to use for the test")

			#Start load measurement
			self.LOAD = measureLoad.measureLoad("usb")
			self.LOAD.start()

			self.WRITESPEED = self.write()
			if self.WRITESPEED == None:
				controller.sendToClient("error")
			else:
				print "Writespeed: "+self.WRITESPEED
				controller.sendToClient(self.WRITESPEED)

			time.sleep(10)

			self.READSPEED = self.read()
			if self.READSPEED == None:
				controller.sendToClient("error")
			else:
				print "Readspeed: "+self.READSPEED
				controller.sendToClient(self.READSPEED)

			time.sleep(1)

			controller.communication.sendFinished()

			if controller.communication.waitForAck() == False:
				print "[Error] No 'ACK' response from Server"

			#Stop load measurement
			self.LOAD.STOP=True
			self.LOAD.join() 

        	#Trying to create png
			image_file=self.LOAD.export()
			if image_file != None:
				print "Sending picture"
				controller.sendImageToClient(image_file)
			else:
				controller.sendToClient("image_error")

		except Exception, e:
			print "[USB Speedtest Error] "+str(e)
			controller.sendToClient("error")
			try:
				self.LOAD.STOP=True
				self.LOAD.join()
			except:
				pass
		finally:
			self.cleanUp()


	def read(self):
		t0 = self.DEFAULT_TIMER()
		os.popen("cat "+self.MOUNTFOLDER+'/'+self.TESTFILE+" > /dev/null")

		t1 = self.DEFAULT_TIMER()
		t = t1-t0

		if DEBUG:
			print "Time to read the file: "+str(t)+"sec"

		return str('%.2f' % (self.FILESIZE/1024/1024/t))+ " MB/s"


	def write(self):
		t0 = self.DEFAULT_TIMER()

		string="dd if=/dev/zero of="+self.MOUNTFOLDER+'/'+self.TESTFILE+" bs=1M count=100"
		if DEBUG:
			print "DD string: " + string
		os.popen(string)

		self.FILESIZE=os.path.getsize(self.MOUNTFOLDER+'/'+self.TESTFILE)

		t1 = self.DEFAULT_TIMER()
		t = t1-t0

		if DEBUG:
			print "Time to write the file: "+str(t)+"sec"

		return str('%.2f' % (self.FILESIZE/1024/1024/t))+ " MB/s"


	def cleanUp(self):
		if os.path.exists(self.MOUNTFOLDER+'/'+self.TESTFILE):
			os.popen("rm "+self.MOUNTFOLDER+'/'+self.TESTFILE)


	def getID(self):
	    return self.ID

