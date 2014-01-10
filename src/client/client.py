#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Tamas Marton


import comm_client
import model
from kivy.app import App
import gui
from threading import Thread
import time

DEBUG = 1

class Controller(App):
    title = 'Router Performance Client'

    def __init__(self):
        super(Controller,self).__init__()

        self.SERVERIP = '0'

        self.communication = comm_client.CommClient(self)
        self.model = model.Model()
        self.sToDo = []

        self.ACTIVE = True
        self.STATE = 'DISCONNECTED'

    def runTask(self, message):
        self.taskToDo = self.parseMessage(message)

        if not (self.taskToDo[0] == None):
            task = self.model.getTask(self.taskToDo[0])
            self.taskToDo.pop(0)
            self.gui.updateExecutionStatus(task)
            task.execute(self, self.taskToDo)


    def getResults(self):
        resultdict = {}
        j = 0
        for i in self.model.taskList:
            if i.RESULT != None:
                resultdict[j] = i.RESULT
                i.RESULT = None 
                j+=1

        return resultdict


    def setServerDisabledTasks(self, mlist):
        if mlist != "None":
            tlist = mlist.split(',')
            for i in tlist:
                self.model.removeTask(int(i))


    def receiveMessageFromServer(self):
        try:
            message = self.communication.receiveMessage()
            return message
        except:
            raise


    def receiveImageFromServer(self):
        try:
            img_data = self.communication.receiveImage()
            return img_data
        except:
            raise


    def sendMessageToServer(self, msg):
        try:
            self.communication.sendMessage(msg)
        except:
            raise

    def sendTasksToServer(self, mylist):
        try:
            id_list = ''
            for i in mylist:
                id_list+=str(self.model.getTaskIDByName(i))+','
            id_list = id_list[:-1]
            print id_list

            if self.communication.ISCONNECTED:
                self.sendMessageToServer(id_list)
        except:
            print "[Send Tasks to Server Error] "
            self.STATE="DISCONNECTED"


    def parseMessage(self, message):
        orders = None
        try:
            orders = message.split(';')
            orders[0] = int(orders[0])

        except ValueError, e:
            print "[Unable to parse message] "+str(e)
        finally:
            return orders


    def build(self):
        self.gui = gui.GUI()
        return self.gui


def main_loop():
    while cr.ACTIVE:
        print "STATE: "+cr.STATE
        if cr.communication.ISCONNECTED == False:
            cr.STATE == 'DISCONNECTED'

        if cr.STATE == 'DISCONNECTED':
            if not cr.communication.ISCONNECTED:
                time.sleep(2)
            else:
                cr.STATE = 'CONNECTED'

        elif cr.STATE == 'CONNECTED':
            msg = ''
            cr.gui.connectpopup.title='Getting information from server'
            try:
                print "Getting disabled tasks"
                msg=cr.receiveMessageFromServer()
                print "Finished"
                cr.setServerDisabledTasks(msg)
            except Exception, e:
                print "[Main Loop Running State Error] "+str(e)
                cr.STATE="DISCONNECTED"
                cr.gui.connectpopup.dismiss()
                continue
            cr.gui.switchToTab("Tasks")
            cr.gui.connectpopup.dismiss()
            cr.STATE = 'IDLE'

        elif cr.STATE == 'IDLE':
            time.sleep(2)

        elif cr.STATE == 'RUNNING':
            msg = ''
            counter = 0
            cr.gui.updateProgressBar(counter)
            while msg != "end":
                try:
                    msg = cr.receiveMessageFromServer()
                except Exception, e:
                    print "[Main Loop Running State Error] "+str(e)
                    cr.STATE="DISCONNECTED"
                    continue
                if DEBUG:
                    print "Received message from Server: "+msg
                if msg != "end":
                    counter += 1
                    cr.runTask(msg)
                    cr.gui.updateProgressBar(counter)
            if msg == "end":
                cr.gui.getResults()
                cr.gui.switchToTab("Results")
                cr.STATE = 'RESULT'

        elif cr.STATE == 'RESULT':
            time.sleep(2)

        cr.gui.setConnectionStatus(cr.communication.ISCONNECTED)


if __name__ == '__main__':
    try:
        cr = Controller()
        thread = Thread(target=main_loop, args=())
        thread.start()
        cr.run()
    except Exception, e:
        print str(e)
    finally:
        cr.ACTIVE = False
        if cr.communication.ISCONNECTED:
            cr.sendMessageToServer("disconnect")
            cr.communication.disconnectFromServer()
