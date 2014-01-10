#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright Tamas Marton 2013
#
#
#
#

import time
import speedtest_cli


DEBUG=1

class taskSpeedtest:

    def __init__(self, count='10'):
        '''
        Initialize the main variables
        '''
        self.ID = 6
        self.NAME='Internet Speedtest'
        self.DESCRIPTION='''Measuring your internet connection speed.
First on your computer, then on your router'''
        self.CLIENTDOWN=None
        self.CLIENTUP=None
        self.ROUTERDOWN=None
        self.ROUTERUP=None
        self.ENABLED = True
        self.RESULT = None


    def execute(self, controller, message):
        '''
        Executing the speedtest on the client, then waiting for the server to complete the speedtest on
        the router.
        '''
        self.RESULT = None
        print("------------------------------------------------------------")
        print "Name: "+self.NAME
        print self.DESCRIPTION
        print("------------------------------------------------------------")

        try:
            controller.communication.setTimeout(600)
            print "Getting Download, Upload speed on the Client.."
            print "This may take some time"
            controller.gui.sendToLog("Getting Download, Upload speed on the Client..")
            controller.gui.sendToLog("This may take some time")

            speedtest_cli.speedtest()

            self.CLIENTDOWN = speedtest_cli.DOWNSPEED
            self.CLIENTUP = speedtest_cli.UPSPEED

            if self.CLIENTDOWN == None:
                controller.sendMessageToServer("error")
                raise Exception("Unable to measure download speed on client.")
            if self.CLIENTUP == None:
                controller.sendMessageToServer("error")
                raise Exception("Unable to measure upload speed on client")

            print "\nDowndload speed: "+self.CLIENTDOWN
            controller.gui.sendToLog("Downdload speed on the Client: "+self.CLIENTDOWN)
            controller.sendMessageToServer(self.CLIENTDOWN)
            time.sleep(2)
            print "Upload speed: "+self.CLIENTUP
            controller.gui.sendToLog("Upload speed on the Client: "+self.CLIENTUP)
            controller.sendMessageToServer(self.CLIENTUP)

            controller.communication.sendFinished()
            controller.gui.sendToLog("Client finished.")

            print "Getting Download, Upload speed on the router.."
            print "This may take a few minutes"
            controller.gui.sendToLog("Getting Download, Upload speed on the router..")
            controller.gui.sendToLog("This may take a few minutes")


            msg = controller.receiveMessageFromServer()
            self.ROUTERDOWN = msg
            print "Download speed on the Router: " + self.ROUTERDOWN
            controller.gui.sendToLog("Download speed on the Router: " + self.ROUTERDOWN)

            msg = controller.receiveMessageFromServer()
            self.ROUTERUP = msg
            print "Upload speed on the Router: " + self.ROUTERUP
            controller.gui.sendToLog("Upload speed on the Router: " + self.ROUTERUP)


            if controller.communication.waitForFinished() == False:
                raise Exception("No 'Finished' response from Server")

            controller.communication.sendAck()
            controller.gui.sendToLog("Router finished.")

            text_result=(" Download speed on this Client: "+self.CLIENTDOWN+'''
'''+" Upload speed on this Client: "+self.CLIENTUP+'''

'''+" Download speed on the Router: "+self.ROUTERDOWN+'''
'''+" Upload speed on the Router: "+self.ROUTERUP)+'''

 To get the best results make sure that you are connecting to the internet with a cable. Wireless solutions (Wi-Fi, 3G etc. may be negatively affect the results)'''


        except RuntimeError,e :
            print "[Speedtest error] "+str(e)
            controller.gui.sendToLog("[Speedtest error] "+str(e))
            text_result = "An error occurred during the task: "+str(e)

        except Exception,e:
            print "[Speedtest error] "+str(e)
            controller.communication.sendError()
            controller.gui.sendToLog("[Speedtest error] "+str(e))
            text_result = "An error occurred during the task: "+str(e)

        self.RESULT={'name': self.NAME, 'result': text_result, 'image': None}




    def getID(self):
        return self.ID

