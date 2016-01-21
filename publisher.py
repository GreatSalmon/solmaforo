#! /usr/bin/python
import os, sys
import time

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import pdb
import traceback
import mcpread

import socket


import solmaforo_utils as utils

#test line
#publish.single("home/test/ernestotest", "hello test",qos=0, hostname="broker.mqttdashboard.com", port=1883, client_id="rascaberri")

#params

Host = "212.72.74.21" # corresponds to "broker.mqttdashboard.com"
Port = 1883
ClientId = "rascaberri"
Topic = "home/test/ernestotest"


NumberOfMeasuresBetweenSends = 2 # Must be Integer >= 1
TimeConnectedAfterSend = 1 * 60
KeepAlive = False
#movistar
#InetConnectionString = '/usr/bin/modem3g/sakis3g --sudo "connect" USBMODEM="12d1:1c23" USBINTERFACE="2" APN="web.tmovil.cl" APN_USER="web" APN_PASS="web"'

#entel
InetConnectionString = '/usr/bin/modem3g/sakis3g --sudo "connect" USBMODEM="12d1:1506" USBINTERFACE="0" APN="imovil.entelpcs.cl" APN_USER="web" APN_PASS="web"'
InetDisconnectionString = '/usr/bin/modem3g/sakis3g --sudo "disconnect"'
# end params

# Global Variables


	

def DoInitialChecks():
	if NumberOfMeasuresBetweenSends < 1:
		raise "NumberOfMeasuresBetweenSends must be equal or greater than 1"

# Checks internet connection by pinging a fast address (google)
# Must find another way if this consumes to much data
def IsInternetOn():
	host = "8.8.8.8" #(google-public-dns-a.google.com)
	port = 53 #tcp
	#Service: domain (DNS/TCP)
	try:
		socket.setdefaulttimeout(1)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		utils.Log(str(ex))
		pass
	return False


def SendData(msg):
	success = False
	utils.Log("Sending Message: " + msg)
	try:
		publish.single(Topic, msg,qos=0, hostname=Host, port=Port, client_id=ClientId)

		utils.Log("Message sent")
		success = True	
	except Exception as e:
		utils.Log("Error in sending message. Details: %s" %e)
		success = False

	return success


def ConnectToInternet():
	utils.Log("Connecting to the Internet...")
	#check if already connected
	if IsInternetOn():
		myMAC, myIP = utils.GetAddresses()
		utils.Log("Already connected with IP: "+ myIP)
		return
	else:
		#connect via 3g
		p = os.popen(InetConnectionString)
		line = p.read()
		utils.Log(line)

def DisconnectFromInternet():
	utils.Log("Disconnecting from the Internet...")
	p = os.popen(InetDisconnectionString)
	line = p.read()
	utils.Log(line)


def GetCountOfMessagesInBuffer():
	i = -1
	with open(utils.BufferFile) as f:
		for i, l in enumerate(f):
			pass
	utils.Log("Number of lines in buffer: " + str(i+1))
	return i + 1

def DeleteBufferFile():
	with open(utils.BufferFile, "w"):
		pass

def GetLinesInBuffer():
	with open(utils.BufferFile, 'r') as bufferfile:
		msgs = bufferfile.read()
	return msgs

def SendMessagesInBuffer():
	msgs = ""
	msgs = GetLinesInBuffer();
	if msgs != "":
		dataSent = SendData(msgs)
		while not dataSent:
			dataSent = SendData(msgs)
			ConnectToInternet()
			msgs = GetLinesInBuffer();
			time.sleep(5)

def SendFirstMessage():
	ConnectToInternet()
	SendMessagesInBuffer()
	DeleteBufferFile()
	if not KeepAlive:
		DisconnectFromInternet()
	utils.Log("End sending first message")

def EternalLoop():
	while True:
		ConnectToInternet()
		if GetCountOfMessagesInBuffer() >= NumberOfMeasuresBetweenSends:
			utils.Log("Sending messages in buffer")
			SendMessagesInBuffer()
			DeleteBufferFile()
			if not KeepAlive:
				time.sleep(TimeConnectedAfterSend)
				DisconnectFromInternet()
				break
		time.sleep(1 * 60)


def StartProgram():
	DoInitialChecks()
	try:
		SendFirstMessage()

		EternalLoop()
	except Exception as e:
		utils.Log("Uncaught error. Loop will restart. Details: " + str(traceback.format_exc()))
		StartProgram()


#Start main program
if __name__ == '__main__':
	utils.Log("Starting publisher program")
	StartProgram()




