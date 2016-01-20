Protocol: http://www.hivemq.com/blog/how-to-get-started-with-mqtt
Hosting: https://www.openshift.com/

example of simca file

DateTime	Data1	Data2	Temp1	Temp2
2015/12/24 10:00	3.22 	2.10 	25.30 	17.13

### ESTIMATED BYTES SENT:
Bytes:
It is a string of length 41 - 5 spaces - 7 characters with no info = 29
String of length 29 using UTF-8: 11*29 = 319
Header size of MQTT: 20
Total message every 15 minutes: 339 bytes

Bytes sent per hour: 1356 ~ 1 kB per hour

### REAL BYTES SENT:
## Using ifconfig, sending one line of data, corresponding to a string of length 31
## Sending a UTF-8 string of length 31: 31*11 = 341 bytes

BEFORE
rx bytes: 16489, tx bytes: 18073

AFTER
rx bytes: 17281, tx: 18973

BYTES:
Received: 792, Transmitted: 900

### TEST CON MODEM CARGADO
Se le cargo 6000 pesos el 15/01/2016 a las 15:06
Veremos si se conecta y cuanto dura
a las 15:16 pedi que lo reiniciaran pues no mostraba datos
El Lo reinició a las 16:14
A las 16:19 apareció el primer dato



### MONITOR DATA USAGE WITH NETHOGS
## sudo nethogs ppp0

### POWER CONSUMPTION
Raspi:
power supply: 5V
minimum current: 600 - 1800mA
source: raspi regulatory compliance and safety information

Huawei E173 3G usb modem stick:
Maximum power consumption 2.5W
Power supply:5v
=> 500 mA
source: www.simplytech.eu/product_info.php%3Fproducts_id%3D30+&cd=1&hl=en&ct=clnk&gl=cl

### MODEM INFO

Para que functione el modem Huawei E3131 con chip Entel (suponiendo que ya funciona con el Huawei E173s-g Movistar):
1- Agregar archivo de configuracion "12d1:15ca" (incluido en esta carpeta) al archivo tar "/usr/share/usb_modeswitch/configPack.tar.gz"
2- Agregar las siguientes lineas al archivo "/lib/udev/rules.d/40-usb_modeswitch.rules", en la seccion Huawei:
	# Huawei E3131 (Entel)
	ATTRS{idVendor}=="12d1", ATTRS{idProduct}=="15ca", RUN+="usb_modeswitch '%b/%k'"
3- Fin. Use el comando "lsusb" para confirmar que el dispositivo Huawei dice "LTE/UMTS/GSM Modem/Networkcard"


Entel: 12d1:15ca
Modelo: E3131
bInterfaceClass:  "mass storage"


Movistar: 12d1:1c23
Modelo: E173s-6
bInterfaceClass: Vendor Specific Class

Message content.
Try with:
55534243123456780000000000000011062000000100000000000000000000 (http://carlini.es/internet-movil-con-el-modem-3g-usb-huawei-e173u-2-en-la-raspberry-pi/)
55534243123456780000000000000011060000000000000000000000000000 (http://www.draisberghof.de/usb_modeswitch/bb/viewtopic.php?f=4&t=1295)


19/01/2016 21h: 791 MB
Verificar el 20 en la mañana: 791 MB tambien

Ver si hay baja de voltaje cuando modem se conecta a internet
guardar datos cada 3 minutos, mandar datos cada 6 minutos
hacer algo cuando el espacio en disco se empieza a acabar en el raspi

