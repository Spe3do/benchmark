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

class taskSamba:

	def __init__(self):
		self.ID = 3
		self.NAME='Samba Test'
		self.DESCRIPTION='Testing the reading and writing speed'
		self.FOLDER ="TEMPSAMBA"
		self.MOUNTFOLDER="/mnt"
		self.MDIR=os.path.join(self.MOUNTFOLDER,self.FOLDER)

		self.ENABLED = True

		self.checkRequirements()

		self.ORIGINALSTATUS = None


	def checkRequirements(self):
		if os.popen("opkg list-installed | grep samba36-server") == '':
			self.ENABLED = False
			
		if os.popen("opkg list-installed | grep rrdtool") == '':
			self.ENABLED = False

	def preparation(self):
		if self.MOUNTFOLDER == None:
			raise Exception("No folder to use for the test")

		if os.popen("ps | grep [n]mbd").read() == '':
			self.ORIGINALSTATUS = False
		else:
			print "Samba server is running."
			self.ORIGINALSTATUS = True

		if self.ORIGINALSTATUS:
			print "Stopping SAMBA"
			os.popen("/etc/init.d/samba stop")

		print "Backup original configuration"

		if os.path.exists("/etc/samba/smb.conf.template"):
			os.rename("/etc/samba/smb.conf.template","/etc/samba/back_smb.conf.template")
			os.popen("cp data/smb.conf.template /etc/samba/")
			
		os.rename("/etc/config/samba","/etc/config/samba.back")

		my_config='''
config samba
	option 'name'			'OpenWrt'
	option 'workgroup'		'WORKGROUP'
	option 'description'	'OpenWrt'
	option 'homes'			'1'

config 'sambashare'
	option 'name' 'Shares'
    option 'path' '''+"'"+self.MOUNTFOLDER+"'"'''
    option 'guest_ok' 'yes'
    option 'create_mask' '0777'
   	option 'dir_mask' '0777'
   	option 'read_only' 'no'
'''
		

		print "Write our config for the test"

		cfile = open("/etc/config/samba", 'w')
		cfile.write(my_config)
		cfile.close

		

	def executeTask(self, controller):
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")

		try:
			self.MOUNTFOLDER = controller.WORKFOLDER

			controller.sendToClient(str(self.ID)+';' +controller.SERVERIP+';'+"Shares"+';'+self.FOLDER)
			time.sleep(1)
			self.preparation()

			os.mkdir(self.MDIR)
			os.popen("chmod 777 "+self.MDIR)

			#Start load measurement
			self.LOAD = measureLoad.measureLoad("samba")
			self.LOAD.start()

			if DEBUG:
				print "Starting SAMBA"

			os.popen("/etc/init.d/samba start")
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
			controller.communication.sendError()
			print "[Samba IO Error] "+str(e)
			try:
				self.LOAD.STOP=True
				self.LOAD.join() 
			except:
				pass

		except Exception, e:
			controller.communication.sendError()
			print "[Samba Error] "+str(e)
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
	Stopping samba server, and remove the temporaray folder, finally restore the original
	configuration, and service status
	"""
	def cleanUp(self):
		if DEBUG:
			print "Stopping SAMBA"

		os.popen("/etc/init.d/samba stop")

		if os.path.exists(self.MDIR):
			shutil.rmtree(self.MDIR)

		if os.path.exists("/etc/config/samba.back"):
			if os.path.exists("/etc/config/samba"):
				print "Restoring original configuration"
				os.remove("/etc/config/samba")
			os.rename("/etc/config/samba.back","/etc/config/samba")

		if os.path.exists("/etc/samba/back_smb.conf.template"):
			if os.path.exists("/etc/samba/smb.conf.template"):
				os.remove("/etc/samba/smb.conf.template")
			os.rename("/etc/samba/back_smb.conf.template","/etc/samba/smb.conf.template")

		if self.ORIGINALSTATUS:
			print "Restoring original service status"
			os.popen("/etc/init.d/samba start")

