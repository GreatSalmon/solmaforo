#!/usr/bin/python

import RPi.GPIO as GPIO
import math

#GPIO.setmode(GPIO.BCM) #esto significa que el numero que se pasa a la funcion es el numero de GPIO

#GPIO.setup(11,GPIO.OUT,initial=GPIO.HIGH)
#GPIO.cleanup()
GPIO.setwarnings(False)
import os,sys
import spidev
import time
import datetime
from ftplib import FTP
import bz2
import traceback
import syslog



# CONNEXIONES entre RASPBERRY PI Y MCP32g08
# RASPBERRYPI     | MCP3208
# ------------------------
# PIN 19 (GPIO 10)| D IN
# PIN 21 (GPIO  9)| D OUT
# PIN 23 (GPIO 11)| CLK
# PIN 24 (GPIO  8)| CS
#                 |
# PIN 1  (3.3V)   | VDD
# PIN 1  (3.3V)   | VREF
# PIN 39 (GND)    | AGND
# PIN 39 (GND)    | DGND


# PINES DEL SIMCA
# RASPI          | SIMCA     | Nombre
# -------------------------------------
# MCP 1          | PIN 8     | DETECTOR
# MCP 2          | PIN 9     | MONITOR
# MCP 3          | PIN 10    | TEMP INTERNA (CONFIRMAR)
#   ?            | PIN 11    | TEMP EXTERNA (CONFIRMAR)
# GPIO 5         | PIN 14    | LED IR
# GPIO 6         | PIN 15    | LED UV
# GPIO 13        | PIN 16    | BOMBA


# LISTA DE COSAS QUE HACER
# AL INICIAR EL PROGRAMA
#
# 1. LEER ARCHIVO DE CONF
# 2. LEER DETECTOR Y MONITOR. SI LOS VALORES SON ERRONEOS, LANZAR ADVERTENCIA
# 3. ESPERAR QUE SE ESTABILICE LA TEMPERATURA: LEER TEMP INTERNA Y QUE SEA >= "TEMPESTABLE" GRADOS. 
# 4. BOMBEAR 1 MINUTO, PARAR 1 MINUTO, BOMBEAR 1 MINUTO, PARAR
# 5. COMENZAR PROGRAMA
#
#
# CADA 15 MIN
# A. LANZAR BOMBA TBOMBA MIN. TBOMBA: SE LEE EN EL ARCHIVO DE CONFIGURACION
# B. ESPERAR 15 MIN
# C. LANZAR LED IR 30 SEC 
# D. LEER DETECTOR Y MONITOR NPROM VECES, TOMAR PROMEDIO. NPROM: SE LEE DEL ARCHIVO DE CONFIGURACION
# E. GUARDAR DATOS. LA HORA DEBE CORRESPONDER A LOS 15 MINUTOS ANTERIORES. (RESTAR 15 MIN A LA HORA ACTUAL)
# F. APAGAR LED IR
# G. ENCENDER LED UV 30 SEG
# H. LEER DATOS COMO EN D.
# I. GUARDAR DATOS COMO EN E.
# H. APAGAR LED UV
# J. LANZAR BOMBA COMO EN A.
#
# CREAR CHECKSIMCA.PY, APARTE
#

# setup GPIOS
spi = spidev.SpiDev()
spi.open(0,0)
dataSentToday = False
GPIO.setmode(GPIO.BCM) #esto significa que el numero que se pasa a la funcion es el numero de GPIO

GPIO.setup(5,GPIO.OUT, initial=GPIO.LOW) # LED IR
GPIO.setup(6,GPIO.OUT, initial=GPIO.LOW) # LED UV
GPIO.setup(13,GPIO.OUT, initial=GPIO.LOW) # BOMBA

def LeerConf(variable):
	p = os.popen("grep '" + variable + "' /home/pi/simca/conf.dat")
	linea = p.readlines()
	split = linea[0].split("=")
	return split[1]

def BorrarArchivo():
	if os.path.exists("/home/pi/simca/simca.log"):
		 os.remove("/home/pi/simca/simca.log")

def GenerarNombreArchivo():
	arch = "J-" + time.strftime("%m%d%y") + ".dat"
	return arch

def NPROM():
	return int(LeerConf('NPROM'))

def TEMPESTABLE():
	return float(LeerConf('TEMPESTABLE'))

def TBOMBA():
	return float(LeerConf('TBOMBA'))

def V_te():
	return float(LeerConf('V_te'))

def V_ti():
	return float(LeerConf('V_ti'))

def B_0():
	return float(LeerConf('B_0'))

def R_0():
	return float(LeerConf('R_0'))

def R_aux():
	return float(LeerConf('R_aux'))

def ActivarGPIO(numGPIO, encender):
	if encender:
		GPIO.output(numGPIO, GPIO.HIGH)
	else:
		GPIO.output(numGPIO, GPIO.LOW)

def ReadADC(channel):
	if channel > 7 or channel < 0:
		return 'bad input'
	if channel == 0:
		#00000000
		middlebit = 0
	elif channel == 1:
		#01000000
		middlebit = 64
	elif channel == 2:
		#10000000
		middlebit = 128
	elif channel == 3:
		#11000000
		middlebit = 192
	else:
		print 'ReadADC not yet implemented for channel ' + str(channel)
	r = spi.xfer2([6, middlebit , 0])
	adcout = ( (r[1] & 15) << 8) + r[2]
	return adcout


def ReadVoltsFromMCP(channel): #channel: 0 to 7
	rawvalue = ReadADC(channel)
	voltsvalue = rawvalue * 4.83 / 4096
	return voltsvalue

def SendDataToServer():
	ftp = FTP('ambiente.usach.cl')
	fpas = open('/home/pi/papa/ftp.pas','r')
	pwd = bz2.decompress(fpas.read())
	ftp.login('root',pwd)
	ftp.cwd('/var/www/html/uv/data_simca_test/')
	print ftp.storlines('STOR test.dat' , open('/home/pi/papa/data.dat')) 
	ftp.close()

def LeerArchivoConf():
	#lee el archivo de conf y guarda los datos como variables. Hacer esto en tiempo real?
	notyetimplemented=1

def LeerDetector():
	#lee el valor del detector.
	voltsDetector = ReadVoltsFromMCP(0)
	return voltsDetector

def LeerDetectorYMonitorPromedio():
	#Lee el detector NPROM veces, devuelve el promedio
	suma = 0
	for i in range(NPROM()):
		suma += LeerDetector()
	promedioDetector = suma / NPROM()
	suma = 0
	for i in range(NPROM()):
	  suma += LeerMonitor()
	promedioMonitor = suma / NPROM()
	return promedioDetector, promedioMonitor

def LeerMonitor():
	#lee el valor del Monitor
	voltsMonitor = ReadVoltsFromMCP(1)
	return voltsMonitor

def LeerTempInterna():
	# lee el valor de la temp interna
	voltsTemp = ReadVoltsFromMCP(2)
	if voltsTemp > 0:
		 R_ntc_int = (V_ti() / voltsTemp)*R_aux() - R_aux()
		 if R_ntc_int > 0:
			  T_int = (1 / (math.log( R_ntc_int/R_0(),10) / B_0() + 1/298.5) - 273.5)
		 else:
			  T_int = 99
	else:
		 T_int = 99
	return T_int

def LeerTempExterna():
	# lee el valor de la temp externa
	voltsTemp = ReadVoltsFromMCP(3)
	if voltsTemp > 0:
		 R_ntc_ext = (V_te() / voltsTemp)*R_aux() - R_aux()
		 if R_ntc_ext > 0:
			  T_ext = (1 / (math.log( R_ntc_ext/R_0(),10) / B_0() + 1/298.5) - 273.5)
		 else:
			  T_ext = 99
	else:
		 T_ext = 99
	return T_ext

def MostrarError(dispositivoFallado, detalles):
	Guardar('El dispositivo: ' + str(dispositivoFallado) + ' ha fallado. Detalles: '+ detalles +'. El programa se terminara ahora.')
	# sys.exit()

def EsperarTemperaturaEstable():
	return
	# esta funcion espera que la temperatura sea superior a TEMPESTABLE para continuar el programa, no activa todavia
	tempInterna = LeerTempInterna()
	#print 'temperatura=' + str(tempInterna)
	while tempInterna < TEMPESTABLE():
		#print tempInterna, TEMPESTABLE()
		tempInterna = LeerTempInterna()
		time.sleep(5)
	
def ActivarBomba(duracion):
	#duracion: duracion de la bomba encendida en segundos
	Guardar("Encendiendo Bomba")
	ActivarGPIO(13,True)   
	time.sleep(duracion)
	Guardar("Apagando Bomba")
	ActivarGPIO(13,False)

def BombeoInicial():   
# 4. BOMBEAR 1 MINUTO, PARAR 1 MINUTO, BOMBEAR 1 MINUTO, PARAR
	ActivarBomba(60)   
	time.sleep(60)
	ActivarBomba(60) ## 60

def Guardar(actividad):
	now = datetime.datetime.now()
	f = open('/home/pi/simca/simca.log','a')
	f.write(time.strftime(actividad + ";   " + "%H:%M:%S" + "  %d-%m-%Y" + '\r\n'))
	f.close()
	time.sleep(1)

def GuardarDatos(linea):   
	f = open("/home/pi/simca/data/" + archivo,'a')
	# print 'guardando la siguiente linea: '
	#Guardar(linea)
	f.write(linea)
	f.close()

def FormatearDatos(horaDecimal,detectorIR, detectorUV, monitorIR, monitorUV, tempInterna, tempExterna):
	now = datetime.datetime.now()
	if horaDecimal > 10:
		a1 = str("{:.5f}".format(horaDecimal))
	else:  
		a1 = str("{:6f}".format(horaDecimal))

	if tempInterna >= 10:
		a2 =  str("{:.5f}".format(tempInterna)) 
	elif tempInterna < 0 and tempInterna > -10:
		a2 =  str("{:.5f}".format(tempInterna))       
	elif tempInterna < -10.0:
		a2 =  str("{:.4f}".format(tempInterna))       
	else: 
		a2 =  str("{:.6f}".format(tempInterna)) 

	if tempExterna >= 10:
		a3 =  str("{:.5f}".format(tempExterna)) 
	elif tempExterna < 0 and tempExterna > -10:
		a3 =  str("{:.5f}".format(tempExterna)) 
	elif tempExterna < -10:
		a3 =  str("{:.4f}".format(tempExterna)) 
	else:
		a3 =  str("{:.6f}".format(tempExterna))
	
	dat = a1 +'    '+ str("{:.6f}".format(detectorIR)) +'    '+ str("{:.6f}".format(monitorIR)) +'    '+ str("{:.6f}".format(detectorUV)) +'    '+ str("{:.6f}".format(monitorUV)) +'    ' + a2 + '    ' + a3 + '    '+ now.strftime('%X') +'    '+ now.strftime('%d-%m-%Y')
	datos = dat + "\r\n"
	Guardar(dat)
	return datos
  
def ComenzarSimca():
	BorrarArchivo()
	Guardar("Comenzando Simca. Si desea terminar el programa, lance killsimca.py")
	Guardar("Archivo = " + archivo)
	#print "antes de leer temperatura"
	atem = LeerTempInterna()
	#print "Temperatura ", atem
	Guardar("Temperatura interna al inicio del monitoreo = " + str(atem))
	LeerArchivoConf()
	ActivarGPIO(5,True) #enciende el LED IR
	time.sleep(2)  #10
	#while True:
	valorDetector = LeerDetector()   
	valorMonitor = LeerMonitor()
	ActivarGPIO(5,False)
	if valorDetector == 0:
		MostrarError('detector', 'Detector mide un valor nulo')
	if valorMonitor == 0:
		MostrarError('monitor', 'Monitor mide un valor nulo')
	EsperarTemperaturaEstable()
	BombeoInicial()

def syslog_trace(trace):
	#Log a python stack trace to syslog
	# This file is in /var/log/syslog
	log_lines = trace.split('\n')
	for line in log_lines:
		if len(line):
			syslog.syslog(line)

def main():
	ComenzarSimca()
	header = "Hora_Dec    Det_IR      Mon_IR      Det_UV      Mon_UV      T_int       T_ext       Hora        Fecha \r\n"
	if os.path.exists("/home/pi/simca/data/" + archivo):
			b = 1
	else:
			GuardarDatos(header)
	Guardar("Entrando en programa principal")
	while True:
		now = datetime.datetime.now()   
		if now.minute in [0,15,30,45]:
			Guardar('Activando Bomba')
			ActivarBomba(TBOMBA())
			Guardar('Esperando 13 minutos')
			time.sleep(13*60)  ## 13*60
			Guardar('Encendiendo LED Infrarrojo durante 30 segundos')
			ActivarGPIO(5, True)
			time.sleep(30) ## 30
			Guardar('Leyendo datos IR')
			detectorIR, monitorIR = LeerDetectorYMonitorPromedio()
			Guardar('Apagando LED Infrarrojo')
			ActivarGPIO(5, False)
			Guardar('Encendiendo LED UV durante 30 segundos')
			ActivarGPIO(6, True)
			time.sleep(30) ## 30
			Guardar('Leyendo datos UV')
			detectorUV, monitorUV = LeerDetectorYMonitorPromedio()
			Guardar('Apagando LED UV')
			ActivarGPIO(6,False)
			Guardar('Leyendo temperaturas')
			tempInterna = LeerTempInterna()
			tempExterna = LeerTempExterna()
			Guardar('Guardando datos')
			horaDecimal = float(now.hour + float(now.minute)/60 + float(now.second)/3600)
			#datos = str(horaDecimal) +';'+ str(detectorIR) +';'+ str(monitorIR) +';'+ str(detectorUV) +';'+ str(monitorUV) +';'+ str(tempInterna) +';'+ str(tempExterna) +';'+ now.strftime('%X') +';'+ now.strftime('%d/%m/%Y') + '\n'
			datos = FormatearDatos(horaDecimal, detectorIR, detectorUV, monitorIR, monitorUV, tempInterna, tempExterna)
			Guardar(datos)
			GuardarDatos(datos)
	

if __name__ == '__main__':
	try:   
		archivo = GenerarNombreArchivo() # Genera el nombre del archivo
		main()
	except:
		syslog_trace(traceback.format_exc())


