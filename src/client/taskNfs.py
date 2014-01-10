# -*- coding: utf-8 -*-
# Author: Tamas Marton

import os
import platform
import time
import tempfile

DEBUG = 1

class taskNfs:

	def __init__(self):
		'''
		Initialize the main variables
		'''
		self.ID = 4
		self.NAME='NFS Test'
		self.DESCRIPTION="""Testing the reading and writing speed of the NFS share running on the router. 
[b][color=#36acd8]Steps:[/color][/b] 
[b]1)[/b] Test the writing speed by copying a 100MB file to the share
[b]2)[/b] Test the reading speed by copying the same file back to this machine"""
		self.OS = platform.system()
		self.WRITESPEED='0'
		self.READSPEED='0'
		self.TESTFILE="testfile_100M"
		self.ENABLED = True
		self.RESULT = None

		self.IMGFILE = os.path.join(tempfile.gettempdir(),'nfs.png')

		if self.OS != "Windows":
			self.LOCALFOLDER = os.path.join(tempfile.gettempdir(),"NFS")
			self.TESTPATH="./Testfiles/"+self.TESTFILE
			self.DEFAULT_TIMER=time.time
			self.FILESIZE=os.path.getsize(self.TESTPATH)

		self.checkRequirements()


	def checkRequirements(self):
		'''
		NFS test is only enabled if client's OS is not Windows, and if client has root privilege
		'''
		if self.OS == "Windows":
			self.ENABLED = False

		elif not 'SUDO_UID' in os.environ.keys():
			self.ENABLED = False

	
	def parse(self, message):
		"""
		Parsing the message came from the Server, for the task specific variables
		"""
		self.IPTOCONNECT=message[0]
		self.SHARENAME=message[1]
		self.SHAREFOLDER=message[2]
		if DEBUG:
			print "IPTOCONNECT: "+self.IPTOCONNECT
			print "SHARENAME: "+self.SHARENAME
			print "SHAREFOLDER: "+self.SHAREFOLDER


	def execute(self, controller, message):
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")
		self.parse(message)
		text_result = ""
		try:
			if os.path.isfile(self.IMGFILE):
				os.remove(self.IMGFILE)

			if controller.communication.waitForReady():
				os.popen("mkdir "+self.LOCALFOLDER)
				string = "sudo mount -o rw -t nfs "+self.IPTOCONNECT+':'+self.SHARENAME+" "+self.LOCALFOLDER
				if DEBUG:
					print "Mount: " + string
					controller.gui.sendToLog("Mount: "+string)
				time.sleep(5)
				os.popen(string)

				print "Testing write speed..."
				controller.gui.sendToLog("Testing the writing speed...")
				self.WRITESPEED=self.write()
				controller.sendMessageToServer(self.WRITESPEED)
				print "The write speed is: "+str(self.WRITESPEED)
				controller.gui.sendToLog("The write speed is: "+str(self.WRITESPEED))

				print "Testing read speed..."
				controller.gui.sendToLog("Testing the reading speed...")
				self.READSPEED=self.read()
				controller.sendMessageToServer(self.READSPEED)
				print "The read speed is: "+str(self.READSPEED)
				controller.gui.sendToLog("The read speed is: "+str(self.READSPEED))

				time.sleep(1)
				controller.communication.sendFinished()

				#Receiving plot from Server
				msg = controller.receiveImageFromServer()
				if msg == "error":
					self.IMGFILE = None
					raise Exception("Router Error")
				elif msg == "image_error":
					self.IMGFILE = None
					raise Exception("No Image Received")
				else:
					print "Write image"
					image_data = msg
					image = open(self.IMGFILE,'wb')
					image.write(image_data)
					image.close()

				if controller.communication.waitForAck() == False:
					raise Exception("No 'ACK' response from Server")

				controller.gui.sendToLog("Unmounting, and cleanup")

				text_result = " Average writing speed: "+self.WRITESPEED +'''
'''+" Average reading speed: "+self.READSPEED

		except EnvironmentError,e:
			if str(e)=="windows":
				controller.sendMessageToServer("windows")
				print "[NFS Environment Error] Windows is not supported"

			if str(e)=="nopriviledge":
				controller.sendMessageToServer("nopriviledge")
				print "[NFS Environment Error] You have to be root to mount a NFS share"

		except RuntimeError,e:
			print "[NFS Error] "+str(e)
 			controller.gui.sendToLog("[NFS Error] "+str(e))
 			text_result = "An error occurred during the task: "+str(e)

		except Exception ,e:
			print "[NFS Error] "+str(e)
			controller.gui.sendToLog("[NFS Error] "+str(e))
			text_result = "An error occurred during the task: "+str(e)

		finally:
			self.cleanUp()
			stat = self.getMultimediaStatistics()
			if stat != '':
				text_result += '''

::

 '''+stat
			self.RESULT = {'name': self.NAME, 'result': text_result, 'image': self.IMGFILE}


	def read(self):
		"""
		In Linux, we have to flush the filecache, otherwise the copy will be done instantly
		In Mac OSX there is no such filecache problem

		Copy the TESTFILE from the share to /dev/null and measuring the time it takes to get the speed
		"""
		if self.OS == "Linux":
			os.popen("sync ; sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'")

		dst = "/dev/null"	
		scr = os.path.join(self.LOCALFOLDER,self.SHAREFOLDER,self.TESTFILE)

		t0 = self.DEFAULT_TIMER()
		#shutil.copy2(scr,dst)
		os.popen("cp "+scr+" "+dst)

		t1 = self.DEFAULT_TIMER()
		t = t1-t0

		if DEBUG:
			print "Time to read the file: "+str(t)+"sec"

		return str('%.2f' % (self.FILESIZE/1024/1024/t))+ " MB/s"


	def write(self):
		"""
		Copy the TESTFILE from the client to the mounted folder, and measuring the time it takes to get the speed
		"""
		dst = os.path.join(self.LOCALFOLDER,self.SHAREFOLDER)

		t0 = self.DEFAULT_TIMER()
		os.popen("cp "+self.TESTPATH+" "+dst)
		t1 = self.DEFAULT_TIMER()

		t = t1-t0

		if DEBUG:
			print "Time to write the file: "+str(t)+"sec"
			print "FILESIZE: "+str(self.FILESIZE/1024.0/1024.0) +" MB"

		return str('%.2f' % (self.FILESIZE/1024/1024/t))+ " MB/s"


	def getMultimediaStatistics(self):
		'''
		Return statistics based on the result of the measurement in execute()
		'''
		text = ''
		if (self.READSPEED == '0') or (self.WRITESPEED == '0'):
			return text
		else:
			bitrate_dvd = 6000 /8/1024.0
			bitrate_hd720 = 10000/8/1024.0
			bitrate_hd1080 = 15000/8/1024.0
			bitrate_bd = 40000/8/1024.0

			rspeed = float(self.READSPEED[:-5])
			wspeed = float(self.WRITESPEED[:-5])

			text += ('''Based on the measured writing speed to copy a file to the router will take:
 1GB: '''+str('%.2f' % (1000/wspeed/60.0))+''' minutes
 5GB: '''+str('%.2f' % (5000/wspeed/60.0))+''' minutes 
 10GB: '''+str('%.2f' % (10000/wspeed/60.0))+''' minutes 

 Based on the measured reading speed in theory you can play up to 
 '''+str(int(rspeed/bitrate_dvd))+''' DVD quality (bitrate: 6Mbit/s) or
 '''+str(int(rspeed/bitrate_hd720))+''' HD-rip 720p (bitrate: 10Mbit/s ) or 
 '''+str(int(rspeed/bitrate_hd1080))+''' HD-rip 1080p (bitrate: 15Mbit/s ) or 
 '''+str(int(rspeed/bitrate_bd))+" Blueray (bitrate: 40Mbit/s) movies")

		return text


	def cleanUp(self):
		"""
		If mounted unmount, then if exists remove the temporary directery used for mounting the share
		"""
		try:
			if self.OS != "Windows":
				if DEBUG:
					print "Unmounting..."
				if os.path.ismount(self.LOCALFOLDER):
					os.popen("umount " + self.LOCALFOLDER)

				if os.path.exists(self.LOCALFOLDER):
					os.rmdir(self.LOCALFOLDER)


		except Exception, e:
			print "[NFS Cleanup Error] "+str(e)


	def getID(self):
		return self.ID


