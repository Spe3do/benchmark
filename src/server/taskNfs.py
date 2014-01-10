#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright Tamas Marton 2013
#
#
#
#

import os
import shutil
import measureLoad
import time

DEBUG = 1

class taskNfs:

	def __init__(self):
		self.ID = 4
		self.NAME='NFS Test'
		self.DESCRIPTION='Testing the reading and writing speed'
		self.FOLDER ="TEMPNFS"
		self.MOUNTFOLDER = "/mnt"
		self.MDIR=os.path.join(self.MOUNTFOLDER,self.FOLDER)

		self.ENABLED = True

		self.checkRequirements()

		self.ORIGINALSTATUSPORTMAP = None
		self.ORIGINALSTATUSNFSD = None


	def checkRequirements(self):
		if os.popen("opkg list-installed | grep nfs-kernel-server") == '':
			self.ENABLED = False
		if os.popen("opkg list-installed | grep rrdtool") == '':
			self.ENABLED = False


	def preparation(self):
		if self.MOUNTFOLDER == None:
			raise Exception("No folder to use for the test")

		if os.popen("ps | grep [p]ortmap").read() == '':
			self.ORIGINALSTATUSPORTMAP = False
		else:
			self.ORIGINALSTATUSPORTMAP = True

		if os.popen("ps | grep [r]pc.mountd").read() == '':
			self.ORIGINALSTATUSNFSD = False
		else:
			self.ORIGINALSTATUSNFSD = True

		if self.ORIGINALSTATUSPORTMAP:
			print "Stopping Portmap"
			os.popen("/etc/init.d/portmap stop")
		if self.ORIGINALSTATUSNFSD:
			print "Stopping NFSD"
			os.popen("/etc/init.d/nfsd stop")

		print "Backup original configuration"
		os.rename("/etc/exports","/etc/exports.back")

		my_config=self.MOUNTFOLDER+"	*(rw,all_squash,insecure,async,no_subtree_check)"
		print "Write our config for the test"

		cfile = open("/etc/exports", 'w')
		cfile.write(my_config)
		cfile.close


	def executeTask(self, controller):
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")
		controller.communication.setTimeout(60.0)
		
		try:
			self.MOUNTFOLDER = controller.WORKFOLDER

			controller.sendToClient(str(self.ID)+';' +controller.SERVERIP+';'+str(self.MOUNTFOLDER)+';'+self.FOLDER)
			time.sleep(1)
			self.preparation()

			os.mkdir(self.MDIR)
			os.popen("chmod 777 "+self.MDIR)

			#Start load measurement
			self.LOAD = measureLoad.measureLoad("nfs")
			self.LOAD.start()

			if DEBUG:
				print "Starting NFS"

			os.popen("/etc/init.d/portmap start")
			os.popen("/etc/init.d/nfsd start")
			controller.communication.sendReady()

			msg = controller.receiveFromClient()			
			self.WRITESPEED = msg
			print "WriteSpeed: " + self.WRITESPEED

			msg = controller.receiveFromClient()	
			self.READSPEED = msg
			print "ReadSpeed: " + self.READSPEED

			if controller.communication.waitForFinished() == False:
				raise Exception("No 'Finished' response from Client")
			else:

				#Stop load measurement
				self.LOAD.STOP=True
				self.LOAD.join() 

	        	#Trying to create png
				image_file=self.LOAD.export()
				if image_file != None:
					print "Sending picture"
					controller.sendImageToClient(image_file)
				else:
					controller.communication.sendIMGError()

				controller.communication.sendAck()

		except IOError, e:
			print "[NFS IO Error] "+str(e)
			controller.communication.sendError()
			try:
				self.LOAD.STOP=True
				self.LOAD.join() 
			except:
				pass

		except Exception,e:
			print "[NFS Error]: "+str(e)
			controller.communication.sendError()
			try:
				self.LOAD.STOP=True
				self.LOAD.join()
			except:
				pass

		finally:
			self.cleanUp()


	def getID(self):
	    return self.ID


	"""
	Stopping nfs server, and remove the temporaray folder, finalley restore the 
	original configuration and service status
	"""
	def cleanUp(self):
		if DEBUG:
			print "Stopping NFS"

		os.popen("/etc/init.d/portmap stop")
		os.popen("/etc/init.d/nfsd stop")
		
		if os.path.exists(self.MDIR):
			shutil.rmtree(self.MDIR)

		if os.path.exists("/etc/exports.back"):
			if os.path.exists("/etc/exports"):
				print "Restoring original configuration"
				os.remove("/etc/exports")
			os.rename("/etc/exports.back","/etc/exports")

		if self.ORIGINALSTATUSPORTMAP:
			print "Restoring original service status"
			os.popen("/etc/init.d/portmap start")
		if self.ORIGINALSTATUSNFSD:
			os.popen("/etc/init.d/nfsd start")

