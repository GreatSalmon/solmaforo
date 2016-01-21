#!/usr/bin/python
 
import spidev
import time
import os
import traceback
import solmaforo_utils as utils


TimeBetweenMeasures = 3 * 60 # 3 minutes

RefVolts = 3.3

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
def DoInitialChecks():
	if TimeBetweenMeasures < 0:
		raise "TimeBetweenMeasures must be positive"


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

def GetUVB(channel):
	measurementCnt = 100
	voltsMean = 0
	for i in range(measurementCnt):
		volts = GetVolts(channel)
		voltsMean += volts
		time.sleep(0.01)

	voltsMean = voltsMean/measurementCnt
	return voltsMean


def GetMeasurement():
	mac, ip = utils.GetAddresses()	
	timestamp, timeOffset = GetTimeStampWithOffset() #offset from UTC time, in hours
	uvb = GetUVB(channel=0)
	msg = "%s; %s; %s; %s; %s; %s" % (ip, mac, Location, timestamp, timeOffset, uvb)
	return msg

def SaveMeasurementToBuffer():
	msg = GetMeasurement()
	utils.Log("Saving following line to buffer: ")
	utils.Log(msg)
	with open(BufferFile, "a") as bufferfile:
		bufferfile.write(msg + ",\n")


def EternalReader():
	while True:
		SaveMeasurementToBuffer()
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
	StartProgram()
	









