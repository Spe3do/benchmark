#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Tamas Marton

import argparse     # argparse make it easy to write user-friendy cli interface
from time import sleep
import os
import re

# Import own modules
import comm_server
import model

# Controller
# This is the main controlling class. Responsibilities:
#   - Initialize and execute the given task(s)
#   - Communicate with the client
#   - Export the results
class Controller:

    def __init__(self):
        self.setServerIP()

        self.model = model.Model()
        self.task_list = None

        self.STATE = 'DISCONNECTED'

        self.communication = comm_server.CommServer(self)

        self.WORKFOLDER = None


    def listeningForConnection(self):
        self.communication.startListening()
        self.STATE = 'CONNECTED'


    def runTask(self):
        if self.task_list != None: 
            tasklist = self.model.populateTaskList(self.task_list)
            for i in tasklist:
                i.executeTask(self)
                sleep(90)

    def getFolder(self):
        try:
            data = os.popen("df | awk '{printf $4 }{print $6} ' | sort -nr | head -1").read()
            match = re.search(r'(\d+)(/?.+)',data)
            size = int(match.group(1))
            folder = match.group(2)

            print "Folder name: "+folder+" Avaliable: "+str(size/1024)+" MB"
            if size > 153600:
                print "This folder has enogh free space"
                self.WORKFOLDER=folder
            else:
                print "No enogh space for samba,nfs,usb speed test"
        except Exception, e:
            print "[getFolder Error] "+str(e)



    def sendToClient(self, message):
        try:
            self.communication.sendMessage(message)
        except:
            raise


    def sendImageToClient(self, data):
        try:
            self.communication.sendPicture(data)
        except:
            raise


    def receiveFromClient(self):
        try:
            msg = self.communication.receiveMessage()
            return msg
        except:
            raise


    def setServerIP(self):
        #self.SERVERIP='127.0.0.1'
        self.SERVERIP=os.popen("uci -P/var/state get network.lan.ipaddr").read().rstrip()


    def setTaskList(self, tasks):
        self.task_list = tasks


# Convert the comma separated tasks to a normal list and return it
def commaToList(tasks):
    tasks_list = None
    try:
        tasks_list   = tasks.split(',')

        tasks_list = [int(i) for i in tasks_list]

        return tasks_list
    except ValueError, e:
        print "[Parsing message from Client Error] "+str(e)


# Main entry point
# Parsing the command line arguments and passing the given tasks as a list to
# the Controller
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Router benchmarking tool - Server')
    parser.add_argument('-t','--task', help='Run the given measurement tasks. The tasks should be listed by comma separated for example: 1,2,3,4', required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    cr = Controller() 

    while True:
        print "Server State: "+cr.STATE

        if cr.STATE == 'DISCONNECTED':
            cr.getFolder()
            cr.listeningForConnection()

        elif cr.STATE == 'CONNECTED':
            print "Sending disabled tasks."
            try:
                cr.sendToClient(cr.model.getDisabledTasks())
            except Exception, e:
                print "[Main Loop Error] "+str(e)
                cr.STATE= 'DISCONNECTED'
                continue

            cr.STATE = 'IDLE'

        elif cr.STATE == 'IDLE':
            try:
                msg_task = cr.receiveFromClient()

                if msg_task == 'disconnect':
                    # cr.communication.stopListening();
                    # cr.STATE= 'DISCONNECTED'
                    # continue
                    break
                else:
                    cr.setTaskList(commaToList(msg_task))
                    cr.STATE = 'RUNNING'

            except Exception,e :
                print "[Main Loop Error] "+str(e)
                cr.STATE= 'DISCONNECTED'
                continue


        elif cr.STATE == 'RUNNING':
            cr.runTask()
            cr.sendToClient("end")
            cr.STATE = 'IDLE'


    cr.sendToClient("disconnect")
    cr.communication.stopListening();


