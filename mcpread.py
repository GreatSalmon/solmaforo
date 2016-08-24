#!/usr/bin/python
 
import spidev
import time
import os
import traceback
import solmaforo_utils as utils


TimeBetweenMeasures = 5 * 60 # 5 minutes

RefVolts = 3.3


# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
def DoInitialChecks():
	if TimeBetweenMeasures < 0:
		raise "TimeBetweenMeasures must be positive"

def SetTypeOfDevice():
	global DeviceType # solmaforo or simca
	DeviceType = utils.GetConfigParam("DeviceType").lower()
	utils.Log(DeviceType)
	if DeviceType != "solmaforo" and DeviceType != "simca":
		raise "Must set DeviceType to Solmaforo or Simca in config file"

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
	volts = (data * RefVolts) / float(1023)
	volts = round(volts,places)
	return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
	temp = ((data * 330)/float(1023))-50
	temp = round(temp,places)
	return temp

def GetVolts(channel):
	level = ReadChannel(channel)
	volts = ConvertVolts(level,2)
	return volts

def GetTimeStampWithOffset(): #offset from UTC time, in hours
	cmd = "date +'%z'"
	p = os.popen(cmd)
	line = p.read().strip()

	timeOffset = int(line)/100

	cmd = "date -u +'%Y-%m-%d %H:%M:%S'"
	p = os.popen(cmd)
	line = p.read().strip()

	timestamp = line

	return timestamp, timeOffset

def GetMeasureFromMCP(channel):
	measurementCnt = 100
	voltsMean = 0
	for i in range(measurementCnt):
		volts = GetVolts(channel)
		voltsMean += volts
		time.sleep(0.01)

	voltsMean = voltsMean/measurementCnt
	return voltsMean


def GetMeasurementForSolmaforo():
	mac, ip = utils.GetAddresses()	
	timestamp, timeOffset = GetTimeStampWithOffset() #offset from UTC time, in hours
	location = utils.GetConfigParam("Location")
	gain = float(utils.GetConfigParam("Gain_uv"))
	offset = float(utils.GetConfigParam("Offset_uv"))	
	uvb = (GetMeasureFromMCP(channel=0) - offset) * gain
        if uvb < 0:
             uvb = 0
	msg = "%s; %s; %s; %s; %s; %s; %s" % (ip, mac, DeviceType, location, timestamp, timeOffset, uvb) 
	return msg

def GetMeasurementForSimca():
	mac, ip = utils.GetAddresses()	
	timestamp, timeOffset = GetTimeStampWithOffset() #offset from UTC time, in hours
	location = utils.GetConfigParam("Location")
	dato1 = GetMeasureFromMCP(channel=0)
	dato2 = GetMeasureFromMCP(channel=1)
	temp1 = GetMeasureFromMCP(channel=2)
	temp2 = GetMeasureFromMCP(channel=3)

	msg = "%s; %s; %s; %s; %s; %s; %s; %s; %s; %s" % (ip, mac, DeviceType, location, timestamp, timeOffset, dato1,dato2,temp1,temp2) 
	return msg


def SaveMeasurementToBuffer(msg):
	utils.Log("Saving following line to buffer: ")
	utils.Log(msg)
	with open(utils.BufferFile, "a") as bufferfile:
		bufferfile.write(msg + ",\n")

def SaveMeasurementToPermanentFile(msg):
	utils.Log("Saving line to permanent file.")
	with open(utils.PermanentFile, "a") as bufferfile:
		bufferfile.write(msg + ",\n")

        statinfo = os.stat(utils.PermanentFile)
        if statinfo.st_size > 500000000:
                os.remove(utils.PermanentFile)


def GetMeasurement():
	msg = ""
	if DeviceType == "solmaforo":
		msg = GetMeasurementForSolmaforo()
	else: #simca
		msg = GetMeasurementForSimca()
	return msg

def EternalReader():
	while True:
		msg = GetMeasurement()
		SaveMeasurementToBuffer(msg)
		SaveMeasurementToPermanentFile(msg)
		time.sleep(TimeBetweenMeasures)

def StartProgram():
	try:
		EternalReader()
	except Exception as e:
		utils.Log("Uncaught error. Loop will restart. Details: " + str(traceback.format_exc()))
		StartProgram()



# Start Program
if __name__ == '__main__':
	utils.Log("Starting reader program")
	DoInitialChecks()
	SetTypeOfDevice()
	StartProgram()
	









