#! /usr/bin/python
import os, sys
import datetime
import time
import random
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import pdb
import traceback, logging
import mcpread

import socket
import fcntl
import struct

import urllib2


Location = "USACH"
Host = "broker.mqttdashboard.com"
Port = 1883
ClientId = "rascaberri"
Topic = "home/test/ernestotest"
LogFile = "/home/pi/solmaforo/logs.log"
TimeBetweenMsgs = 3 * 60
TimeConnected = 1 * 60
KeepAlive = True
#movistar
#InetConnectionString = '/usr/bin/modem3g/sakis3g --sudo "connect" USBMODEM="12d1:1c23" USBINTERFACE="2" APN="web.tmovil.cl" APN_USER="web" APN_PASS="web"'

#entel
InetConnectionString = '/usr/bin/modem3g/sakis3g --sudo "connect" USBMODEM="12d1:1506" USBINTERFACE="0" APN="imovil.entelpcs.cl" APN_USER="web" APN_PASS="web"'

InetDisconnectionString = '/usr/bin/modem3g/sakis3g --sudo "disconnect"'


def Log(msg):
	with open(LogFile, "a") as logfile:
		logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "; " + msg + "\n")
	print(msg)

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
		Log(str(ex))
		pass
	return False

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])

def GetAddresses():
	#Try to get PPP0 (mobile) address
	#If it doesn't work, get Local ethernet address
	try:
		myMAC = open('/sys/class/net/eth0/address').read().strip()
		myIP = get_ip_address("ppp0")
	except IOError as e:
		try:
			myMAC = open('/sys/class/net/eth0/address').read().strip()
			myIP = get_ip_address("eth0")
		except IOError as e:
			myIP = "No IP"

	return myMAC, myIP

def SendData(msg):
	success = False
	Log("Sending Message: " + msg)
	try:
		publish.single(Topic, msg,qos=0, hostname=Host, port=Port, client_id=ClientId)
		Log("Message sent")
		success = True	
	except Exception as e:
		Log("Error in sending message. Details: %s" %e)
		success = False

	return success


def ConnectToInternet():
	Log("Connecting to the Internet...")
	#check if already connected
	if IsInternetOn():
		Log("Already connected")
		return
	else:
		#connect via 3g
		p = os.popen(InetConnectionString)
		line = p.read()
		Log(line)

def DisconnectFromInternet():
	Log("Disconnecting from the Internet...")
	p = os.popen(InetDisconnectionString)
	line = p.read()
	Log(line)

def GetTimeStampWithOffset(): #offset from UTC time, in hours
	cmd = "date +'%z'"
	p = os.popen(cmd)
	line = p.read().strip()
	Log(line)
	timeOffset = int(line)/100

	cmd = "date -u +'%Y-%m-%d %H:%M:%S'"
	p = os.popen(cmd)
	line = p.read().strip()
	Log(line)
	timestamp = line

	return timestamp, timeOffset

def GetUVB(channel):
	measurementCnt = 100
	voltsMean = 0
	for i in range(measurementCnt):
		volts = mcpread.GetVolts(channel)
		voltsMean += volts
		time.sleep(0.01)

	voltsMean = voltsMean/measurementCnt
	return voltsMean


def SendMessage():
	mac, ip = GetAddresses()
	
	timestamp, timeOffset = GetTimeStampWithOffset() #offset from UTC time, in hours
	data1 = GetUVB(channel=0)
	data2 = random.randint(15,30)
	msg = "%s; %s; %s; %s; %s; %s; %s" % (ip, mac, Location, timestamp, timeOffset, data1, data2)
	dataSent = False
	while not dataSent:
		dataSent = SendData(msg)
		time.sleep(5)


def EternalLoop():
	while True:
		ConnectToInternet()
		SendMessage()
		time.sleep(TimeConnected)
		if not KeepAlive:
			DisconnectFromInternet()
		time.sleep(TimeBetweenMsgs - TimeConnected)

def StartProgram():
	try:
		EternalLoop()
	except Exception as e:
		logging.error(traceback.format_exc())
		Log("Uncaught error. Loop will restart. Details: " + str(traceback.format_exc()))
		StartProgram()


#Start main program

Log("Starting SIMCA program")
StartProgram()




