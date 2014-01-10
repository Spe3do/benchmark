# -*- coding: utf-8 -*-
# Author: Tamas Marton

import speedtest_cli
import time
import os

DEBUG = 1

class taskSpeedtest:

	def __init__(self):
		self.ID = 6
		self.NAME='Internet Speedtest'
		self.DESCRIPTION='Measuring your download an upload speed'
		self.CLIENTDOWN=None
		self.CLIENTUP=None
		self.SERVERDOWN=None
		self.SERVERUP=None
		self.ENABLED=True

		self.checkRequirements()

	def checkRequirements(self):
		if os.popen("opkg list-installed | grep python-expat").read() == '':
			self.ENABLED = False


	def executeTask(self, controller):
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")
		controller.sendToClient(str(self.ID))
		try: 
			controller.communication.setTimeout(600)
			print("Waiting for Client to finish the speedtest...")
			
			msg = controller.receiveFromClient()
			if msg == "error":
				raise Exception("Client error")

			else:
				self.CLIENTDOWN = msg
				print "Download speed on Client: " + self.CLIENTDOWN

			msg = controller.receiveFromClient()
			if msg == "error":
				raise Exception("Client error")
			else:
				self.CLIENTUP = msg
				print "Upload speed on Client: " + self.CLIENTUP

			if controller.communication.waitForFinished() == False:
				raise Exception("No 'Finished' response from Client")

			print "Getting Download, Upload speed on the Router.."
			print "This will take a few minutes"
			speedtest_cli.speedtest()

			self.SERVERDOWN = speedtest_cli.DOWNSPEED
			self.SERVERUP = speedtest_cli.UPSPEED

			if self.SERVERDOWN == None:
				controller.sendToClient("error")
				raise Exception("Unable to measure download speed on the Server")
			if self.SERVERUP == None:
				controller.sendToClient("error")
				raise Exception("Unable to measure upload speed on the Server")

			print "\nDownload speed on the Router: "+self.SERVERDOWN
			controller.sendToClient(self.SERVERDOWN)
			time.sleep(1)
			print "Upload speed on the Router: "+self.SERVERUP
			controller.sendToClient(self.SERVERUP)
			time.sleep(1)

			controller.communication.sendFinished()

			if controller.communication.waitForAck() == False:
				raise Exception("No 'Ack' response from Client")

		except Exception,e:
			print "[Speedtest Error] "+str(e)
			controller.sendToClient("error")


	def getID(self):
	    return self.ID

