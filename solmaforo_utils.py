import datetime
import socket
import fcntl
import struct

LogFile = "/home/pi/solmaforo_logs/logs.log"
BufferFile = "/home/pi/solmaforo_logs/buffer"

def GetConfigParam(param):
	with open(ConfigFile, 'r') as config:
		line = config.readline()
		while line != "":
			split = line.split('=')
			if split[0] == param:
				return split[1].strip().lower()
			line = config.readline()
	raise "param not found: " + param


def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])

def Log(msg):
	print(msg.strip())
	with open(LogFile, "a") as logfile:
		logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "; " + msg + "\n")

def GetAddresses():
	#Try to get PPP0 (mobile) address
	#If it doesn't work, get Local ethernet address
	try:
		myMAC = open('/sys/class/net/eth0/address').read().strip()
		myIP = get_ip_address("eth0")
	except IOError as e:
		Log(str(e))
		try:
			myMAC = open('/sys/class/net/wwan0/address').read().strip()
			myIP = get_ip_address("ppp0")
		except IOError as e:
			Log(str(e))
			myMAC = "No MAC"
			myIP = "No IP"

	return myMAC, myIP