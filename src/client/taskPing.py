#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright Tamas Marton 2013
#
#
#
#

import platform
import os
import re


DEBUG=0

class taskPing:

    def __init__(self):
        '''
        Initialize the main variables
        '''
        self.ID = 1
        self.NAME='Ping Test'
        self.DESCRIPTION='Testing the round-trip-time between the client and the router.'
        self.OS = platform.system()
        self.ENABLED = True
        self.RESULT = None

        self.MINPING=None
        self.AVGPING=None
        self.MAXPING=None


    def execute(self, controller, message):
        '''
        Waiting the server to measure the ping, then receiving the measurement, parsing, storing
        and displaying it
        '''
        self.RESULT = None
        print("------------------------------------------------------------")
        print "Name: "+self.NAME
        print self.DESCRIPTION
        print("------------------------------------------------------------")
        result_text = ''
        try:
            controller.gui.sendToLog("Starting ping test")
            data = controller.communication.receiveMessage()

            controller.gui.sendToLog(data)
            self.parse(data)

            result_text = (" Minimum: "+self.MINPING+''' ms
'''+" Maximum: "+self.MAXPING+''' ms
'''+" Average: "+self.AVGPING+" ms")

            controller.communication.sendAck()
            if controller.communication.waitForFinished() == False:
                raise Exception("No Finished response from Router")

        except Exception, e:
            print "[Ping Error] "+str(e)
            controller.gui.sendToLog("[Ping Error] "+str(e))
            controller.communication.sendError()
            text_result = "An error occurred during the task: "+str(e)
        finally:
            self.RESULT={'name': self.NAME, 'result': result_text, 'image': None}


    def parse(self, data):
        '''
        Parsing the data received from the server.
        '''
        try:
            match = re.search(r'Min: (\d+?(.\d+|)) Avg: (\d+?(.\d+|)) Max: (\d+?(.\d+|))',data)
            self.MINPING=match.group(1)
            self.AVGPING=match.group(3)
            self.MAXPING=match.group(5)

            print "MINPING: " + str(self.MINPING)
            print "AVGPING: " + str(self.AVGPING)
            print "MAXPING: " + str(self.MAXPING)

        except Exception, e:
            print "[Ping Parse Error] "+str(e) 


    def getID(self):
        return self.ID

