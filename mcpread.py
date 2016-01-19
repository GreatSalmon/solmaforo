#!/usr/bin/python
 
import spidev
import time
import os

RefVolts = 3.3

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
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
