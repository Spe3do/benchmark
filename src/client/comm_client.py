# -*- coding: utf-8 -*-
# Author: Tamas Marton

import socket
import time

DEBUG=0

class CommClient:

    def __init__(self, controller, port=33318, mybuffer=1024):
        self.IP = controller.SERVERIP
        self.PORT= port
        self.BUFFER=mybuffer
        self.TIMEOUT=180.0
        self.ISCONNECTED = False
        self.controller = controller

        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.TIMEOUT)


        self.ERROR="ERROR"
        self.TIMEOUT="TIMEOUT"
        self.IMGERROR="IMGERROR" 


    def setTimeout(self, time):
        self.sock.settimeout(time)


    def getTimeout(self):
        return str(self.sock.gettimeout())


    def validateIP(self, t_ip):
        try:
            socket.inet_aton(t_ip)
            return True
        except:
            return False


    def connectToServer(self):
        self.IP = self.controller.SERVERIP
        try:
            if not self.validateIP(self.IP):
                raise Exception("Invalid IP address")

            if not self.ISCONNECTED:
                self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(180.0)
                print "Connect to: " +self.IP +':'+str(self.PORT)
                self.sock.connect((self.IP,self.PORT))
                self.ISCONNECTED = True
        except socket.error,e:
            print "[Socket Error] "+str(e)
            self.controller.gui.connectpopup.title="Error: "+str(e)
        except Exception,b:
            print "[Connect to Server Error] "+str(b)
            self.controller.gui.connectpopup.title="Error: "+str(b)


    def disconnectFromServer(self):
        if self.ISCONNECTED:
            self.sock.close()
            self.ISCONNECTED = False
            print "Disconnect from: " +self.IP +':'+str(self.PORT)


    def receiveMessage(self):
        try:
            msg = self.sock.recv(self.BUFFER)
            if DEBUG:
                print ">>>Receiving message...: "+str(msg)
            if msg == self.ERROR:
                raise RuntimeError("Router Error")

            return msg

        except socket.timeout:
            self.ISCONNECTED = False 
            raise IOError(self.TIMEOUT)
        except socket.error, b:
            self.ISCONNECTED = False
            raise Exception("[Receiving Message Error] "+str(b))
        except:
            raise


    def receiveImage(self):
        try:
            img_data = ''
            while True:
                msg = self.sock.recv(self.BUFFER)
                if msg == self.IMGERROR:
                    raise RuntimeError("Router Error")
                elif msg == "no_more_data":
                    break
                else: 
                    img_data+=msg
            return img_data 
        except socket.timeout:
            self.ISCONNECTED = False 
            raise IOError(self.TIMEOUT)
        except socket.error, b:
            self.ISCONNECTED = False
            raise Exception("[Receiving Image Socket Error] "+str(b))
        except:
            raise


    def sendMessage(self, message):   
        try:
            count = len(message)
            time.sleep(1)
            if count != self.sock.send(message):
                raise Exception("[Send Message Error] couldn't send all the message")
            if DEBUG:
                print '<<<Sending a message to client: ' + message
        except socket.error, s:
            self.ISCONNECTED = False
            raise Exception("[Send Message Socket Error] "+str(s))
        except:
            raise

    
    def sendError(self):
        self.sendMessage(self.ERROR)


    def sendReady(self):
        self.sendMessage("READY")

    
    def waitForReady(self):
        try:
            msg = self.receiveMessage()
        except IOError,e:
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
        except IOError,e:
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
        except IOError,e:
            if str(e) == self.TIMEOUT:
                return False
                
        if msg == "ACK":
            return True
        else:
            return False

