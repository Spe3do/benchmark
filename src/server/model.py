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

        self.taskList.append(taskPing.taskPing())
        self.taskList.append(taskUsb.taskUsb())
        self.taskList.append(taskSamba.taskSamba())
        self.taskList.append(taskNfs.taskNfs())
        self.taskList.append(taskIperf.taskIperf())
        self.taskList.append(taskSpeedtest.taskSpeedtest())


    def addTask(self, t):
        self.taskList.append(t)


    def getDisabledTasks(self):
        txt = ''
        for i in self.taskList:
            if i.ENABLED == False:
                txt += str(i.ID)+','

        if len(txt) != 0:
            txt = txt[:-1]
        else:
            txt = 'None'

        print txt

        return txt


    def populateTaskList(self, idList):
        tasksToRun = []
        try:
            for i in self.taskList:
                if self.checkID(i.getID(), idList) == True:
                    tasksToRun.append(i)
        except Exception, e:
            print "[Popupate Task List Error] "+str(e)
        return tasksToRun


    def getTaskList(self):
        return self.taskList


    def checkID(self, t, iList):
        for i in iList:
            if t == i:
                return True

        return False
