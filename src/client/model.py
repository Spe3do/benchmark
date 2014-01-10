# -*- coding: utf-8 -*-
# Author: Tamas Marton

import taskPing
import taskIperf
import taskSamba
import taskNfs
import taskUsb
import taskSpeedtest

class Model:

    def __init__(self):
        self.taskList = []

        ping = taskPing.taskPing()
        if ping.ENABLED:
            self.taskList.append(ping)

        usb = taskUsb.taskUsb()
        if usb.ENABLED:
            self.taskList.append(usb)

        samba = taskSamba.taskSamba()
        if samba.ENABLED:
            self.taskList.append(samba)

        nfs = taskNfs.taskNfs()
        if nfs.ENABLED:
            self.taskList.append(nfs)

        iperf = taskIperf.taskIperf()
        if iperf.ENABLED:
            self.taskList.append(iperf)
        
        speedtest = taskSpeedtest.taskSpeedtest()
        if speedtest.ENABLED:
            self.taskList.append(speedtest)



        # self.taskList.append(taskPing.taskPing())
        # self.taskList.append(taskIperf.taskIperf())
        # self.taskList.append(taskSamba.taskSamba())
        # self.taskList.append(taskNfs.taskNfs())
        # self.taskList.append(taskUsb.taskUsb())
        # self.taskList.append(taskSpeedtest.taskSpeedtest())

        # print "leng: "+str(len(self.taskList))

        # for t in range(len(self.taskList)):
        #     print str(t)

        #     if not self.taskList[t].ENABLED:
        #         print "delete"
        #         del self.taskList[t]



    def addTask(self, t):
        self.taskList.append(t)


    def getTask(self, myid):
        tasksToRun = None
        for i in self.taskList:
            if i.ID == myid:
                tasksToRun=i

        return tasksToRun


    def removeTask(self, tid):
        for i in self.taskList:
            if i.ID == tid:
                self.taskList.remove(i)


    def getTaskIDByName(self, name):
        for i in self.taskList:
            if i.NAME == name:
                return i.ID


    def getTaskList(self):
        return self.taskList

    def getTasksNameList(self):
        namelist = []
        for i in self.taskList:
            namelist.append(i.NAME)
        
        return namelist

    def getTasksListOfDict(self):
        info = {}
        for i in self.taskList:
            tempdict = {'name': i.NAME, 'desc': i.DESCRIPTION, 'is_selected': False}
            info[i.ID] = tempdict

        return info