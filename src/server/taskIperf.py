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
import time

import measureLoad

DEBUG = 0

class taskIperf:


    def __init__(self):
        self.ID = 2
        self.NAME='Iperf Test'
        self.DESCRIPTION='Testing the network speed between the Client and the Router'

        self.OS = platform.system()
        if self.OS == "Darwin":
            self.IPERFPATH="../Client/Programs/Iperf/Darwin/iperf"
        if self.OS == "Linux":
            self.IPERFPATH="iperf"
        if self.OS == "Windows":
            self.IPERFPATH ="..\Client\Programs\Iperf\Windows\iperf.exe"

        if DEBUG:
            print "IPERFPATH: "+self.IPERFPATH


        self.ENABLED = True

        self.checkRequirements()


    def checkRequirements(self):
        if os.popen("opkg list-installed | grep iperf").read() == '':
            self.ENABLED = False
        if os.popen("opkg list-installed | grep rrdtool") == '':
            self.ENABLED = False

    # - Start Iperf server in a subprocess, sending task information to client
    # - Reveice measurement data from client
    # - Kill Iperf server
    def executeTask(self,controller):
        print("------------------------------------------------------------")
        print "Name: "+self.NAME
        print self.DESCRIPTION
        print("------------------------------------------------------------")
        try:
            controller.communication.setTimeout(90)

            self.IPTOCONNECT = controller.communication.getClientIP()
            controller.sendToClient(str(self.ID)+';' +controller.SERVERIP)

            #Start load measurement
            self.LOAD = measureLoad.measureLoad("iperf")
            self.LOAD.start()

            if controller.communication.waitForReady():
                print "Connecting to Iperf server on: "+self.IPTOCONNECT
                string = str(self.IPERFPATH)+ " -t 60 -c "+str(self.IPTOCONNECT)
                print string
                ms = os.popen(string).read()
            else:
                print "[Error] No 'ready' response from Client"

            self.DATA = self.regular(ms)

            controller.communication.sendFinished()

            time.sleep(1)
            
            if self.DATA == None:
                controller.sendToClient("error")
                raise Exception("Unable to measure local network speed")
            else:
                controller.sendToClient(self.DATA)

            if controller.communication.waitForAck() == False:
                print "[Error] No 'ack' response from Client"

            print "Measured Speed: " + self.DATA

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
            print "[Iperf Error] "+str(e)
            controller.sendToClient("error")

    def regular(self, data):
        speed = None
        try:
            if DEBUG:
                print "DATA in regular: "
                print data

            match = re.search(r'(\d+.\d+) ?(Gbits|Mbits|Kbits)/sec', data)
            speed = match.group()

            if DEBUG:
                print "After regexp: "
                print speed

        except Exception, e:
            print "[Iperf Parsing Error] "+str(e)
        finally:
            return speed

        
    def getID(self):
        return self.ID