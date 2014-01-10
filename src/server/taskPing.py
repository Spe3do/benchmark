# -*- coding: utf-8 -*-
# Author: Tamas Marton

import os
import re

DEBUG = 1

class taskPing:

    def __init__(self):
        self.ID = 1
        self.NAME='Ping Test'
        self.DESCRIPTION='Testing the round-trip-time between the clinet and the router.'
        self.ENABLED = True
        self.COUNT = '10'


    def executeTask(self, controller):
        print("------------------------------------------------------------")
        print "Name: "+self.NAME
        print self.DESCRIPTION
        print("------------------------------------------------------------")
        self.MINPING=None
        self.AVGPING=None
        self.MAXPING=None

        try:
            self.IPTOPING = controller.communication.getClientIP()
            if DEBUG:
                print "Ip to ping: "+str(self.IPTOPING)

            controller.sendToClient(str(self.ID))

            os.popen("ping -c 1 -q "+self.IPTOPING)
            ms = os.popen("ping -c "+self.COUNT+" -q "+self.IPTOPING).read()
            print "Command output: "+str(ms)
            data = self.regular(ms)

            controller.sendToClient(data)

            if controller.communication.waitForAck() == False:
                raise Exception("No ACK response from Client")
            else:
                controller.communication.sendFinished()

        except Exception, e:
            print "[Ping Error] "+str(e)


    def regular(self, data):
        match = re.search(r'(\d+?(.\d+|))/(\d+?(.\d+|))/(\d+?(.\d+|))',data)
        self.MINPING = match.group(1)
        self.AVGPING = match.group(3)
        self.MAXPING = match.group(5)

        if DEBUG:
            print "After running regular expression: " + match.group()

        concat = "Min: " + self.MINPING + " Avg: " +self.AVGPING+ " Max: " +self.MAXPING
        print concat

        return concat
        
        
    def getID(self):
        return self.ID

