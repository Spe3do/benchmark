# -*- coding: utf-8 -*-
# Author: Tamas Marton

import platform
import os
import re
import subprocess
from time import sleep
import tempfile

DEBUG = 1

class taskIperf:


	def __init__(self):
		'''
		Initialize the main variables
		'''
		self.ID = 2
		self.NAME='Iperf Test'
		self.DESCRIPTION='''Testing the local network speed between the Client and the Router.'''
		self.OS = platform.system()
		self.ENABLED = True
		self.RESULT = None
		self.IMGFILE = os.path.join(tempfile.gettempdir(),'iperf.png')

		if DEBUG:
			print "The current OS is " + self.OS

		if self.OS == "Windows":
			self.IPERFPATH=".\Programs\Iperf\Windows\iperf.exe"

		if self.OS == "Darwin":
			self.IPERFPATH="./Programs/Iperf/Darwin/iperf"

		if self.OS == "Linux":
			if os.uname()[4] == "x86_64":
				self.IPERFPATH="./Programs/Iperf/Linux/iperf_64"
			
			if os.uname()[4] == "i686":
				self.IPERFPATH="./Programs/Iperf/Linux/iperf_32"

		self.checkRequirements()

	def checkRequirements(self):
		if not os.path.exists(self.IPERFPATH):
			self.ENABLED = False


	def parse(self, message):
		"""
		Parsing the message came from the Server, for the task specific variables
		"""
		self.IPTOCONNECT = message[0]


	def execute(self, controller, message):
		self.parse(message)
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")

		try:
			if os.path.isfile(self.IMGFILE):
				os.remove(self.IMGFILE)
			
			controller.communication.setTimeout(90)
			process = subprocess.Popen(self.IPERFPATH+" -s ", shell=True,stdout=subprocess.PIPE)

			if DEBUG:
				print "Iperf server is listening for connections"
				controller.gui.sendToLog("Iperf server is listening for connections")

			sleep(5)
			controller.communication.sendReady()
			controller.gui.sendToLog("Testing speed...")

			if controller.communication.waitForFinished():
				if self.OS != "Windows":
					os.popen("killall iperf")
				if self.OS == "Windows":
					os.popen("taskkill /IM iperf.exe /F")

				controller.gui.sendToLog("Stopping Iperf server")

			else:
				raise Exception("No 'finished' response from Server")

			msg = controller.receiveMessageFromServer()
			self.SPEED = msg
			print "Local network speed: " + self.SPEED
			controller.gui.sendToLog("Local network speed: " + self.SPEED)
			text_result = " Local network speed: "+self.SPEED+'''

::

 This result means that a program running on your router can send you data at this speed.
 If your router, computer and wire capable of gigabit speeds or your devices know the newest wireless standards this result doesn't mean the overal network performance of the router which can be much higher.''' 

			controller.communication.sendAck()


			msg = controller.receiveImageFromServer()
			if msg == "image_error":
				self.IMGFILE = None
				raise Exception("No Image Received")
			else:
				print "Write image"
				image_data = msg
				image = open(self.IMGFILE,'wb')
				image.write(image_data)
				image.close()


		except Exception, e:
			print "[Iperf Error] "+str(e)
			controller.gui.sendToLog("[Iperf Error] "+str(e))
			text_result = "An error occurred during the task: "+str(e)

			if str(e) == "No 'finished' response from Server":
				if self.OS != "Windows":
					os.popen("killall iperf")
				if self.OS == "Windows":
					os.popen("taskkill /IM iperf.exe /F")
			

		self.RESULT = {'name': self.NAME, 'result': text_result, 'image': self.IMGFILE}



	def regular(self, data):
		if DEBUG:
			print data

		match = re.search(r'(\d+.\d+) ?(Gbits|Mbits|Kbits)/sec', data)
		speed = match.group()

		print speed

		return speed


	def getID(self):
		return self.ID
