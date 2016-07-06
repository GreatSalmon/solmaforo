## Solmaforo

Python tool to control and send data from a UV radiation sensor. Works with a Raspberry Pi A+ or B+.

Voltage levels coming from the sensor are converted to a digital signal and interpreted using the RPi.GPIO library.

A line of data is created with a timestamp and the current UV level.

Data is sent to the Internet using an Ethernet cable (Raspi B+), or a Wifi or 3G dongle.

The data is sent using the MQTT protocol. The data arrives to a web server (see my other project, clientemqtt)
