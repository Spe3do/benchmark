# -*- coding: utf-8 -*-
# Author: Tamas Marton

import socket
from time import sleep

DEBUG=0

# Implement the connection and the communication with the client
class CommServer:

    def __init__(self, controller, port=33318, mybuffer=1024):
        self.IP = controller.SERVERIP
        self.PORT = port
        self.BUFFER = mybuffer
        self.TIMEOUT= 180

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.TIMEOUT)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print "Default timeout: "+str(self.sock.gettimeout())

        self.ERROR="ERROR"
        self.TIMEOUT="TIMEOUT"
        self.IMGERROR="IMGERROR" 


    def setTimeout(self, time):
        self.sock.settimeout(time)


    def getTimeout(self):
        return str(self.sock.gettimeout())
        

    def startListening(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.IP, self.PORT))
            print 'Listening on: ' + self.IP + ':' + str(self.PORT)
            self.sock.listen(1)
            self.client,self.address=self.sock.accept()
            print "Incomming connection from client: ", self.address
            self.sock.settimeout(180.0)
        except Exception,e:
            print "[Error] Can't bind or listen socket, because: "+str(e)
            exit()


    def stopListening(self):
        self.client.close()
        self.sock.close()
        print "Closing connenction with client: ", self.address


    def sendMessage(self, message,mtime=1):
        try:
            count = len(message)
            sleep(mtime)
            if count != self.client.send(message):
                raise RuntimeError("not all the data has been transfered, maybe a socket error")
            if DEBUG:
                print '<<<Sending a message to client: ' + message
        except Exception,e:
            print "[Error] Can't send the message, because: "+ str(e)


    def sendPicture(self, mfile):
        try:
            img = open(mfile, 'r')
            while True:
                chunck = img.readline(self.BUFFER)
                if not chunck:
                    print "Sending picture finished"
                    self.sendMessage("no_more_data")
                    sleep(1)
                    break
                self.sendMessage(chunck, 0)
        except Exception, e:
            print "[Image Sending Error] "+str(e)
            

    def getClientIP(self):
        return self.address[0]


    def receiveMessage(self):
        try:
            msg = self.client.recv(self.BUFFER)
            if DEBUG:
                print ">>>Receiving message...:"+str(msg)
            if msg == self.ERROR:
                raise Exception("Router Error")

            return msg
            
        except socket.timeout:
            self.ISCONNECTED = False 
            raise IOError(self.TIMEOUT)
        except socket.error, b:
            self.ISCONNECTED = False
            raise Exception("[Receiving Message Error] "+str(b))
        except:
            raise


    def sendReady(self):
        self.sendMessage("READY")


    def sendError(self):
        self.sendMessage(self.ERROR)


    def sendIMGError(self):
        self.sendMessage(self.IMGERROR)

    
    def waitForReady(self):
        try:
            msg = self.receiveMessage()
        except IOError:
            if str(e) == self.TIMEOUT:
                return False

        if msg == "READY":
            return True
        else:
            return False

    
    def sendFinished(self):
        self.sendMessage("FINISHED")  


    def waitForFinished(self):
        try:
            msg = self.receiveMessage()
        except IOError:
            if str(e) == self.TIMEOUT:
                return False

        if msg == "FINISHED":
            return True
        else:
            return False

    def sendAck(self):
        self.sendMessage("ACK")


    def waitForAck(self):
        try:
            msg = self.receiveMessage()
        except IOError:
            if str(e) == self.TIMEOUT:
                return False

        if msg == "ACK":
            return True
        else:
            return False

