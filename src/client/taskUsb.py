# -*- coding: utf-8 -*-
# Author: Tamas Marton

import os
import tempfile

DEBUG = 1

class taskUsb:

	def __init__(self):
		'''
		Initialize the main variables
		'''
		self.ID = 5
		self.NAME='USB Speed Test'
		self.DESCRIPTION="""Testing the reading and writing speed of the USB device connected to your router
[b][color=#36acd8]Steps:[/color][/b]
[b]1)[/b] Testing the writing speed of the USB device directly on the router
[b]2)[/b] Testing the reading speed of the USB device """
		self.READSPEED = None
		self.WRITESPEED = None
		self.ENABLED = True
		self.RESULT = None
		self.IMGFILE = os.path.join(tempfile.gettempdir(),'usb.png')


	def execute(self, controller, message):
		self.RESULT = None
		print("------------------------------------------------------------")
		print "Name: "+self.NAME
		print self.DESCRIPTION
		print("------------------------------------------------------------")

		try:
			if os.path.isfile(self.IMGFILE):
				os.remove(self.IMGFILE)

			controller.communication.setTimeout(300)
			if DEBUG:
				print "Timeout: "+controller.communication.getTimeout()

			print "Waiting for Server to complete the task..."
			controller.gui.sendToLog("Waiting for Server to complete the task...")

			msg = controller.receiveMessageFromServer()
			if msg == "error":
				raise Exception("Router error")
			else:
				self.WRITESPEED = msg
				print "Average writing speed to the USB device: " + self.WRITESPEED
				controller.gui.sendToLog("Average writing speed to the USB device: " + self.WRITESPEED)

			msg = controller.receiveMessageFromServer()
			if msg == "error":
				raise Exception("Router error")
			else:
				self.READSPEED = msg
				print "Average reading speed from the USB device: " + self.READSPEED
				controller.gui.sendToLog("Average reading speed from the USB device: " + self.READSPEED)
				

			text_result = (" Average writing speed to the USB device: "+self.WRITESPEED+'''
'''+" Average reading speed from the USB device: "+self.READSPEED)

			if controller.communication.waitForFinished() == False:
				print "[Error] No 'Finished' response from Server"
			else:
				controller.communication.sendAck()

			#Receiving plot from Server
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
			print "[USB Test Error] " +str(e)
			controller.gui.sendToLog("[USB Test Error] " +str(e))
			text_result = "An error occurred during the task: "+str(e)

		self.RESULT = {'name': self.NAME, 'result': text_result, 'image': self.IMGFILE}


	def getID(self):
		return self.ID


